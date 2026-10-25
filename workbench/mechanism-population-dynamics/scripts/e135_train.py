"""E135 single FP32 MoE student, fixed native H->Y regression plus original aux."""
from __future__ import annotations
import argparse, contextlib, copy, json, random, tempfile, time
from pathlib import Path
import numpy as np
import torch
import e135_common as c

assets, base, WB = c.assets, c.base, c.WB
COMMON_SHA = "2a84af164ad55853f171effd345c2719c760219119b9200e8cb47768d435a989"
PREPARE_SHA = "47db49fcca8e2d2443741baded5b8fc85d3a0bfe7cb20573aa69009f443df034"


def preflight(args, *, _self_test_only=False, full_hash=False):
    if assets.sha(WB / "scripts/e135_common.py") != COMMON_SHA: raise ValueError("Frozen E135 common helper differs")
    c.source_proof(); manifest = c.cache_manifest(args.cache_root, full_hash=full_hash)
    dims = manifest["dimensions"]
    if not _self_test_only:
        if dims != c.DIMS or manifest["prepare_proof"]["driver_sha256"] != PREPARE_SHA or manifest["prepare_proof"]["common_sha256"] != COMMON_SHA:
            raise ValueError("Registered cache dimensions/preparation source differ")
        if manifest["splits"]["train"]["positions"] != 8_388_608: raise ValueError("Expected exact8,388,608 source positions")
    arrays = {split: {key: np.load(args.cache_root / f"{split}_{key}.npy", mmap_mode="r", allow_pickle=False) for key in ("H", "Y")} for split in ("train", "held")}
    count = arrays["train"]["H"].shape[0]; orders = np.load(args.cache_root / "epoch_orders.npy", allow_pickle=False)
    if orders.shape != (4, count) or any(not np.array_equal(np.sort(order), np.arange(count)) for order in orders): raise ValueError("Expected exactly four full fixed permutations")
    rng = np.random.default_rng(135)
    if not np.array_equal(orders, np.stack([rng.permutation(count) for _ in range(4)])): raise ValueError("Registered epoch order differs")
    for split in arrays:
        shape = (len(arrays[split]["H"]), dims["batch_size"], dims["seq_len"], dims["hidden"])
        if any(value.shape != shape or value.dtype != np.uint16 for value in arrays[split].values()): raise ValueError("BF16-bit cache shape/dtype differs")
    energy = manifest["splits"]["train"]["energy_mean"]
    if not np.isfinite(energy) or energy <= 0: raise ValueError("Global training energy denominator undefined")
    return manifest, arrays, orders, dims


def amp(device): return torch.autocast(device.split(":")[0], dtype=torch.bfloat16)


def gradient_audit(normalized, lb, z, student, loads):
    selected = int(loads.argmax()); gate = student.block.gate.weight; expert = student.block.experts[selected].up_proj.weight
    result = {"selected_expert": selected, "scope": "Connected finite gradients; zero auxiliary gradient is valid at stationary/uniform load"}
    for name, objective, parameters in (("normalized_output_MSE", normalized, [gate, expert]), ("LB", lb, [gate]), ("z", z, [gate])):
        gradients = torch.autograd.grad(objective, parameters, retain_graph=True, allow_unused=True)
        if any(value is None or not torch.isfinite(value).all() for value in gradients): raise RuntimeError(f"Disconnected/nonfinite {name} gradient")
        result[name + "_gradient_norms"] = [float(value.float().norm()) for value in gradients]
    return result


@torch.no_grad()
def evaluate_split(student, arrays, energy, split_energy, device, budget):
    squared, elements = 0., 0
    for index in range(len(arrays["H"])):
        budget.check(); hidden = c.from_bits(arrays["H"][index], device); target = c.from_bits(arrays["Y"][index], device)
        with amp(device): prediction = student(hidden)
        difference = prediction.float() - target.float()
        if not torch.isfinite(difference).all(): raise RuntimeError("Nonfinite function-evaluation output")
        squared += float(difference.double().square().sum()); elements += difference.numel(); student.last_router_logits = None
    mse = squared / elements
    return {"positions": elements // arrays["H"].shape[-1], "elements": elements, "MSE": mse,
            "normalized_by_fixed_training_energy": mse / energy, "relative_to_own_split_teacher_energy": mse / split_energy if split_energy > 0 else None}


def train(args, *, _self_test_only=False):
    manifest, arrays, orders, dims = preflight(args, _self_test_only=_self_test_only)
    count, steps = len(orders[0]), int(orders.size)
    if not _self_test_only and (count, steps) != (1024, 4096): raise ValueError("Registered four-epoch4096 schedule required")
    if _self_test_only and args.device != "cpu": raise ValueError("_self_test_only is CPU-only")
    if not _self_test_only: gpu = c.select_gpu(args.physical_gpu)
    else: gpu = {"device": "cpu"}
    output = args.output; output.mkdir(parents=True, exist_ok=True)
    if (output / "checkpoint.pt").exists() and not args.resume: raise ValueError("Existing student state requires explicit --resume")
    energy = manifest["splits"]["train"]["energy_mean"]
    scientific = {"experiment": "E135", "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"),
        "cache_root": str(args.cache_root), "dimensions": dims, "seed": 1, "init_std": .02, "steps": steps, "epochs": 4,
        "lr": 3e-4, "warmup_fraction": .1, "weight_decay": .1, "betas": [.9, .95], "eps": 1e-8,
        "lb_coef": .01, "z_coef": .001, "grad_clip": 1., "normalizer": energy,
        "driver_sha256": assets.sha(__file__), "common_sha256": COMMON_SHA, "CPU_test": _self_test_only}
    config_hash = base.digest_json(scientific); previous = assets.read(output / "training_summary.json") if args.resume else None
    lr_args = argparse.Namespace(steps=steps, lr=3e-4, warmup_fraction=.1); args.device = "cpu" if _self_test_only else "cuda:0"
    random.seed(1); np.random.seed(1); torch.manual_seed(1)
    with c.Budget(Path(manifest["budget_file"]), "student_train") as budget:
        if args.resume:
            checkpoint = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
            if checkpoint.get("schema") != "E135-student-v1" or checkpoint.get("config_hash") != config_hash: raise ValueError("Student resume configuration/cache differs")
            student = c.bank_from_state(checkpoint["student_state"], args.device, dims=dims); initial_hash = checkpoint["initial_tensor_sha256"]
            step = int(checkpoint["step"]); exposure = np.asarray(checkpoint["cache_batch_counts"], dtype=np.uint32)
        else:
            student = base.TensorMoE(dims["hidden"], dims["expert_size"], dims["experts"], dims["top_k"], .02)
            if any(value.dtype != torch.float32 for value in student.parameters()): raise ValueError("Student master parameters must be FP32")
            initial_hash = c.tensor_state_hash(student.state_dict()); student = student.to(args.device); step = 0; exposure = np.zeros(count, np.uint32)
        if not 0 <= step <= steps or not np.array_equal(exposure, np.bincount(orders.reshape(-1)[:step], minlength=count)):
            raise ValueError("Resume cache exposure prefix differs from immutable epoch orders")
        optimizer = torch.optim.AdamW(student.parameters(), lr=3e-4, betas=(.9, .95), eps=1e-8, weight_decay=.1)
        if args.resume:
            optimizer.load_state_dict(checkpoint["optimizer"]); base.restore_rng(checkpoint["rng"], args); del checkpoint
        history = previous.get("evaluations", []) if previous and previous.get("config_hash") == config_hash else []
        provenance = {"experiment": "E135", "schema": "E135-student-v1", "scientific": scientific, "config_hash": config_hash,
            "initial_tensor_sha256": initial_hash, "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"],
            "cache_manifest_sha256": scientific["cache_manifest_sha256"], "gpu_preflight": gpu,
            "scope": "Single seed1, frozen native function cache; no language labels, teacher expert IDs/router supervision, or output gain"}
        assets.write(output / "provenance.json", provenance)
        def save(path):
            state = student.state_dict()
            c.atomic_torch_save(path, {"schema": "E135-student-v1", "experiment": "E135", "step": step, "planned_steps": steps,
                "student_state": state, "moe": state, "optimizer": optimizer.state_dict(), "rng": base.rng_state(args),
                "config_hash": config_hash, "initial_tensor_sha256": initial_hash, "cache_batch_counts": exposure,
                "cache_manifest_sha256": scientific["cache_manifest_sha256"], "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"]})
        if not args.resume:
            if (output / "initial.pt").exists(): raise FileExistsError("Immutable initial student already exists")
            save(output / "initial.pt"); (output / "initial.pt").chmod(0o444)
        def measure():
            result = {"step": step, "train": evaluate_split(student, arrays["train"], energy, energy, args.device, budget),
                "held": evaluate_split(student, arrays["held"], energy, manifest["splits"]["held"]["energy_mean"], args.device, budget)}
            base.emit("function_MSE", **result); return result
        status, start_step, timings = "running", step, []
        try:
            if not any(row["step"] == step for row in history): history.append(measure())
            with (output / "train_steps.jsonl").open("a" if args.resume else "w") as log:
                while step < steps:
                    if args.max_updates and step - start_step >= args.max_updates: status = "invocation_update_limit"; break
                    budget.check(); update_started = time.monotonic(); epoch_index, position = divmod(step, count); index = int(orders[epoch_index, position])
                    hidden, target = c.from_bits(arrays["train"]["H"][index], args.device), c.from_bits(arrays["train"]["Y"][index], args.device)
                    optimizer.zero_grad(set_to_none=True); rate = base.lr_at(step, lr_args)
                    for group in optimizer.param_groups: group["lr"] = rate
                    with amp(args.device): prediction = student(hidden)
                    mse = (prediction.float() - target.float()).square().mean(); normalized = mse / energy
                    lb, z, loads, _ = student.losses_and_load(); objective = normalized + .01 * lb + .001 * z
                    if not torch.isfinite(objective): raise RuntimeError("Nonfinite registered normalized-MSE+aux objective")
                    if step == 0:
                        assets.write(output / "gradient_audit.json", gradient_audit(normalized, lb, z, student, loads))
                    objective.backward(); student.last_router_logits = None
                    norm = float(torch.nn.utils.clip_grad_norm_(student.parameters(), 1., error_if_nonfinite=True)); optimizer.step(); exposure[index] += 1; step += 1
                    if args.device.startswith("cuda"): torch.cuda.synchronize()
                    seconds = time.monotonic() - update_started; timings.append(seconds)
                    row = {"step": step, "epoch": epoch_index, "within_epoch_position": position, "cache_batch_index": index,
                        "position_exposures": step * dims["batch_size"] * dims["seq_len"], "MSE": float(mse.detach()), "normalized_MSE": float(normalized.detach()),
                        "lb_raw": float(lb.detach()), "z_raw": float(z.detach()), "objective": float(objective.detach()), "lr": rate,
                        "gradient_norm_before_clip": norm, "expert_load": loads.cpu().tolist(), "actual_H_dtype": str(hidden.dtype),
                        "actual_Y_dtype": str(target.dtype), "seconds": seconds, "positions_per_second": dims["batch_size"] * dims["seq_len"] / seconds}
                    log.write(json.dumps(row, allow_nan=False) + "\n"); log.flush(); base.emit("student_update", **{key: value for key, value in row.items() if key != "expert_load"})
                    event_every = 2 if _self_test_only else 512
                    if step % event_every == 0:
                        history.append(measure()); save(output / "checkpoint.pt")
                        assets.write(output / "training_summary.json", {"status": "running", "step": step, "config_hash": config_hash, "evaluations": history})
                if step == steps: status = "complete"
        except Exception as error:
            status = "failed_or_incomplete"; assets.write(output / "failure.json", {"step": step, "error": f"{type(error).__name__}: {error}"}); raise
        finally:
            save(output / "checkpoint.pt")
            result = {"experiment": "E135", "status": status, "step": step, "planned_steps": steps, "config_hash": config_hash,
                "initial_tensor_sha256": initial_hash, "final_tensor_sha256": c.tensor_state_hash(student.state_dict()),
                "cache_manifest_sha256": scientific["cache_manifest_sha256"], "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"],
                "unique_source_positions": manifest["splits"]["train"]["positions"], "position_exposures": step * dims["batch_size"] * dims["seq_len"],
                "cache_batch_exposure_counts": exposure.tolist(), "evaluations": history, "fixed_training_energy": energy,
                "positions_per_second_after_first": dims["batch_size"] * dims["seq_len"] / float(np.mean(timings[1:] or timings)) if timings else None}
            assets.write(output / "training_summary.json", result)
            if args.summary: assets.write(args.summary, result)
    return result


def self_test():
    torch.set_num_threads(1); torch.manual_seed(135)
    with tempfile.TemporaryDirectory(prefix="e135_student_cpu_") as directory:
        root = Path(directory); cache = root / "cache"; cache.mkdir()
        dims = {"hidden": 8, "expert_size": 8, "experts": 4, "top_k": 2, "seq_len": 4, "batch_size": 2}
        teacher = base.TensorMoE(8, 8, 4, 2, .02).bfloat16().eval(); records = {}
        for split, count in (("train", 4), ("held", 2)):
            h = torch.randn(count, 2, 4, 8).bfloat16(); ys = []
            with torch.no_grad(), amp("cpu"):
                for batch in h: ys.append(teacher(batch))
            y = torch.stack(ys); np.save(cache / f"{split}_H.npy", c.bf16_bits(h)); np.save(cache / f"{split}_Y.npy", c.bf16_bits(y))
            records[split] = {"positions": count * 8, "energy_mean": float(y.double().square().mean())}
        rng = np.random.default_rng(135); np.save(cache / "epoch_orders.npy", np.stack([rng.permutation(4) for _ in range(4)]))
        files = {path.name: {"sha256": assets.sha(path), "size_bytes": path.stat().st_size} for path in cache.iterdir()}
        assets.write(cache / "manifest.json", {"schema": "E135-native-function-cache-v1", "status": "complete", "dimensions": dims,
            "files": files, "splits": records, "budget_file": str(root / "budget.json"), "teacher_block_tensor_sha256": c.tensor_state_hash(teacher.state_dict())})
        def make(name, *extra): return parser().parse_args(["--mode", "train", "--cache-root", str(cache), "--output", str(root / name), "--device", "cpu", *extra])
        full = train(make("full"), _self_test_only=True)
        train(make("split", "--max-updates", "3"), _self_test_only=True)
        train(make("split", "--resume", str(root / "split/checkpoint.pt")), _self_test_only=True)
        a, b = [torch.load(root / name / "checkpoint.pt", map_location="cpu", weights_only=False) for name in ("full", "split")]
        parameter_error = max(float((a["student_state"][key] - b["student_state"][key]).abs().max()) for key in a["student_state"])
        optimizer_error = max(float((value - b["optimizer"]["state"][key][name]).abs().max()) for key, values in a["optimizer"]["state"].items() for name, value in values.items() if torch.is_tensor(value))
        assert parameter_error == optimizer_error == 0 and a["optimizer"]["param_groups"] == b["optimizer"]["param_groups"]
        assert torch.equal(a["rng"]["torch"], b["rng"]["torch"]) and np.array_equal(a["cache_batch_counts"], np.full(4, 4))
        assert full["position_exposures"] == 4 * records["train"]["positions"]
        assert torch.load(root / "full/initial.pt", weights_only=False)["step"] == 0
        result = {"passed": True, "CPU_only": True, "parameter_resume_max_error": parameter_error, "optimizer_resume_max_error": optimizer_error,
            "exact_four_pass_exposure_and_bf16_bits": True, "fixed_global_energy_and_schedule": True,
            "driver_sha256": assets.sha(__file__), "common_sha256": COMMON_SHA}
        assets.write(WB / "results/e135/train_self_test.json", result); return result


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "train", "self-test"), default="preflight")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    p.add_argument("--output", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student")); p.add_argument("--resume", type=Path)
    p.add_argument("--summary", type=Path); p.add_argument("--max-updates", type=int, default=0); p.add_argument("--physical-gpu", type=int, default=0)
    p.add_argument("--device", default="cuda:0"); return p


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, arrays, orders, dims = preflight(args, full_hash=True)
        result = {"status": "CPU_preflight_only", "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"), "steps": int(orders.size),
                  "positions": manifest["splits"]["train"]["positions"], "energy": manifest["splits"]["train"]["energy_mean"], "dimensions": dims}
    else: result = train(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
