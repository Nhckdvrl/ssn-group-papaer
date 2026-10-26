"""E142 shared random-gate cohort: Dolma-only native vectors and final predictors.

Seed1 is the observed E135 pilot reused in S and R. Input-file intervals are
conditional on each finite cohort and locked Hcal maps, never seed-level CIs.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeForCausalLM
import e135_capture as operators
import e135_readout as legacy
import e139_readout as old_readout
import e142_components as joint

c, assets, base, WB = joint.c, joint.assets, joint.base, joint.WB
STUDENTS = joint.STUDENTS
PAIRS = tuple(("teacher", name) for name in STUDENTS) + tuple(itertools.combinations(STUDENTS, 2))
METRICS = old_readout.METRICS


@torch.no_grad()
def natural_predictions(model, teacher, banks, manifest, args, budget):
    data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
    if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Original Dolma held windows differ")
    dtype = argparse.Namespace(device="cuda:0", dtype="bfloat16"); names = ("teacher", *STUDENTS)
    rows = {left + "_to_" + right: [] for left, right in PAIRS}; chain = hashlib.sha256(); noise = {}
    token_arrays = {key: np.lib.format.open_memmap(args.raw_output / f"{key}_Dolma_metrics.npy", mode="w+", dtype=np.float32,
        shape=(512, 512, len(METRICS))) for key in rows}
    for index, (tokens, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
        budget.check(); start = index * 16; chain.update(tokens.numpy().astype("<i8", copy=False).tobytes())
        ids = tokens[:, :-1].to("cuda:0"); target = tokens[:, 1:].to("cuda:0")
        predictions = {}
        for name in names:
            budget.check(); model.model.layers[9].mlp = teacher if name == "teacher" else banks[name]
            if name != "teacher": banks[name].inner.measurement = {}
            predict = lambda: base.forward_logits(model, ids, dtype).float().log_softmax(-1)
            predictions[name] = predict()
            if index == 0:
                repeated = predict(); noise[name] = legacy.pred.repeat_noise(predictions[name], repeated, target); del repeated
        for left, right in PAIRS:
            key = left + "_to_" + right; values = legacy.pred.previous.metrics(predictions[left], predictions[right], target)
            if not torch.isfinite(values).all(): raise RuntimeError("Nonfinite E142 natural prediction metric")
            token_arrays[key][start:start + len(ids)] = values.cpu().numpy()
            sums = values.double().sum(1).cpu().numpy()
            rows[key].extend({**row, "tokens": 512, **dict(zip(METRICS, value.tolist()))}
                for row, value in zip(metadata, sums))
        del predictions
        base.emit("E142_Dolma_natural_predictors", sequences=start + len(ids))
    model.model.layers[9].mlp = teacher
    for array in token_arrays.values(): array.flush()
    raw = args.raw_output / "Dolma_natural_rows.json"; assets.write(raw, {"pairs": rows, "input_sha256": chain.hexdigest()})
    return {"population": "Dolma_held_positions_only", "precision": "BF16 whole logits then FP32 logsoftmax",
        "pairs": {key: {"global": old_readout.input_summary(value, "Dolma_held_positions"),
            "sources": {source: old_readout.input_summary([row for row in value if row["source"] == source], "Dolma_held_positions")
                for source in sorted({row["source"] for row in value})}} for key, value in rows.items()},
        "raw": str(raw), "raw_sha256": assets.sha(raw),
        "token_arrays": {key: {"path": str(args.raw_output / f"{key}_Dolma_metrics.npy"),
            "sha256": assets.sha(args.raw_output / f"{key}_Dolma_metrics.npy")} for key in rows},
        "input_sha256": chain.hexdigest(), "first_batch_repeat_noise": noise,
        "pair_orientation": "q=left name, p=right name; NLLgap=right-left; both KL directions"}


@torch.no_grad()
def run(args):
    manifest, teacher_state, states, proofs, old_records = joint.preflight(args)
    gpu = c.select_gpu(args.physical_gpu); args.raw_output.mkdir(parents=True, exist_ok=True)
    result = {"experiment": "E142", "status": "partial", "stage": args.stage, "script_sha256": assets.sha(__file__),
        "components_script_sha256": assets.sha(joint.__file__), "training_script_sha256": joint.TRAIN_SHA,
        "native_trace_script_sha256": joint.inherited.NATIVE_SHA, "gpu_preflight": gpu, "condition_proofs": proofs,
        "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"),
        "old_reference": {name: {"path": item["path"], "sha256": item["sha256"]} for name, item in old_records.items()},
        "population": "Dolma_held_positions_only", "cohort_weights": [1/3, 1/3, 1/3], "scope": __doc__, "errors": {}}
    with joint.training.Budget(args.budget_file, "readout_" + args.stage) as budget:
        model = OlmoeForCausalLM.from_pretrained(manifest["model"], dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
        teacher = model.model.layers[9].mlp; teacher_hash = c.tensor_state_hash(teacher.state_dict())
        prefix = base.sampled_parameter_hash(model, "model.layers.9.mlp.")
        if teacher_hash != manifest["teacher_block_tensor_sha256"] or prefix != manifest["teacher_prefix_hash"]:
            raise ValueError("Exact public native teacher/prefix differs")
        initial_gate_weight = states["initial"]["seed1"]["block.gate.weight"].to("cuda:0")
        banks = {phase: {name: operators.MeasuredPublic(states[phase][name]) for name in STUDENTS}
            for phase in ("initial", "final")}; states.clear()
        before = {(phase, name): c.tensor_state_hash(bank.inner.state_dict()) for phase, group in banks.items()
            for name, bank in group.items()}
        stages = ("components", "predictions") if args.stage == "all" else (args.stage,)
        for stage in stages:
            try:
                if stage == "components":
                    result[stage] = joint.run_components(model, teacher, banks, proofs, manifest, old_records,
                        initial_gate_weight, args, budget)
                else:
                    result[stage] = natural_predictions(model, teacher, banks["final"], manifest, args, budget)
                    result[stage]["old_cohorts_reference"] = {
                        "R_F": {"path": old_records["R_F"]["path"], "sha256": old_records["R_F"]["sha256"],
                            "predictions": old_records["R_F"]["record"]["predictions"]},
                        "T": {"path": old_records["T"]["path"], "sha256": old_records["T"]["sha256"],
                            "predictions": old_records["T"]["record"]["predictions"]}}
            except Exception as error:
                result["errors"][stage] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = teacher
            assets.write(args.summary, result)
        model.model.layers[9].mlp = teacher
        if c.tensor_state_hash(teacher.state_dict()) != teacher_hash or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != prefix:
            raise RuntimeError("Read-only original public teacher/prefix mutated")
        if any(c.tensor_state_hash(bank.inner.state_dict()) != before[phase, name] for phase, group in banks.items() for name, bank in group.items()):
            raise RuntimeError("Read-only E142 student parameters mutated")
        result["status"] = "complete" if args.stage == "all" and not result["errors"] else "partial"
        result["completed_requested_stages"] = [stage for stage in stages if stage in result]; assets.write(args.summary, result)
    return result


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("preflight", "evaluate", "self-test"), default="preflight")
    p.add_argument("--preflight-phase", choices=("initial", "all"), default="all")
    p.add_argument("--stage", choices=("all", "components", "predictions"), default="all")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    p.add_argument("--e135-student-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student"))
    for seed in (0, 2):
        p.add_argument(f"--e139-seed{seed}-dir", type=Path, default=Path(f"/tmp/xiang-moe-20261025/e139_seed{seed}"))
        p.add_argument(f"--e138-seed{seed}-dir", type=Path, default=Path(f"/tmp/xiang-moe-20261025/e138_seed{seed}"))
        p.add_argument(f"--shared-seed{seed}-dir", type=Path, default=Path(f"/tmp/xiang-moe-20261025/e142_seed{seed}"))
    for old in (136, 138, 139, 140):
        p.add_argument(f"--e{old}-budget-file", type=Path, default=Path(f"/tmp/xiang-moe-20261025/e{old}_budget.json"))
    p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e142_budget.json"))
    p.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e142_readout"))
    p.add_argument("--summary", type=Path, default=WB / "results/e142/readout.json")
    p.add_argument("--physical-gpu", type=int, default=0); return p


def self_test():
    result = joint.self_test()
    assert len(PAIRS) == 6 and len(METRICS) == 6
    toy = [{"word": "a", "source": "x", "file_id": "1", "tokens": 2, **dict(zip(METRICS, [2, 4, 8, 4, 6, 2]))},
           {"word": "b", "source": "x", "file_id": "2", "tokens": 1, **dict(zip(METRICS, [2, 3, 4, 1, 2, 1]))}]
    assert old_readout.input_summary(toy, "Dolma_held_positions")["nll_gap_right_minus_left"]["point"] == 5/3
    result.update({"six_final_Dolma_predictor_pairs": True, "input_file_cluster_math": True,
        "readout_sha256": assets.sha(__file__)})
    assets.write(WB / "results/e142/readout_self_test.json", result); return result


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, teacher, states, proofs, old_records = joint.preflight(args, initial_only=args.preflight_phase == "initial")
        result = {"status": "CPU_preflight_only", "phase": args.preflight_phase, "proofs": proofs,
            "old_records": {name: {"path": row["path"], "sha256": row["sha256"]} for name, row in old_records.items()},
            "readout_sha256": assets.sha(__file__), "components_sha256": assets.sha(joint.__file__)}
    else: result = run(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
