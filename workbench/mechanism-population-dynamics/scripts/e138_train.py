"""E138 two new fixed-assignment students; fresh expert seeds0/2, reused cache.

The already observed E136 seed1 is a fixed pilot, never retrained here.
Only expert initialization varies; all training constants/exposures stay fixed.
"""
from __future__ import annotations
import argparse, fcntl, json, random, socket, tempfile, time
from pathlib import Path
import numpy as np
import torch
import e135_common as c
import e135_train as source
import e136_train as oracle_helpers

assets, base, WB = c.assets, c.base, c.WB
SOURCE_SHA = "8343f7e87b7ec8a1e027d3ec83bb3d2d7bfd649424a453ba9cc3e53ae3368cb7"


class Budget(c.Budget):
    def __init__(self, path, phase): super().__init__(path, phase, limit=5400.)
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E138", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state.get("experiment") != "E138" or state["host"] != socket.gethostname(): raise ValueError("E138 uses a separate additive one-node ledger, never E135/E136/E137")
            result = operation(state); assets.write(self.path, state); return result
    def check(self):
        consumed = self.update(lambda state: state["completed_seconds"] + sum(time.monotonic() - value["started"] for value in state["active"].values()))
        if consumed >= 5400: raise TimeoutError("E138 1.5-GPU-hour aggregate budget exhausted")
        return consumed


def expert_hash(state): return c.tensor_state_hash({key: value for key, value in state.items() if key.startswith("block.experts.")})
def gate_hash(state): return c.tensor_state_hash({"block.gate.weight": state["block.gate.weight"]})


def seeded_bank(seed, dims):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    return base.TensorMoE(dims["hidden"], dims["expert_size"], dims["experts"], dims["top_k"], .02)


def preflight(args, *, _self_test_only=False, full_hash=False):
    if assets.sha(WB / "scripts/e135_train.py") != SOURCE_SHA: raise ValueError("Frozen E135 source trainer differs")
    if assets.sha(WB / "scripts/e136_train.py") != "8c620871df90c2a10ea9be5b629727ce063164483ab8a0d22cb846e6f6841b55": raise ValueError("Frozen E136 helper differs")
    manifest, arrays, orders, dims = source.preflight(args, _self_test_only=_self_test_only, full_hash=full_hash)
    if not _self_test_only and assets.sha(args.cache_root / "manifest.json") != "2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43":
        raise ValueError("Exact immutable registered H/Y cache manifest required")
    if args.seed not in (0, 2): raise ValueError("Only new seeds0/2: existing E136 seed1 is not retrained")
    if Path(args.budget_file).resolve() == Path(manifest["budget_file"]).resolve(): raise ValueError("E135 ledger must not be reused")
    old_budget = assets.read(args.budget_file)
    if old_budget and old_budget.get("experiment") != "E138": raise ValueError("Cannot reuse any other experiment's ledger")
    reference = torch.load(args.reference_initial, map_location="cpu", mmap=True, weights_only=False)
    if (reference.get("schema") != "E135-student-v1" or reference.get("experiment") != "E135" or reference.get("step") != 0
            or reference.get("cache_manifest_sha256") != assets.sha(args.cache_root / "manifest.json") or reference["optimizer"]["state"]):
        raise ValueError("Immutable seed1 reference must be a genuine E135 initial checkpoint")
    reference_experts = expert_hash(reference["student_state"])
    if c.tensor_state_hash(reference["student_state"]) != reference["initial_tensor_sha256"] or any(value.dtype != torch.float32 for value in reference["student_state"].values()):
        raise ValueError("Seed1 reference full FP32 initial tensor proof differs")
    seed1 = seeded_bank(1, dims); seed1_hash = expert_hash(seed1.state_dict()); del seed1
    if seed1_hash != reference_experts or (not _self_test_only and seed1_hash != "c0c6a2ba4e11f8951abb6de4d4f6f016246e9c84f30d145afcb5cdf7bbd982f4"):
        raise ValueError("Same-constructor seed1 expert-only reconstruction differs from fixed observed pilot")
    teacher = torch.load(args.cache_root / "teacher_block.pt", map_location="cpu", mmap=True, weights_only=False)
    if c.tensor_state_hash(teacher["state"]) != manifest["teacher_block_tensor_sha256"]: raise ValueError("Native teacher state proof differs")
    bank = seeded_bank(args.seed, dims); rng = base.rng_state(argparse.Namespace(device="cpu"))
    state = bank.state_dict(); before = expert_hash(state)
    state["block.gate.weight"] = teacher["state"]["gate.weight"].float().clone()
    if expert_hash(state) != before or before == seed1_hash: raise RuntimeError("Fresh experts must be preserved and distinct from seed1")
    if any(value.dtype != torch.float32 for value in state.values()): raise ValueError("All new student parameters must be FP32 masters")
    proof = {"initialization_kind": "E138 fresh TensorMoE constructor, then teacher gate copy; not a copied E135 initial",
        "expert_seed": args.seed, "initial_expert_only_sha256": before, "oracle_initial_expert_only_sha256": before,
        "oracle_initial_full_tensor_sha256": c.tensor_state_hash(state), "oracle_gate_FP32_sha256": gate_hash(state),
        "teacher_gate_BF16_sha256": c.tensor_state_hash({"gate.weight": teacher["state"]["gate.weight"]}),
        "seed1_constructor_check": {"reference_initial": str(args.reference_initial), "reference_initial_sha256": assets.sha(args.reference_initial),
            "reconstructed_expert_only_sha256": seed1_hash, "reference_expert_only_sha256": reference_experts, "training_launched": False},
        "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"), "source_trainer_sha256": SOURCE_SHA,
        "source_oracle_helper_sha256": assets.sha(WB / "scripts/e136_train.py"),
        "scope": "Only expert seed varies; teacher gate values/rows supplied and frozen; no individual-expert targets"}
    return manifest, arrays, orders, dims, state, rng, proof


support_check = oracle_helpers.support_check

def train(args, *, _self_test_only=False):
    if args.output is None: args.output = Path(f"/tmp/xiang-moe-20261025/e138_seed{args.seed}")
    manifest, arrays, orders, dims, oracle, inherited_rng, initial_proof = preflight(args, _self_test_only=_self_test_only)
    steps, count = int(orders.size), orders.shape[1]
    if not _self_test_only and steps != 4096: raise ValueError("Registered4096 updates required")
    if _self_test_only and args.device != "cpu": raise ValueError("_self_test_only is CPU-only")
    gpu = {"device": "cpu"} if _self_test_only else c.select_gpu(args.physical_gpu)
    args.device = "cpu" if _self_test_only else "cuda:0"; output = args.output; output.mkdir(parents=True, exist_ok=True)
    if args.device.startswith("cuda") and not args.resume:
        inherited_rng["cuda"] = torch.cuda.get_rng_state_all()
    if (output / "checkpoint.pt").exists() and not args.resume: raise ValueError("Existing oracle checkpoint requires --resume")
    scientific = {"experiment": "E138", "seed": args.seed, "initialization": initial_proof, "dimensions": dims, "steps": steps, "epochs": 4,
        "fixed_training_energy": manifest["splits"]["train"]["energy_mean"], "optimizer": "fresh expert-only AdamW(.9,.95),eps1e-8,wd.1,clip1",
        "lr": 3e-4, "warmup_fraction": .1, "lb_coef": .01, "z_coef": .001, "gate_frozen": True,
        "driver_sha256": assets.sha(__file__), "budget_file": str(args.budget_file), "CPU_test": _self_test_only, "cohort": {"new_seeds": [0, 2], "observed_pilot_seed": 1, "population_weights": [1/3, 1/3, 1/3]}}
    config_hash = base.digest_json(scientific); previous = assets.read(output / "training_summary.json") if args.resume else None
    energy = manifest["splits"]["train"]["energy_mean"]; lr_args = argparse.Namespace(steps=steps, lr=3e-4, warmup_fraction=.1)
    with Budget(args.budget_file, f"train_seed{args.seed}") as budget:
        if args.resume:
            checkpoint = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
            if checkpoint.get("schema") != "E138-fixed-assignment-student-v1" or checkpoint.get("config_hash") != config_hash: raise ValueError("Oracle resume configuration differs")
            student = c.bank_from_state(checkpoint["student_state"], args.device, dims=dims); step = checkpoint["step"]
            exposure = np.asarray(checkpoint["cache_batch_counts"], dtype=np.uint32)
        else: student = c.bank_from_state(oracle, args.device, dims=dims); step = 0; exposure = np.zeros(count, np.uint32)
        if not 0 <= step <= steps or not np.array_equal(exposure, np.bincount(orders.reshape(-1)[:step], minlength=count)): raise ValueError("Wrong oracle cache exposure prefix")
        student.block.gate.requires_grad_(False)
        trainable = [(name, value) for name, value in student.named_parameters() if value.requires_grad]
        if not trainable or any(not name.startswith("block.experts.") for name, _ in trainable): raise RuntimeError("Only experts may be optimized")
        frozen_gate = student.block.gate.weight.detach().clone()
        if gate_hash(student.state_dict()) != initial_proof["oracle_gate_FP32_sha256"]: raise ValueError("Gate no longer equals initial supplied teacher gate")
        optimizer = torch.optim.AdamW([value for _, value in trainable], lr=3e-4, betas=(.9, .95), eps=1e-8, weight_decay=.1)
        if args.resume: optimizer.load_state_dict(checkpoint["optimizer"]); base.restore_rng(checkpoint["rng"], args); del checkpoint
        else: base.restore_rng(inherited_rng, args)
        provenance = {"experiment": "E138", "schema": "E138-fixed-assignment-student-v1", "scientific": scientific, "config_hash": config_hash,
            "initialization": initial_proof, "trainable_parameters": [name for name, _ in trainable], "gpu_preflight": gpu,
            "scope": "E138 fixed finite cohort: new expert seeds0/2 and observed E136 seed1 pilot; same frozen assignment and expert-only clipping. No seed selection, additional training, or teacher-fitting eligibility gates."}
        assets.write(output / "provenance.json", provenance)
        def save(path):
            if not torch.equal(student.block.gate.weight, frozen_gate): raise RuntimeError("Supplied gate was mutated")
            state = student.state_dict(); c.atomic_torch_save(path, {"schema": "E138-fixed-assignment-student-v1", "experiment": "E138", "seed": args.seed, "step": step,
                "student_state": state, "moe": state, "optimizer": optimizer.state_dict(), "rng": base.rng_state(args),
                "config_hash": config_hash, "cache_manifest_sha256": initial_proof["cache_manifest_sha256"],
                "initialization": initial_proof, "gate_tensor_sha256": gate_hash(state), "cache_batch_counts": exposure})
        if not args.resume:
            if (output / "initial.pt").exists(): raise FileExistsError("Immutable E138 initial exists")
            save(output / "initial.pt"); (output / "initial.pt").chmod(0o444)
        history = previous.get("evaluations", []) if previous and previous.get("config_hash") == config_hash else []
        def measure():
            result = {"step": step, "train": source.evaluate_split(student, arrays["train"], energy, energy, args.device, budget),
                "held": source.evaluate_split(student, arrays["held"], energy, manifest["splits"]["held"]["energy_mean"], args.device, budget)}
            base.emit("E138_MSE", **result); return result
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
                    if not torch.isfinite(objective): raise RuntimeError("Nonfinite oracle total-Y/aux objective")
                    if lb.requires_grad or z.requires_grad: raise RuntimeError("Aux unexpectedly has expert-dependent gradients under frozen gate/fixed H")
                    if step == 0:
                        selected = int(loads.argmax()); gradient = torch.autograd.grad(normalized, student.block.experts[selected].up_proj.weight, retain_graph=True)[0]
                        if not torch.isfinite(gradient).all(): raise RuntimeError("Nonfinite expert gradient")
                        teacher = torch.load(args.cache_root / "teacher_block.pt", map_location="cpu", mmap=True, weights_only=False)
                        support = support_check(student, teacher["state"]["gate.weight"], hidden, args.device)
                        if support["full_row_selected_slot_mismatch_rows"] or support["selected_weight_max_abs_difference"] != 0: raise RuntimeError(f"Actual teacher/oracle support differs: {support}")
                        assets.write(output / "gradient_audit.json", {"normalized_MSE_expert_grad_norm": float(gradient.float().norm()),
                            "gate_requires_grad": False, "aux_direct_expert_gradient": "absent", "support": support,
                            "global_clip_scope": "expert gradients only; removal of router gradient clip coupling is part of oracle treatment"})
                    objective.backward(); student.last_router_logits = None
                    if student.block.gate.weight.grad is not None: raise RuntimeError("Frozen gate received a gradient")
                    norm = float(torch.nn.utils.clip_grad_norm_([value for _, value in trainable], 1., error_if_nonfinite=True)); optimizer.step()
                    if not torch.equal(student.block.gate.weight, frozen_gate): raise RuntimeError("Optimizer modified frozen gate")
                    exposure[index] += 1; step += 1
                    if args.device.startswith("cuda"): torch.cuda.synchronize()
                    seconds = time.monotonic() - started; times.append(seconds)
                    row = {"step": step, "epoch": epoch, "cache_batch_index": index, "position_exposures": step * dims["batch_size"] * dims["seq_len"],
                        "MSE": float(mse.detach()), "normalized_MSE": float(normalized.detach()), "lb_raw": float(lb), "z_raw": float(z),
                        "objective": float(objective.detach()), "lr": lr, "expert_gradient_norm_before_clip": norm,
                        "gate_unchanged": True, "seconds": seconds, "positions_per_second": dims["batch_size"] * dims["seq_len"] / seconds}
                    log.write(json.dumps(row, allow_nan=False) + "\n"); log.flush(); base.emit("E138_update", **row)
                    if step % (2 if _self_test_only else 512) == 0:
                        history.append(measure()); save(output / "checkpoint.pt")
                        assets.write(output / "training_summary.json", {"status": "running", "step": step, "config_hash": config_hash, "evaluations": history})
                if step == steps: status = "complete"
        except Exception as error:
            status = "failed_or_incomplete"; assets.write(output / "failure.json", {"step": step, "error": f"{type(error).__name__}: {error}"}); raise
        finally:
            save(output / "checkpoint.pt")
            result = {"experiment": "E138", "seed": args.seed, "status": status, "step": step, "planned_steps": steps, "expected_MSE_event_steps": list(range(0, steps + 1, 2 if _self_test_only else 512)), "config_hash": config_hash, "initialization": initial_proof,
                "gate_tensor_sha256_after": gate_hash(student.state_dict()), "final_expert_only_sha256": expert_hash(student.state_dict()),
                "final_tensor_sha256": c.tensor_state_hash(student.state_dict()), "cache_batch_exposure_counts": exposure.tolist(),
                "position_exposures": step * dims["batch_size"] * dims["seq_len"], "evaluations": history,
                "positions_per_second_after_first": dims["batch_size"] * dims["seq_len"] / float(np.mean(times[1:] or times)) if times else None}
            assets.write(output / "training_summary.json", result)
            if args.summary: assets.write(args.summary, result)
    return result


def self_test():
    torch.set_num_threads(1); torch.manual_seed(136)
    with tempfile.TemporaryDirectory(prefix="e138_fixed_assignment_cpu_") as directory:
        root = Path(directory); cache = root / "cache"; cache.mkdir(); dims = {"hidden": 8, "expert_size": 8, "experts": 4, "top_k": 2, "seq_len": 4, "batch_size": 2}
        teacher = base.TensorMoE(8, 8, 4, 2, .02).bfloat16().eval(); records = {}
        c.atomic_torch_save(cache / "teacher_block.pt", {"state": teacher.block.state_dict()})
        for split, count in (("train", 4), ("held", 2)):
            h = torch.randn(count, 2, 4, 8).bfloat16()
            with torch.no_grad(), source.amp("cpu"): y = torch.stack([teacher(value) for value in h])
            np.save(cache / f"{split}_H.npy", c.bf16_bits(h)); np.save(cache / f"{split}_Y.npy", c.bf16_bits(y))
            records[split] = {"positions": count * 8, "energy_mean": float(y.double().square().mean())}
        rng = np.random.default_rng(135); np.save(cache / "epoch_orders.npy", np.stack([rng.permutation(4) for _ in range(4)]))
        files = {path.name: {"sha256": assets.sha(path), "size_bytes": path.stat().st_size} for path in cache.iterdir()}
        original_budget = root / "e135_budget.json"; assets.write(original_budget, {"experiment": "E135", "untouched": True}); budget_before = assets.sha(original_budget)
        manifest = {"schema": "E135-native-function-cache-v1", "status": "complete", "dimensions": dims, "files": files, "splits": records,
            "budget_file": str(original_budget), "teacher_block_tensor_sha256": c.tensor_state_hash(teacher.block.state_dict())}
        assets.write(cache / "manifest.json", manifest); torch.manual_seed(1); initial = base.TensorMoE(8, 8, 4, 2, .02)
        reference = root / "e135_initial.pt"; c.atomic_torch_save(reference, {"schema": "E135-student-v1", "experiment": "E135", "step": 0,
            "cache_manifest_sha256": assets.sha(cache / "manifest.json"), "student_state": initial.state_dict(),
            "initial_tensor_sha256": c.tensor_state_hash(initial.state_dict()), "optimizer": {"state": {}}, "rng": base.rng_state(argparse.Namespace(device="cpu"))})
        source_before = assets.sha(reference)
        def make(name, *extra): return parser().parse_args(["--cache-root", str(cache), "--reference-initial", str(reference), "--output", str(root / name),
            "--budget-file", str(root / "e138_budget.json"), "--device", "cpu", *extra])
        a0 = preflight(make("unused0"), _self_test_only=True)[-1]
        args2 = make("unused2"); args2.seed = 2; a2 = preflight(args2, _self_test_only=True)[-1]
        assert a0["initial_expert_only_sha256"] != a2["initial_expert_only_sha256"]
        assert a0["oracle_gate_FP32_sha256"] == a2["oracle_gate_FP32_sha256"]
        full = train(make("full"), _self_test_only=True); train(make("split", "--max-updates", "3"), _self_test_only=True)
        train(make("split", "--resume", str(root / "split/checkpoint.pt")), _self_test_only=True)
        a, b = [torch.load(root / name / "checkpoint.pt", weights_only=False) for name in ("full", "split")]
        assert all(torch.equal(a["student_state"][key], b["student_state"][key]) for key in a["student_state"])
        assert all(torch.equal(value, b["optimizer"]["state"][key][field]) for key, row in a["optimizer"]["state"].items() for field, value in row.items() if torch.is_tensor(value))
        start = torch.load(root / "full/initial.pt", weights_only=False)
        assert expert_hash(start["student_state"]) == a0["initial_expert_only_sha256"]
        assert a0["seed1_constructor_check"]["reference_expert_only_sha256"] == expert_hash(initial.state_dict())
        assert a["optimizer"]["state"] and not start["optimizer"]["state"]
        assert all(name.startswith("block.experts.") for name in assets.read(root / "full/provenance.json")["trainable_parameters"])
        assert gate_hash(a["student_state"]) == gate_hash(start["student_state"]) and expert_hash(a["student_state"]) != expert_hash(start["student_state"])
        assert np.array_equal(a["cache_batch_counts"], np.full(4, 4)) and torch.equal(a["rng"]["torch"], b["rng"]["torch"])
        assert assets.sha(reference) == source_before and assets.sha(original_budget) == budget_before
        result = {"passed": True, "CPU_only": True, "exact_expert_initialization_and_frozen_gate": True, "fresh_expert_only_optimizer": True,
            "actual_full_row_teacher_support_same": True, "aux_has_no_direct_expert_gradient": True, "exact_resume_parameters_optimizer_RNG": True,
            "four_pass_exposure": True, "seed0_seed2_distinct_experts_same_gate": True, "seed1_constructor_matches_observed_reference": True, "E135_source_assets_and_budget_unchanged": True, "driver_sha256": assets.sha(__file__)}
        assets.write(WB / "results/e138/self_test.json", result); return result


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "train", "self-test"), default="preflight")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    p.add_argument("--seed", type=int, choices=(0, 2), default=0)
    p.add_argument("--output", type=Path); p.add_argument("--resume", type=Path)
    p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_budget.json")); p.add_argument("--summary", type=Path)
    p.add_argument("--physical-gpu", type=int, default=0); p.add_argument("--max-updates", type=int, default=0); p.add_argument("--device", default="cuda:0"); return p


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, arrays, orders, dims, state, rng, proof = preflight(args)
        result = {"status": "CPU_preflight_only", "initialization": proof, "steps": int(orders.size), "energy": manifest["splits"]["train"]["energy_mean"], "driver_sha256": assets.sha(__file__)}
    else: result = train(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
