"""E138 joint native components: fixed three-student cohort, population weight1/3.

Teacher is a reference, never a fourth student. Actual selected-subset BF16
components are observed jointly; no off-support queries or fitted coordinates.
"""
from __future__ import annotations
import argparse, copy, json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from transformers import OlmoeForCausalLM
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock
import e137_components as native
import e138_train as training

c, assets, base, WB = training.c, training.assets, training.base, training.WB
STUDENTS = ("seed0", "seed1", "seed2")
MOMENTS = ("mean_teacher_SSE", "mean_bias_SSE", "cohort_variance", "identity_residual")
EXPERT = ("on_count", "teacher_content_energy", "content_seed0_SSE", "content_seed1_SSE", "content_seed2_SSE",
          *["content_" + key for key in MOMENTS], "teacher_component_energy", "component_seed0_SSE", "component_seed1_SSE", "component_seed2_SSE",
          *["component_" + key for key in MOMENTS], "teacher_product_rounding_SSE", *[name + "_product_rounding_SSE" for name in STUDENTS])
AGG = ("positions", "teacher_native_energy", "native_seed0_SSE", "native_seed1_SSE", "native_seed2_SSE",
       *["native_" + key for key in MOMENTS], "teacher_FP64_sum_energy", "FP64_sum_seed0_SSE", "FP64_sum_seed1_SSE", "FP64_sum_seed2_SSE",
       *["FP64_sum_" + key for key in MOMENTS], "teacher_native_minus_FP64_sum_SSE", "teacher_FP32_minus_FP64_sum_SSE",
       *[name + "_native_minus_FP64_sum_SSE" for name in STUDENTS], *[name + "_FP32_minus_FP64_sum_SSE" for name in STUDENTS])
TRAIN_SHA = "65840e0c3befd7ac4c68ccbf9fdd3bdee946f4e3b8067074b9e5c2d632716200"
NATIVE_SHA = "86c57c0bc40c14d7778c036e92380e97ef3a071feeba4be484b2b45cc39bee63"


def cohort_moments(teacher, students):
    """Same vector units, finite-cohort population moments, no n-1 correction."""
    teacher, students = teacher.double(), students.double(); mean = students.mean(0)
    errors = (students - teacher).square().sum(-1)
    mse = errors.mean(0); bias = (mean - teacher).square().sum(-1); variance = (students - mean).square().sum(-1).mean(0)
    return errors, (mse, bias, variance, mse - bias - variance)


def preflight(args, *, initial_only=False):
    for name, expected in (("e138_train.py", TRAIN_SHA), ("e137_components.py", NATIVE_SHA)):
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError("Frozen E138/native-trace source differs")
    old_args = copy.copy(args); old_args.phase = "all"
    manifest, old, old_proofs, items, metadata, htarget = native.preflight(old_args)
    states = {"teacher": old["teacher"], "initial": {"seed1": old["oracle_initial"]}, "final": {"seed1": old["oracle_final"]}}
    proofs = {"seed1": {"initial": old_proofs["oracle_initial"], "final": old_proofs["oracle_final"], "scope": "Already observed E136 pilot reused, not a new prospective seed"}}
    for seed in (0, 2):
        new_args = copy.copy(args); new_args.seed = seed
        _, _, _, _, initial, _, expected = training.preflight(new_args)
        directory = getattr(args, f"seed{seed}_dir"); provenance = assets.read(directory / "provenance.json"); summary = assets.read(directory / "training_summary.json")
        proofs[f"seed{seed}"] = {}
        endpoints = (("initial", 0, "initial.pt"),) if initial_only else (("initial", 0, "initial.pt"), ("final", 4096, "checkpoint.pt"))
        for phase, step, filename in endpoints:
            path = directory / filename; cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = cp["student_state"]
            if (cp.get("experiment"), cp.get("schema"), cp.get("seed"), cp.get("step")) != ("E138", "E138-fixed-assignment-student-v1", seed, step): raise ValueError("Wrong new student identity/endpoint")
            if (cp["initialization"] != expected or cp["config_hash"] != provenance["config_hash"] or cp["cache_manifest_sha256"] != assets.sha(args.cache_root / "manifest.json")
                    or provenance["scientific"]["driver_sha256"] != TRAIN_SHA or any(value.dtype != torch.float32 for value in state.values())
                    or training.gate_hash(state) != expected["oracle_gate_FP32_sha256"]): raise ValueError("New student immutable source/config/gate proof differs")
            digest = c.tensor_state_hash(state)
            if step == 0 and (digest != expected["oracle_initial_full_tensor_sha256"] or cp["optimizer"]["state"]
                    or np.any(cp["cache_batch_counts"])): raise ValueError("Fresh initial tensor/optimizer/exposure differs")
            if step == 4096 and (summary.get("status") != "complete" or summary.get("step") != 4096 or digest != summary["final_tensor_sha256"]
                    or not np.array_equal(cp["cache_batch_counts"], np.full(1024, 4)) or [row["step"] for row in summary["evaluations"]] != list(range(0, 4097, 512))): raise ValueError("Exact full4096/four-pass/nine-event endpoint required")
            states[phase][f"seed{seed}"] = state
            proofs[f"seed{seed}"][phase] = {"checkpoint": str(path), "checkpoint_sha256": assets.sha(path), "full_tensor_sha256": digest,
                "expert_only_tensor_sha256": training.expert_hash(state), "gate_tensor_sha256": training.gate_hash(state), "seed": seed, "step": step, "config_hash": cp["config_hash"]}
        del initial
    for phase in (("initial",) if initial_only else ("initial", "final")):
        if len({training.gate_hash(states[phase][name]) for name in STUDENTS}) != 1: raise ValueError("Cohort gate identity differs")
    if len({training.expert_hash(states["initial"][name]) for name in STUDENTS}) != 3: raise ValueError("Three distinct initial experts required")
    return manifest, states, proofs, items, metadata, htarget


@torch.no_grad()
def measure_batch(blocks, hidden, query, sequence, budget):
    traces = {}
    for name, block in blocks.items():
        budget.check()
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16): traces[name] = native.native_trace(block, hidden, query)
    teacher = traces["teacher"]; batch = int(sequence.max()) + 1; experts = len(blocks["teacher"].experts)
    by_expert = torch.zeros((batch, experts, len(EXPERT)), device=hidden.device, dtype=torch.float64)
    sums64 = {name: torch.zeros_like(trace["sum"], dtype=torch.float64) for name, trace in traces.items()}; support = {}
    for name in STUDENTS:
        trace = traces[name]; support[name] = {"selected_slot_mismatch_rows": int((trace["selected"] != teacher["selected"]).any(-1).sum()),
            "applied_weight_max_abs_difference": float((trace["weights"] - teacher["weights"]).float().abs().max())}
        if support[name]["selected_slot_mismatch_rows"] or support[name]["applied_weight_max_abs_difference"] != 0: raise RuntimeError(f"Fixed native support differs: {support}")
    for e in range(experts):
        ref = teacher["experts"][e]; qi = ref["query"]; seq = sequence[qi]
        current = [traces[name]["experts"][e] for name in STUDENTS]
        if any(not torch.equal(row["query"], qi) for row in current): raise RuntimeError("Native selected row order differs across cohort")
        content_error, content = cohort_moments(ref["f"], torch.stack([row["f"] for row in current]))
        component_error, component = cohort_moments(ref["component"], torch.stack([row["component"] for row in current]))
        values = (torch.bincount(seq, minlength=batch), native.grouped(native.norm2(ref["f"]), seq, batch),
            *[native.grouped(row, seq, batch) for row in content_error], *[native.grouped(row, seq, batch) for row in content],
            native.grouped(native.norm2(ref["component"]), seq, batch), *[native.grouped(row, seq, batch) for row in component_error],
            *[native.grouped(row, seq, batch) for row in component], native.grouped(native.norm2(ref["product_floor"]), seq, batch),
            *[native.grouped(native.norm2(row["product_floor"]), seq, batch) for row in current])
        by_expert[:, e] = torch.stack(values, -1)
        for name, trace in traces.items(): sums64[name].index_add_(0, qi, trace["experts"][e]["component"].double())
    err, moments = cohort_moments(teacher["native"], torch.stack([traces[name]["native"] for name in STUDENTS]))
    err64, moments64 = cohort_moments(sums64["teacher"], torch.stack([sums64[name] for name in STUDENTS]))
    values = (torch.bincount(sequence, minlength=batch), native.grouped(native.norm2(teacher["native"]), sequence, batch),
        *[native.grouped(row, sequence, batch) for row in err], *[native.grouped(row, sequence, batch) for row in moments],
        native.grouped(native.norm2(sums64["teacher"]), sequence, batch), *[native.grouped(row, sequence, batch) for row in err64],
        *[native.grouped(row, sequence, batch) for row in moments64],
        native.grouped(native.norm2(teacher["native"].double() - sums64["teacher"]), sequence, batch),
        native.grouped(native.norm2(teacher["sum"].double() - sums64["teacher"]), sequence, batch),
        *[native.grouped(native.norm2(traces[name]["native"].double() - sums64[name]), sequence, batch) for name in STUDENTS],
        *[native.grouped(native.norm2(traces[name]["sum"].double() - sums64[name]), sequence, batch) for name in STUDENTS])
    return by_expert.cpu().numpy(), torch.stack(values, -1).cpu().numpy(), support


def ratios(expert, aggregate):
    e = {key: float(expert[..., i].sum()) for i, key in enumerate(EXPERT)}; a = {key: float(aggregate[..., i].sum()) for i, key in enumerate(AGG)}
    divide = lambda x, y: x / y if y > 0 else None
    result = {key + "_per_position": divide(value, a["positions"]) for key, value in a.items() if key != "positions"}
    result.update({key + "_per_position": divide(e[key], a["positions"]) for key in EXPERT if key.startswith("component_") or "product_rounding" in key})
    result["component_cross_covariance_per_position"] = divide(a["FP64_sum_cohort_variance"] - e["component_cohort_variance"], a["positions"])
    for key in ("mean_teacher_SSE", "mean_bias_SSE", "cohort_variance"):
        result["native_" + key + "_relative_teacher_energy"] = divide(a["native_" + key], a["teacher_native_energy"])
    return result


def summarize(expert, aggregate, metadata, population):
    key = lambda row: row["word"] if population == "POS_held_targets" else (row["source"], row["file_id"])
    labels = list(dict.fromkeys(key(row) for row in metadata)); groups = [np.array([i for i, row in enumerate(metadata) if key(row) == label]) for label in labels]
    eg, ag = np.stack([expert[index].sum(0) for index in groups]), np.stack([aggregate[index].sum(0) for index in groups])
    point = ratios(expert, aggregate); draws = np.random.default_rng(138).integers(0, len(groups), (1000, len(groups)))
    values = [ratios(eg[index].sum(0), ag[index].sum(0)) for index in draws]
    output = {key: {"point": value, "ci95": np.quantile([row[key] for row in values], [.025, .975]).tolist()
        if value is not None and all(row[key] is not None for row in values) else None, "defined_draws": sum(row[key] is not None for row in values)} for key, value in point.items()}
    per_expert = []
    for e, row in enumerate(expert.sum(0)):
        record = {"expert": e, **dict(zip(EXPERT, row.tolist()))}; count = record["on_count"]
        for kind in ("content", "component"):
            energy = record["teacher_" + kind + "_energy"]
            for name in MOMENTS:
                value = record[kind + "_" + name]
                record[kind + "_" + name + "_per_on_position"] = value / count if count else None
                record[kind + "_" + name + "_relative_teacher_energy"] = value / energy if energy > 0 else None
        per_expert.append(record)
    return {"global": output, "per_expert": per_expert, "uncovered_experts": [row["expert"] for row in per_expert if row["on_count"] == 0],
        "input_clusters": len(groups), "bootstrap_seed": 138, "bootstrap_iterations": 1000,
        "scope": "Fixed cohort population weights1/3. CI resamples input word/file clusters, never students or the3 shared pairs. Native rounding is separate from FP64 component cross covariance."}


@torch.no_grad()
def run_components(model, teacher, banks, manifest, items, metadata, archived_h, args, budget):
    data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
    if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Original held windows differ")
    result = {}; pos_items, pos_meta = map(list, zip(*[(item, row) for item, row in zip(items, metadata) if row["split"] == "held"]))
    for phase in ("initial", "final"):
        blocks = {"teacher": teacher, **{name: banks[phase][name].block for name in STUDENTS}}
        for population in ("Dolma_held_positions", "POS_held_targets"):
            echunks, achunks, rows, support = [], [], [], []
            if population == "Dolma_held_positions":
                harray = np.load(args.cache_root / "held_H.npy", mmap_mode="r"); iterator = enumerate(data.iter_fixed("held", windows, 16))
            else: iterator = native.source.operators.protocol.batches(pos_items, 16, "cuda:0", model.config.pad_token_id or 1)
            for entry in iterator:
                budget.check()
                if population == "Dolma_held_positions":
                    index, (_, meta) = entry; hidden = c.from_bits(harray[index], "cuda:0"); query = torch.arange(8192, device="cuda:0"); sequence = torch.arange(16, device="cuda:0").repeat_interleave(512)
                else:
                    start, ids, mask, last, targets = entry; captured = {}
                    def collect(module, inputs): captured["H"] = inputs[0].detach().clone(); raise native.PrefixCaptured()
                    handle = teacher.register_forward_pre_hook(collect)
                    try:
                        try:
                            with torch.autocast("cuda", dtype=torch.bfloat16): model.model(input_ids=ids, attention_mask=mask, use_cache=False)
                        except native.PrefixCaptured: pass
                    finally: handle.remove()
                    hidden = captured["H"]; query = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last; sequence = torch.arange(len(ids), device="cuda:0")
                    if not np.array_equal(hidden.reshape(-1, 2048)[query].float().cpu().numpy(), archived_h[start:start + len(ids)]): raise ValueError("Exact POS Htarget replay differs")
                    meta = pos_meta[start:start + len(ids)]
                e, a, s = measure_batch(blocks, hidden, query, sequence, budget); echunks.append(e); achunks.append(a); support.append(s); rows.extend(meta)
                base.emit("E138_joint_components", phase=phase, population=population, sequences=len(rows))
            expert, aggregate = np.concatenate(echunks), np.concatenate(achunks)
            path = args.raw_output / f"{phase}_{population}_components.npz"; np.savez(path, expert=expert, aggregate=aggregate)
            meta_path = path.with_suffix(".json"); assets.write(meta_path, {"rows": rows, "expert_fields": EXPERT, "aggregate_fields": AGG, "support": support})
            result[phase + "_" + population] = {"raw": str(path), "raw_sha256": assets.sha(path), "metadata": str(meta_path), "metadata_sha256": assets.sha(meta_path),
                "sequences": len(rows), "summary": summarize(expert, aggregate, rows, population)}
            assets.write(args.raw_output / "components_progress.json", result)
    return result


def self_test():
    class Gate(nn.Module):
        def __init__(self, count): super().__init__(); self.count = count
        def forward(self, h):
            value = torch.zeros((len(h), self.count), dtype=h.dtype)
            if self.count == 3: value[:, 2] = -100
            return value
    class Constant(nn.Module):
        def __init__(self, value): super().__init__(); self.value = value
        def forward(self, h): return torch.full_like(h, self.value)
    class Block(nn.Module):
        def __init__(self, values):
            super().__init__(); self.gate = Gate(len(values)); self.experts = nn.ModuleList([Constant(v) for v in values]); self.top_k = 2; self.num_experts = len(values); self.norm_topk_prob = False
        def forward(self, h): return OlmoeSparseMoeBlock.forward(self, h)
    class NoBudget:
        def check(self): pass
    h = torch.randn(2, 3, 2).bfloat16(); query = torch.tensor([1, 5]); seq = torch.tensor([0, 1])
    same = {"teacher": Block([1., 1.]), **{name: Block([2., 2.]) for name in STUDENTS}}
    e, a, s = measure_batch(same, h, query, seq, NoBudget()); r = ratios(e, a)
    assert r["native_cohort_variance_per_position"] == 0 and r["native_mean_bias_SSE_per_position"] > 0
    same["teacher"] = Block([2., 2.]); e0, a0, _ = measure_batch(same, h, query, seq, NoBudget()); z = ratios(e0, a0)
    assert z["native_mean_teacher_SSE_per_position"] == z["component_cohort_variance_per_position"] == 0
    cancelling = {"teacher": Block([1., 1.]), "seed0": Block([0., 2.]), "seed1": Block([1., 1.]), "seed2": Block([2., 0.])}
    e, a, _ = measure_batch(cancelling, h, query, seq, NoBudget()); r = ratios(e, a)
    assert r["component_cohort_variance_per_position"] > 0 and r["FP64_sum_cohort_variance_per_position"] == 0
    assert r["component_cross_covariance_per_position"] == -r["component_cohort_variance_per_position"]
    assert abs(r["native_identity_residual_per_position"]) < 1e-14 and abs(r["component_identity_residual_per_position"]) < 1e-14
    uncovered = {"teacher": Block([1., 1., 1.]), **{name: Block([2., 2., 2.]) for name in STUDENTS}}
    ue, ua, _ = measure_batch(uncovered, h, query, seq, NoBudget())
    us = summarize(ue, ua, [{"word": "x"}, {"word": "y"}], "POS_held_targets")
    assert us["uncovered_experts"] == [2] and us["per_expert"][2]["content_cohort_variance_per_on_position"] is None
    return {"passed": True, "CPU_only": True, "identical_students_zero_variance": True, "common_bias_not_cohort_variance": True,
        "opposite_component_variation_cancels": True, "native_selected_row_contract": True, "finite_cohort_weight_one_third": True, "script_sha256": assets.sha(__file__)}
