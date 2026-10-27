"""E157: reintegrate frozen task subbanks into the common mature P receiver."""
import argparse
import os
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=0)
_early, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early.physical_gpu)):
    raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
import copy
import json
import math
from pathlib import Path
import numpy as np
import torch
from torch import nn
import e156_run as prev
import e157_analyze as analysis

n, h, loading = prev.n, prev.h, prev.loading
RESULT = n.WB / "results/e157"
RAW = Path.home() / "mechpop_cache/e157_task_subbank_reintegration"
GROUPS, DONORS, SHARED = ("Bio", "Math"), ("A", "B"), ("P", "A", "B")


def proof():
    return {**prev.proof(), **{f: n.sha(n.WB / "scripts" / f) for f in ("e157_run.py", "e157_analyze.py")}}


def assemble_subbank(models, blocks, donor, shared, keep):
    """Copy registries only; parent gate and every unselected routed function stay P."""
    keep = np.asarray(keep)
    layers, experts = len(blocks[0]), len(blocks[0][0].experts)
    if keep.dtype != np.bool_ or keep.shape != (layers, experts) or not keep[:, -1].all():
        raise ValueError("Expected layer/expert boolean mask including the shared slot")
    if donor not in range(3) or shared not in range(3):
        raise ValueError("Invalid function source")
    model = models[0]
    for layer, target in enumerate(model.model.layers):
        template = blocks[0][layer]
        if template.num_shared_experts != 1 or template.always_active_experts not in (None, []):
            raise ValueError("Unexpected native shared-expert interface")
        block = copy.copy(template)
        block._modules = dict(template._modules)
        block._parameters = dict(template._parameters)
        block._buffers = dict(template._buffers)
        block.gate = blocks[0][layer].gate
        routed = [blocks[donor if keep[layer, e] else 0][layer].experts[e] for e in range(experts - 1)]
        block.experts = nn.ModuleList(routed + [blocks[shared][layer].experts[-1]])
        target.mlp = block
    return model


class OracleGate(nn.Module):
    def __init__(self, values):
        super().__init__()
        self.register_buffer("logits", torch.tensor(values, dtype=torch.float32))

    def forward(self, x):
        return self.logits.to(x).expand(x.shape[0], -1)


def self_test():
    torch.set_num_threads(1)
    torch.manual_seed(157)
    values = ((2., 4., 8., 10.), (3., 6., 12., 20.), (5., 10., 15., 30.))
    gates = ((math.log(4), math.log(2), 0., 100.), (0., math.log(3), math.log(5), -100.),
             (math.log(2), math.log(7), 0., -100.))
    models = []
    for i, label in enumerate(SHARED):
        cfg_cls, _, _ = loading._classes(label, complete=False)
        name = "codex_e154_parent" if label == "P" else f"codex_e150_source_{i-1}"
        module = __import__(name + ".modeling_emo", fromlist=["EmoSparseMoeBlock"])
        cfg = cfg_cls(hidden_size=4, intermediate_size=4, num_experts=4,
                      num_experts_per_tok=3, num_shared_experts=1, norm_topk_prob=False)
        block = module.EmoSparseMoeBlock(cfg, 4, 1, None)
        block.gate = OracleGate(gates[i])
        block.experts = nn.ModuleList([prev.v.Constant(x) for x in values[i]])
        layer, model = nn.Module(), nn.Module()
        layer.mlp = block
        model.model = nn.Module()
        model.model.layers = nn.ModuleList([layer])
        models.append(model)
    blocks = n.original_blocks(models)
    before = [n.old.tensor_hash(m.state_dict()) for m in models]
    x = torch.ones((1, 6, 4))
    native = [m.model.layers[0].mlp(x)[0].clone() for m in models]
    patterns = np.array([[0, 0, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1], [0, 1, 0, 1]], bool)
    controls = 0
    for keep in patterns:
        for donor in range(3):
            for shared in range(3):
                model = assemble_subbank(models, blocks, donor, shared, keep[None])
                block = model.model.layers[0].mlp
                assert block.gate is blocks[0][0].gate
                for e in range(3):
                    assert block.experts[e] is blocks[donor if keep[e] else 0][0].experts[e]
                assert block.experts[-1] is blocks[shared][0].experts[-1]
                expected = values[shared][-1] + (4 / 7) * values[donor if keep[0] else 0][0] + (2 / 7) * values[donor if keep[1] else 0][1]
                actual = block(x)[0]
                assert torch.allclose(actual, torch.full_like(actual, expected), atol=1e-5, rtol=0)
                if not keep[:-1].any() or keep[:-1].all():
                    other = n.assemble(models, blocks, (0, 0, donor if keep[:-1].all() else 0, shared))
                    assert torch.equal(actual, other.model.layers[0].mlp(x)[0])
                n.restore(models, blocks)
                controls += 1
    for i, model in enumerate(models):
        assert model.model.layers[0].mlp is blocks[i][0]
        assert torch.equal(model.model.layers[0].mlp(x)[0], native[i])
        assert n.old.tensor_hash(model.state_dict()) == before[i]
    stats = analysis.self_test()
    n.write(RESULT / "self_test.json", {"status": "passed", "CPU_only": True, "source_sha256": proof(),
            "unequal_gate_source_oracles": controls, "empty_all_and_partial_masks": True,
            "original_registries_and_values_restored": True, "statistics": stats})
    return {"status": "passed", "oracle_cases": controls}


def prepare():
    tests = n.read(RESULT / "self_test.json")
    if tests["status"] != "passed" or tests["source_sha256"] != proof():
        raise ValueError("Matching complete CPU tests required")
    old = n.read(prev.RESULT / "manifest.json")
    plan = n.read(prev.RESULT / "plan.json")
    ledger = n.read(prev.RESULT / "budget.json")
    selector = n.read(prev.RESULT / "selectors.json")
    if old["status"] != "complete" or any(x["status"] != "complete" for x in ledger["attempts"]):
        raise ValueError("Complete E156 run required")
    if old["source_sha256"] != prev.proof() or n.sha(prev.RESULT / "plan.json") != old["plan_sha256"]:
        raise ValueError("Previous source/plan differs")
    if n.sha(prev.RESULT / "selectors.json") != old["selectors_sha256"] or not selector["calibration_only"] or selector["test_labels_used"]:
        raise ValueError("Frozen validation-only selector required")
    for record in (old["raw"], selector["raw"], plan["task_input"], plan["legacy_cal_input"]):
        if n.sha(record["path"]) != record["sha256"]:
            raise ValueError("Inherited source changed")
    with np.load(selector["raw"]["path"], allow_pickle=False) as f:
        masks = f["masks"].copy()
    if masks.dtype != bool or masks.shape != (2, 16, 128) or not masks[:, :, -1].all() or not np.all(masks.sum(-1) == 32):
        raise ValueError("Wrong inherited task masks")
    with np.load(old["raw"]["path"], allow_pickle=False) as f:
        if f["native_candidate_loglikelihood"].shape != (3, 2, 128, 4) or f["common_success"].sum() != 44:
            raise ValueError("Wrong E156 reference")
    RAW.mkdir(parents=True, exist_ok=True)
    result = {"experiment": "E157", "status": "prepared", "source_sha256": proof(),
              "previous_manifest_sha256": n.sha(prev.RESULT / "manifest.json"),
              "previous_plan_sha256": n.sha(prev.RESULT / "plan.json"), "previous_raw": old["raw"],
              "masks": selector["raw"], "selector_sha256": n.sha(prev.RESULT / "selectors.json"),
              "task_input": plan["task_input"], "task_data_plan_sha256": plan["task_data_plan_sha256"],
              "legacy_cal_input": plan["legacy_cal_input"], "source_records": plan["source_records"],
              "pad_token_id": plan["pad_token_id"], "group_names": list(GROUPS), "donor_names": list(DONORS),
              "shared_names": list(SHARED), "new_full_conditions": 12, "native_full_replays": 3,
              "group_routed_intersection_per_layer": np.sum(masks[0, :, :-1] & masks[1, :, :-1], axis=-1).tolist(),
              "new_conditions": [{"group": g, "R_donor": r, "S_source": s} for g in GROUPS for r in DONORS for s in SHARED],
              "inherited_restricted_scope": "Only g=question subject has E156 masked identity; off-domain masked unmeasured",
              "bootstrap": {"seed": 157001, "resamples": 1000, "unit": "paired question within fixed subjects"},
              "scope": "Reintegration into P with other routed functions preserved, unchanged native full routing; no training."}
    n.old.immutable_json(RESULT / "plan.json", result)
    return {"status": "prepared"}


class Budget(n.old.Budget):
    def __init__(self):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e157", "task_subbank_reintegration", 9000


@torch.no_grad()
def evaluate(physical):
    plan = n.read(RESULT / "plan.json")
    if plan["source_sha256"] != proof() or n.read(RESULT / "self_test.json")["source_sha256"] != proof():
        raise ValueError("Frozen numerical source differs")
    if n.sha(prev.RESULT / "manifest.json") != plan["previous_manifest_sha256"] or n.sha(prev.RESULT / "plan.json") != plan["previous_plan_sha256"]:
        raise ValueError("Previous run metadata differs")
    if n.sha(prev.TASK / "data_plan.json") != plan["task_data_plan_sha256"] or n.sha(prev.RESULT / "selectors.json") != plan["selector_sha256"]:
        raise ValueError("Task/selector recipe differs")
    for record in (plan["previous_raw"], plan["masks"], plan["task_input"], plan["legacy_cal_input"]):
        if n.sha(record["path"]) != record["sha256"]:
            raise ValueError("Frozen input/reference differs")
    for label, record in plan["source_records"].items():
        if n.sha(prev.PREVIOUS / f"manifest_{label}.json") != record["manifest_sha256"]:
            raise ValueError("Canonical source record differs")
    target = RAW / "scores.npz"
    if target.exists():
        raise ValueError("Refusing to overwrite E157 raw")
    with np.load(plan["task_input"]["path"], allow_pickle=False) as f:
        a = {k: f[k].copy() for k in f.files}
    with np.load(plan["previous_raw"]["path"], allow_pickle=False) as f:
        old = {k: f[k].copy() for k in f.files}
    with np.load(plan["masks"]["path"], allow_pickle=False) as f:
        masks = f["masks"].copy()
    with np.load(plan["legacy_cal_input"]["path"], allow_pickle=False) as f:
        cal, cv = f["cal"][:2, :129].copy(), f["cal_mask"][:2, :128].copy()
    lock = None
    try:
        with Budget() as budget:
            lock = n.old.gpu_lock(physical)
            models, before, before_buffers = [], [], []
            ids = torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            attention = torch.cat((torch.ones((2, 1), dtype=torch.bool, device="cuda:0"), torch.from_numpy(cv).to("cuda:0")), 1)
            for label in SHARED:
                budget.check()
                model = loading.load_cpu_bf16(label)
                models.append(model)
                if sum(p.numel() for p in model.parameters()) != 13568641024:
                    raise ValueError("Unexpected native source size")
                record = plan["source_records"][label]
                ph, bh = n.old.tensor_hash(model.state_dict()), n.old.tensor_hash(n.buffers(model))
                if ph != record["parameter_hash"] or bh != record["buffer_hash"]:
                    raise ValueError("Canonical parameter/buffer mismatch")
                before.append(ph)
                before_buffers.append(bh)
                native_cal = record["calibration"]
                if n.sha(native_cal["path"]) != native_cal["sha256"]:
                    raise ValueError("Canonical calibration raw differs")
                with np.load(native_cal["path"], allow_pickle=False) as f:
                    expected = torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                actual = n.fwd(model, ids[:, :-1], attention[:, :-1])
                if not torch.equal(actual, expected):
                    raise ValueError("Native calibration differs")
                with n.restricted.restricted_gates(model, np.ones((2, 16, 128), bool)):
                    if not torch.equal(n.fwd(model, ids[:, :-1], attention[:, :-1]), expected):
                        raise ValueError("Native all-slot identity differs")
                del actual, expected
                n.old.emit("E157_source_loaded", source=label, peak_GB=torch.cuda.max_memory_allocated() / 1e9)
            del ids, attention
            blocks = n.original_blocks(models)
            empty, all_routed = np.zeros((16, 128), bool), np.ones((16, 128), bool)
            empty[:, -1] = True
            identity_cases = 0
            for question in (0, 64):
                budget.check()
                n.restore(models, blocks)
                seqs = prev.sequences(a["test_ids"], a["test_offsets"], range(question * 4, question * 4 + 4))
                prompt, group = int(a["prompt_tokens"][question]), int(a["subject"][question])
                _, _, ref = h.score_candidates(models[0], seqs, prompt, plan["pad_token_id"])
                for donor, keep in [(1, empty), (1, all_routed), (2, all_routed)]:
                    for shared in range(3):
                        model = assemble_subbank(models, blocks, donor, shared, keep)
                        score, counts, first = h.score_candidates(model, seqs, prompt, plan["pad_token_id"])
                        r = 0 if not keep[:, :-1].any() else donor
                        if not np.array_equal(score, old["candidate_loglikelihood"][r, shared, 0, question]) or not np.array_equal(counts, a["answer_tokens"][question]):
                            raise ValueError("Empty/all subbank source identity differs")
                        if prev.kl(ref, first) != old["first_answer_token_KL_vs_P"][r, shared, 0, question]:
                            raise ValueError("Empty/all first-token reference identity differs")
                        del first
                        identity_cases += 1
                keep = np.broadcast_to(masks[group], (4, 16, 128)).copy()
                for donor in (1, 2):
                    for shared in range(3):
                        model = n.assemble(models, blocks, (0, 0, donor, shared))
                        with n.restricted.restricted_gates(model, keep):
                            expected, counts, first_expected = h.score_candidates(model, seqs, prompt, plan["pad_token_id"])
                        if not np.array_equal(expected, old["candidate_loglikelihood"][donor, shared, 1, question]):
                            raise ValueError("Inherited E156 restricted readout differs")
                        model = assemble_subbank(models, blocks, donor, shared, masks[group])
                        with n.restricted.restricted_gates(model, keep):
                            score, got_counts, first = h.score_candidates(model, seqs, prompt, plan["pad_token_id"])
                        if not np.array_equal(score, expected) or not torch.equal(first, first_expected) or not np.array_equal(got_counts, counts):
                            raise ValueError("Partial and whole-bank masked operators differ")
                        del first, first_expected
                        identity_cases += 1
                del ref
            n.restore(models, blocks)
            n.old.emit("E157_structural_controls_passed", cases=identity_cases, new_scientific_scores_read=False)
            values = np.empty((2, 2, 3, 128, 4), np.float64)
            relative = np.empty((2, 2, 3, 128), np.float64)
            native = np.empty((3, 128, 4), np.float64)
            native_relative = np.empty((3, 128), np.float64)
            for question in range(128):
                budget.check()
                n.restore(models, blocks)
                seqs = prev.sequences(a["test_ids"], a["test_offsets"], range(question * 4, question * 4 + 4))
                prompt = int(a["prompt_tokens"][question])
                refs = []
                for source, model in enumerate(models):
                    score, counts, first = h.score_candidates(model, seqs, prompt, plan["pad_token_id"])
                    if not np.array_equal(score, old["native_candidate_loglikelihood"][source, 0, question]) or not np.array_equal(counts, a["answer_tokens"][question]):
                        raise ValueError("All-question native E156 replay differs")
                    native[source, question] = score
                    refs.append(first)
                for source, first in enumerate(refs):
                    native_relative[source, question] = prev.kl(refs[0], first)
                    if native_relative[source, question] != old["native_first_answer_token_KL_vs_P"][source, 0, question]:
                        raise ValueError("Native first-token reference replay differs")
                for group in range(2):
                    budget.check()
                    for r, donor in enumerate((1, 2)):
                        for shared in range(3):
                            model = assemble_subbank(models, blocks, donor, shared, masks[group])
                            score, counts, first = h.score_candidates(model, seqs, prompt, plan["pad_token_id"])
                            if not np.array_equal(counts, a["answer_tokens"][question]):
                                raise ValueError("Answer token counts differ")
                            values[group, r, shared, question] = score
                            relative[group, r, shared, question] = prev.kl(refs[0], first)
                            del first
                del refs
                if (question + 1) % 8 == 0:
                    n.old.emit("E157_questions", questions=question + 1, total=128, peak_GB=torch.cuda.max_memory_allocated() / 1e9)
            n.restore(models, blocks)
            if any(n.old.tensor_hash(m.state_dict()) != x for m, x in zip(models, before)):
                raise ValueError("Source parameters mutated")
            if any(n.old.tensor_hash(n.buffers(m)) != x for m, x in zip(models, before_buffers)):
                raise ValueError("Source buffers mutated")
            if not all(np.isfinite(x).all() for x in (values, relative, native, native_relative)):
                raise ValueError("Nonfinite full-model readouts")
            np.savez_compressed(target, candidate_loglikelihood=values, first_answer_token_KL_vs_P=relative,
                                native_candidate_loglikelihood=native, native_first_answer_token_KL_vs_P=native_relative,
                                gold=a["gold"], subject=a["subject"], answer_tokens=a["answer_tokens"], answer_chars=a["answer_chars"],
                                common_success=old["common_success"], group_names=np.array(GROUPS), donor_names=np.array(DONORS), shared_names=np.array(SHARED))
            n.write(RESULT / "manifest.json", {"experiment": "E157", "status": "complete", "source_sha256": proof(),
                    "plan_sha256": n.sha(RESULT / "plan.json"), "previous_raw_sha256": plan["previous_raw"]["sha256"],
                    "raw": {"path": str(target), "sha256": n.sha(target), "size_bytes": target.stat().st_size},
                    "source_parameter_hashes": before, "source_buffer_hashes": before_buffers,
                    "controls": {"canonical_parameter_buffer_and_cal_exact": True, "native_all_slot_identity_exact": True,
                                 "empty_and_all_R_reproduce_previous_full": True, "on_domain_masked_operator_identity_exact": True,
                                 "native_all_question_LL_and_first_token_replay_exact": True, "candidate_prefix_causal_and_counts_exact": True,
                                 "source_parameters_buffers_unchanged": True},
                    "structural_control_cases": identity_cases, "new_full_conditions": 12, "native_full_replays": 3,
                    "physical_gpu": physical, "visible_device_uuid": str(torch.cuda.get_device_properties(0).uuid),
                    "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                    "inherited_restricted": "E156 only on-domain; no new 128-question masked measurement, off-domain masked unmeasured",
                    "scope": "P dense/gate and unselected R functions; task-selected corresponding R from A/B, S independently P/A/B; zero training."})
    finally:
        if lock is not None:
            lock.close()
    return {"status": "complete"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("self-test", "prepare", "evaluate"))
    p.add_argument("--physical-gpu", type=int, default=0)
    args = p.parse_args()
    torch.set_num_threads(4)
    out = self_test() if args.mode == "self-test" else prepare() if args.mode == "prepare" else evaluate(args.physical_gpu)
    print(json.dumps(out, indent=2), flush=True)
