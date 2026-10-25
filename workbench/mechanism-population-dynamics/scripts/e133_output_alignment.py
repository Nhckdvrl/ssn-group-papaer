"""E133 fixed cal-only uniform/support output baselines; no training or tuning.

Inputwise full-vector MSE under fixed coordinates, not an exact HC-SMoE
reproduction or a novel matching/theorem claim. Cauchy diagnostics describe
real sums on the cal cache, not held predictions or exact BF16 equivariance.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, time
from pathlib import Path
import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
import e132_bank_grafting as old

assets, base, WB = old.assets, old.base, old.WB
E132_SHA = "ed269682c2ad7e62f8fc5bac407e1834e8de304125e6c7d0794c414d6441e8e0"
METHODS = ("uniform_output", "support_output")


def array_sha(value):
    value = np.ascontiguousarray(value)
    return hashlib.sha256(str((value.shape, value.dtype.str)).encode() + value.tobytes()).hexdigest()


def calibration_capture(capture, path):
    cal = np.asarray(capture["split"]) == "cal"
    with np.load(path, allow_pickle=False) as raw: weights = np.asarray(raw["gate_weights"])[cal].astype(np.float64)
    hidden = np.asarray(capture["Htarget"])[cal].astype(np.float32)
    if hidden.shape != (512, 2048) or weights.shape != (512, 64): raise ValueError("Expected fixed cal512 H/weights")
    if not np.isfinite(hidden).all() or not np.isfinite(weights).all() or (weights < 0).any(): raise ValueError("Invalid cal input/nonnegative support")
    identity = {key: np.asarray(capture[key])[cal].tolist() for key in ("item_id", "input_sha256", "split")}
    return hidden, weights, {"cal_input_sha256": array_sha(hidden), "cal_weights_sha256": array_sha(weights),
                              "cal_identity_sha256": base.digest_json(identity), "items": int(cal.sum()), "held_used": False}


@torch.no_grad()
def output_cache(bank, hidden, name, identity, args):
    folder = args.raw_output / "cal_cache"; folder.mkdir(parents=True, exist_ok=True)
    path, manifest_path = folder / f"{name}.npy", folder / f"{name}.json"
    key = {"script_sha256": assets.sha(__file__), "source_tensor_sha256": identity["metadata"]["source_tensor_sha256"],
           "capture_sha256": identity["capture_sha256"], "cal_input_sha256": array_sha(hidden),
           "precision": "FP32 master expert, captured H cast BF16, BF16 autocast, output stored FP32", "expert_batch_size": 512}
    previous = assets.read(manifest_path)
    if path.exists():
        if not previous or previous.get("identity") != key or assets.sha(path) != previous.get("sha256"):
            raise ValueError("Existing cal output cache has different source/precision/SHA")
        return np.load(path, mmap_mode="r", allow_pickle=False), previous
    temporary = path.with_suffix(".partial.npy")
    values = np.lib.format.open_memmap(temporary, mode="w+", dtype=np.float32, shape=(512, 64, 2048))
    inputs = torch.from_numpy(hidden).to(device="cuda:0", dtype=torch.bfloat16)
    for expert, module in enumerate(bank.block.experts):
        with torch.autocast("cuda", dtype=torch.bfloat16): output = module(inputs)
        if not torch.isfinite(output).all(): raise RuntimeError(f"Nonfinite cal expert output: {name}/{expert}")
        values[:, expert] = output.float().cpu().numpy()
    values.flush(); del values, inputs, output
    temporary.replace(path)
    record = {"identity": key, "path": str(path), "sha256": assets.sha(path), "shape": [512, 64, 2048], "dtype": "float32"}
    assets.write(manifest_path, record)
    return np.load(path, mmap_mode="r", allow_pickle=False), record


def costs(target, source, weights):
    """Float64 direct differences, with no norm-dot cancellation or normalization."""
    target, source, weights = np.asarray(target, dtype=np.float64), np.asarray(source, dtype=np.float64), np.asarray(weights, dtype=np.float64)
    if target.shape != source.shape or weights.shape != target.shape[:2]: raise ValueError("Cal output/support dimensions differ")
    if not all(np.isfinite(value).all() for value in (target, source, weights)) or (weights < 0).any(): raise ValueError("Nonfinite outputs/negative support")
    n, experts, _ = target.shape; uniform, support = np.empty((experts, experts)), np.empty((experts, experts))
    mass = weights.sum(1); importance = mass[:, None] * weights
    for e in range(experts):
        for start in range(0, experts, 8):
            delta = target[:, e, None, :] - source[:, start:start + 8, :]
            squared = np.einsum("njd,njd->nj", delta, delta)
            uniform[e, start:start + 8] = squared.mean(0)
            support[e, start:start + 8] = (importance[:, e, None] * squared).mean(0)
    diagnostics = {"items": n, "mass_min_max": [float(mass.min()), float(mass.max())], "mass_mean": float(mass.mean()),
        "zero_mass_inputs": int((mass == 0).sum()), "nonzero_support_count_per_expert": (weights > 0).sum(0).tolist(),
        "support_weight_sum_per_expert": weights.sum(0).tolist(), "unconstrained_zero_support_rows": np.flatnonzero(weights.sum(0) == 0).tolist(),
        "weight_definition": "Captured top8 softmax weights, unselected0; importance=s_n*w_ne, without frequency or mass renormalization"}
    return {"uniform_output": uniform, "support_output": support}, diagnostics


def select_calibration(target, source, weights):
    matrices, diagnostics = costs(target, source, weights)
    t, s, w = np.asarray(target, dtype=np.float64), np.asarray(source, dtype=np.float64), np.asarray(weights, dtype=np.float64)
    result = {}
    for method, matrix in matrices.items():
        ia, ib = linear_sum_assignment(matrix); permutation = np.empty(len(ia), dtype=int); permutation[ia] = ib
        delta = np.zeros((len(w), t.shape[2]), dtype=np.float64)
        for e, j in enumerate(permutation): delta += w[:, e, None] * (s[:, j] - t[:, e])
        error = float(np.square(delta).sum(1).mean())
        bound = float(matrices["support_output"][np.arange(len(permutation)), permutation].sum())
        result[method] = {"target_to_source": permutation.tolist(), "cost_matrix": matrix.tolist(),
            "assignment_cost": float(matrix[np.arange(len(permutation)), permutation].sum()),
            "cal_mixture_squared_l2_mean": error, "cal_cauchy_upper_bound": bound, "bound_minus_actual": bound - error,
            "bound_scope": "Same cal cache, float64 real weighted sums; no held or BF16-program guarantee",
            "zero_support_rows": diagnostics["unconstrained_zero_support_rows"] if method == "support_output" else [],
            "zero_row_ties": "Ordinary Hungarian assignment under the full bijection; no held/secondary score"}
    return {"methods": result, "support": diagnostics, "direction": "target slot e -> source expert permutation[e]", "held_used_for_fitting": False,
            "statistics_precision": "Float64 direct delta squared; BF16 expert outputs are stored exactly as FP32"}


def secondary_function_scores(target, source, alignment):
    """Held U/A evaluated under already locked output maps; no rematching."""
    for key in ("item_id", "input_sha256", "word", "split"):
        if not np.array_equal(target[key], source[key]): raise ValueError(f"Secondary fixed anchors differ: {key}")
    cal, held = target["split"] == "cal", target["split"] == "held"
    residuals, coverage, use = {}, {}, held.copy()
    for who, capture in (("target", target), ("source", source)):
        for key in ("U", "A"):
            residual, covered, cov = old.matching.residualize(capture[key], capture["word"], cal, held)
            residuals[who, key], coverage[who + "_" + key] = residual, cov; use &= covered
    scores = {}
    for method in METHODS:
        permutation = np.asarray(alignment["methods"][method]["target_to_source"], dtype=int)
        scores[method] = {"target_to_source_locked": permutation.tolist(), "function": {
            key: old.matching.column_scores(residuals["target", key][use], residuals["source", key][use],
                                            np.arange(len(permutation)), permutation, 1e-8) for key in ("U", "A")}}
    return {"scope": "Pre-registered secondary; fixed cal-output maps evaluated on held scalar U/A, without held rematching or method selection; does not replace E130 matcher",
            "coverage": coverage, "n_cal_items": int(cal.sum()), "n_held_items_evaluated": int(use.sum()), "methods": scores}


def paired_contrast(method, references):
    if not method or any(len(reference) != len(method) for reference in references): raise ValueError("Incomplete paired old/new rows")
    rows = []
    for index, value in enumerate(method):
        other = [reference[index] for reference in references]
        if any(any(value[key] != row[key] for key in ("source", "file_id", "window", "tokens")) for row in other):
            raise ValueError("Old/new window sequence differs")
        rows.append({**{key: value[key] for key in ("source", "file_id", "window", "tokens")},
            "nll_new_minus_reference": value["student_nll"] - float(np.mean([row["student_nll"] for row in other])),
            "kl_new_minus_reference": value["kl_teacher_to_student"] - float(np.mean([row["kl_teacher_to_student"] for row in other]))})
    return old.summaries(rows, ("nll_new_minus_reference", "kl_new_minus_reference"))


def reference_rows(pair, target_id, source_id, identities, input_hash, natural_rows):
    if pair["status"] != "complete" or pair["target"] != target_id or pair["source"] != source_id: raise ValueError("Wrong E132 ring reference")
    if pair["source_assets"] != identities: raise ValueError("Old/new model/source proof differs")
    path = Path(pair["raw_sequences"])
    if assets.sha(path) != pair["raw_sha256"]: raise ValueError("Immutable E132 raw SHA differs")
    if input_hash != pair["input_sha256"]: raise ValueError("Actual whole-LM input hash differs from E132")
    previous = assets.read(path)
    if previous["target"] != target_id or previous["source"] != source_id: raise ValueError("E132 raw identity differs")
    old_rows = previous["conditions"]["natural_target"]
    if len(natural_rows) != len(old_rows) or len(natural_rows) != 512: raise ValueError("Incomplete natural-target old/new reference")
    keys = ("source", "file_id", "window", "tokens", "teacher_nll", "student_nll")
    if any(any(a[key] != b[key] for key in keys) for a, b in zip(natural_rows, old_rows)):
        difference = max(abs(a["student_nll"] - b["student_nll"]) for a, b in zip(natural_rows, old_rows))
        raise ValueError(f"Natural target per-sequence reference differs; max_abs_sum_delta={difference}")
    for name in ("graft_U", "graft_router", "random_132", "random_133", "random_134"):
        if previous["status"][name]["status"] != "complete": raise ValueError(f"E132 reference condition incomplete: {name}")
    return previous["conditions"], {"raw_path": str(path), "raw_sha256": pair["raw_sha256"],
        "input_sha256": input_hash, "source_assets_exact_match": True, "natural_target_sequence_NLL_exact_match": True}


@torch.no_grad()
def evaluate_pair(index, args, started, old_result):
    target_id, source_id = old.IDS[index], old.IDS[(index + 1) % 5]
    target, tc, tp, ts, ti = old.load_asset(args.bank_root, target_id)
    source, sc, sp, ss, si = old.load_asset(args.bank_root, source_id)
    th, weights, cal_identity = calibration_capture(tc, ti["metadata"]["functional_capture"])
    sh, _, source_cal_identity = calibration_capture(sc, si["metadata"]["functional_capture"])
    if not np.array_equal(th, sh) or cal_identity["cal_identity_sha256"] != source_cal_identity["cal_identity_sha256"]:
        raise ValueError("Target/source cal profile inputs differ")
    if Path(tp["args"]["model"]).resolve() != Path(sp["args"]["model"]).resolve(): raise ValueError("Frozen model source differs")
    target, source = target.to("cuda:0"), source.to("cuda:0")
    tcache, tproof = output_cache(target, th, target_id, ti, args)
    scache, sproof = output_cache(source, sh, source_id, si, args)
    alignment = select_calibration(tcache, scache, weights)  # No held reference is passed into fitting.
    pair_id = f"target{index}_from_source{(index + 1) % 5}"
    fit_path = args.raw_output / f"{pair_id}_calibration.json"
    assets.write(fit_path, {"alignment": alignment, "cal_identity": cal_identity, "output_caches": {"target": tproof, "source": sproof}})
    secondary = secondary_function_scores(tc, sc, alignment)  # Only after the cal-only maps are fixed on disk.
    data = base.TokenData(tp["args"]["data"], 512); windows = data.fixed_windows("held", 512, tp["args"]["eval_seed"])
    old.fidelity.guard_inputs(tp, data, windows); old.fidelity.guard_inputs(sp, data, windows)
    model = old.OlmoForCausalLM.from_pretrained(tp["args"]["model"], dtype=torch.bfloat16, local_files_only=True,
        attn_implementation="sdpa").to("cuda:0").eval(); model.requires_grad_(False); model.config.use_cache = False
    original = model.model.layers[9].mlp
    if base.sampled_parameter_hash(model, "model.layers.9.mlp.") != old.FROZEN: raise ValueError("Frozen backbone differs")
    modules = {"source_coupled": source}
    for method in METHODS:
        permutation = alignment["methods"][method]["target_to_source"]
        experts = [source.block.experts[j] for j in permutation]
        modules[method] = old.SharedMoE(target.block.gate, experts, 8)
        modules[f"source_gauge_{method}"] = old.SharedMoE(old.PermutedGate(source.block.gate, permutation), experts, 8)
    status = {name: {"status": "running"} for name in ("natural_target", *modules, *[f"gauge_direct_{method}" for method in METHODS])}
    raw = {name: [] for name in status}; input_hash = hashlib.sha256(); completed = 0; identity_floor = None
    scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16")
    for batch_index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
        if time.monotonic() - started >= args.max_hours * 3600: break
        input_hash.update(batch.numpy().astype("<i8", copy=False).tobytes()); batch = batch.to("cuda:0"); labels = batch[:, 1:]
        model.model.layers[9].mlp = target
        teacher = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
        raw["natural_target"].extend(old.rows_from_logps(teacher, teacher, labels, metadata))
        if batch_index == 0:
            model.model.layers[9].mlp = old.SharedMoE(target.block.gate, list(target.block.experts), 8)
            identity = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            values = old.fidelity.token_metrics(teacher, identity, labels)
            identity_floor = {"tokens": labels.numel(), "kl_max_abs": float(values[..., 0].abs().max()),
                "nll_delta_max_abs": float(values[..., 3].abs().max()), "log_probability_max_abs": float((teacher - identity).abs().max())}
            del values, identity
        source_lp = None
        for name, module in modules.items():
            if status[name]["status"] != "running": continue
            try:
                model.model.layers[9].mlp = module
                student = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                raw[name].extend(old.rows_from_logps(teacher, student, labels, metadata))
                if name == "source_coupled": source_lp = student
                if name.startswith("source_gauge_"):
                    method = name[len("source_gauge_"):]
                    if source_lp is None: raise RuntimeError("Source baseline missing for direct gauge KL")
                    raw[f"gauge_direct_{method}"].extend(old.rows_from_logps(source_lp, student, labels, metadata))
                if name != "source_coupled": del student
            except Exception as error:
                status[name] = {"status": "failed", "error": f"{type(error).__name__}: {error}", "batch": batch_index}
                if name.startswith("source_gauge_"): status[f"gauge_direct_{name[len('source_gauge_'):]}"] = {"status": "failed", "error": "Source/gauge unavailable"}
        target.last_router_logits = source.last_router_logits = None
        del teacher, source_lp; completed += 1
        base.emit("output_alignment_batch", target=target_id, source=source_id, completed=completed, total=32)
    model.model.layers[9].mlp = original
    if base.sampled_parameter_hash(model, "model.layers.9.mlp.") != old.FROZEN: raise RuntimeError("Frozen backbone changed")
    if old.tensor_state_hash(target.state_dict()) != ti["metadata"]["source_tensor_sha256"] or old.tensor_state_hash(source.state_dict()) != si["metadata"]["source_tensor_sha256"]:
        raise RuntimeError("Original expert bank changed")
    for name, record in status.items():
        if record["status"] == "running":
            record["status"] = "complete" if len(raw[name]) == 512 else "incomplete_budget"
            if record["status"] == "complete": record["metrics"] = old.summaries(raw[name])
    for name, summary in (("natural_target", ts), ("source_coupled", ss)):
        if status[name]["status"] == "complete":
            legacy = next(row["held"]["file"] for row in summary["evaluations"] if row["step"] == 62500)
            status[name]["legacy_NLL_difference"] = status[name]["metrics"]["global"]["student_nll"]["mean"] - legacy["mean"]
    identities = {"target": ti, "source": si}; contrasts = {}
    try:
        previous, reference = reference_rows(old_result["pairs"][pair_id], target_id, source_id, identities, input_hash.hexdigest(), raw["natural_target"])
        for method in METHODS:
            contrasts[method] = {name: paired_contrast(raw[method], [previous[key] for key in keys]) if status[method]["status"] == "complete" else None
                for name, keys in {"E132_U": ["graft_U"], "E132_router": ["graft_router"], "E132_mean_three_random": [f"random_{seed}" for seed in old.RANDOM_SEEDS]}.items()}
        reference["status"] = "matched"
    except Exception as error: reference = {"status": "mismatch_or_incomplete", "error": f"{type(error).__name__}: {error}"}
    attempt = len(list(args.raw_output.glob(f"{pair_id}_attempt*_sequences.json"))) + 1
    raw_path = args.raw_output / f"{pair_id}_attempt{attempt:02d}_sequences.json"
    assets.write(raw_path, {"target": target_id, "source": source_id, "conditions": raw, "status": status})
    result = {"status": "complete" if completed == 32 and reference["status"] == "matched" and not any(value["status"] == "failed" for value in status.values()) else "incomplete_or_failed",
        "target": target_id, "source": source_id, "alignment": alignment, "cal_identity": cal_identity, "output_caches": {"target": tproof, "source": sproof},
        "secondary_fixed_map_U_A": secondary,
        "calibration_file": str(fit_path), "calibration_sha256": assets.sha(fit_path), "conditions": status, "identity_numeric_floor": identity_floor,
        "paired_old_reference": reference, "new_minus_E132": contrasts, "source_assets": identities,
        "held_window_hash": base.digest_json(windows), "input_sha256": input_hash.hexdigest(), "completed_batches": completed,
        "raw_sequences": str(raw_path), "raw_sha256": assets.sha(raw_path), "gauge_scope": "Each gauge_direct_* is direct KL(p_source||source_gauge) and paired NLL delta, not difference of target KLs"}
    del model, target, source, modules; gc.collect(); torch.cuda.empty_cache()
    return result


def run(args):
    if assets.sha(WB / "scripts/e132_bank_grafting.py") != E132_SHA: raise ValueError("Frozen E132 implementation differs")
    old_result = assets.read(args.e132_summary)
    if not old_result or old_result.get("status") != "complete" or old_result.get("script_sha256") != E132_SHA: raise ValueError("Complete frozen E132 result required")
    for name, expected in old_result["frozen_sources"].items():
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError(f"Frozen source differs: {name}")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", ""); physical = args.physical_gpu
    if physical is None:
        if not visible.isdigit(): raise ValueError("Specify one physical GPU index explicitly")
        physical = int(visible)
    if visible and visible != str(physical): raise ValueError("Visible GPU differs from requested physical GPU")
    if torch.cuda.is_initialized(): raise RuntimeError("CUDA initialized before occupancy check")
    gpu = assets.gpu_status(physical)
    result = {"experiment": "E133", "status": "partial", "script_sha256": assets.sha(__file__), "E132_script_sha256": E132_SHA,
        "E132_summary": str(args.e132_summary), "E132_summary_sha256": assets.sha(args.e132_summary), "precision": old_result["precision"],
        "gpu_preflight": gpu, "fixed_ring": old_result["fixed_ring"], "pairs": {}, "baseline_scope": __doc__,
        "sampling_note": "Five fixed edges share models; file CIs describe evaluation uncertainty only, no across-edge/seed CI"}
    if not assets.gpu_free(gpu): result["status"] = "deferred_gpu_busy_or_unavailable"; assets.write(args.summary, result); return result
    previous = assets.read(args.summary); prior = previous.get("elapsed_wall_seconds", 0.) if previous and previous.get("script_sha256") == result["script_sha256"] else 0.
    result["previous_wall_seconds_charged"] = prior; os.environ["CUDA_VISIBLE_DEVICES"] = str(physical); started = time.monotonic() - prior
    for index, edge in enumerate(result["fixed_ring"]):
        name = f"target{index}_from_source{(index + 1) % 5}"
        if index >= args.max_pairs or time.monotonic() - started >= args.max_hours * 3600:
            result["pairs"][name] = {"status": "not_run_fixed_pair_limit_or_budget", **edge}; continue
        try: result["pairs"][name] = evaluate_pair(index, args, started, old_result)
        except Exception as error:
            result["pairs"][name] = {"status": "failed", **edge, "error": f"{type(error).__name__}: {error}"}
            gc.collect()
            if torch.cuda.is_initialized(): torch.cuda.empty_cache()
        assets.write(args.summary, result)
    result["status"] = "complete" if all(pair["status"] == "complete" for pair in result["pairs"].values()) else "partial"
    result["global_descriptive"] = old.global_descriptive(result["pairs"])
    result["elapsed_wall_seconds"] = time.monotonic() - started
    assets.write(args.summary, result); return result


def self_test():
    torch.set_num_threads(1)
    rng = np.random.default_rng(133); n, e, d = 7, 4, 3
    target, source = rng.normal(size=(n, e, d)), rng.normal(size=(n, e, d))
    weights = rng.uniform(.1, 2., size=(n, e)); weights[:, 3] = 0; weights[0] = 0
    matrices, info = costs(target, source, weights)
    brute_uniform, brute_support = np.zeros((e, e)), np.zeros((e, e))
    for a in range(e):
        for b in range(e):
            for i in range(n):
                distance = sum((target[i, a, k] - source[i, b, k]) ** 2 for k in range(d))
                brute_uniform[a, b] += distance / n; brute_support[a, b] += weights[i].sum() * weights[i, a] * distance / n
    assert np.allclose(matrices["uniform_output"], brute_uniform, rtol=1e-14, atol=1e-14)
    assert np.allclose(matrices["support_output"], brute_support, rtol=1e-14, atol=1e-14)
    assert info["unconstrained_zero_support_rows"] == [3] and info["mass_min_max"][1] > 1 and info["zero_mass_inputs"] == 1
    permutation = np.array([2, 0, 3, 1]); inverse = np.argsort(permutation)
    same = select_calibration(target, target[:, permutation], np.ones((n, e)) * .6)
    for method in METHODS:
        assert same["methods"][method]["target_to_source"] == inverse.tolist()
        assert same["methods"][method]["cal_mixture_squared_l2_mean"] == 0
    selection = select_calibration(target, source, weights)
    for method in METHODS:
        value = selection["methods"][method]
        assert value["cal_mixture_squared_l2_mean"] <= value["cal_cauchy_upper_bound"] + 1e-12
        permutation = value["target_to_source"]
        brute_error = np.mean([sum(sum(weights[i, a] * (source[i, permutation[a], k] - target[i, a, k]) for a in range(e)) ** 2 for k in range(d)) for i in range(n)])
        assert np.isclose(value["cal_mixture_squared_l2_mean"], brute_error, rtol=1e-14, atol=1e-14)
    # Exercise the real extraction function, including invalid held-only weights.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="e133_cal_isolation_") as directory:
        capture = {"split": np.array(["cal"] * 512 + ["held"] * 512), "item_id": np.arange(1024),
                   "input_sha256": np.array([str(i) for i in range(1024)]), "Htarget": np.zeros((1024, 2048), np.float32)}
        capture["Htarget"][:512, :3] = rng.normal(size=(512, 3))
        gate_weights = np.zeros((1024, 64), np.float32); gate_weights[:, :8] = .0625
        path = Path(directory) / "capture.npz"; np.savez(path, gate_weights=gate_weights)
        before_h, before_w, before_identity = calibration_capture(capture, path)
        capture["Htarget"][512:] = 1000; gate_weights[512:] = -1; np.savez(path, gate_weights=gate_weights)
        after_h, after_w, after_identity = calibration_capture(capture, path)
        assert np.array_equal(before_h, after_h) and np.array_equal(before_w, after_w) and before_identity == after_identity
    words = np.array([f"w{i%8}" for i in range(80)]); split = np.array(["cal"] * 40 + ["held"] * 40)
    u = rng.normal(size=(80, e)); profile = {"word": words, "split": split, "U": u, "A": u * .3,
        "item_id": np.arange(80), "input_sha256": np.array([str(i) for i in range(80)])}
    other = {**profile, "U": u[:, [2, 0, 3, 1]], "A": u[:, [2, 0, 3, 1]] * .3}
    secondary = secondary_function_scores(profile, other, same)
    for method in METHODS:
        for key in ("U", "A"):
            assert np.isclose(secondary["methods"][method]["function"][key]["mean"], 1)
            assert secondary["methods"][method]["function"][key]["n_valid_columns"] == e
    locked = json.dumps(same, sort_keys=True)
    other["U"][40:] = rng.normal(size=(40, e)); secondary_function_scores(profile, other, same)
    assert json.dumps(same, sort_keys=True) == locked
    rows = [{"source": "s", "file_id": str(i), "window": 0, "tokens": count, "student_nll": count, "kl_teacher_to_student": count} for i, count in enumerate((2, 4))]
    previous = [{**row, "student_nll": row["student_nll"] + row["tokens"], "kl_teacher_to_student": row["kl_teacher_to_student"] + row["tokens"]} for row in rows]
    paired = paired_contrast(rows, [previous, previous, previous])["global"]
    assert paired["nll_new_minus_reference"]["ci95"] == [-1., -1.] and paired["kl_new_minus_reference"]["mean"] == -1
    assert assets.sha(WB / "scripts/e132_bank_grafting.py") == E132_SHA
    tiny = base.TensorMoE(8, 8, 4, 2, .02).eval(); before_hash = old.tensor_state_hash(tiny.state_dict())
    before_order = tuple(id(module) for module in tiny.block.experts); hidden = torch.randn(7, 8)
    with torch.no_grad():
        for module in tiny.block.experts: module(hidden)
        identity = old.SharedMoE(tiny.block.gate, list(tiny.block.experts), 2)
        assert torch.equal(tiny(hidden[None]), identity(hidden[None]))
    assert old.tensor_state_hash(tiny.state_dict()) == before_hash and before_order == tuple(id(module) for module in tiny.block.experts)
    result = {"passed": True, "device": "cpu", "script_sha256": assets.sha(__file__), "costs_match_direct_brute_force": True,
        "known_relabel_target_to_source_direction": True, "weighted_Cauchy_nonnegative_mass_over1_and_zero_support": True,
        "held_not_used_for_fit": True, "secondary_known_relabel_and_no_rematching": True,
        "original_modules_unchanged": True, "paired_old_new_file_statistics": True, "no_GPU_or_full_LM": True}
    assets.write(WB / "results/e133/self_test.json", result); print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bank-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e132_banks"))
    parser.add_argument("--e132-summary", type=Path, default=WB / "results/e132/bank_grafting.json")
    parser.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e133_output_alignment"))
    parser.add_argument("--summary", type=Path, default=WB / "results/e133/output_alignment.json")
    parser.add_argument("--max-pairs", type=int, default=5); parser.add_argument("--max-hours", type=float, default=1.)
    parser.add_argument("--physical-gpu", type=int)
    args = parser.parse_args()
    if args.self_test: self_test()
    else:
        if not 1 <= args.max_pairs <= 5 or not 0 < args.max_hours <= 1: parser.error("Fixed five-ring, cumulative budget<=1h")
        if args.raw_output.resolve().is_relative_to(WB): parser.error("Output caches/raw must remain outside git")
        print(json.dumps(run(args), indent=2), flush=True)
