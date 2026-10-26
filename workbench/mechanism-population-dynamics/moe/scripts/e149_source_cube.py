"""E149: system-wide backbone x router x expert-bank source cube, no training."""
from __future__ import annotations
import argparse
import os
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=0)
_early, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early.physical_gpu)):
    raise ValueError("Requested physical GPU/visibility differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early.physical_gpu)

import copy
import itertools
import json
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeConfig, OlmoeForCausalLM
import e148_common as c
import e148_readout as previous
from e144145_analyze import input_stats

RESULT = c.WB / "results/e149"
RAW = c.DURABLE.parent / "e149_native_source_cube"
CASES = tuple(itertools.product(range(2), repeat=3))


def proof():
    return {**c.code_proof(), "e149_source_cube.py": c.sha(__file__)}


def original_blocks(models):
    return [[layer.mlp for layer in model.model.layers] for model in models]


def assemble(models, blocks, case):
    backbone, gates, experts = case
    model = models[backbone]
    for layer, module in enumerate(model.model.layers):
        gate = blocks[gates][layer]
        bank = blocks[experts][layer]
        module.mlp = c.old.Assembled(gate, range(gate.num_experts), list(bank.experts))
    return model


def restore(models, blocks):
    for model, group in zip(models, blocks):
        for layer, block in zip(model.model.layers, group): layer.mlp = block


class Budget(c.old.Budget):
    def __init__(self):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e149", "global_source_cube", 3600


def self_test():
    torch.manual_seed(149); torch.set_num_threads(1)
    cfg = OlmoeConfig(vocab_size=64, hidden_size=16, intermediate_size=16, num_hidden_layers=2, num_attention_heads=2,
                      num_key_value_heads=2, num_experts=4, num_experts_per_tok=2, attention_dropout=0., norm_topk_prob=False,
                      tie_word_embeddings=False, max_position_embeddings=32)
    cfg._attn_implementation = "eager"
    models = [OlmoeForCausalLM(cfg).bfloat16().float().eval() for _ in range(2)]
    states = [copy.deepcopy(m.state_dict()) for m in models]
    blocks = original_blocks(models)
    ids = torch.randint(0, 64, (2, 7))
    with torch.no_grad():
        native = [c.shader(m, ids).logits.clone() for m in models]
        for case in CASES:
            m = assemble(models, blocks, case)
            for name, tensor in m.named_parameters():
                source = case[1] if ".mlp.gate." in name else case[2] if ".mlp.experts." in name else case[0]
                assert torch.equal(tensor, states[source][name])
            output = c.shader(m, ids).logits
            if case == (0, 0, 0): assert torch.equal(output, native[0])
            if case == (1, 1, 1): assert torch.equal(output, native[1])
        restore(models, blocks)
        for model, state in zip(models, states):
            for name, value in model.state_dict().items(): assert torch.equal(value, state[name])
    # A known three-factor function validates signed finite differences.
    y = {x: 1+2*x[0]+3*x[1]+5*x[2]+7*x[1]*x[2]+11*x[0]*x[1]*x[2] for x in CASES}
    third = sum((-1)**(3-sum(x))*v for x, v in y.items())
    assert third == 11
    d = {"status": "passed", "CPU_only": True, "source_sha256": proof(), "checks": {
        "all_eight_source_parameter_assignments": True, "native_corner_BF16_logits_exact": True,
        "all_source_parameters_unchanged": True, "signed_three_way_difference_known_answer": True}}
    c.write(RESULT / "self_test.json", d)
    return d


@torch.no_grad()
def evaluate(physical):
    tests = c.read(RESULT / "self_test.json")
    if tests["status"] != "passed" or tests["source_sha256"] != proof(): raise ValueError("Matching cube known-answer checks required")
    plan, records = previous.completed()
    with np.load(plan["plan_path"]) as data: held = data["held"].copy()
    lock = None
    result = {"experiment": "E149", "status": "partial", "source_sha256": proof(), "plan_sha256": plan["plan_sha256"],
              "factor_order": ["backbone", "all_gates", "all_expert_banks"], "source_order": ["A", "B"],
              "cases": [list(x) for x in CASES], "controls": {}, "scope": __doc__}
    try:
        with Budget() as budget:
            lock = c.old.gpu_lock(physical)
            models, sources = [], []
            for name in ("A", "B"):
                budget.check(); model, info = previous.load_receiver(records[name], 672)
                models.append(model); sources.append(info)
            blocks = original_blocks(models)
            before = [c.old.tensor_hash(m.state_dict()) for m in models]
            buffers = [c.old.tensor_hash(c.buffer_state(m)) for m in models]
            evaluations = [next(e for e in records[n]["evaluations"] if e["step"] == 672) for n in ("A", "B")]
            arrays = []
            for e in evaluations:
                if c.sha(e["logits"]["path"]) != e["logits"]["sha256"]: raise ValueError("Source native logits changed")
                arrays.append(np.load(e["logits"]["path"], mmap_mode="r"))
            values = np.empty((8, 64, 512, 2, 4), np.float32)
            for start in range(0, 64, 8):
                budget.check()
                tokens = torch.from_numpy(held[start:start+8].astype(np.int64)).to("cuda:0")
                target = tokens[:, 1:]
                reference_logits = [torch.from_numpy(np.array(a[start:start+8], copy=True)).view(torch.bfloat16).to("cuda:0") for a in arrays]
                references = [r.float().log_softmax(-1) for r in reference_logits]
                for index, case in enumerate(CASES):
                    budget.check()
                    model = assemble(models, blocks, case)
                    logits = c.shader(model, tokens[:, :-1]).logits
                    if case in ((0, 0, 0), (1, 1, 1)):
                        src = case[0]
                        if not torch.equal(logits, reference_logits[src]): raise ValueError("Full-system native corner failed exact replay")
                    p = logits.float().log_softmax(-1)
                    for ref in range(2): values[index, start:start+8, :, ref] = c.old.prediction_metrics(references[ref], p, target).cpu().numpy()
                    del logits, p
                c.emit("E149_cube_batch", sequences=start+8, peak_GB=torch.cuda.max_memory_allocated()/1e9)
                del references, reference_logits, tokens
            restore(models, blocks)
            if any(c.old.tensor_hash(m.state_dict()) != h for m, h in zip(models, before)): raise ValueError("Cube evaluation mutated source parameters")
            if any(c.old.tensor_hash(c.buffer_state(m)) != h for m, h in zip(models, buffers)): raise ValueError("Cube evaluation mutated registered buffers")
            if not np.array_equal(values[..., 0, 0], values[..., 1, 0]): raise ValueError("NLL depends on the chosen reference")
            RAW.mkdir(parents=True, exist_ok=True)
            path = RAW / "cube_metrics.npz"
            if path.exists(): raise ValueError("Refusing to replace existing cube readout")
            np.savez_compressed(path, metrics=values, cases=np.array(CASES), fields=np.array(c.old.METRICS))
            result.update(status="complete", source_checkpoints=sources, controls={"both_native_corners_bitwise_equal": True,
                "all_parameters_and_registered_buffers_unchanged": True, "NLL_reference_invariant": True},
                raw={"path": str(path), "sha256": c.sha(path), "size_bytes": path.stat().st_size},
                peak_allocated_bytes=torch.cuda.max_memory_allocated(), physical_gpu=physical, visible_device_uuid=str(torch.cuda.get_device_properties(0).uuid))
            c.write(RESULT / "manifest.json", result)
    finally:
        if lock is not None: lock.close()
    return {"status": result["status"], "peak_GB": result["peak_allocated_bytes"]/1e9}


def analyze():
    manifest = c.read(RESULT / "manifest.json")
    if manifest["status"] != "complete" or manifest["source_sha256"] != proof(): raise ValueError("Sealed complete cube required")
    plan = c.verify_plan(); raw = manifest["raw"]
    if c.sha(raw["path"]) != raw["sha256"]: raise ValueError("Cube raw SHA differs")
    with np.load(raw["path"], allow_pickle=False) as f: a = f["metrics"].astype(float).mean(2)
    stats = lambda v: input_stats(np.asarray(v), plan["selected"], 149001)
    nll = {case: a[i, :, 0, 0] for i, case in enumerate(CASES)}
    result = {"experiment": "E149", "status": "complete", "cases": {}, "one_factor_flips": {}, "interactions": {},
              "scope": "One ancestral checkpoint and two order-history endpoints; input-file CIs do not describe training-seed populations."}
    for i, case in enumerate(CASES):
        name = "".join("AB"[x] for x in case)
        result["cases"][name] = {"sources": dict(zip(manifest["factor_order"], ["AB"[x] for x in case])), "nll": stats(nll[case]),
            "nll_minus_AAA": stats(nll[case]-nll[(0, 0, 0)]), "nll_minus_BBB": stats(nll[case]-nll[(1, 1, 1)]),
            **{f"{ref}_to_variant_KL": stats(a[i, :, r, 1]) for r, ref in enumerate("AB")},
            **{f"variant_to_{ref}_KL": stats(a[i, :, r, 2]) for r, ref in enumerate("AB")}}
    for axis, group in enumerate(manifest["factor_order"]):
        for fixed in itertools.product(range(2), repeat=2):
            low = list(fixed); low.insert(axis, 0); high = list(low); high[axis] = 1
            result["one_factor_flips"][f"{group}_B_minus_A_others_{fixed}"] = stats(nll[tuple(high)]-nll[tuple(low)])
    for axes in ((0, 1), (0, 2), (1, 2)):
        other = next(x for x in range(3) if x not in axes)
        for fixed in range(2):
            delta = np.zeros(64)
            for x, y in itertools.product(range(2), repeat=2):
                case = [0, 0, 0]; case[axes[0]] = x; case[axes[1]] = y; case[other] = fixed
                delta += (-1)**(2-x-y)*nll[tuple(case)]
            key = f"{manifest['factor_order'][axes[0]]}_x_{manifest['factor_order'][axes[1]]}_other_{fixed}"
            result["interactions"][key] = stats(delta)
    result["interactions"]["backbone_x_complete_MoE"] = stats(nll[(1, 1, 1)]-nll[(0, 1, 1)]-nll[(1, 0, 0)]+nll[(0, 0, 0)])
    result["interactions"]["three_way"] = stats(sum((-1)**(3-sum(k))*v for k, v in nll.items()))
    c.write(RESULT / "summary.json", result)
    print(json.dumps({k: {"nll":v["nll"]["point"], "KL_from_A":v["A_to_variant_KL"]["point"]} for k,v in result["cases"].items()}, indent=2))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("self-test", "evaluate", "analyze")); p.add_argument("--physical-gpu", type=int, default=0)
    args = p.parse_args(); torch.set_num_threads(4)
    out = self_test() if args.mode == "self-test" else evaluate(args.physical_gpu) if args.mode == "evaluate" else analyze()
    if args.mode != "analyze": print(json.dumps({"status":out["status"]}, indent=2))
