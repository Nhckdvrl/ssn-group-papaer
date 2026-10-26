"""E139 paired free-router students: same expert initials as E138, original E135 objective."""
from __future__ import annotations
import argparse, fcntl, json, random, socket, tempfile, time
from pathlib import Path
from unittest import mock
import numpy as np
import torch
import e135_common as c
import e135_train as source
import e138_train as fixed

assets, base, WB = c.assets, c.base, c.WB
SOURCE_SHA = "8343f7e87b7ec8a1e027d3ec83bb3d2d7bfd649424a453ba9cc3e53ae3368cb7"
FIXED_SHA = "65840e0c3befd7ac4c68ccbf9fdd3bdee946f4e3b8067074b9e5c2d632716200"
CACHE_SHA = "2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43"


class Budget(c.Budget):
    def __init__(self, path, phase): super().__init__(path, phase, limit=5400.)
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E139", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state.get("experiment") != "E139" or state["host"] != socket.gethostname():
                raise ValueError("E139 requires its own node-local additive 5400-second ledger")
            result = operation(state); assets.write(self.path, state); return result
    def check(self):
        consumed = self.update(lambda state: state["completed_seconds"] + sum(time.monotonic() - value["started"] for value in state["active"].values()))
        if consumed >= 5400: raise TimeoutError("E139 1.5-GPU-hour aggregate budget exhausted")
        return consumed


expert_hash, gate_hash = fixed.expert_hash, fixed.gate_hash


def seeded_bank(seed, dims):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    return base.TensorMoE(dims["hidden"], dims["expert_size"], dims["experts"], dims["top_k"], .02)


def include_device_rng(rng, device, resume):
    if device.startswith("cuda") and not resume:
        rng["cuda"] = torch.cuda.get_rng_state_all()
    return rng


def preflight(args, *, _self_test_only=False, full_hash=False):
    if assets.sha(WB / "scripts/e135_train.py") != SOURCE_SHA or assets.sha(WB / "scripts/e138_train.py") != FIXED_SHA:
        raise ValueError("Frozen E135/E138 source differs")
    manifest, arrays, orders, dims = source.preflight(args, _self_test_only=_self_test_only, full_hash=full_hash)
    manifest_sha = assets.sha(args.cache_root / "manifest.json")
    if not _self_test_only and manifest_sha != CACHE_SHA: raise ValueError("Exact registered native H/Y cache required")
    if args.seed not in (0, 2): raise ValueError("Only new E139 seeds0/2; observed E135 seed1 is reused")
    if Path(args.budget_file).resolve() == Path(manifest["budget_file"]).resolve() or Path(args.budget_file).resolve() == Path(args.e138_budget_file).resolve():
        raise ValueError("E139 ledger must be separate from E135 and E138")
    old_budget = assets.read(args.budget_file)
    if old_budget and old_budget.get("experiment") != "E139": raise ValueError("E139 ledger identity differs")
    reference = torch.load(args.reference_initial, map_location="cpu", mmap=True, weights_only=False)
    if (reference.get("experiment"), reference.get("schema"), reference.get("step")) != ("E135", "E135-student-v1", 0):
        raise ValueError("Observed free seed1 initial checkpoint identity differs")
    if reference.get("cache_manifest_sha256") != manifest_sha or reference["optimizer"]["state"] or np.any(reference["cache_batch_counts"]):
        raise ValueError("Observed free seed1 initial cache/optimizer/exposure differs")
    reference_state = reference["student_state"]
    reference_hash = c.tensor_state_hash(reference_state)
    if reference_hash != reference["initial_tensor_sha256"] or any(value.dtype != torch.float32 for value in reference_state.values()):
        raise ValueError("Observed free seed1 full FP32 tensor proof differs")
    seed1 = seeded_bank(1, dims)
    seed1_hash = c.tensor_state_hash(seed1.state_dict())
    if seed1_hash != reference_hash: raise ValueError("Seed1 same-constructor full state differs from observed E135 pilot")
    del seed1, reference_state, reference
    bank = seeded_bank(args.seed, dims); state = bank.state_dict(); rng = base.rng_state(argparse.Namespace(device="cpu"))
    if any(value.dtype != torch.float32 for value in state.values()): raise ValueError("Free student FP32 masters required")
    fixed_path = args.fixed_initial or Path(f"/tmp/xiang-moe-20261025/e138_seed{args.seed}/initial.pt")
    fixed_cp = torch.load(fixed_path, map_location="cpu", mmap=True, weights_only=False)
    if (fixed_cp.get("experiment"), fixed_cp.get("schema"), fixed_cp.get("seed"), fixed_cp.get("step")) != ("E138", "E138-fixed-assignment-student-v1", args.seed, 0):
        raise ValueError("Matched E138 fixed initial checkpoint identity differs")
    if fixed_cp.get("cache_manifest_sha256") != manifest_sha or fixed_cp["optimizer"]["state"] or np.any(fixed_cp["cache_batch_counts"]):
        raise ValueError("Matched E138 initial cache/optimizer/exposure differs")
    fixed_state = fixed_cp["student_state"]
    if (expert_hash(state) != expert_hash(fixed_state) or expert_hash(state) != fixed_cp["initialization"]["initial_expert_only_sha256"]
            or c.tensor_state_hash(fixed_state) != fixed_cp["initialization"]["oracle_initial_full_tensor_sha256"]):
        raise ValueError("Paired expert initialization or fixed initial tensor proof differs")
    if gate_hash(state) == gate_hash(fixed_state): raise ValueError("Free gate unexpectedly equals copied teacher gate")
    proof = {"initialization_kind": "E135 free TensorMoE constructor, no teacher gate copy", "expert_seed": args.seed,
        "free_initial_full_tensor_sha256": c.tensor_state_hash(state), "free_initial_expert_only_sha256": expert_hash(state),
        "free_initial_gate_sha256": gate_hash(state), "matched_fixed_initial": str(fixed_path),
        "matched_fixed_initial_sha256": assets.sha(fixed_path), "matched_fixed_expert_only_sha256": expert_hash(fixed_state),
        "observed_seed1_initial": str(args.reference_initial), "observed_seed1_initial_sha256": assets.sha(args.reference_initial),
        "observed_seed1_full_tensor_sha256": reference_hash, "reconstructed_seed1_full_tensor_sha256": seed1_hash,
        "cache_manifest_sha256": manifest_sha, "source_trainer_sha256": SOURCE_SHA, "fixed_trainer_sha256": FIXED_SHA,
        "scope": "Experts exactly pair with fixed group seed-by-seed; free gate is independently initialized and trained. Seed1 is an observed reused pilot."}
    return manifest, arrays, orders, dims, state, rng, proof


def train(args, *, _self_test_only=False):
    if args.output is None: args.output = Path(f"/tmp/xiang-moe-20261025/e139_seed{args.seed}")
    manifest, arrays, orders, dims, initial, rng, proof = preflight(args, _self_test_only=_self_test_only)
    steps, count = int(orders.size), orders.shape[1]
    if not _self_test_only and (steps, count) != (4096, 1024): raise ValueError("Exact4096/four-pass training required")
    if _self_test_only and args.device != "cpu": raise ValueError("CPU self-test may not initialize GPU")
    gpu = {"device": "cpu"} if _self_test_only else c.select_gpu(args.physical_gpu)
    args.device = "cpu" if _self_test_only else "cuda:0"; output = args.output; output.mkdir(parents=True, exist_ok=True)
    include_device_rng(rng, args.device, args.resume)
    if (output / "checkpoint.pt").exists() and not args.resume: raise ValueError("Existing E139 checkpoint requires explicit --resume")
    scientific = {"experiment": "E139", "seed": args.seed, "initialization": proof, "dimensions": dims, "steps": steps, "epochs": 4,
        "fixed_training_energy": manifest["splits"]["train"]["energy_mean"], "optimizer": "fresh full-model AdamW(.9,.95),eps1e-8,wd.1,clip1",
        "lr": 3e-4, "warmup_fraction": .1, "lb_coef": .01, "z_coef": .001, "gate_frozen": False,
        "driver_sha256": assets.sha(__file__), "budget_file": str(args.budget_file), "CPU_test": _self_test_only,
        "cohort": {"new_seeds": [0, 2], "observed_pilot_seed": 1, "population_weights": [1/3, 1/3, 1/3]}}
    config_hash = base.digest_json(scientific); previous = assets.read(output / "training_summary.json") if args.resume else None
    energy = manifest["splits"]["train"]["energy_mean"]; lr_args = argparse.Namespace(steps=steps, lr=3e-4, warmup_fraction=.1)
    with Budget(args.budget_file, f"train_seed{args.seed}") as budget:
        if args.resume:
            cp = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
            if cp.get("schema") != "E139-free-routing-student-v1" or cp.get("config_hash") != config_hash or cp.get("seed") != args.seed:
                raise ValueError("E139 resume identity/config differs")
            student = c.bank_from_state(cp["student_state"], args.device, dims=dims); step = int(cp["step"])
            exposure = np.asarray(cp["cache_batch_counts"], dtype=np.uint32)
        else:
            student = c.bank_from_state(initial, args.device, dims=dims); step = 0; exposure = np.zeros(count, np.uint32)
        if not 0 <= step <= steps or not np.array_equal(exposure, np.bincount(orders.reshape(-1)[:step], minlength=count)):
            raise ValueError("E139 cache exposure prefix differs from immutable order")
        if not all(value.requires_grad for value in student.parameters()): raise ValueError("Free router and experts must all train")
        optimizer = torch.optim.AdamW(student.parameters(), lr=3e-4, betas=(.9, .95), eps=1e-8, weight_decay=.1)
        if args.resume: optimizer.load_state_dict(cp["optimizer"]); base.restore_rng(cp["rng"], args); del cp
        else: base.restore_rng(rng, args)
        history = previous.get("evaluations", []) if previous and previous.get("config_hash") == config_hash else []
        provenance = {"experiment": "E139", "schema": "E139-free-routing-student-v1", "scientific": scientific, "config_hash": config_hash,
            "initialization": proof, "trainable_parameters": [name for name, value in student.named_parameters() if value.requires_grad],
            "gpu_preflight": gpu, "scope": "Paired free-router treatment: same experts/cache/target/optimizer budget as fixed group; gate information, auxiliary gradients, full clip and decay coupling jointly differ."}
        assets.write(output / "provenance.json", provenance)
        def save(path):
            state = student.state_dict()
            c.atomic_torch_save(path, {"schema": "E139-free-routing-student-v1", "experiment": "E139", "seed": args.seed, "step": step,
                "student_state": state, "moe": state, "optimizer": optimizer.state_dict(), "rng": base.rng_state(args),
                "config_hash": config_hash, "cache_manifest_sha256": proof["cache_manifest_sha256"],
                "initialization": proof, "cache_batch_counts": exposure})
        if not args.resume:
            if (output / "initial.pt").exists(): raise FileExistsError("Immutable E139 initial already exists")
            save(output / "initial.pt"); (output / "initial.pt").chmod(0o444)
        def measure():
            row = {"step": step, "train": source.evaluate_split(student, arrays["train"], energy, energy, args.device, budget),
                "held": source.evaluate_split(student, arrays["held"], energy, manifest["splits"]["held"]["energy_mean"], args.device, budget)}
            base.emit("E139_MSE", **row); return row
        status, start_step, times = "running", step, []
        try:
            if not any(row["step"] == step for row in history): history.append(measure())
            with (output / "train_steps.jsonl").open("a" if args.resume else "w") as log:
                while step < steps:
                    if args.max_updates and step - start_step >= args.max_updates: status = "invocation_update_limit"; break
                    budget.check(); started = time.monotonic(); epoch, position = divmod(step, count); index = int(orders[epoch, position])
                    hidden, target = c.from_bits(arrays["train"]["H"][index], args.device), c.from_bits(arrays["train"]["Y"][index], args.device)
                    optimizer.zero_grad(set_to_none=True); lr = base.lr_at(step, lr_args)
                    for group in optimizer.param_groups: group["lr"] = lr
                    with source.amp(args.device): prediction = student(hidden)
                    mse = (prediction.float() - target.float()).square().mean(); normalized = mse / energy
                    lb, z, loads, _ = student.losses_and_load(); objective = normalized + .01 * lb + .001 * z
                    if not torch.isfinite(objective): raise RuntimeError("Nonfinite registered E135 normalized MSE+aux objective")
                    if step == 0: assets.write(output / "gradient_audit.json", source.gradient_audit(normalized, lb, z, student, loads))
                    objective.backward(); student.last_router_logits = None
                    norm = float(torch.nn.utils.clip_grad_norm_(student.parameters(), 1., error_if_nonfinite=True)); optimizer.step()
                    exposure[index] += 1; step += 1
                    if args.device.startswith("cuda"): torch.cuda.synchronize()
                    seconds = time.monotonic() - started; times.append(seconds)
                    row = {"step": step, "epoch": epoch, "within_epoch_position": position, "cache_batch_index": index,
                        "position_exposures": step * dims["batch_size"] * dims["seq_len"], "MSE": float(mse.detach()),
                        "normalized_MSE": float(normalized.detach()), "lb_raw": float(lb.detach()), "z_raw": float(z.detach()),
                        "objective": float(objective.detach()), "lr": lr, "gradient_norm_before_clip": norm,
                        "expert_load": loads.cpu().tolist(), "actual_H_dtype": str(hidden.dtype), "actual_Y_dtype": str(target.dtype),
                        "seconds": seconds, "positions_per_second": dims["batch_size"] * dims["seq_len"] / seconds}
                    log.write(json.dumps(row, allow_nan=False) + "\n"); log.flush()
                    base.emit("E139_update", **{key: value for key, value in row.items() if key != "expert_load"})
                    if step % (2 if _self_test_only else 512) == 0:
                        history.append(measure()); save(output / "checkpoint.pt")
                        assets.write(output / "training_summary.json", {"status": "running", "step": step, "config_hash": config_hash, "evaluations": history})
                if step == steps: status = "complete"
        except Exception as error:
            status = "failed_or_incomplete"; assets.write(output / "failure.json", {"step": step, "error": f"{type(error).__name__}: {error}"}); raise
        finally:
            save(output / "checkpoint.pt")
            result = {"experiment": "E139", "seed": args.seed, "status": status, "step": step, "planned_steps": steps,
                "expected_MSE_event_steps": list(range(0, steps + 1, 2 if _self_test_only else 512)), "config_hash": config_hash,
                "initialization": proof, "final_tensor_sha256": c.tensor_state_hash(student.state_dict()),
                "final_expert_only_sha256": expert_hash(student.state_dict()), "final_gate_sha256": gate_hash(student.state_dict()),
                "cache_batch_exposure_counts": exposure.tolist(), "position_exposures": step * dims["batch_size"] * dims["seq_len"],
                "evaluations": history, "positions_per_second_after_first": dims["batch_size"] * dims["seq_len"] / float(np.mean(times[1:] or times)) if times else None}
            assets.write(output / "training_summary.json", result)
            if args.summary: assets.write(args.summary, result)
    return result


def self_test():
    with mock.patch.object(torch.cuda, "get_rng_state_all", return_value=[torch.tensor([1], dtype=torch.uint8)]) as mocked:
        assert include_device_rng({"torch": "cpu"}, "cuda:0", None)["cuda"][0].tolist() == [1]
        assert "cuda" not in include_device_rng({"torch": "cpu"}, "cpu", None)
        assert "cuda" not in include_device_rng({"torch": "cpu"}, "cuda:0", Path("checkpoint.pt"))
        assert mocked.call_count == 1
    torch.set_num_threads(1); torch.manual_seed(139)
    with tempfile.TemporaryDirectory(prefix="e139_free_router_cpu_") as directory:
        root = Path(directory); cache = root / "cache"; cache.mkdir()
        dims = {"hidden": 8, "expert_size": 8, "experts": 4, "top_k": 2, "seq_len": 4, "batch_size": 2}
        teacher = base.TensorMoE(8, 8, 4, 2, .02).bfloat16().eval(); c.atomic_torch_save(cache / "teacher_block.pt", {"state": teacher.block.state_dict()})
        records = {}
        for split, count in (("train", 4), ("held", 2)):
            hidden = torch.randn(count, 2, 4, 8).bfloat16()
            with torch.no_grad(), source.amp("cpu"): target = torch.stack([teacher(row) for row in hidden])
            np.save(cache / f"{split}_H.npy", c.bf16_bits(hidden)); np.save(cache / f"{split}_Y.npy", c.bf16_bits(target))
            records[split] = {"positions": count * 8, "energy_mean": float(target.double().square().mean())}
        rng = np.random.default_rng(135); np.save(cache / "epoch_orders.npy", np.stack([rng.permutation(4) for _ in range(4)]))
        files = {path.name: {"sha256": assets.sha(path), "size_bytes": path.stat().st_size} for path in cache.iterdir()}
        e135_budget = root / "e135_budget.json"; e138_budget = root / "e138_budget.json"
        assets.write(e135_budget, {"experiment": "E135", "untouched": True}); assets.write(e138_budget, {"experiment": "E138", "untouched": True})
        manifest = {"schema": "E135-native-function-cache-v1", "status": "complete", "dimensions": dims, "files": files,
            "splits": records, "budget_file": str(e135_budget), "teacher_block_tensor_sha256": c.tensor_state_hash(teacher.block.state_dict())}
        assets.write(cache / "manifest.json", manifest); manifest_sha = assets.sha(cache / "manifest.json")
        seed1 = seeded_bank(1, dims); seed1_state = seed1.state_dict(); seed1_hash = c.tensor_state_hash(seed1_state)
        reference = root / "e135_initial.pt"
        c.atomic_torch_save(reference, {"schema": "E135-student-v1", "experiment": "E135", "step": 0,
            "cache_manifest_sha256": manifest_sha, "student_state": seed1_state, "initial_tensor_sha256": seed1_hash,
            "optimizer": {"state": {}}, "cache_batch_counts": np.zeros(4, np.uint32)})
        seed0 = seeded_bank(0, dims); fixed_state = seed0.state_dict(); expected_experts = expert_hash(fixed_state)
        fixed_state["block.gate.weight"] = teacher.block.gate.weight.float().clone()
        fixed_initial = root / "e138_seed0_initial.pt"
        c.atomic_torch_save(fixed_initial, {"schema": "E138-fixed-assignment-student-v1", "experiment": "E138", "seed": 0, "step": 0,
            "cache_manifest_sha256": manifest_sha, "student_state": fixed_state, "optimizer": {"state": {}},
            "cache_batch_counts": np.zeros(4, np.uint32), "initialization": {
                "initial_expert_only_sha256": expected_experts, "oracle_initial_full_tensor_sha256": c.tensor_state_hash(fixed_state)}})
        originals = {str(path): assets.sha(path) for path in (reference, fixed_initial, e135_budget, e138_budget)}
        def make(name, *extra):
            return parser().parse_args(["--cache-root", str(cache), "--reference-initial", str(reference),
                "--fixed-initial", str(fixed_initial), "--e138-budget-file", str(e138_budget),
                "--output", str(root / name), "--budget-file", str(root / "e139_budget.json"),
                "--device", "cpu", *extra])
        proof = preflight(make("unused"), _self_test_only=True)[-1]
        assert proof["free_initial_expert_only_sha256"] == proof["matched_fixed_expert_only_sha256"]
        assert proof["free_initial_gate_sha256"] != gate_hash(fixed_state) and proof["reconstructed_seed1_full_tensor_sha256"] == seed1_hash
        full = train(make("full"), _self_test_only=True)
        train(make("split", "--max-updates", "3"), _self_test_only=True)
        train(make("split", "--resume", str(root / "split/checkpoint.pt")), _self_test_only=True)
        a, b = [torch.load(root / name / "checkpoint.pt", weights_only=False) for name in ("full", "split")]
        assert all(torch.equal(a["student_state"][key], b["student_state"][key]) for key in a["student_state"])
        assert all(torch.equal(value, b["optimizer"]["state"][key][field]) for key, row in a["optimizer"]["state"].items()
                   for field, value in row.items() if torch.is_tensor(value))
        assert full["status"] == "complete" and full["step"] == 16 and np.array_equal(a["cache_batch_counts"], np.full(4, 4))
        assert gate_hash(a["student_state"]) != proof["free_initial_gate_sha256"]
        assert expert_hash(a["student_state"]) != proof["free_initial_expert_only_sha256"]
        assert all(assets.sha(path) == digest for path, digest in originals.items())
        result = {"passed": True, "CPU_only": True, "paired_expert_initialization": True,
            "free_gate_trainable_and_changed": True, "same_constructor_seed1_full_state": True,
            "exact_resume_parameters_optimizer_RNG": torch.equal(a["rng"]["torch"], b["rng"]["torch"]),
            "four_pass_exposure": True, "old_assets_unchanged": True, "driver_sha256": assets.sha(__file__)}
        assets.write(WB / "results/e139/self_test.json", result); return result


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "train", "self-test"), default="preflight")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    p.add_argument("--fixed-initial", type=Path)
    p.add_argument("--seed", type=int, choices=(0, 2), default=0); p.add_argument("--output", type=Path)
    p.add_argument("--resume", type=Path); p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e139_budget.json"))
    p.add_argument("--e138-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_budget.json"))
    p.add_argument("--summary", type=Path); p.add_argument("--physical-gpu", type=int, default=0)
    p.add_argument("--max-updates", type=int, default=0); p.add_argument("--device", default="cuda:0")
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, arrays, orders, dims, state, rng, proof = preflight(args)
        result = {"status": "CPU_preflight_only", "initialization": proof, "steps": int(orders.size),
                  "energy": manifest["splits"]["train"]["energy_mean"], "driver_sha256": assets.sha(__file__)}
    else: result = train(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
