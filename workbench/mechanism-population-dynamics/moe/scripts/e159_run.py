"""E159: do unchanged expert functions change roles with different partners?"""
import argparse
import os
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=0)
_early, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early.physical_gpu)):
    raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
from contextlib import ExitStack
from pathlib import Path
import json
import numpy as np
import torch
from torch import nn
import e156_run as prev
import e159_analyze as analysis

n, v, h, loading = prev.n, prev.v, prev.h, prev.loading
RESULT = n.WB / "results/e159"
RAW = Path.home() / "mechpop_cache/e159_unchanged_function_partner_role"
SOURCES = ("P", "A", "B", "zero")
MEASURED = ((0, 0), (3, 0), (3, 1), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3))


def proof():
    return {**prev.proof(), "e159_run.py": n.sha(__file__),
            "e159_analyze.py": n.sha(analysis.__file__)}


def immutable_npz(path, arrays):
    if path.exists():
        with np.load(path, allow_pickle=False) as old:
            if set(old.files) != set(arrays) or any(not np.array_equal(old[k], x) for k, x in arrays.items()):
                raise ValueError("Refusing to overwrite different arrays: " + str(path))
    else:
        np.savez_compressed(path, **arrays)


def self_test():
    models = []
    torch.set_num_threads(1)
    class Gate(nn.Module):
        def __init__(self, values):
            super().__init__()
            self.register_buffer("values", torch.tensor(values, dtype=torch.float32).log())
        def forward(self, hidden):
            return self.values.to(hidden.dtype).expand(hidden.shape[0], -1)
    for i, label in enumerate(SOURCES[:3]):
        cfg_cls, _, _ = loading._classes(label, complete=False)
        name = "codex_e154_parent" if label == "P" else f"codex_e150_source_{i-1}"
        module = __import__(name + ".modeling_emo", fromlist=["EmoSparseMoeBlock"])
        cfg = cfg_cls(hidden_size=4, intermediate_size=4, num_experts=4,
                      num_experts_per_tok=2, num_shared_experts=1, norm_topk_prob=False)
        block = module.EmoSparseMoeBlock(cfg, 4, 1, None)
        block.gate = Gate(((1., 2., 4., 1.), (8., 1., 1., 1.), (1., 1., 16., 1.))[i])
        block.experts = nn.ModuleList([v.Constant((2., 3., 5.)[i]) for _ in range(3)] + [v.Constant((10., 20., 30.)[i])])
        layer = nn.Module(); layer.mlp = block
        model = nn.Module(); model.model = nn.Module(); model.model.layers = nn.ModuleList([layer])
        models.append(model)
    blocks = n.original_blocks(models)
    ph = [n.old.tensor_hash(m.state_dict()) for m in models]
    checks = 0
    hidden = torch.ones((1, 6, 4))
    p_weight = float(torch.softmax(blocks[0][0].gate(hidden.view(-1, 4))[:, :-1], -1)[0].max())
    for r in range(3):
        for s in range(3):
            for zero_r, zero_s in ((False, False), (True, False), (False, True), (True, True)):
                model = n.assemble(models, blocks, (0, 0, r, s))
                try:
                    with ExitStack() as contexts:
                        if zero_r: contexts.enter_context(v.suppress(model, "routed"))
                        if zero_s: contexts.enter_context(v.suppress(model, "shared"))
                        value = model.model.layers[0].mlp(hidden)[0]
                    expected = (0. if zero_s else (10., 20., 30.)[s]) + (0. if zero_r else p_weight * (2., 3., 5.)[r])
                    if not torch.allclose(value, torch.full_like(value, expected), atol=2e-6):
                        raise ValueError("Source/gate/zero-collapse known-answer failure")
                    checks += 1
                finally:
                    n.restore(models, blocks)
    if any(n.old.tensor_hash(m.state_dict()) != x for m, x in zip(models, ph)):
        raise ValueError("CPU source restoration differs")
    if any(m.model.layers[0].mlp is not blocks[i][0] for i, m in enumerate(models)):
        raise ValueError("CPU source module registry differs")
    n.write(RESULT / "self_test.json", {"status": "passed", "CPU_only": True, "source_sha256": proof(),
            "unequal_native_gate_source_and_zero_oracles": checks, "source_registry_and_buffers_restored": True,
            "statistics": analysis.self_test()})
    return {"status": "passed", "source_zero_oracles": checks}


def prepare():
    tests = n.read(RESULT / "self_test.json")
    if tests["status"] != "passed" or tests["source_sha256"] != proof():
        raise ValueError("Matching complete CPU tests required")
    prior_plan = n.read(prev.RESULT / "plan.json")
    prior_manifest = n.read(prev.RESULT / "manifest.json")
    prior_budget = n.read(prev.RESULT / "budget.json")
    if prior_manifest["status"] != "complete" or any(x["status"] != "complete" for x in prior_budget["attempts"]):
        raise ValueError("Complete inherited source cross required")
    if prior_manifest["source_sha256"] != prev.proof() or n.sha(prev.RESULT / "plan.json") != prior_manifest["plan_sha256"]:
        raise ValueError("Inherited source protocol differs")
    if n.sha(prior_manifest["raw"]["path"]) != prior_manifest["raw"]["sha256"]:
        raise ValueError("Inherited source cross raw differs")
    with np.load(prior_manifest["raw"]["path"], allow_pickle=False) as f:
        inherited = {k: f[k].copy() for k in f.files}
    native, source_records = [], []
    for label in SOURCES[:3]:
        path = n.WB / f"results/e155/manifest_{label}.json"
        m = n.read(path)
        if m["status"] != "complete" or n.sha(m["raw"]["path"]) != m["raw"]["sha256"]:
            raise ValueError("Native necessity reference differs")
        with np.load(m["raw"]["path"], allow_pickle=False) as f:
            for k in ("gold", "subject", "answer_tokens", "answer_chars"):
                if not np.array_equal(f[k], inherited[k]): raise ValueError("Reference population differs")
            if tuple(f["conditions"]) != ("native", "routed_zero", "shared_zero", "all_moe_zero"):
                raise ValueError("Native necessity condition order differs")
            native.append(f["candidate_loglikelihood"].copy())
        source_records.append({"path": str(path), "sha256": n.sha(path), "raw": m["raw"]})
    full = inherited["candidate_loglikelihood"][:, :, 0]
    common = (full.argmax(-1) == inherited["gold"]).all((0, 1))
    if common.sum() != 33 or [int((common & (inherited["subject"] == s)).sum()) for s in (0, 1)] != [30, 3]:
        raise ValueError("Already-sealed all-nine full-success cohort differs")
    RAW.mkdir(parents=True, exist_ok=True)
    refs = {"full_candidate_loglikelihood": full, "native_reference_candidate_loglikelihood": np.stack(native),
            "all_nine_full_success": common, "common_native_success": inherited["common_success"],
            **{k: inherited[k] for k in ("gold", "subject", "answer_tokens", "answer_chars")}}
    ref_path = RAW / "references.npz"
    immutable_npz(ref_path, refs)
    plan = {"experiment": "E159", "status": "prepared", "source_sha256": proof(),
            "task_input": prior_plan["task_input"], "task_data_plan_sha256": prior_plan["task_data_plan_sha256"],
            "pad_token_id": prior_plan["pad_token_id"], "source_records": prior_plan["source_records"],
            "legacy_cal_input": prior_plan["legacy_cal_input"],
            "references": {"path": str(ref_path), "sha256": n.sha(ref_path)},
            "inherited_cross_manifest": {"path": str(prev.RESULT / "manifest.json"), "sha256": n.sha(prev.RESULT / "manifest.json"), "raw": prior_manifest["raw"]},
            "native_reference_records": source_records, "source_names": list(SOURCES),
            "measured_cells": [list(x) for x in MEASURED], "full_cells_inherited": "E156 full 3x3; PP freshly replayed exactly",
            "new_unknown_source_zero_cells": [[3, 1], [3, 2], [1, 3], [2, 3]],
            "bootstrap": {"unit": "paired questions within two fixed subjects", "seed": 159001, "resamples": 1000},
            "secondary": "all nine inherited full source cells correct:33=30 biology+3 mathematics; points/counts only",
            "primary": "unchanged S source: shared necessity varies over R partners; unchanged R source: routed necessity varies over S partners",
            "identity_not_discovery": "At fixed R, changes of S necessity over S source equal old full-quality differences; symmetric for R.",
            "limit_gpu_seconds": 10800, "scope": "P dense/gate fixed. Actual expert functions/partners change, H and downstream routing endogenous. No new training, no KV cache, no universal initialization claim."}
    n.old.immutable_json(RESULT / "plan.json", plan)
    return {"status": "prepared", "measured_conditions": 8, "unknown_zero_conditions": 4}


class Budget(n.old.Budget):
    def __init__(self):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e159", "unchanged_function_partner_role", 10800


@torch.no_grad()
def measure(models, blocks, r, s, seqs, prompt, pad):
    n.restore(models, blocks)
    model = n.assemble(models, blocks, (0, 0, 0 if r == 3 else r, 0 if s == 3 else s))
    try:
        with ExitStack() as contexts:
            if r == 3: contexts.enter_context(v.suppress(model, "routed"))
            if s == 3: contexts.enter_context(v.suppress(model, "shared"))
            score, count, first = h.score_candidates(model, seqs, prompt, pad)
        del first
        return score, count
    finally:
        n.restore(models, blocks)


@torch.no_grad()
def evaluate(physical):
    plan = n.read(RESULT / "plan.json")
    if plan["source_sha256"] != proof() or n.read(RESULT / "self_test.json")["source_sha256"] != proof():
        raise ValueError("Frozen complete numerical source differs")
    for record in (plan["task_input"], plan["references"], plan["legacy_cal_input"], plan["inherited_cross_manifest"]):
        if n.sha(record["path"]) != record["sha256"]: raise ValueError("Frozen input/reference differs")
    for record in plan["native_reference_records"]:
        if n.sha(record["path"]) != record["sha256"] or n.sha(record["raw"]["path"]) != record["raw"]["sha256"]:
            raise ValueError("Native necessity source differs")
    if n.sha(prev.TASK / "data_plan.json") != plan["task_data_plan_sha256"]:
        raise ValueError("Task recipe differs")
    if (RAW / "scores.npz").exists() or (RESULT / "manifest.json").exists():
        raise ValueError("Refusing to replace completed raw")
    with np.load(plan["task_input"]["path"], allow_pickle=False) as f: a = {k: f[k].copy() for k in f.files}
    with np.load(plan["references"]["path"], allow_pickle=False) as f: refs = {k: f[k].copy() for k in f.files}
    with np.load(plan["legacy_cal_input"]["path"], allow_pickle=False) as f:
        cal, cv = f["cal"][:2, :129].copy(), f["cal_mask"][:2, :128].copy()
    lock = None
    try:
        with Budget() as budget:
            lock = n.old.gpu_lock(physical)
            models, before, buffers = [], [], []
            ids = torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            attention = torch.cat((torch.ones((2, 1), dtype=torch.bool, device="cuda:0"), torch.from_numpy(cv).to("cuda:0")), 1)
            for label in SOURCES[:3]:
                budget.check()
                model = loading.load_cpu_bf16(label); models.append(model)
                if sum(p.numel() for p in model.parameters()) != 13568641024 or len(model.model.layers) != 16:
                    raise ValueError("Unexpected mature architecture")
                record = plan["source_records"][label]
                ph, bh = n.old.tensor_hash(model.state_dict()), n.old.tensor_hash(n.buffers(model))
                if ph != record["parameter_hash"] or bh != record["buffer_hash"]:
                    raise ValueError("Canonical source parameters/buffers differ")
                before.append(ph); buffers.append(bh)
                c = record["calibration"]
                if n.sha(c["path"]) != c["sha256"]: raise ValueError("Canonical calibration differs")
                with np.load(c["path"], allow_pickle=False) as f:
                    expected = torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                if not torch.equal(n.fwd(model, ids[:, :-1], attention[:, :-1]), expected):
                    raise ValueError("Canonical native calibration differs")
                del expected
                n.old.emit("E159_source_loaded", source=label, peak_GB=torch.cuda.max_memory_allocated() / 1e9)
            blocks = n.original_blocks(models)
            del ids, attention
            values = np.empty((4, 4, 128, 4), dtype=np.float64)
            values[:3, :3] = refs["full_candidate_loglikelihood"]
            measured = np.zeros((4, 4), dtype=bool)
            for r, s in MEASURED: measured[r, s] = True
            for q in range(128):
                budget.check()
                seqs = prev.sequences(a["test_ids"], a["test_offsets"], range(q * 4, q * 4 + 4))
                prompt = int(a["prompt_tokens"][q])
                for r, s in MEASURED:
                    score, counts = measure(models, blocks, r, s, seqs, prompt, plan["pad_token_id"])
                    if not np.array_equal(counts, a["answer_tokens"][q]): raise ValueError("Answer token counts differ")
                    expected_index = {(0, 0): 0, (3, 0): 1, (0, 3): 2, (3, 3): 3}.get((r, s))
                    if expected_index is not None and not np.array_equal(score, refs["native_reference_candidate_loglikelihood"][0, expected_index, q]):
                        raise ValueError("All-question P native/zero replay differs from E155")
                    values[r, s, q] = score
                # Fixed input-only positive controls: zeroed donor weights cannot
                # affect predictions. Check both collapsed axes, not new science.
                if q in (0, 64):
                    for r in range(3):
                        for s in range(3):
                            for branch in ("routed", "shared"):
                                n.restore(models, blocks)
                                model = n.assemble(models, blocks, (0, 0, r, s))
                                try:
                                    with v.suppress(model, branch):
                                        replay, counts, first = h.score_candidates(model, seqs, prompt, plan["pad_token_id"])
                                    expected = values[3, s, q] if branch == "routed" else values[r, 3, q]
                                    if not np.array_equal(replay, expected): raise ValueError("Source-zero collapse real control differs")
                                    del first
                                finally: n.restore(models, blocks)
                if (q + 1) % 16 == 0:
                    n.old.emit("E159_questions", questions=q + 1, total=128, peak_GB=torch.cuda.max_memory_allocated() / 1e9)
            n.restore(models, blocks)
            for model, ph, bh in zip(models, before, buffers):
                if n.old.tensor_hash(model.state_dict()) != ph or n.old.tensor_hash(n.buffers(model)) != bh:
                    raise ValueError("Source parameters/buffers mutated")
            if not np.isfinite(values).all(): raise ValueError("Nonfinite candidate score")
            arrays = {"candidate_loglikelihood": values, "source_names": np.array(SOURCES), "measured_cells": measured,
                      **{k: refs[k] for k in ("native_reference_candidate_loglikelihood", "all_nine_full_success", "common_native_success")},
                      **{k: a[k] for k in ("gold", "subject", "answer_tokens", "answer_chars")}}
            path = RAW / "scores.npz"
            immutable_npz(path, arrays)
            n.write(RESULT / "manifest.json", {"experiment": "E159", "status": "complete", "source_sha256": proof(),
                    "plan_sha256": n.sha(RESULT / "plan.json"), "raw": {"path": str(path), "sha256": n.sha(path), "size_bytes": path.stat().st_size},
                    "measured_cells": [list(x) for x in MEASURED], "unknown_zero_conditions": 4, "new_measured_question_conditions": 1024,
                    "unknown_question_conditions": 512, "P_replayed_question_conditions": 512, "fixed_zero_collapse_control_calls": 36,
                    "canonical_parameter_hashes": before, "canonical_buffer_hashes": buffers,
                    "controls": {"canonical_parameters_buffers_and_native_cal_exact": True, "all_128_P_full_and_three_zero_replays_exact": True,
                                 "zeroed_source_collapse_36_real_controls_exact": True, "all_candidate_prefixes_causal_and_counts_exact": True,
                                 "source_modules_parameters_buffers_restored": True},
                    "physical_gpu": physical, "visible_device_uuid": str(torch.cuda.get_device_properties(0).uuid),
                    "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                    "scope": plan["scope"]})
    finally:
        if lock is not None: lock.close()
    return {"status": "complete"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("self-test", "prepare", "evaluate"))
    p.add_argument("--physical-gpu", type=int, default=0)
    args = p.parse_args(); torch.set_num_threads(4)
    out = self_test() if args.mode == "self-test" else prepare() if args.mode == "prepare" else evaluate(args.physical_gpu)
    print(json.dumps(out, indent=2), flush=True)
