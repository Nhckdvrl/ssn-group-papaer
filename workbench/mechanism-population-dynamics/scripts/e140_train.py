"""E140 teacher-gate warmstart: same full fixed initial tensors, train all parameters."""
from __future__ import annotations
import argparse, copy, fcntl, json, socket, tempfile, time
from pathlib import Path
from unittest import mock
import numpy as np
import torch
import e135_common as c
import e135_train as source
import e136_train as oracle
import e138_train as fixed

assets, base, WB = c.assets, c.base, c.WB
SOURCE_SHA = "8343f7e87b7ec8a1e027d3ec83bb3d2d7bfd649424a453ba9cc3e53ae3368cb7"
FIXED_SHA = "65840e0c3befd7ac4c68ccbf9fdd3bdee946f4e3b8067074b9e5c2d632716200"
ORACLE_SHA = "8c620871df90c2a10ea9be5b629727ce063164483ab8a0d22cb846e6f6841b55"
CACHE_SHA = "2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43"


class Budget(c.Budget):
    def __init__(self, path, phase): super().__init__(path, phase, limit=5400.)
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E140", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state.get("experiment") != "E140" or state["host"] != socket.gethostname():
                raise ValueError("E140 requires its own node-local additive 5400-second ledger")
            result = operation(state); assets.write(self.path, state); return result
    def check(self):
        consumed = self.update(lambda state: state["completed_seconds"] + sum(time.monotonic() - value["started"] for value in state["active"].values()))
        if consumed >= 5400: raise TimeoutError("E140 1.5-GPU-hour aggregate budget exhausted")
        return consumed


expert_hash, gate_hash = fixed.expert_hash, fixed.gate_hash


def require_source_rng(rng, device, resume):
    if device.startswith("cuda") and not resume and ("cuda" not in rng or len(rng["cuda"]) != 1):
        raise ValueError("Exact fixed initial CUDA RNG for one visible GPU required")
    return rng


def preflight(args, *, _self_test_only=False, full_hash=False):
    if any(assets.sha(WB / "scripts" / name) != expected for name, expected in
            (("e135_train.py", SOURCE_SHA), ("e136_train.py", ORACLE_SHA), ("e138_train.py", FIXED_SHA))):
        raise ValueError("Frozen E135/E136/E138 source differs")
    manifest, arrays, orders, dims = source.preflight(args, _self_test_only=_self_test_only, full_hash=full_hash)
    manifest_sha = assets.sha(args.cache_root / "manifest.json")
    if not _self_test_only and manifest_sha != CACHE_SHA: raise ValueError("Exact registered native H/Y cache required")
    if args.seed not in (0, 1, 2): raise ValueError("Exactly three prospective E140 seeds0/1/2")
    if Path(args.budget_file).resolve() in {Path(path).resolve() for path in
            (manifest["budget_file"], args.e136_budget_file, args.e138_budget_file, args.e139_budget_file)}:
        raise ValueError("E140 ledger must be separate from E135/E136/E138/E139")
    old_budget = assets.read(args.budget_file)
    if old_budget and old_budget.get("experiment") != "E140": raise ValueError("E140 ledger identity differs")
    fixed_path = args.fixed_initial or (args.e136_oracle_dir / "initial.pt" if args.seed == 1 else
        getattr(args, f"e138_seed{args.seed}_dir") / "initial.pt")
    fixed_cp = torch.load(fixed_path, map_location="cpu", mmap=True, weights_only=False)
    expected_identity = (("E136", "E136-assignment-oracle-v1", None, 0) if args.seed == 1 else
        ("E138", "E138-fixed-assignment-student-v1", args.seed, 0))
    if (fixed_cp.get("experiment"), fixed_cp.get("schema"), fixed_cp.get("seed"), fixed_cp.get("step")) != expected_identity:
        raise ValueError("Matched E136/E138 fixed initial checkpoint identity differs")
    if fixed_cp.get("cache_manifest_sha256") != manifest_sha or fixed_cp["optimizer"]["state"] or np.any(fixed_cp["cache_batch_counts"]):
        raise ValueError("Matched fixed initial cache/optimizer/exposure differs")
    original = copy.copy(args); original.budget_file = args.e136_budget_file if args.seed == 1 else args.e138_budget_file
    if args.seed == 1:
        _, _, _, _, expected_state, _, expected = oracle.preflight(original, _self_test_only=_self_test_only)
    else:
        _, _, _, _, expected_state, _, expected = fixed.preflight(original, _self_test_only=_self_test_only)
    state = fixed_cp["student_state"]; digest = c.tensor_state_hash(state)
    if (fixed_cp.get("initialization") != expected or digest != expected["oracle_initial_full_tensor_sha256"]
            or digest != c.tensor_state_hash(expected_state) or any(value.dtype != torch.float32 for value in state.values())
            or gate_hash(state) != expected["oracle_gate_FP32_sha256"]):
        raise ValueError("Exact matched fixed full FP32 initial state/gate/source differs")
    provenance_path = fixed_path.parent / "provenance.json"; provenance = assets.read(provenance_path)
    expected_driver = ORACLE_SHA if args.seed == 1 else FIXED_SHA
    if provenance.get("config_hash") != fixed_cp.get("config_hash") or provenance["scientific"]["driver_sha256"] != expected_driver:
        raise ValueError("Matched fixed initial provenance/driver differs")
    rng = copy.deepcopy(fixed_cp["rng"])
    if not all(key in rng for key in ("torch", "numpy", "python")): raise ValueError("Fixed initial RNG incomplete")
    rng_digest = c.tensor_state_hash({"torch": rng["torch"], **{f"cuda_{i}": value for i, value in enumerate(rng.get("cuda", []))}})
    proof = {"initialization_kind": "Exact complete E136/E138 fixed initial FP32 tensor values; gate now trainable", "expert_seed": args.seed,
        "initial_full_tensor_sha256": digest, "initial_expert_only_sha256": expert_hash(state), "initial_gate_sha256": gate_hash(state),
        "fixed_initial": str(fixed_path), "fixed_initial_sha256": assets.sha(fixed_path),
        "fixed_initial_schema": fixed_cp["schema"], "fixed_initial_experiment": fixed_cp["experiment"],
        "fixed_initial_provenance": str(provenance_path), "fixed_initial_provenance_sha256": assets.sha(provenance_path),
        "fixed_initial_rng_tensor_sha256": rng_digest, "fixed_initial_cuda_rng_states": len(rng.get("cuda", [])),
        "cache_manifest_sha256": manifest_sha, "source_trainer_sha256": SOURCE_SHA, "fixed_trainer_sha256": expected_driver,
        "scope": "Same full initial gate+experts and RNG as matched fixed seed; new E140 full-parameter optimizer/update protocol."}
    return manifest, arrays, orders, dims, state, rng, proof


def train(args, *, _self_test_only=False):
    if args.output is None: args.output = Path(f"/tmp/xiang-moe-20261025/e140_seed{args.seed}")
    manifest, arrays, orders, dims, initial, rng, proof = preflight(args, _self_test_only=_self_test_only)
    steps, count = int(orders.size), orders.shape[1]
    if not _self_test_only and (steps, count) != (4096, 1024): raise ValueError("Exact4096/four-pass training required")
    if _self_test_only and args.device != "cpu": raise ValueError("CPU self-test may not initialize GPU")
    gpu = {"device": "cpu"} if _self_test_only else c.select_gpu(args.physical_gpu)
    args.device = "cpu" if _self_test_only else "cuda:0"; output = args.output; output.mkdir(parents=True, exist_ok=True)
    require_source_rng(rng, args.device, args.resume)
    if (output / "checkpoint.pt").exists() and not args.resume: raise ValueError("Existing E140 checkpoint requires explicit --resume")
    scientific = {"experiment": "E140", "seed": args.seed, "initialization": proof, "dimensions": dims, "steps": steps, "epochs": 4,
        "fixed_training_energy": manifest["splits"]["train"]["energy_mean"], "optimizer": "fresh full-model AdamW(.9,.95),eps1e-8,wd.1,clip1",
        "lr": 3e-4, "warmup_fraction": .1, "lb_coef": .01, "z_coef": .001, "gate_frozen": False,
        "driver_sha256": assets.sha(__file__), "budget_file": str(args.budget_file), "CPU_test": _self_test_only,
        "cohort": {"prospective_seeds": [0, 1, 2], "population_weights": [1/3, 1/3, 1/3]},
        "gate_initialization": "exact native teacher gate from matched fixed initial; trainable"}
    config_hash = base.digest_json(scientific); previous = assets.read(output / "training_summary.json") if args.resume else None
    energy = manifest["splits"]["train"]["energy_mean"]; lr_args = argparse.Namespace(steps=steps, lr=3e-4, warmup_fraction=.1)
    with Budget(args.budget_file, f"train_seed{args.seed}") as budget:
        if args.resume:
            cp = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
            if cp.get("schema") != "E140-native-router-warmstart-v1" or cp.get("config_hash") != config_hash or cp.get("seed") != args.seed:
                raise ValueError("E140 resume identity/config differs")
            student = c.bank_from_state(cp["student_state"], args.device, dims=dims); step = int(cp["step"])
            exposure = np.asarray(cp["cache_batch_counts"], dtype=np.uint32)
        else:
            student = c.bank_from_state(initial, args.device, dims=dims); step = 0; exposure = np.zeros(count, np.uint32)
            if c.tensor_state_hash(student.state_dict()) != proof["initial_full_tensor_sha256"]:
                raise ValueError("E140 initial full parameter tensor differs after module construction")
        if not 0 <= step <= steps or not np.array_equal(exposure, np.bincount(orders.reshape(-1)[:step], minlength=count)):
            raise ValueError("E140 cache exposure prefix differs from immutable order")
        if not all(value.requires_grad for value in student.parameters()): raise ValueError("Free router and experts must all train")
        optimizer = torch.optim.AdamW(student.parameters(), lr=3e-4, betas=(.9, .95), eps=1e-8, weight_decay=.1)
        if args.resume: optimizer.load_state_dict(cp["optimizer"]); base.restore_rng(cp["rng"], args); del cp
        else: base.restore_rng(rng, args)
        history = previous.get("evaluations", []) if previous and previous.get("config_hash") == config_hash else []
        provenance = {"experiment": "E140", "schema": "E140-native-router-warmstart-v1", "scientific": scientific, "config_hash": config_hash,
            "initialization": proof, "trainable_parameters": [name for name, value in student.named_parameters() if value.requires_grad],
            "gpu_preflight": gpu, "scope": "Full initial FP32 parameters/RNG pair exactly with fixed group. All gate/expert parameters train; aux, full clip and decay coupling follow original E135 objective."}
        assets.write(output / "provenance.json", provenance)
        def save(path):
            state = student.state_dict()
            c.atomic_torch_save(path, {"schema": "E140-native-router-warmstart-v1", "experiment": "E140", "seed": args.seed, "step": step,
                "student_state": state, "moe": state, "optimizer": optimizer.state_dict(), "rng": base.rng_state(args),
                "config_hash": config_hash, "cache_manifest_sha256": proof["cache_manifest_sha256"],
                "initialization": proof, "cache_batch_counts": exposure})
        if not args.resume:
            if (output / "initial.pt").exists(): raise FileExistsError("Immutable E140 initial already exists")
            save(output / "initial.pt"); (output / "initial.pt").chmod(0o444)
        def measure():
            row = {"step": step, "train": source.evaluate_split(student, arrays["train"], energy, energy, args.device, budget),
                "held": source.evaluate_split(student, arrays["held"], energy, manifest["splits"]["held"]["energy_mean"], args.device, budget)}
            base.emit("E140_MSE", **row); return row
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
                    base.emit("E140_update", **{key: value for key, value in row.items() if key != "expert_load"})
                    if step % (2 if _self_test_only else 512) == 0:
                        history.append(measure()); save(output / "checkpoint.pt")
                        assets.write(output / "training_summary.json", {"status": "running", "step": step, "config_hash": config_hash, "evaluations": history})
                if step == steps: status = "complete"
        except Exception as error:
            status = "failed_or_incomplete"; assets.write(output / "failure.json", {"step": step, "error": f"{type(error).__name__}: {error}"}); raise
        finally:
            save(output / "checkpoint.pt")
            result = {"experiment": "E140", "seed": args.seed, "status": status, "step": step, "planned_steps": steps,
                "expected_MSE_event_steps": list(range(0, steps + 1, 2 if _self_test_only else 512)), "config_hash": config_hash,
                "initialization": proof, "final_tensor_sha256": c.tensor_state_hash(student.state_dict()),
                "final_expert_only_sha256": expert_hash(student.state_dict()), "final_gate_sha256": gate_hash(student.state_dict()),
                "cache_batch_exposure_counts": exposure.tolist(), "position_exposures": step * dims["batch_size"] * dims["seq_len"],
                "evaluations": history, "positions_per_second_after_first": dims["batch_size"] * dims["seq_len"] / float(np.mean(times[1:] or times)) if times else None}
            assets.write(output / "training_summary.json", result)
            if args.summary: assets.write(args.summary, result)
    return result


def self_test():
    with mock.patch.object(torch.cuda, "get_rng_state_all") as getter:
        ready = {"torch": torch.tensor([1], dtype=torch.uint8), "cuda": [torch.tensor([2], dtype=torch.uint8)]}
        assert require_source_rng(ready, "cuda:0", None) is ready
        assert require_source_rng({"torch": torch.tensor([1], dtype=torch.uint8)}, "cpu", None)
        assert require_source_rng({"torch": torch.tensor([1], dtype=torch.uint8)}, "cuda:0", Path("checkpoint.pt"))
        try: require_source_rng({"torch": torch.tensor([1], dtype=torch.uint8)}, "cuda:0", None)
        except ValueError: pass
        else: raise AssertionError("Missing source CUDA RNG must fail before GPU training")
        getter.assert_not_called()
    torch.set_num_threads(1); torch.manual_seed(140)
    with tempfile.TemporaryDirectory(prefix="e140_native_router_cpu_") as directory:
        root = Path(directory); cache = root / "cache"; cache.mkdir()
        dims = {"hidden": 8, "expert_size": 8, "experts": 4, "top_k": 2, "seq_len": 4, "batch_size": 2}
        teacher = base.TensorMoE(8, 8, 4, 2, .02).bfloat16().eval()
        c.atomic_torch_save(cache / "teacher_block.pt", {"state": teacher.block.state_dict()})
        records = {}
        for split, count in (("train", 4), ("held", 2)):
            hidden = torch.randn(count, 2, 4, 8).bfloat16()
            with torch.no_grad(), source.amp("cpu"): target = torch.stack([teacher(row) for row in hidden])
            np.save(cache / f"{split}_H.npy", c.bf16_bits(hidden)); np.save(cache / f"{split}_Y.npy", c.bf16_bits(target))
            records[split] = {"positions": count * 8, "energy_mean": float(target.double().square().mean())}
        order_rng = np.random.default_rng(135)
        np.save(cache / "epoch_orders.npy", np.stack([order_rng.permutation(4) for _ in range(4)]))
        files = {entry.name: {"sha256": assets.sha(entry), "size_bytes": entry.stat().st_size} for entry in cache.iterdir()}
        budgets = {experiment: root / f"{experiment.lower()}_budget.json" for experiment in ("E135", "E136", "E138", "E139")}
        for experiment, path in budgets.items(): assets.write(path, {"experiment": experiment, "untouched": True})
        manifest = {"schema": "E135-native-function-cache-v1", "status": "complete", "dimensions": dims, "files": files,
            "splits": records, "budget_file": str(budgets["E135"]),
            "teacher_block_tensor_sha256": c.tensor_state_hash(teacher.block.state_dict())}
        assets.write(cache / "manifest.json", manifest); manifest_sha = assets.sha(cache / "manifest.json")
        seed1 = fixed.seeded_bank(1, dims); reference = root / "e135_initial.pt"
        seed1_state = seed1.state_dict()
        c.atomic_torch_save(reference, {"schema": "E135-student-v1", "experiment": "E135", "step": 0,
            "cache_manifest_sha256": manifest_sha, "student_state": seed1_state,
            "initial_tensor_sha256": c.tensor_state_hash(seed1_state), "optimizer": {"state": {}},
            "cache_batch_counts": np.zeros(4, np.uint32), "rng": base.rng_state(argparse.Namespace(device="cpu"))})
        source_dirs = {1: root / "e136_oracle", 0: root / "e138_seed0", 2: root / "e138_seed2"}
        for directory in source_dirs.values(): directory.mkdir()
        def make(seed, name, *extra):
            return parser().parse_args(["--cache-root", str(cache), "--reference-initial", str(reference),
                "--e136-oracle-dir", str(source_dirs[1]), "--e138-seed0-dir", str(source_dirs[0]),
                "--e138-seed2-dir", str(source_dirs[2]), "--e136-budget-file", str(budgets["E136"]),
                "--e138-budget-file", str(budgets["E138"]), "--e139-budget-file", str(budgets["E139"]),
                "--output", str(root / name), "--budget-file", str(root / "e140_budget.json"),
                "--device", "cpu", "--seed", str(seed), *extra])
        for seed in (0, 1, 2):
            helper_args = make(seed, "unused_source")
            helper_args.budget_file = budgets["E136"] if seed == 1 else budgets["E138"]
            if seed == 1:
                _, _, _, _, state, rng, initial_proof = oracle.preflight(helper_args, _self_test_only=True)
                experiment, schema, driver = "E136", "E136-assignment-oracle-v1", ORACLE_SHA
            else:
                _, _, _, _, state, rng, initial_proof = fixed.preflight(helper_args, _self_test_only=True)
                experiment, schema, driver = "E138", "E138-fixed-assignment-student-v1", FIXED_SHA
            folder = source_dirs[seed]; config_hash = f"tiny-{experiment}-{seed}"
            cp = {"schema": schema, "experiment": experiment, "step": 0, "student_state": state,
                "optimizer": {"state": {}}, "rng": rng, "initialization": initial_proof,
                "cache_batch_counts": np.zeros(4, np.uint32), "config_hash": config_hash,
                "cache_manifest_sha256": manifest_sha}
            if seed != 1: cp["seed"] = seed
            c.atomic_torch_save(folder / "initial.pt", cp)
            assets.write(folder / "provenance.json", {"config_hash": config_hash, "scientific": {"driver_sha256": driver}})
        originals = {str(path): assets.sha(path) for path in [reference, *budgets.values(),
            *(folder / "initial.pt" for folder in source_dirs.values())]}
        proofs = {seed: preflight(make(seed, f"unused{seed}"), _self_test_only=True)[-1] for seed in (0, 1, 2)}
        for seed, proof in proofs.items():
            cp = torch.load(source_dirs[seed] / "initial.pt", weights_only=False)
            assert proof["initial_full_tensor_sha256"] == c.tensor_state_hash(cp["student_state"])
            assert proof["initial_gate_sha256"] == gate_hash(cp["student_state"])
        full = train(make(1, "full"), _self_test_only=True)
        train(make(1, "split", "--max-updates", "3"), _self_test_only=True)
        train(make(1, "split", "--resume", str(root / "split/checkpoint.pt")), _self_test_only=True)
        a, b = [torch.load(root / name / "checkpoint.pt", weights_only=False) for name in ("full", "split")]
        initial = torch.load(root / "full/initial.pt", weights_only=False)
        fixed_initial = torch.load(source_dirs[1] / "initial.pt", weights_only=False)
        assert c.tensor_state_hash(initial["student_state"]) == c.tensor_state_hash(fixed_initial["student_state"])
        assert not initial["optimizer"]["state"] and np.all(initial["cache_batch_counts"] == 0)
        assert torch.equal(initial["rng"]["torch"], fixed_initial["rng"]["torch"])
        assert all(torch.equal(a["student_state"][key], b["student_state"][key]) for key in a["student_state"])
        assert all(torch.equal(value, b["optimizer"]["state"][key][field]) for key, row in a["optimizer"]["state"].items()
                   for field, value in row.items() if torch.is_tensor(value))
        assert full["status"] == "complete" and full["step"] == 16
        assert np.array_equal(a["cache_batch_counts"], np.full(4, 4))
        assert gate_hash(a["student_state"]) != proofs[1]["initial_gate_sha256"]
        assert expert_hash(a["student_state"]) != proofs[1]["initial_expert_only_sha256"]
        assert all(assets.sha(path) == digest for path, digest in originals.items())
        result = {"passed": True, "CPU_only": True, "three_exact_fixed_initial_states": True,
            "fresh_full_parameter_optimizer": True, "source_CUDA_rng_required": True, "gate_trainable_and_changed": True,
            "exact_resume_parameters_optimizer_RNG": torch.equal(a["rng"]["torch"], b["rng"]["torch"]),
            "four_pass_exposure": True, "old_assets_unchanged": True, "driver_sha256": assets.sha(__file__)}
        assets.write(WB / "results/e140/self_test.json", result); return result


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "train", "self-test"), default="preflight")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    p.add_argument("--fixed-initial", type=Path)
    p.add_argument("--e136-oracle-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_oracle"))
    p.add_argument("--e138-seed0-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_seed0"))
    p.add_argument("--e138-seed2-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_seed2"))
    p.add_argument("--seed", type=int, choices=(0, 1, 2), default=0); p.add_argument("--output", type=Path)
    p.add_argument("--resume", type=Path); p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e140_budget.json"))
    p.add_argument("--e136-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_budget.json"))
    p.add_argument("--e138-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_budget.json"))
    p.add_argument("--e139-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e139_budget.json"))
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
