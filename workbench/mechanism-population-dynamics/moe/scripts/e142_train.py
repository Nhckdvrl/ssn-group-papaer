"""E142 shared random seed1 gate; each new seed preserves its own E139 experts/RNG."""
from __future__ import annotations
import argparse, copy, fcntl, json, socket, tempfile, time
from pathlib import Path
from unittest import mock
import numpy as np
import torch
import e135_common as c
import e135_train as source
import e139_train as free

assets, base, WB = c.assets, c.base, c.WB
SOURCE_SHA = "8343f7e87b7ec8a1e027d3ec83bb3d2d7bfd649424a453ba9cc3e53ae3368cb7"
FREE_SHA = "93ac8504e21364ca94d6dd5ca18c22493850c41e74b7f0d1cfe12b398e3bcbac"
CACHE_SHA = "2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43"


class Budget(c.Budget):
    def __init__(self, path, phase): super().__init__(path, phase, limit=5400.)
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E142", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state.get("experiment") != "E142" or state["host"] != socket.gethostname():
                raise ValueError("E142 requires its own node-local additive 5400-second ledger")
            result = operation(state); assets.write(self.path, state); return result
    def check(self):
        consumed = self.update(lambda state: state["completed_seconds"] + sum(time.monotonic() - value["started"] for value in state["active"].values()))
        if consumed >= 5400: raise TimeoutError("E142 1.5-GPU-hour aggregate budget exhausted")
        return consumed


expert_hash, gate_hash = free.expert_hash, free.gate_hash


def require_source_rng(rng, device, resume):
    if device.startswith("cuda") and not resume and ("cuda" not in rng or len(rng["cuda"]) != 1):
        raise ValueError("Exact own E139 initial CUDA RNG for one visible GPU required")
    return rng


def preflight(args, *, _self_test_only=False, full_hash=False):
    if assets.sha(WB / "scripts/e135_train.py") != SOURCE_SHA or assets.sha(WB / "scripts/e139_train.py") != FREE_SHA:
        raise ValueError("Frozen E135/E139 source differs")
    manifest, arrays, orders, dims = source.preflight(args, _self_test_only=_self_test_only, full_hash=full_hash)
    manifest_sha = assets.sha(args.cache_root / "manifest.json")
    if not _self_test_only and manifest_sha != CACHE_SHA: raise ValueError("Exact registered native H/Y cache required")
    if args.seed not in (0, 2): raise ValueError("Only new E142 seeds0/2; observed E135 seed1 is reused")
    if Path(args.budget_file).resolve() in {Path(path).resolve() for path in
            (manifest["budget_file"], args.e136_budget_file, args.e138_budget_file, args.e139_budget_file, args.e140_budget_file)}:
        raise ValueError("E142 ledger must be separate from E135/E136/E138/E139/E140")
    old_budget = assets.read(args.budget_file)
    if old_budget and old_budget.get("experiment") != "E142": raise ValueError("E142 ledger identity differs")
    pilot = torch.load(args.reference_initial, map_location="cpu", mmap=True, weights_only=False)
    if (pilot.get("experiment"), pilot.get("schema"), pilot.get("step"), pilot.get("cache_manifest_sha256")) != (
            "E135", "E135-student-v1", 0, manifest_sha) or pilot["optimizer"]["state"] or np.any(pilot["cache_batch_counts"]):
        raise ValueError("Exact observed E135 seed1 initial gate source differs")
    pilot_state = pilot["student_state"]
    pilot_digest = c.tensor_state_hash(pilot_state)
    if pilot_digest != pilot["initial_tensor_sha256"] or any(value.dtype != torch.float32 for value in pilot_state.values()):
        raise ValueError("Observed E135 seed1 initial full tensor proof differs")
    pilot_provenance = assets.read(args.reference_initial.parent / "provenance.json")
    if pilot_provenance["config_hash"] != pilot["config_hash"] or pilot_provenance["scientific"]["driver_sha256"] != SOURCE_SHA:
        raise ValueError("Observed E135 seed1 source/config differs")
    shared_gate = pilot_state["block.gate.weight"].clone(); shared_gate_sha = gate_hash(pilot_state)
    source_path = args.free_initial or getattr(args, f"e139_seed{args.seed}_dir") / "initial.pt"
    old = torch.load(source_path, map_location="cpu", mmap=True, weights_only=False)
    if (old.get("experiment"), old.get("schema"), old.get("seed"), old.get("step"), old.get("cache_manifest_sha256")) != (
            "E139", "E139-free-routing-student-v1", args.seed, 0, manifest_sha) or old["optimizer"]["state"] or np.any(old["cache_batch_counts"]):
        raise ValueError("Exact own E139 free initial source differs")
    original = copy.copy(args); original.budget_file = args.e139_budget_file
    original.fixed_initial = getattr(args, f"e138_seed{args.seed}_dir") / "initial.pt"
    _, _, _, _, expected_state, _, expected = free.preflight(original, _self_test_only=_self_test_only)
    old_state = old["student_state"]; old_digest = c.tensor_state_hash(old_state)
    if (old.get("initialization") != expected or old_digest != expected["free_initial_full_tensor_sha256"]
            or old_digest != c.tensor_state_hash(expected_state) or any(value.dtype != torch.float32 for value in old_state.values())):
        raise ValueError("Exact own E139 expert/gate source tensor differs")
    source_provenance_path = source_path.parent / "provenance.json"; source_provenance = assets.read(source_provenance_path)
    if source_provenance["config_hash"] != old["config_hash"] or source_provenance["scientific"]["driver_sha256"] != FREE_SHA:
        raise ValueError("E139 free initial provenance/source differs")
    state = dict(old_state); state["block.gate.weight"] = shared_gate
    if expert_hash(state) != expert_hash(old_state) or gate_hash(state) != shared_gate_sha or gate_hash(state) == gate_hash(old_state):
        raise ValueError("E142 must preserve own experts and replace only gate with observed seed1 random gate")
    rng = copy.deepcopy(old["rng"])
    if not all(key in rng for key in ("torch", "numpy", "python")): raise ValueError("Own E139 initial RNG incomplete")
    rng_digest = c.tensor_state_hash({"torch": rng["torch"], **{f"cuda_{i}": value for i, value in enumerate(rng.get("cuda", []))}})
    proof = {"initialization_kind": "Own E139 seed expert tensor/RNG, observed E135 seed1 random FP32 gate only", "expert_seed": args.seed,
        "initial_full_tensor_sha256": c.tensor_state_hash(state), "initial_expert_only_sha256": expert_hash(state),
        "initial_gate_sha256": shared_gate_sha, "own_R_initial_full_tensor_sha256": old_digest,
        "own_R_initial_expert_only_sha256": expert_hash(old_state), "own_R_initial_gate_sha256": gate_hash(old_state),
        "own_R_initial": str(source_path), "own_R_initial_sha256": assets.sha(source_path),
        "own_R_initial_provenance": str(source_provenance_path), "own_R_initial_provenance_sha256": assets.sha(source_provenance_path),
        "own_R_initial_rng_tensor_sha256": rng_digest, "own_R_initial_cuda_rng_states": len(rng.get("cuda", [])),
        "shared_seed1_random_gate_source": str(args.reference_initial), "shared_seed1_random_gate_source_sha256": assets.sha(args.reference_initial),
        "shared_seed1_random_gate_source_full_tensor_sha256": pilot_digest,
        "cache_manifest_sha256": manifest_sha, "source_trainer_sha256": SOURCE_SHA, "own_R_trainer_sha256": FREE_SHA,
        "scope": "Only initial gate replaced; own independent expert values and RNG retained, full E135 optimizer protocol and trainable gate."}
    return manifest, arrays, orders, dims, state, rng, proof


def train(args, *, _self_test_only=False):
    if args.output is None: args.output = Path(f"/tmp/xiang-moe-20261025/e142_seed{args.seed}")
    manifest, arrays, orders, dims, initial, rng, proof = preflight(args, _self_test_only=_self_test_only)
    steps, count = int(orders.size), orders.shape[1]
    if not _self_test_only and (steps, count) != (4096, 1024): raise ValueError("Exact4096/four-pass training required")
    if _self_test_only and args.device != "cpu": raise ValueError("CPU self-test may not initialize GPU")
    gpu = {"device": "cpu"} if _self_test_only else c.select_gpu(args.physical_gpu)
    args.device = "cpu" if _self_test_only else "cuda:0"; output = args.output; output.mkdir(parents=True, exist_ok=True)
    require_source_rng(rng, args.device, args.resume)
    if (output / "checkpoint.pt").exists() and not args.resume: raise ValueError("Existing E142 checkpoint requires explicit --resume")
    scientific = {"experiment": "E142", "seed": args.seed, "initialization": proof, "dimensions": dims, "steps": steps, "epochs": 4,
        "fixed_training_energy": manifest["splits"]["train"]["energy_mean"], "optimizer": "fresh full-model AdamW(.9,.95),eps1e-8,wd.1,clip1",
        "lr": 3e-4, "warmup_fraction": .1, "lb_coef": .01, "z_coef": .001, "gate_frozen": False,
        "driver_sha256": assets.sha(__file__), "budget_file": str(args.budget_file), "CPU_test": _self_test_only,
        "cohort": {"new_seeds": [0, 2], "observed_pilot_seed": 1, "population_weights": [1/3, 1/3, 1/3]},
        "gate_initialization": "exact E135 seed1 untrained random FP32 gate, shared across students and trainable"}
    config_hash = base.digest_json(scientific); previous = assets.read(output / "training_summary.json") if args.resume else None
    energy = manifest["splits"]["train"]["energy_mean"]; lr_args = argparse.Namespace(steps=steps, lr=3e-4, warmup_fraction=.1)
    with Budget(args.budget_file, f"train_seed{args.seed}") as budget:
        if args.resume:
            cp = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
            if cp.get("schema") != "E142-shared-random-router-v1" or cp.get("config_hash") != config_hash or cp.get("seed") != args.seed:
                raise ValueError("E142 resume identity/config differs")
            student = c.bank_from_state(cp["student_state"], args.device, dims=dims); step = int(cp["step"])
            exposure = np.asarray(cp["cache_batch_counts"], dtype=np.uint32)
        else:
            student = c.bank_from_state(initial, args.device, dims=dims); step = 0; exposure = np.zeros(count, np.uint32)
            if c.tensor_state_hash(student.state_dict()) != proof["initial_full_tensor_sha256"]:
                raise ValueError("E142 initial full parameter tensor differs after module construction")
        if not 0 <= step <= steps or not np.array_equal(exposure, np.bincount(orders.reshape(-1)[:step], minlength=count)):
            raise ValueError("E142 cache exposure prefix differs from immutable order")
        if not all(value.requires_grad for value in student.parameters()): raise ValueError("Free router and experts must all train")
        optimizer = torch.optim.AdamW(student.parameters(), lr=3e-4, betas=(.9, .95), eps=1e-8, weight_decay=.1)
        if args.resume: optimizer.load_state_dict(cp["optimizer"]); base.restore_rng(cp["rng"], args); del cp
        else: base.restore_rng(rng, args)
        history = previous.get("evaluations", []) if previous and previous.get("config_hash") == config_hash else []
        provenance = {"experiment": "E142", "schema": "E142-shared-random-router-v1", "scientific": scientific, "config_hash": config_hash,
            "initialization": proof, "trainable_parameters": [name for name, value in student.named_parameters() if value.requires_grad],
            "gpu_preflight": gpu, "scope": "Own E139 expert initial values/RNG preserved; only gate set to the observed E135 seed1 random initial gate. All parameters train with original E135 full optimizer/aux/clip."}
        assets.write(output / "provenance.json", provenance)
        def save(path):
            state = student.state_dict()
            c.atomic_torch_save(path, {"schema": "E142-shared-random-router-v1", "experiment": "E142", "seed": args.seed, "step": step,
                "student_state": state, "moe": state, "optimizer": optimizer.state_dict(), "rng": base.rng_state(args),
                "config_hash": config_hash, "cache_manifest_sha256": proof["cache_manifest_sha256"],
                "initialization": proof, "cache_batch_counts": exposure})
        if not args.resume:
            if (output / "initial.pt").exists(): raise FileExistsError("Immutable E142 initial already exists")
            save(output / "initial.pt"); (output / "initial.pt").chmod(0o444)
        def measure():
            row = {"step": step, "train": source.evaluate_split(student, arrays["train"], energy, energy, args.device, budget),
                "held": source.evaluate_split(student, arrays["held"], energy, manifest["splits"]["held"]["energy_mean"], args.device, budget)}
            base.emit("E142_MSE", **row); return row
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
                    base.emit("E142_update", **{key: value for key, value in row.items() if key != "expert_load"})
                    if step % (2 if _self_test_only else 512) == 0:
                        history.append(measure()); save(output / "checkpoint.pt")
                        assets.write(output / "training_summary.json", {"status": "running", "step": step, "config_hash": config_hash, "evaluations": history})
                if step == steps: status = "complete"
        except Exception as error:
            status = "failed_or_incomplete"; assets.write(output / "failure.json", {"step": step, "error": f"{type(error).__name__}: {error}"}); raise
        finally:
            save(output / "checkpoint.pt")
            result = {"experiment": "E142", "seed": args.seed, "status": status, "step": step, "planned_steps": steps,
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
        else: raise AssertionError("Missing own E139 CUDA RNG must fail before GPU training")
        getter.assert_not_called()
    torch.set_num_threads(1); torch.manual_seed(142)
    with tempfile.TemporaryDirectory(prefix="e142_shared_random_cpu_") as directory:
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
        budgets = {experiment: root / f"{experiment.lower()}_budget.json" for experiment in ("E135", "E136", "E138", "E139", "E140")}
        for experiment, path in budgets.items(): assets.write(path, {"experiment": experiment, "untouched": True})
        manifest = {"schema": "E135-native-function-cache-v1", "status": "complete", "dimensions": dims, "files": files,
            "splits": records, "budget_file": str(budgets["E135"]),
            "teacher_block_tensor_sha256": c.tensor_state_hash(teacher.block.state_dict())}
        assets.write(cache / "manifest.json", manifest); manifest_sha = assets.sha(cache / "manifest.json")
        pilot_dir = root / "e135_student"; pilot_dir.mkdir(); reference = pilot_dir / "initial.pt"
        seed1 = free.seeded_bank(1, dims); pilot_state = seed1.state_dict(); pilot_config = "tiny-E135-seed1"
        c.atomic_torch_save(reference, {"schema": "E135-student-v1", "experiment": "E135", "step": 0,
            "cache_manifest_sha256": manifest_sha, "student_state": pilot_state,
            "initial_tensor_sha256": c.tensor_state_hash(pilot_state), "optimizer": {"state": {}},
            "cache_batch_counts": np.zeros(4, np.uint32), "config_hash": pilot_config,
            "rng": base.rng_state(argparse.Namespace(device="cpu"))})
        assets.write(pilot_dir / "provenance.json", {"config_hash": pilot_config, "scientific": {"driver_sha256": SOURCE_SHA}})
        free_dirs = {seed: root / f"e139_seed{seed}" for seed in (0, 2)}
        fixed_dirs = {seed: root / f"e138_seed{seed}" for seed in (0, 2)}
        for folder in (*free_dirs.values(), *fixed_dirs.values()): folder.mkdir()
        def make(seed, name, *extra):
            return parser().parse_args(["--cache-root", str(cache), "--reference-initial", str(reference),
                "--e139-seed0-dir", str(free_dirs[0]), "--e139-seed2-dir", str(free_dirs[2]),
                "--e138-seed0-dir", str(fixed_dirs[0]), "--e138-seed2-dir", str(fixed_dirs[2]),
                "--e136-budget-file", str(budgets["E136"]), "--e138-budget-file", str(budgets["E138"]),
                "--e139-budget-file", str(budgets["E139"]), "--e140-budget-file", str(budgets["E140"]),
                "--output", str(root / name), "--budget-file", str(root / "e142_budget.json"),
                "--device", "cpu", "--seed", str(seed), *extra])
        for seed in (0, 2):
            bank = free.seeded_bank(seed, dims); fixed_state = bank.state_dict(); expected_experts = expert_hash(fixed_state)
            fixed_state["block.gate.weight"] = teacher.block.gate.weight.float().clone()
            c.atomic_torch_save(fixed_dirs[seed] / "initial.pt", {"schema": "E138-fixed-assignment-student-v1", "experiment": "E138",
                "seed": seed, "step": 0, "cache_manifest_sha256": manifest_sha, "student_state": fixed_state,
                "optimizer": {"state": {}}, "cache_batch_counts": np.zeros(4, np.uint32), "initialization": {
                    "initial_expert_only_sha256": expected_experts, "oracle_initial_full_tensor_sha256": c.tensor_state_hash(fixed_state)}})
            helper_args = make(seed, "unused_source"); helper_args.budget_file = budgets["E139"]
            helper_args.fixed_initial = fixed_dirs[seed] / "initial.pt"
            _, _, _, _, state, rng, proof = free.preflight(helper_args, _self_test_only=True)
            config_hash = f"tiny-E139-seed{seed}"
            c.atomic_torch_save(free_dirs[seed] / "initial.pt", {"schema": "E139-free-routing-student-v1", "experiment": "E139",
                "seed": seed, "step": 0, "cache_manifest_sha256": manifest_sha, "student_state": state,
                "optimizer": {"state": {}}, "cache_batch_counts": np.zeros(4, np.uint32),
                "initialization": proof, "rng": rng, "config_hash": config_hash})
            assets.write(free_dirs[seed] / "provenance.json", {"config_hash": config_hash, "scientific": {"driver_sha256": FREE_SHA}})
        original_paths = [reference, pilot_dir / "provenance.json", *budgets.values(),
            *(folder / "initial.pt" for folder in free_dirs.values()),
            *(folder / "initial.pt" for folder in fixed_dirs.values())]
        originals = {str(path): assets.sha(path) for path in original_paths}
        proofs = {seed: preflight(make(seed, f"unused{seed}"), _self_test_only=True)[-1] for seed in (0, 2)}
        assert proofs[0]["initial_gate_sha256"] == proofs[2]["initial_gate_sha256"] == gate_hash(pilot_state)
        assert proofs[0]["initial_expert_only_sha256"] != proofs[2]["initial_expert_only_sha256"]
        for seed in (0, 2):
            assert proofs[seed]["initial_expert_only_sha256"] == proofs[seed]["own_R_initial_expert_only_sha256"]
        full = train(make(0, "full"), _self_test_only=True)
        train(make(0, "split", "--max-updates", "3"), _self_test_only=True)
        train(make(0, "split", "--resume", str(root / "split/checkpoint.pt")), _self_test_only=True)
        a, b = [torch.load(root / name / "checkpoint.pt", weights_only=False) for name in ("full", "split")]
        initial = torch.load(root / "full/initial.pt", weights_only=False)
        old = torch.load(free_dirs[0] / "initial.pt", weights_only=False)
        assert expert_hash(initial["student_state"]) == expert_hash(old["student_state"])
        assert gate_hash(initial["student_state"]) == gate_hash(pilot_state)
        assert not initial["optimizer"]["state"] and np.all(initial["cache_batch_counts"] == 0)
        assert torch.equal(initial["rng"]["torch"], old["rng"]["torch"])
        assert all(torch.equal(a["student_state"][key], b["student_state"][key]) for key in a["student_state"])
        assert all(torch.equal(value, b["optimizer"]["state"][key][field]) for key, row in a["optimizer"]["state"].items()
                   for field, value in row.items() if torch.is_tensor(value))
        assert full["status"] == "complete" and full["step"] == 16
        assert np.array_equal(a["cache_batch_counts"], np.full(4, 4))
        assert gate_hash(a["student_state"]) != proofs[0]["initial_gate_sha256"]
        assert expert_hash(a["student_state"]) != proofs[0]["initial_expert_only_sha256"]
        assert all(assets.sha(path) == digest for path, digest in originals.items())
        result = {"passed": True, "CPU_only": True, "shared_random_gate_exact": True,
            "own_experts_and_RNG_preserved": True, "fresh_full_parameter_optimizer": True,
            "source_CUDA_rng_required": True, "gate_trainable_and_changed": True,
            "exact_resume_parameters_optimizer_RNG": torch.equal(a["rng"]["torch"], b["rng"]["torch"]),
            "four_pass_exposure": True, "old_assets_unchanged": True, "driver_sha256": assets.sha(__file__)}
        assets.write(WB / "results/e142/self_test.json", result); return result


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "train", "self-test"), default="preflight")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    p.add_argument("--free-initial", type=Path)
    p.add_argument("--e139-seed0-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e139_seed0"))
    p.add_argument("--e139-seed2-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e139_seed2"))
    p.add_argument("--e138-seed0-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_seed0"))
    p.add_argument("--e138-seed2-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_seed2"))
    p.add_argument("--seed", type=int, choices=(0, 2), default=0); p.add_argument("--output", type=Path)
    p.add_argument("--resume", type=Path); p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e142_budget.json"))
    p.add_argument("--e136-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_budget.json"))
    p.add_argument("--e138-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_budget.json"))
    p.add_argument("--e139-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e139_budget.json"))
    p.add_argument("--e140-budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e140_budget.json"))
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
