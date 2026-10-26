"""E148 sealed trajectory statistics and reciprocal legal L9 transplants.

A donor's complete L9 in the receiver backbone is a block graft, not the donor
native predictor. No hidden-state or expert matching is fitted on held inputs.
"""
from __future__ import annotations
import argparse
import os
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=0)
_device, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_device.physical_gpu)):
    raise ValueError("Requested GPU/visibility differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_device.physical_gpu)

import collections
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
import e148_common as c
from e144145_analyze import input_stats


def completed():
    plan = c.verify_plan()
    records = {name: c.read(c.RESULT / f"{name}.json") for name in ("parent", "A", "B", "A-repeat")}
    for name, row in records.items():
        if row["status"] != "complete" or row["source_sha256"] != c.code_proof() or row["plan_sha256"] != plan["plan_sha256"]:
            raise ValueError("All frozen branches must complete before scientific readout")
        if name != "parent" and row["step"] != 672: raise ValueError("Incomplete fork endpoint")
    parent = records["parent"]["snapshots"][-1]
    for name in ("A", "B", "A-repeat"):
        if records[name]["parent_checkpoint_sha256"] != parent["sha256"] or records[name]["initial_parent_state_sha256"] != parent["state_tensor_sha256"]:
            raise ValueError("Forks did not start from exactly one parent")
        if records[name]["initial_parent_buffer_sha256"] != parent["buffer_tensor_sha256"]:
            raise ValueError("Fork parent RoPE/buffers differ")
    if len({records[n]["chains"]["suffix"] for n in ("A", "B", "A-repeat")}) != 1:
        raise ValueError("Common suffix byte/order chain differs")
    pools = {}
    for name in ("A", "B", "A-repeat"):
        log = records[name]["update_log"]
        if c.sha(log["path"]) != log["sha256"]: raise ValueError("Update log changed")
        entries = [json.loads(x) for x in Path(log["path"]).read_text().splitlines()]
        if [e["step"] for e in entries] != list(range(33, 673)): raise ValueError("Update count/cursor differs")
        pools[name] = collections.Counter(e["token_batch_sha256"] for e in entries if e["phase"] == "pulse")
    if not (pools["A"] == pools["B"] == pools["A-repeat"]): raise ValueError("Pulse exposure multiset differs")
    return plan, records


def find_checkpoint(record, step):
    info = next(x for x in record["snapshots"] if x["step"] == step)
    if c.sha(info["path"]) != info["sha256"]: raise ValueError("Checkpoint bytes changed")
    cp = torch.load(info["path"], map_location="cpu", mmap=True, weights_only=False)
    if cp["step"] != step or cp["source_sha256"] != c.code_proof(): raise ValueError("Wrong checkpoint identity")
    return cp, info


def load_receiver(record, step):
    cp, info = find_checkpoint(record, step)
    if cp["schema"] != "E148-full-v1": raise ValueError("Complete receiver state required")
    model = c.load_bf16().float().eval()
    model.load_state_dict(cp["state"], strict=True)
    c.restore_buffers(model, cp["buffers"])
    return model, info


def load_bank(record, step, config):
    cp, info = find_checkpoint(record, step)
    prefix = "model.layers.9.mlp."
    state = {k.removeprefix(prefix): v for k, v in cp["state"].items() if k.startswith(prefix)}
    block = c.old.block_from_state(state, config, "cuda:0")
    return block, info


class Zero(nn.Module):
    def __init__(self, block):
        super().__init__(); self.gate = block.gate
    def forward(self, hidden):
        return torch.zeros_like(hidden), self.gate(hidden.reshape(-1, hidden.shape[-1]))


@torch.no_grad()
def transplants(physical):
    plan, records = completed()
    with np.load(plan["plan_path"]) as raw: held = raw["held"].copy()
    lock = None
    result = {"experiment": "E148", "stage": "reciprocal_L9_grafts", "status": "partial", "source_sha256": c.code_proof(),
              "plan_sha256": plan["plan_sha256"], "receivers": {}, "scope": __doc__}
    try:
        with c.Budget("reciprocal_endpoint_readout") as budget:
            lock = c.old.gpu_lock(physical)
            for step in (160, 672):
                for receiver in ("A", "B"):
                    budget.check()
                    donor = "B" if receiver == "A" else "A"
                    model, rp = load_receiver(records[receiver], step)
                    original = model.model.layers[9].mlp
                    bank, dp = load_bank(records[donor], step, model.config)
                    ops = {"native": original,
                           "bank_only": c.old.Assembled(original, range(64), list(bank.experts)),
                           "gate_only": c.old.Assembled(bank, range(64), list(original.experts)),
                           "complete_L9_graft": c.old.Assembled(bank, range(64), list(bank.experts)), "zero_L9": Zero(original)}
                    controls = {"identity_bank": c.old.Assembled(original, range(64), list(original.experts))}
                    extra = {}
                    if receiver == "A":
                        repeat, repeat_proof = load_bank(records["A-repeat"], step, model.config)
                        ops["repeat_bank"] = c.old.Assembled(original, range(64), list(repeat.experts))
                        extra["repeat"] = repeat_proof
                    if step == 672:
                        late, late_proof = load_bank(records[receiver], 608, model.config)
                        ops["own_late_bank"] = c.old.Assembled(original, range(64), list(late.experts))
                        extra["own_late"] = late_proof
                    names = list(ops)
                    metrics = np.empty((len(names), 64, 512, len(c.old.METRICS)), np.float32)
                    floors = {}
                    before = c.old.tensor_hash(model.state_dict())
                    for start in range(0, 64, 8):
                        budget.check()
                        tokens = torch.from_numpy(held[start:start+8].astype(np.int64)).to("cuda:0")
                        target = tokens[:, 1:]
                        model.model.layers[9].mlp = original
                        reference = c.shader(model, tokens[:, :-1]).logits.float().log_softmax(-1)
                        for name, op in ops.items():
                            budget.check()
                            model.model.layers[9].mlp = op
                            pred = c.shader(model, tokens[:, :-1]).logits.float().log_softmax(-1)
                            metrics[names.index(name), start:start+8] = c.old.prediction_metrics(reference, pred, target).cpu().numpy()
                            if name == "native" and start == 0: floors["native_repeat_logp_max_abs"] = float((reference-pred).abs().max())
                            del pred
                        if start == 0:
                            for name, op in controls.items():
                                model.model.layers[9].mlp = op
                                p = c.shader(model, tokens[:, :-1]).logits.float().log_softmax(-1)
                                floors[name+"_logp_max_abs"] = float((reference-p).abs().max())
                                del p
                        del reference, tokens
                    if any(v != 0 for v in floors.values()): raise ValueError("Native/self assembly floor nonzero")
                    model.model.layers[9].mlp = original
                    if c.old.tensor_hash(model.state_dict()) != before: raise ValueError("Readout mutated receiver parameters")
                    path = c.LOCAL / f"graft_{step}_{receiver}.npz"
                    if path.exists(): raise ValueError("Refusing to replace graft raw")
                    np.savez_compressed(path, metrics=metrics, names=np.array(names), fields=np.array(c.old.METRICS))
                    key = f"step{step}_{receiver}"
                    result["receivers"][key] = {"receiver": receiver, "donor": donor, "step": step,
                        "receiver_checkpoint": rp, "donor_checkpoint": dp, "extra_sources": extra,
                        "raw": {"path": str(path), "sha256": c.sha(path)}, "floors": floors, "read_only": True}
                    c.write(c.RESULT / "grafts.json", result)
                    c.emit("E148_grafts_complete", step=step, receiver=receiver, variants=len(names))
                    del model, ops, controls, bank, original
                    if receiver == "A": del repeat
                    if step == 672: del late
                    torch.cuda.empty_cache()
            result.update(status="complete", physical_gpu=physical, visible_device_uuid=str(torch.cuda.get_device_properties(0).uuid))
            c.write(c.RESULT / "grafts.json", result)
    finally:
        if lock is not None: lock.close()
    return {"status": result["status"], "receivers": len(result["receivers"])}


def evaluation(record, step):
    row = next(x for x in record["evaluations"] if x["step"] == step)
    for key in ("logits", "routing"):
        info = row[key]
        if info is not None and c.sha(info["path"]) != info["sha256"]: raise ValueError("Trajectory raw changed")
    return row


def bits_to_logp(array):
    value = torch.from_numpy(np.array(array, copy=True)).view(torch.bfloat16).float()
    return value.log_softmax(-1)


def stats(values, plan):
    return input_stats(np.asarray(values), plan["selected"], 148001)


def q9_from_capture(raw):
    selected = raw["selected"][9::16].reshape(-1, 8)
    weights = torch.from_numpy(np.array(raw["weights"][9::16], copy=True)).view(torch.bfloat16).double().numpy().reshape(-1, 8)
    q = np.zeros((len(selected), 64), np.float64)
    np.put_along_axis(q, selected.astype(int), weights, axis=1)
    return q


def analyze():
    plan, records = completed()
    result = {"experiment": "E148", "status": "complete", "source_sha256": c.code_proof(), "natural": {}, "pairs": {}, "grafts": {},
              "scope": "One pretrained parent and one finite order pulse; paired input-file intervals, not training-seed population CIs."}
    for branch, record in records.items():
        for row in record["evaluations"]:
            result["natural"][f"{branch}_{row['step']}"] = stats(row["nll_rows"], plan)
    # Exact full-vocabulary KL from stored BF16 logits. Token-chunking bounds RAM.
    pairs = [("A", step, "B", step) for step in (160, 608, 672)] + [("A", step, "A-repeat", step) for step in (160, 608, 672)] + [(b, 608, b, 672) for b in ("A", "B", "A-repeat")]
    with np.load(plan["plan_path"]) as raw: targets = raw["held"][:, 1:].copy()
    for left, ls, right, rs in pairs:
        a, b = evaluation(records[left], ls), evaluation(records[right], rs)
        la, lb = np.load(a["logits"]["path"], mmap_mode="r"), np.load(b["logits"]["path"], mmap_mode="r")
        sums = np.zeros((64, 4), np.float64)
        for seq in range(64):
            for start in range(0, 512, 32):
                p, q = bits_to_logp(la[seq:seq+1, start:start+32]), bits_to_logp(lb[seq:seq+1, start:start+32])
                target = torch.from_numpy(targets[seq:seq+1, start:start+32].astype(np.int64))
                sums[seq] += c.old.prediction_metrics(p, q, target).double().sum((0, 1)).numpy()
        values = sums/512
        key = f"{left}_{ls}_to_{right}_{rs}"
        result["pairs"][key] = {"forward_kl": stats(values[:, 1], plan), "reverse_kl": stats(values[:, 2], plan),
            "nll_right_minus_left": stats(np.array(b["nll_rows"])-np.array(a["nll_rows"]), plan), "top1_agreement": stats(values[:, 3], plan)}
    grafts = c.read(c.RESULT / "grafts.json")
    if grafts["status"] != "complete" or grafts["source_sha256"] != c.code_proof(): raise ValueError("Complete registered grafts required")
    for key, record in grafts["receivers"].items():
        raw = record["raw"]
        if c.sha(raw["path"]) != raw["sha256"]: raise ValueError("Graft raw differs")
        with np.load(raw["path"], allow_pickle=False) as data:
            names = data["names"].tolist(); a = data["metrics"].astype(float).mean(2)
        baseline = a[names.index("native"), :, 0]
        result["grafts"][key] = {name: {"delta_nll": stats(a[i, :, 0]-baseline, plan),
                                       "native_to_variant_kl": stats(a[i, :, 1], plan),
                                       "variant_to_native_kl": stats(a[i, :, 2], plan)} for i, name in enumerate(names)}
    # Predeclared physical-slot trajectory, without fitting a new correspondence.
    routing = {}
    for branch in ("A", "B", "A-repeat"):
        series = {}
        parent = evaluation(records["parent"], 32)
        with np.load(parent["routing"]["path"], allow_pickle=False) as raw:
            parent_selected = raw["selected"].copy()
            parent_q = q9_from_capture(raw)
            parent_affinity = parent_q.T @ parent_q / len(parent_q)
        for step in (160, 288, 608, 672):
            info = evaluation(records[branch], step)
            with np.load(info["routing"]["path"], allow_pickle=False) as raw:
                selected = raw["selected"]
                overlap = (selected[..., :, None] == parent_selected[..., None, :]).sum((-1, -2))/8
                q = q9_from_capture(raw)
                affinity = q.T @ q / len(q)
                series[str(step)] = {"all_layer_top8_overlap_with_parent": overlap.mean(1).reshape(2, 16).mean(0).tolist(),
                                     "L9_top8_overlap_with_parent": float(overlap.mean(1).reshape(2, 16).mean(0)[9]),
                                     "L9_applied_gate_mass": float(q.sum(1).mean()),
                                     "L9_applied_gate_L2_change_per_position": float(np.square(q-parent_q).sum(1).mean()),
                                     "L9_gate_only_affinity_frobenius_change": float(np.linalg.norm(affinity-parent_affinity))}
        routing[branch] = series
    result["routing"] = routing
    result["exposure_audit"] = {"common_parent_verified": True, "pulse_multiset_equal": True, "common_suffix_chain": records["A"]["chains"]["suffix"],
                                 "A_repeat_same_pulse_chain": records["A"]["chains"]["pulse"] == records["A-repeat"]["chains"]["pulse"]}
    c.write(c.RESULT / "summary.json", result)
    return {"status": "complete", "final_A_to_B": result["pairs"]["A_672_to_B_672"],
            "final_A_to_repeat": result["pairs"]["A_672_to_A-repeat_672"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("grafts", "analyze"))
    p.add_argument("--physical-gpu", type=int, default=0)
    args = p.parse_args()
    torch.set_num_threads(4)
    print(json.dumps(transplants(args.physical_gpu) if args.mode == "grafts" else analyze(), indent=2), flush=True)
