"""E138 fixed-cohort joint components, final predictors and known-coordinate A.

Three fixed students include the observed E136 seed1 pilot; intervals resample
inputs, never seeds or their three nonindependent pairs. No U injections/maps.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeForCausalLM
import e124_compare as matching
import e135_capture as operators
import e135_readout as legacy
import e136_capture as old_profiles
import e138_components as joint

c, assets, base, WB = joint.c, joint.assets, joint.base, joint.WB
STUDENTS = joint.STUDENTS
PAIRS = tuple(("teacher", name) for name in STUDENTS) + tuple(itertools.combinations(STUDENTS, 2))
METRICS = ("kl_left_to_right", "left_nll", "right_nll", "nll_gap_right_minus_left", "kl_right_to_left", "top1_agreement")


def input_summary(rows, population):
    names = METRICS; groups = {}
    for row in rows:
        key = row["word"] if population == "POS_held_targets" else (row["source"], row["file_id"])
        groups.setdefault(key, np.zeros(len(names) + 1))[:] += [row[name] for name in names] + [row["tokens"]]
    values = np.array(list(groups.values())); draws = np.random.default_rng(138).integers(0, len(values), (1000, len(values)))
    if population == "POS_held_targets":
        values = values[:, :-1] / values[:, -1:]; point = values.mean(0); samples = values[draws].mean(1)
    else:
        total = values.sum(0); point = total[:-1] / total[-1]; samples = values[draws].sum(1); samples = samples[:, :-1] / samples[:, -1:]
    ci = np.quantile(samples, [.025, .975], axis=0)
    return {"items": len(rows), "input_clusters": len(values), "bootstrap_seed": 138, "bootstrap_iterations": 1000,
        "weighting": "equal word means" if population == "POS_held_targets" else "token mean, file clusters",
        **{name: {"point": float(point[i]), "ci95": ci[:, i].tolist()} for i, name in enumerate(names)}}


@torch.no_grad()
def natural_predictions(model, teacher, banks, data, windows, items, metadata, args, budget):
    dtype = argparse.Namespace(device="cuda:0", dtype="bfloat16"); names = ("teacher", *STUDENTS); results = {}; noise = {}
    head = model.lm_head.weight.detach().float(); bias = model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None
    for population in ("Dolma_held_positions", "POS_held_targets"):
        rows = {a + "_to_" + b: [] for a, b in PAIRS}; chain = hashlib.sha256()
        if population == "POS_held_targets":
            pi, pm = map(list, zip(*[(item, row) for item, row in zip(items, metadata) if row["split"] == "held"]))
            if len(pi) != 512: raise ValueError("Exact fixed POS held512 required")
            iterator = operators.protocol.batches(pi, 16, "cuda:0", model.config.pad_token_id or 1)
            logps = {name: np.lib.format.open_memmap(args.raw_output / f"{name}_POS_logp.npy", mode="w+", dtype=np.float32, shape=(512, head.shape[0])) for name in names}
        else:
            iterator = enumerate(data.iter_fixed("held", windows, 16)); token_arrays = {key: np.lib.format.open_memmap(args.raw_output / f"{key}_Dolma_metrics.npy", mode="w+", dtype=np.float32, shape=(512, 512, len(METRICS))) for key in rows}
        for entry in iterator:
            budget.check()
            if population == "POS_held_targets":
                start, ids, mask, last, target = entry; meta = pm[start:start + len(ids)]
                chain.update(json.dumps([{**row, "last": int(last[i]), "target": int(target[i])} for i, row in enumerate(meta)], sort_keys=True).encode())
            else:
                index, (tokens, meta) = entry; start = index * 16; chain.update(tokens.numpy().astype("<i8", copy=False).tobytes()); ids = tokens[:, :-1].to("cuda:0"); target = tokens[:, 1:].to("cuda:0")
            predictions = {}
            for name in names:
                budget.check(); model.model.layers[9].mlp = teacher if name == "teacher" else banks[name];
                if name != "teacher": banks[name].inner.measurement = {}
                predict = lambda: legacy.pred.pos_logp(model, ids, mask, last, dtype, head, bias) if population == "POS_held_targets" else base.forward_logits(model, ids, dtype).float().log_softmax(-1)
                predictions[name] = predict()
                if start == 0:
                    repeated = predict(); noise[population + "_" + name] = legacy.pred.repeat_noise(predictions[name], repeated, target); del repeated
                if population == "POS_held_targets": logps[name][start:start + len(ids)] = predictions[name].cpu().numpy()
            for a, b in PAIRS:
                key = a + "_to_" + b; values = legacy.pred.previous.metrics(predictions[a], predictions[b], target)
                if not torch.isfinite(values).all(): raise RuntimeError("Nonfinite natural predictor readout")
                if population == "Dolma_held_positions": token_arrays[key][start:start + len(ids)] = values.cpu().numpy(); values = values.double().sum(1)
                values = values.double().cpu().numpy()
                rows[key].extend({**row, "tokens": 1 if population == "POS_held_targets" else 512, **dict(zip(METRICS, value.tolist())),
                    **({"last": int(last[i]), "target": int(target[i])} if population == "POS_held_targets" else {})} for i, (row, value) in enumerate(zip(meta, values)))
            del predictions
            base.emit("E138_natural_predictors", population=population, sequences=start + len(ids))
        model.model.layers[9].mlp = teacher
        if population == "POS_held_targets":
            for array in logps.values(): array.flush()
            arrays = {name: {"path": str(args.raw_output / f"{name}_POS_logp.npy"), "sha256": assets.sha(args.raw_output / f"{name}_POS_logp.npy")} for name in names}
        else:
            for array in token_arrays.values(): array.flush()
            arrays = {key: {"path": str(args.raw_output / f"{key}_Dolma_metrics.npy"), "sha256": assets.sha(args.raw_output / f"{key}_Dolma_metrics.npy")} for key in rows}
        path = args.raw_output / f"{population}_natural_rows.json"; assets.write(path, {"pairs": rows, "input_sha256": chain.hexdigest()})
        results[population] = {"pairs": {key: {"global": input_summary(value, population), **({"sources": {source: input_summary([row for row in value if row["source"] == source], population)
            for source in sorted({row["source"] for row in value})}} if population == "Dolma_held_positions" else {})} for key, value in rows.items()},
            "raw": str(path), "raw_sha256": assets.sha(path), "arrays": arrays, "input_sha256": chain.hexdigest(),
            "precision": "BF16 backbone, true FP32 final vocabulary head" if population == "POS_held_targets" else "BF16 whole logits then FP32 logsoftmax"}
        assets.write(args.raw_output / "natural_progress.json", results)
    return {"populations": results, "first_batch_repeat_noise": noise, "pair_orientation": "q=left name, p=right name; NLLgap=p-q; both KL directions", "scope": __doc__}


def fixed_A(a, b):
    if a["A"].ndim != 2 or a["A"].shape[1] != 64 or b["A"].shape != a["A"].shape: raise ValueError("Fixed A requires aligned all64 columns")
    if any(not np.isfinite(run[key]).all() for run in (a, b) for key in ("A", "normal_nll")): raise ValueError("Nonfinite A or natural NLL")
    for key in ("item_id", "input_sha256", "word", "split"):
        if not np.array_equal(a[key], b[key]): raise ValueError("Fixed A input identity/order differs")
    cal, held = a["split"] == "cal", a["split"] == "held"
    ar, ah, acov = matching.residualize(a["A"], a["word"], cal, held); br, bh, bcov = matching.residualize(b["A"], b["word"], cal, held)
    use = ah & bh
    if not use.any(): raise ValueError("No fixed POS held items covered by cal words")
    words = a["word"][use]; x, y = ar[use], br[use]; identity = np.arange(64)
    score = matching.column_scores(x, y, identity, identity, 1e-8); groups = [np.flatnonzero(words == word) for word in np.unique(words)]
    draws = np.random.default_rng(138).integers(0, len(groups), (1000, len(groups))) if groups else []
    samples = [matching.column_scores(x[index], y[index], identity, identity, 1e-8) for draw in draws for index in [np.concatenate([groups[i] for i in draw])]]
    finite = [row["mean"] for row in samples if row["mean"] is not None]; changed = sum(row["valid_mapping_positions"] != score["valid_mapping_positions"] for row in samples)
    comparable = len(finite) == len(samples) == 1000 and changed == 0
    return {"known_identity_mapping": list(range(64)), "held_conditional_columns": score, "ci95": np.quantile(finite, [.025, .975]).tolist() if comparable else None,
        "finite_draws": len(finite), "valid_mapping_positions_changed_draws": changed, "coverage_comparable": comparable, "bootstrap_seed": 138,
        "coverage": {"left": acov, "right": bcov}, "raw_difference": matching.raw_difference(a["A"][use], b["A"][use], identity, identity),
        "target_on_counts_left": a["selected_mask"][held].sum(0).tolist(), "target_on_counts_right": b["selected_mask"][held].sum(0).tolist(),
        "scope": "Only A, imposed identity, original all64 row-centering/cal-word offsets. Zero-on columns may inherit common row mean; no independent content claim for uncovered columns. CI requires every draw finite and identical valid-coordinate set."}


def load_A(path):
    with np.load(path, allow_pickle=False) as raw:
        arrays = {key: np.array(raw[key], copy=True) for key in ("A", "normal_nll", "selected_mask", "word", "split", "item_id", "input_sha256")}
    if (arrays["A"].shape != (1024, 64) or arrays["selected_mask"].shape != (1024, 64)
            or any(arrays[key].shape != (1024,) for key in ("normal_nll", "word", "split", "item_id", "input_sha256"))):
        raise ValueError("Immutable A array is not exact fixed1024/all64 plan")
    return arrays


@torch.no_grad()
def capture_A(model, teacher, bank, name, proof, manifest, items, metadata, args, budget):
    path = args.raw_output / f"{name}_A.npz"; summary_path = WB / "results/e138/A" / f"{name}.json"
    if path.exists():
        previous = assets.read(summary_path)
        if not previous or previous.get("raw_sha256") != assets.sha(path) or previous.get("checkpoint_proof") != proof or previous.get("script_sha256") != assets.sha(__file__): raise ValueError("Existing E138 A has different source proof")
        return load_A(path), previous
    if len(items) != 1024 or sum(row["split"] == "held" for row in metadata) != 512: raise ValueError("Exact fixed POS cal/held plan required")
    (teacher_idx, teacher_w, teacher_mask), teacher_proof = old_profiles.teacher_support(args, manifest, metadata)
    arrays = {"A": np.zeros((1024, 64), np.float32), "normal_nll": np.zeros(1024, np.float32), "selected_mask": np.zeros((1024, 64), bool),
        "selected_experts": np.zeros((1024, 8), np.int64), "selected_weights": np.zeros((1024, 8), np.float32)}
    scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16", _head_weight_fp32=model.lm_head.weight.detach().float(),
        _head_bias_fp32=model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None)
    support = {"rows": 0, "teacher_slot_mismatch_rows": 0, "teacher_mask_mismatch_rows": 0, "teacher_weight_max_abs_difference": 0.}; noise = {}
    model.model.layers[9].mlp = bank
    try:
        for start, ids, mask, last, targets in operators.protocol.batches(items, 16, "cuda:0", model.config.pad_token_id or 1):
            budget.check(); end = start + len(ids); bank.inner.measurement = {}; normal = operators.protocol.target_log_prob(model, ids, mask, last, targets, scoring)
            if not torch.isfinite(normal).all(): raise RuntimeError("Nonfinite normal POS target log probability")
            full_w, full_idx = bank.inner.last_router_logits.reshape(-1, 64).float().softmax(-1).topk(8, -1)
            rows = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last; selected = full_idx[rows].cpu().numpy(); weights = full_w[rows].cpu().numpy()
            arrays["normal_nll"][start:end] = -normal.cpu().numpy(); arrays["selected_experts"][start:end] = selected; arrays["selected_weights"][start:end] = weights
            np.put_along_axis(arrays["selected_mask"][start:end], selected, True, axis=1)
            support["rows"] += len(ids); support["teacher_slot_mismatch_rows"] += int(np.any(selected != teacher_idx[start:end], axis=1).sum())
            support["teacher_mask_mismatch_rows"] += int(np.any(arrays["selected_mask"][start:end] != teacher_mask[start:end], axis=1).sum())
            support["teacher_weight_max_abs_difference"] = max(support["teacher_weight_max_abs_difference"], float(np.max(np.abs(weights - teacher_w[start:end]))))
            if start == 0: noise["repeat_max_abs_logp"] = float((operators.protocol.target_log_prob(model, ids, mask, last, targets, scoring) - normal).abs().max())
            bank.inner.measurement = {"intervention": True, "drop_slot": None, "last": last}
            if start == 0: noise["identity_max_abs_logp"] = float((operators.protocol.target_log_prob(model, ids, mask, last, targets, scoring) - normal).abs().max())
            for slot in range(8):
                budget.check(); bank.inner.measurement["drop_slot"] = slot
                dropped = operators.protocol.target_log_prob(model, ids, mask, last, targets, scoring)
                if not torch.isfinite(dropped).all(): raise RuntimeError("Nonfinite dropped POS target log probability")
                arrays["A"][np.arange(start, end), selected[:, slot]] = (normal - dropped).cpu().numpy()
            base.emit("E138_A_only", condition=name, sequences=end)
    finally: model.model.layers[9].mlp = teacher; bank.inner.measurement = {}
    if support["teacher_slot_mismatch_rows"] or support["teacher_mask_mismatch_rows"] or support["teacher_weight_max_abs_difference"] != 0: raise RuntimeError(f"Fixed native A support differs: {support}")
    for key in ("word", "split", "input_sha256"): arrays[key] = np.array([row[key] for row in metadata], dtype=str)
    arrays["item_id"] = np.array([row["item_id"] for row in metadata], dtype=np.int64)
    header = {"experiment": "E138", "condition": name, "step": 4096, "A_only": True, "U_computed": False, "checkpoint_proof": proof,
        "script_sha256": assets.sha(__file__), "plan_sha256": assets.sha(args.plan), "teacher_support": support, "teacher_support_proof": teacher_proof,
        "selection_scope": "Full [B*S,64] native top8 first, then target rows; no-renorm slot removal, same full shape", "first_batch_noise": noise}
    arrays["metadata_json"] = np.array(json.dumps(header, allow_nan=False)); np.savez(path, **arrays)
    summary = {**header, "raw": str(path), "raw_sha256": assets.sha(path)}; assets.write(summary_path, summary); return arrays, summary


def reused_A(args, proof, manifest, metadata):
    path = args.e136_raw / "oracle_final_functional.npz"; record_path = WB / "results/e136/functional/oracle_final.json"
    record = assets.read(record_path)
    if not record or assets.sha(path) != record["output_sha256"]: raise ValueError("Immutable seed1 fresh-A source SHA differs")
    with np.load(path, allow_pickle=False) as raw:
        header = json.loads(str(raw["metadata_json"]))
        if (header["experiment"], header["condition"], header["condition_tensor_sha256"], header["plan_sha256"], header["condition_proof"]["checkpoint_sha256"]) != ("E136", "oracle_final", proof["full_tensor_sha256"], assets.PLAN_SHA, proof["checkpoint_sha256"]): raise ValueError("Seed1 A weight/input binding differs")
        for key in ("item_id", "word", "split", "input_sha256"):
            if not np.array_equal(raw[key], np.array([row[key] for row in metadata])): raise ValueError("Seed1 A population differs")
    return load_A(path), {"reused_observed_E136": True, "path": str(path), "sha256": assets.sha(path),
        "summary": str(record_path), "summary_sha256": assets.sha(record_path), "checkpoint_proof": proof}


@torch.no_grad()
def run(args):
    manifest, states, proofs, items, metadata, htarget = joint.preflight(args); gpu = c.select_gpu(args.physical_gpu); args.raw_output.mkdir(parents=True, exist_ok=True)
    result = {"experiment": "E138", "status": "partial", "stage": args.stage, "script_sha256": assets.sha(__file__), "components_script_sha256": assets.sha(joint.__file__),
        "training_script_sha256": joint.TRAIN_SHA, "native_trace_script_sha256": joint.NATIVE_SHA,
        "gpu_preflight": gpu, "condition_proofs": proofs, "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"),
        "POS_plan_sha256": assets.sha(args.plan),
        "cohort_weights": [1/3, 1/3, 1/3], "scope": __doc__, "errors": {}}
    with joint.training.Budget(args.budget_file, "readout_" + args.stage) as budget:
        model = OlmoeForCausalLM.from_pretrained(manifest["model"], dtype=torch.bfloat16, local_files_only=True, attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
        teacher = model.model.layers[9].mlp; teacher_hash = c.tensor_state_hash(teacher.state_dict()); prefix = base.sampled_parameter_hash(model, "model.layers.9.mlp.")
        if teacher_hash != manifest["teacher_block_tensor_sha256"] or prefix != manifest["teacher_prefix_hash"]: raise ValueError("Exact original public teacher differs")
        banks = {phase: {name: operators.MeasuredPublic(states[phase][name]) for name in STUDENTS} for phase in ("initial", "final")}; states.clear()
        before = {(phase, name): c.tensor_state_hash(bank.inner.state_dict()) for phase, group in banks.items() for name, bank in group.items()}
        stages = ("components", "predictions", "A") if args.stage == "all" else (args.stage,)
        for stage in stages:
            try:
                if stage == "components": result[stage] = joint.run_components(model, teacher, banks, manifest, items, metadata, htarget, args, budget)
                elif stage == "predictions":
                    data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
                    if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Fixed Dolma input population differs")
                    result[stage] = natural_predictions(model, teacher, banks["final"], data, windows, items, metadata, args, budget)
                else:
                    _, teacher_proof = old_profiles.teacher_support(args, manifest, metadata)
                    profiles = {"teacher": load_A(args.e135_raw / "teacher_functional.npz")}; summaries = {}
                    profiles["seed1"], summaries["seed1"] = reused_A(args, proofs["seed1"]["final"], manifest, metadata)
                    for name in ("seed0", "seed2"): profiles[name], summaries[name] = capture_A(model, teacher, banks["final"][name], name, proofs[name]["final"], manifest, items, metadata, args, budget)
                    result[stage] = {"profiles": summaries, "pairs": {a + "_to_" + b: fixed_A(profiles[a], profiles[b]) for a, b in PAIRS},
                        "teacher_profile": teacher_proof}
            except Exception as error: result["errors"][stage] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = teacher
            assets.write(args.summary, result)
        model.model.layers[9].mlp = teacher
        if c.tensor_state_hash(teacher.state_dict()) != teacher_hash or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != prefix or any(c.tensor_state_hash(bank.inner.state_dict()) != before[phase, name] for phase, group in banks.items() for name, bank in group.items()): raise RuntimeError("Read-only original/student parameters mutated")
        result["status"] = "complete" if args.stage == "all" and not result["errors"] else "partial"; result["completed_requested_stages"] = [stage for stage in stages if stage in result]; assets.write(args.summary, result)
    return result


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "evaluate", "self-test"), default="preflight")
    p.add_argument("--preflight-phase", choices=("initial", "all"), default="all", help="CPU preflight may check immutable initial states while new training is in progress")
    p.add_argument("--stage", choices=("all", "components", "predictions", "A"), default="all")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache")); p.add_argument("--oracle-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_oracle"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    for seed in (0, 2): p.add_argument(f"--seed{seed}-dir", type=Path, default=Path(f"/tmp/xiang-moe-20261025/e138_seed{seed}"))
    p.add_argument("--e135-raw", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_readout")); p.add_argument("--e136-raw", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_readout"))
    p.add_argument("--plan", type=Path, default=WB / "results/e124/plan.json"); p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_budget.json"))
    p.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e138_readout")); p.add_argument("--summary", type=Path, default=WB / "results/e138/readout.json")
    p.add_argument("--physical-gpu", type=int, default=0); return p


def self_test():
    result = joint.self_test()
    assert tuple(legacy.pred.NAMES) == ("kl_teacher_to_student", "teacher_nll", "student_nll", "nll_gap", "kl_student_to_teacher", "top1_agreement")
    assert len(METRICS) == len(legacy.pred.NAMES) == 6
    toy = [{"word": "a", "source": "x", "file_id": "1", "tokens": 2, **dict(zip(METRICS, [2, 4, 8, 4, 6, 2]))},
           {"word": "b", "source": "x", "file_id": "2", "tokens": 1, **dict(zip(METRICS, [2, 3, 4, 1, 2, 1]))}]
    assert input_summary(toy, "Dolma_held_positions")["nll_gap_right_minus_left"]["point"] == 5/3
    assert input_summary(toy, "POS_held_targets")["nll_gap_right_minus_left"]["point"] == 1.5
    rng = np.random.default_rng(138); a = rng.normal(size=(12, 64)); capture = {"A": a, "word": np.array(["a", "b", "c"] * 4), "split": np.array(["cal"] * 6 + ["held"] * 6),
        "item_id": np.arange(12), "input_sha256": np.array([str(i) for i in range(12)]), "selected_mask": np.ones((12, 64), bool),
        "normal_nll": np.zeros(12)}
    scores = fixed_A(capture, capture); assert scores["held_conditional_columns"]["mean"] > .999999
    result.update({"readout_sha256": assets.sha(__file__), "six_fixed_predictor_pairs": len(PAIRS) == 6, "input_cluster_statistic_math": True, "identity_A_cal_word_offsets": True})
    assets.write(WB / "results/e138/readout_self_test.json", result); return result


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, states, proofs, items, metadata, h = joint.preflight(args, initial_only=args.preflight_phase == "initial"); result = {"status": "CPU_preflight_only", "phase": args.preflight_phase, "proofs": proofs, "POS_Htarget_shape": list(h.shape), "readout_sha256": assets.sha(__file__), "components_sha256": assets.sha(joint.__file__)}
    else: result = run(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
