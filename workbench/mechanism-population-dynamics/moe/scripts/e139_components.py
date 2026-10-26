"""E139 actual native components, one Hcal squared-distance map to seed1 per group/phase."""
from __future__ import annotations
import argparse, copy, json, tempfile
from pathlib import Path
import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
from torch import nn
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock
import e137_components as native
import e138_components as joint
import e139_train as training

c, assets, base, WB = training.c, training.assets, training.base, training.WB
STUDENTS = joint.STUDENTS
AGG = joint.AGG
EXPERT = ("on_count_seed0", "on_count_seed1", "on_count_seed2", "on_count_union", "on_count_all",
          "energy_seed0", "energy_seed1", "energy_seed2", "cohort_mean_energy", "cohort_variance",
          "pair_seed0_seed1_SSE", "pair_seed0_seed2_SSE", "pair_seed1_seed2_SSE",
          "product_floor_seed0_SSE", "product_floor_seed1_SSE", "product_floor_seed2_SSE")
TRAIN_SHA = "93ac8504e21364ca94d6dd5ca18c22493850c41e74b7f0d1cfe12b398e3bcbac"
FIXED_COMPONENTS_SHA = "b177c4daedc480c271fa41d4fd8c1b3b581887667cb741dc6b9cf543a9d297f8"
NATIVE_SHA = joint.NATIVE_SHA


def preflight(args, *, initial_only=False):
    for name, expected in (("e139_train.py", TRAIN_SHA), ("e138_components.py", FIXED_COMPONENTS_SHA), ("e137_components.py", NATIVE_SHA)):
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError(f"Frozen E139 component dependency differs: {name}")
    fixed_args = copy.copy(args); fixed_args.budget_file = args.e138_budget_file
    manifest, fixed_states, fixed_proofs, items, metadata, htarget = joint.preflight(fixed_args, initial_only=initial_only)
    teacher = fixed_states["teacher"]
    free_states = {"initial": {}, "final": {}}; free_proofs = {}
    seed1_dir = args.free_seed1_dir; source_sha = assets.sha(args.cache_root / "manifest.json")
    seed1_provenance = assets.read(seed1_dir / "provenance.json"); seed1_summary = assets.read(seed1_dir / "training_summary.json")
    free_proofs["seed1"] = {"scope": "Already observed E135 free-router pilot reused"}
    for phase, step, filename in (("initial", 0, "initial.pt"), ("final", 4096, "checkpoint.pt")):
        path = seed1_dir / filename; cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = cp["student_state"]
        if (cp.get("experiment"), cp.get("schema"), cp.get("step"), cp.get("cache_manifest_sha256")) != ("E135", "E135-student-v1", step, source_sha):
            raise ValueError("Observed free seed1 checkpoint identity/cache differs")
        if cp.get("config_hash") != seed1_provenance["config_hash"] or seed1_provenance["scientific"]["driver_sha256"] != training.SOURCE_SHA:
            raise ValueError("Observed free seed1 source/config differs")
        digest = c.tensor_state_hash(state)
        if step == 0 and (digest != cp["initial_tensor_sha256"] or cp["optimizer"]["state"] or np.any(cp["cache_batch_counts"])):
            raise ValueError("Observed free seed1 initial state differs")
        if step == 4096 and (seed1_summary.get("status") != "complete" or seed1_summary.get("step") != 4096 or digest != seed1_summary["final_tensor_sha256"]
                or not np.array_equal(cp["cache_batch_counts"], np.full(1024, 4))):
            raise ValueError("Observed free seed1 fixed final differs")
        free_states[phase]["seed1"] = state
        free_proofs["seed1"][phase] = {"checkpoint": str(path), "checkpoint_sha256": assets.sha(path), "full_tensor_sha256": digest,
            "expert_only_tensor_sha256": training.expert_hash(state), "gate_tensor_sha256": training.gate_hash(state), "step": step}
    for seed in (0, 2):
        name = f"seed{seed}"; new_args = copy.copy(args); new_args.seed = seed; new_args.fixed_initial = getattr(args, f"fixed_seed{seed}_dir") / "initial.pt"
        _, _, _, _, initial, _, expected = training.preflight(new_args)
        directory = getattr(args, f"free_seed{seed}_dir"); provenance = assets.read(directory / "provenance.json")
        summary = assets.read(directory / "training_summary.json"); free_proofs[name] = {}
        endpoints = (("initial", 0, "initial.pt"),) if initial_only else (("initial", 0, "initial.pt"), ("final", 4096, "checkpoint.pt"))
        for phase, step, filename in endpoints:
            path = directory / filename; cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = cp["student_state"]
            if (cp.get("experiment"), cp.get("schema"), cp.get("seed"), cp.get("step"), cp.get("cache_manifest_sha256")) != ("E139", "E139-free-routing-student-v1", seed, step, source_sha):
                raise ValueError("New free student endpoint/cache identity differs")
            if (cp["initialization"] != expected or cp["config_hash"] != provenance["config_hash"]
                    or provenance["scientific"]["driver_sha256"] != TRAIN_SHA or any(value.dtype != torch.float32 for value in state.values())):
                raise ValueError("New free student source/config/FP32 proof differs")
            digest = c.tensor_state_hash(state)
            if step == 0 and (digest != expected["free_initial_full_tensor_sha256"] or cp["optimizer"]["state"] or np.any(cp["cache_batch_counts"])):
                raise ValueError("New free initial tensor/optimizer/exposure differs")
            if step == 4096 and (summary.get("status") != "complete" or summary.get("step") != 4096 or digest != summary["final_tensor_sha256"]
                    or not np.array_equal(cp["cache_batch_counts"], np.full(1024, 4)) or [row["step"] for row in summary["evaluations"]] != list(range(0, 4097, 512))):
                raise ValueError("Only full4096 new free endpoint allowed")
            free_states[phase][name] = state
            free_proofs[name][phase] = {"checkpoint": str(path), "checkpoint_sha256": assets.sha(path), "full_tensor_sha256": digest,
                "expert_only_tensor_sha256": training.expert_hash(state), "gate_tensor_sha256": training.gate_hash(state), "step": step}
        if training.expert_hash(free_states["initial"][name]) != training.expert_hash(fixed_states["initial"][name]):
            raise ValueError("Paired free/fixed expert initial state differs")
        del initial
    if training.expert_hash(free_states["initial"]["seed1"]) != training.expert_hash(fixed_states["initial"]["seed1"]):
        raise ValueError("Observed pilot expert initial state not paired")
    return manifest, teacher, {"free": free_states, "fixed": {k: fixed_states[k] for k in ("initial", "final")}}, {"free": free_proofs, "fixed": fixed_proofs}, items, metadata, htarget


def solve_map(cost):
    if cost.shape[0] != cost.shape[1] or not np.isfinite(cost).all(): raise ValueError("Finite square unscaled Hcal cost required")
    rows, cols = linear_sum_assignment(cost)
    mapping = np.empty(len(rows), np.int64); mapping[rows] = cols
    if not np.array_equal(np.sort(mapping), np.arange(len(mapping))): raise RuntimeError("Hungarian map not bijective")
    gap = np.sort(cost, axis=1)[:, 1] - np.sort(cost, axis=1)[:, 0] if len(mapping) > 1 else np.zeros(1)
    return mapping, {"total_cost": float(cost[rows, cols].sum()), "exact_local_row_ties": int(np.count_nonzero(gap == 0)),
        "local_row_best_second_gap_min": float(gap.min()), "local_row_best_second_gap_median": float(np.median(gap)),
        "ambiguity_note": "Local row gaps and full cost matrix are retained; a positive local gap does not prove global assignment uniqueness."}


def dense_components(trace, positions, dimension, experts):
    matrix = torch.zeros((experts, positions, dimension), device=trace["native"].device, dtype=torch.float32)
    support = torch.zeros((experts, positions), device=trace["native"].device, dtype=torch.bool)
    for e in range(experts):
        row = trace["experts"][e]; qi = row["query"]
        matrix[e, qi] = row["component"].float(); support[e, qi] = True
    return matrix, support


@torch.no_grad()
def calibrate(blocks, hcal, budget):
    if hcal.shape != (8192, 2048) or hcal.dtype != np.float32: raise ValueError("Exact native Hcal8192 required")
    experts = len(blocks["seed1"].experts); norms = {name: np.zeros(experts, np.float64) for name in STUDENTS}
    dots = {name: np.zeros((experts, experts), np.float64) for name in ("seed0", "seed2")}
    counts = {name: np.zeros(experts, np.int64) for name in STUDENTS}
    budget.check(); hidden = torch.from_numpy(np.array(hcal, copy=True)).to("cuda:0").bfloat16().reshape(16, 512, 2048)
    query = torch.arange(8192, device="cuda:0")
    with torch.autocast("cuda", dtype=torch.bfloat16): anchor_trace = native.native_trace(blocks["seed1"], hidden, query)
    anchor_matrix, anchor_support = dense_components(anchor_trace, len(query), hidden.shape[-1], experts)
    anchor = anchor_matrix.reshape(experts, -1).double()
    norms["seed1"] = anchor.square().sum(1).cpu().numpy(); counts["seed1"] = anchor_support.sum(1).cpu().numpy()
    del anchor_matrix, anchor_support, anchor_trace
    for name in ("seed0", "seed2"):
        budget.check()
        with torch.autocast("cuda", dtype=torch.bfloat16): trace = native.native_trace(blocks[name], hidden, query)
        matrix, support = dense_components(trace, len(query), hidden.shape[-1], experts)
        current = matrix.reshape(experts, -1).double()
        norms[name] = current.square().sum(1).cpu().numpy(); counts[name] = support.sum(1).cpu().numpy()
        dots[name] = (current @ anchor.T).cpu().numpy()
        del current, matrix, support, trace
    del anchor, hidden
    result = {"identity_seed1": list(range(experts)), "inputs": len(hcal), "support_counts": {name: counts[name].tolist() for name in STUDENTS}, "maps": {}}
    for name in ("seed0", "seed2"):
        cost = norms[name][:, None] + norms["seed1"][None, :] - 2 * dots[name]
        negative = cost < 0; floor = {"raw_minimum_cost": float(cost.min()), "negative_entry_count": int(negative.sum())}
        tolerance = 1e-8 * max(1., float(norms[name].max()), float(norms["seed1"].max()))
        if cost.min() < -tolerance: raise ArithmeticError(f"Hcal squared cost has non-roundoff negative entry: {floor}")
        cost = np.maximum(cost, 0)
        mapping, audit = solve_map(cost)
        result["maps"][name] = {"source_to_seed1": mapping.tolist(), "cost": cost,
            "source_energy": norms[name].tolist(), "seed1_energy": norms["seed1"].tolist(),
            "zero_energy_source_rows": np.flatnonzero(norms[name] == 0).tolist(),
            "zero_energy_seed1_rows": np.flatnonzero(norms["seed1"] == 0).tolist(), "cost_roundoff_floor": floor, **audit}
    return result


@torch.no_grad()
def measure_batch(blocks, teacher, hidden, query, sequence, maps, budget):
    traces = {}
    for name, block in (("teacher", teacher), *[(name, blocks[name]) for name in STUDENTS]):
        budget.check()
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16): traces[name] = native.native_trace(block, hidden, query)
    n, dimension = len(query), hidden.shape[-1]; batch = int(sequence.max()) + 1; experts = len(teacher.experts)
    by_expert = torch.zeros((batch, experts, len(EXPERT)), device=hidden.device, dtype=torch.float64)
    sums64 = {name: torch.zeros((n, dimension), device=hidden.device, dtype=torch.float64) for name in traces}
    for name, trace in traces.items():
        for e in range(experts):
            row = trace["experts"][e]; sums64[name].index_add_(0, row["query"], row["component"].double())
    inverses = {name: np.argsort(maps[name]) for name in STUDENTS}
    for e in range(experts):
        rows, masks, floors = [], [], []
        for name in STUDENTS:
            original = int(inverses[name][e]); row = traces[name]["experts"][original]; qi = row["query"]
            value = torch.zeros((n, dimension), device=hidden.device, dtype=torch.float32); value[qi] = row["component"].float()
            mask = torch.zeros(n, device=hidden.device, dtype=torch.bool); mask[qi] = True
            floor = torch.zeros(n, device=hidden.device, dtype=torch.float64); floor[qi] = native.norm2(row["product_floor"])
            rows.append(value); masks.append(mask); floors.append(floor)
        stacked = torch.stack(rows).double(); mean = stacked.mean(0)
        counts = [native.grouped(mask.double(), sequence, batch) for mask in masks]
        union = masks[0] | masks[1] | masks[2]; all_on = masks[0] & masks[1] & masks[2]
        values = (*counts, native.grouped(union.double(), sequence, batch), native.grouped(all_on.double(), sequence, batch),
            *[native.grouped(native.norm2(row), sequence, batch) for row in rows], native.grouped(native.norm2(mean), sequence, batch),
            native.grouped((stacked - mean).square().sum(-1).mean(0), sequence, batch),
            native.grouped(native.norm2(stacked[0] - stacked[1]), sequence, batch),
            native.grouped(native.norm2(stacked[0] - stacked[2]), sequence, batch),
            native.grouped(native.norm2(stacked[1] - stacked[2]), sequence, batch),
            *[native.grouped(floor, sequence, batch) for floor in floors])
        by_expert[:, e] = torch.stack(values, -1)
    ref = traces["teacher"]; err, moments = joint.cohort_moments(ref["native"], torch.stack([traces[name]["native"] for name in STUDENTS]))
    err64, moments64 = joint.cohort_moments(sums64["teacher"], torch.stack([sums64[name] for name in STUDENTS]))
    values = (torch.bincount(sequence, minlength=batch), native.grouped(native.norm2(ref["native"]), sequence, batch),
        *[native.grouped(row, sequence, batch) for row in err], *[native.grouped(row, sequence, batch) for row in moments],
        native.grouped(native.norm2(sums64["teacher"]), sequence, batch), *[native.grouped(row, sequence, batch) for row in err64],
        *[native.grouped(row, sequence, batch) for row in moments64],
        native.grouped(native.norm2(ref["native"].double() - sums64["teacher"]), sequence, batch),
        native.grouped(native.norm2(ref["sum"].double() - sums64["teacher"]), sequence, batch),
        *[native.grouped(native.norm2(traces[name]["native"].double() - sums64[name]), sequence, batch) for name in STUDENTS],
        *[native.grouped(native.norm2(traces[name]["sum"].double() - sums64[name]), sequence, batch) for name in STUDENTS])
    return by_expert.cpu().numpy(), torch.stack(values, -1).cpu().numpy()


def ratios(expert, aggregate):
    e = {key: float(expert[..., i].sum()) for i, key in enumerate(EXPERT)}; a = {key: float(aggregate[..., i].sum()) for i, key in enumerate(AGG)}
    divide = lambda x, y: x / y if y > 0 else None
    result = {key + "_per_position": divide(value, a["positions"]) for key, value in a.items() if key != "positions"}
    result.update({key + "_per_position": divide(e[key], a["positions"]) for key in EXPERT if key not in ("on_count_seed0", "on_count_seed1", "on_count_seed2", "on_count_union", "on_count_all")})
    result["component_cross_covariance_per_position"] = divide(a["FP64_sum_cohort_variance"] - e["cohort_variance"], a["positions"])
    for key in ("mean_teacher_SSE", "mean_bias_SSE", "cohort_variance"):
        result["native_" + key + "_relative_teacher_energy"] = divide(a["native_" + key], a["teacher_native_energy"])
    return result


def summarize(expert, aggregate, metadata, population):
    key = lambda row: row["word"] if population == "POS_held_targets" else (row["source"], row["file_id"])
    labels = list(dict.fromkeys(key(row) for row in metadata)); groups = [np.array([i for i, row in enumerate(metadata) if key(row) == label]) for label in labels]
    eg, ag = np.stack([expert[index].sum(0) for index in groups]), np.stack([aggregate[index].sum(0) for index in groups])
    point = ratios(expert, aggregate); draws = np.random.default_rng(139).integers(0, len(groups), (1000, len(groups)))
    values = [ratios(eg[index].sum(0), ag[index].sum(0)) for index in draws]
    output = {field: {"point": value, "ci95": np.quantile([row[field] for row in values], [.025, .975]).tolist()
        if value is not None and all(row[field] is not None for row in values) else None,
        "defined_draws": sum(row[field] is not None for row in values)} for field, value in point.items()}
    per_expert = []
    for e, row in enumerate(expert.sum(0)):
        record = {"seed1_coordinate": e, **dict(zip(EXPERT, row.tolist()))}; union = record["on_count_union"]
        record["cohort_variance_per_on_union_position"] = record["cohort_variance"] / union if union else None
        per_expert.append(record)
    return {"global": output, "per_expert": per_expert,
        "uncovered_seed1_coordinates": [row["seed1_coordinate"] for row in per_expert if row["on_count_union"] == 0],
        "input_clusters": len(groups), "bootstrap_seed": 139, "bootstrap_iterations": 1000,
        "scope": "Actual BF16 native components, zero on each model's unselected rows, permuted only by fixed Hcal maps. Input-cluster CI conditional on maps/cohort, never seed CI. Native rounding separate."}


def paired_contrast(free, fixed, population):
    """Free minus fixed using the same input clusters, conditional on both maps."""
    with np.load(free["raw"], allow_pickle=False) as f, np.load(fixed["raw"], allow_pickle=False) as x:
        fe, fa, xe, xa = [np.array(value, copy=True) for value in (f["expert"], f["aggregate"], x["expert"], x["aggregate"])]
    fm, xm = assets.read(free["metadata"]), assets.read(fixed["metadata"])
    if fm["rows"] != xm["rows"] or fe.shape != xe.shape or fa.shape != xa.shape:
        raise ValueError("Free/fixed contrast inputs or sufficient statistics not exactly paired")
    rows = fm["rows"]; key = lambda row: row["word"] if population == "POS_held_targets" else (row["source"], row["file_id"])
    labels = list(dict.fromkeys(key(row) for row in rows)); groups = [np.array([i for i, row in enumerate(rows) if key(row) == label]) for label in labels]
    fg_e, fg_a = np.stack([fe[index].sum(0) for index in groups]), np.stack([fa[index].sum(0) for index in groups])
    xg_e, xg_a = np.stack([xe[index].sum(0) for index in groups]), np.stack([xa[index].sum(0) for index in groups])
    fields = ("native_mean_teacher_SSE_per_position", "native_mean_bias_SSE_per_position", "native_cohort_variance_per_position",
        "FP64_sum_cohort_variance_per_position", "cohort_variance_per_position", "component_cross_covariance_per_position")
    fpoint, xpoint = ratios(fe, fa), ratios(xe, xa)
    draws = np.random.default_rng(139).integers(0, len(groups), (1000, len(groups)))
    samples = [(ratios(fg_e[index].sum(0), fg_a[index].sum(0)), ratios(xg_e[index].sum(0), xg_a[index].sum(0))) for index in draws]
    result = {}
    for field in fields:
        values = [a[field] - b[field] if a[field] is not None and b[field] is not None else None for a, b in samples]
        defined = [value for value in values if value is not None]
        result[field] = {"free": fpoint[field], "fixed": xpoint[field],
            "free_minus_fixed": fpoint[field] - xpoint[field] if fpoint[field] is not None and xpoint[field] is not None else None,
            "paired_input_cluster_ci95": np.quantile(defined, [.025, .975]).tolist() if len(defined) == 1000 else None,
            "defined_draws": len(defined)}
    return {"metrics": result, "input_clusters": len(groups), "bootstrap_seed": 139, "bootstrap_iterations": 1000,
        "scope": "Same held input file/word clusters resampled for both groups; fixed observed cohorts/maps, not a seed treatment-effect CI. No inference from interval overlap."}


@torch.no_grad()
def run_components(model, teacher, banks, proofs, manifest, items, metadata, archived_h, args, budget):
    data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
    if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Fixed Dolma held windows differ")
    hcal_path = Path(manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["path"])
    hcal = np.load(hcal_path, mmap_mode="r", allow_pickle=False)
    if hcal.shape != (8192, 2048) or hcal.dtype != np.float32: raise ValueError("Original public native Hcal8192 shape/dtype differs")
    hcal_sha = assets.sha(hcal_path)
    if hcal_sha != manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["sha256"]:
        raise ValueError("Original public native Hcal SHA differs")
    pos_pairs = [(item, row) for item, row in zip(items, metadata) if row["split"] == "held"]
    if len(pos_pairs) != 512 or archived_h.shape != (512, 2048): raise ValueError("Exact POS held512/Htarget required")
    pos_items, pos_meta = map(list, zip(*pos_pairs))
    result = {"source_proofs": proofs, "components_script_sha256": assets.sha(__file__)}
    identity_record = assets.read(WB / "results/e138/readout.json")
    if not identity_record or identity_record.get("status") != "complete" or identity_record.get("components_script_sha256") != FIXED_COMPONENTS_SHA:
        raise ValueError("Immutable E138 fixed identity reference missing")
    identity_sha = assets.sha(WB / "results/e138/readout.json")
    for phase in ("initial", "final"):
        for group in ("free", "fixed"):
            blocks = {name: banks[group][phase][name].block for name in STUDENTS}
            calibration = calibrate(blocks, hcal, budget)
            cost_path = args.raw_output / f"{group}_{phase}_Hcal_costs.npz"
            np.savez(cost_path, seed0=calibration["maps"]["seed0"].pop("cost"), seed2=calibration["maps"]["seed2"].pop("cost"))
            maps = {"seed1": list(range(64)), **{name: calibration["maps"][name]["source_to_seed1"] for name in ("seed0", "seed2")}}
            calibration.update({"Hcal_path": str(hcal_path), "Hcal_sha256": hcal_sha, "cost_path": str(cost_path), "cost_sha256": assets.sha(cost_path),
                "mapping_scope": "Cost is total uncentered/unscaled vector squared distance over 8192 positions × 2048 coordinates; dividing by their common product would give MSE and leave the map unchanged. One Hungarian to observed seed1 per phase/group; no held remap or physical weight permutation."})
            result[f"{group}_{phase}_calibration"] = calibration
            assets.write(args.raw_output / "components_progress.json", result)
            for population in ("Dolma_held_positions", "POS_held_targets"):
                echunks, achunks, rows = [], [], []
                if population == "Dolma_held_positions":
                    harray = np.load(args.cache_root / "held_H.npy", mmap_mode="r"); iterator = enumerate(data.iter_fixed("held", windows, 16))
                else: iterator = joint.native.source.operators.protocol.batches(pos_items, 16, "cuda:0", model.config.pad_token_id or 1)
                for entry in iterator:
                    budget.check()
                    if population == "Dolma_held_positions":
                        index, (_, meta) = entry; hidden = c.from_bits(harray[index], "cuda:0")
                        query = torch.arange(8192, device="cuda:0"); sequence = torch.arange(16, device="cuda:0").repeat_interleave(512)
                    else:
                        start, ids, mask, last, targets = entry; captured = {}
                        def collect(module, inputs): captured["H"] = inputs[0].detach().clone(); raise native.PrefixCaptured()
                        handle = teacher.register_forward_pre_hook(collect)
                        try:
                            try:
                                with torch.autocast("cuda", dtype=torch.bfloat16): model.model(input_ids=ids, attention_mask=mask, use_cache=False)
                            except native.PrefixCaptured: pass
                        finally: handle.remove()
                        hidden = captured["H"]; query = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last
                        sequence = torch.arange(len(ids), device="cuda:0")
                        if not np.array_equal(hidden.reshape(-1, 2048)[query].float().cpu().numpy(), archived_h[start:start + len(ids)]):
                            raise ValueError("Exact POS native Htarget replay differs")
                        meta = pos_meta[start:start + len(ids)]
                    e, a = measure_batch(blocks, teacher, hidden, query, sequence, maps, budget)
                    echunks.append(e); achunks.append(a); rows.extend(meta)
                    base.emit("E139_joint_components", group=group, phase=phase, population=population, sequences=len(rows))
                expert, aggregate = np.concatenate(echunks), np.concatenate(achunks)
                path = args.raw_output / f"{group}_{phase}_{population}_components.npz"; np.savez(path, expert=expert, aggregate=aggregate)
                meta_path = path.with_suffix(".json"); assets.write(meta_path, {"rows": rows, "expert_fields": EXPERT, "aggregate_fields": AGG,
                    "maps_source_to_seed1": maps, "Hcal_sha256": hcal_sha})
                key = f"{group}_{phase}_{population}"; record = {"raw": str(path), "raw_sha256": assets.sha(path),
                    "metadata": str(meta_path), "metadata_sha256": assets.sha(meta_path), "sequences": len(rows),
                    "summary": summarize(expert, aggregate, rows, population)}
                if group == "fixed":
                    previous = identity_record["components"][f"{phase}_{population}"]
                    record["fixed_identity_reference"] = {"E138_readout": str(WB / "results/e138/readout.json"),
                        "E138_readout_sha256": identity_sha, "raw": previous["raw"], "raw_sha256": previous["raw_sha256"],
                        "summary": previous["summary"]}
                result[key] = record; assets.write(args.raw_output / "components_progress.json", result)
                if group == "fixed":
                    result[f"paired_free_minus_fixed_{phase}_{population}"] = paired_contrast(
                        result[f"free_{phase}_{population}"], record, population)
                    assets.write(args.raw_output / "components_progress.json", result)
    return result


def self_test():
    class Gate(nn.Module):
        def __init__(self, logits): super().__init__(); self.logits = logits
        def forward(self, h): return torch.tensor(self.logits, dtype=h.dtype, device=h.device).expand(len(h), -1)
    class Constant(nn.Module):
        def __init__(self, value): super().__init__(); self.value = value
        def forward(self, h): return torch.full_like(h, self.value)
    class Block(nn.Module):
        def __init__(self, logits, values):
            super().__init__(); self.gate = Gate(logits); self.experts = nn.ModuleList([Constant(x) for x in values]); self.top_k = 2
            self.num_experts = len(values); self.norm_topk_prob = False
        def forward(self, h): return OlmoeSparseMoeBlock.forward(self, h)
    class NoBudget:
        def check(self): pass
    h = torch.randn(2, 3, 2).bfloat16(); query = torch.tensor([1, 5]); seq = torch.tensor([0, 1]); identity = list(range(3))
    teacher = Block([3., 2., -100.], [1., 1., 1.]); same = {name: Block([3., 2., -100.], [2., 2., 2.]) for name in STUDENTS}
    e, a = measure_batch(same, teacher, h, query, seq, {name: identity for name in STUDENTS}, NoBudget()); r = ratios(e, a)
    assert r["native_cohort_variance_per_position"] == r["cohort_variance_per_position"] == 0
    assert r["native_mean_bias_SSE_per_position"] > 0 and abs(r["native_identity_residual_per_position"]) < 1e-14
    mixed = {"seed0": Block([-100., 2., 3.], [1., 2., 1.]), "seed1": Block([3., 2., -100.], [1., 2., 1.]),
             "seed2": Block([3., -100., 2.], [1., 2., 1.])}
    e, a = measure_batch(mixed, teacher, h, query, seq, {name: identity for name in STUDENTS}, NoBudget())
    assert e[:, 0, EXPERT.index("on_count_seed0")].sum() == 0 and e[:, 2, EXPERT.index("on_count_seed0")].sum() == 2
    variance = e[..., EXPERT.index("cohort_variance")]
    pairwise = sum(e[..., EXPERT.index(field)] for field in ("pair_seed0_seed1_SSE", "pair_seed0_seed2_SSE", "pair_seed1_seed2_SSE")) / 9
    energy_identity = (sum(e[..., EXPERT.index(f"energy_{name}")] for name in STUDENTS) / 3
        - e[..., EXPERT.index("cohort_mean_energy")])
    assert np.allclose(variance, pairwise, atol=1e-12) and np.allclose(variance, energy_identity, atol=1e-12)
    cancelling = {"seed0": Block([0., 0., -100.], [0., 2., 1.]),
        "seed1": Block([0., 0., -100.], [1., 1., 1.]), "seed2": Block([0., 0., -100.], [2., 0., 1.])}
    ce, ca = measure_batch(cancelling, teacher, h, query, seq, {name: identity for name in STUDENTS}, NoBudget())
    cr = ratios(ce, ca)
    assert cr["cohort_variance_per_position"] > 0 and cr["FP64_sum_cohort_variance_per_position"] == 0
    assert cr["component_cross_covariance_per_position"] == -cr["cohort_variance_per_position"]
    trace = {"native": torch.zeros(2, 2), "experts": {0: {"query": torch.tensor([1]), "component": torch.tensor([[3., 4.]])},
        1: {"query": torch.tensor([], dtype=torch.long), "component": torch.empty(0, 2)}}}
    dense, support = dense_components(trace, 2, 2, 2)
    assert dense[0, 0].sum() == 0 and dense[0, 1].tolist() == [3., 4.] and support[1].sum() == 0
    matrix = np.array([[2., 0., 3.], [0., 2., 3.], [3., 3., 0.]])
    mapping, _ = solve_map(matrix); assert mapping.tolist() == [1, 0, 2]
    with tempfile.TemporaryDirectory(prefix="e139_paired_contrast_cpu_") as directory:
        root = Path(directory); ae = np.zeros((2, 3, len(EXPERT))); aa = np.zeros((2, len(AGG)))
        be, ba = ae.copy(), aa.copy()
        for array in (aa, ba): array[:, AGG.index("positions")] = 1; array[:, AGG.index("teacher_native_energy")] = 10
        aa[:, AGG.index("native_cohort_variance")] = 2; ba[:, AGG.index("native_cohort_variance")] = 1
        aa[:, AGG.index("FP64_sum_cohort_variance")] = 2; ba[:, AGG.index("FP64_sum_cohort_variance")] = 1
        ae[:, 0, EXPERT.index("cohort_variance")] = 1; be[:, 0, EXPERT.index("cohort_variance")] = .5
        rows = [{"source": "x", "file_id": str(i)} for i in range(2)]; records = []
        for stem, expert, aggregate in (("free", ae, aa), ("fixed", be, ba)):
            raw, meta = root / f"{stem}.npz", root / f"{stem}.json"
            np.savez(raw, expert=expert, aggregate=aggregate); assets.write(meta, {"rows": rows})
            records.append({"raw": str(raw), "metadata": str(meta)})
        contrast = paired_contrast(*records, "Dolma_held_positions")
        assert contrast["metrics"]["native_cohort_variance_per_position"]["free_minus_fixed"] == 1
        assert contrast["metrics"]["component_cross_covariance_per_position"]["free_minus_fixed"] == .5
    return {"passed": True, "CPU_only": True, "same_students_zero_variance": True, "shared_bias_separate": True,
        "different_support_zero_scatter": True, "known_permutation_hungarian": True,
        "opposite_component_variation_cancels": True,
        "component_variance_pairwise_and_energy_identities": True, "paired_input_cluster_free_minus_fixed": True,
        "script_sha256": assets.sha(__file__)}
