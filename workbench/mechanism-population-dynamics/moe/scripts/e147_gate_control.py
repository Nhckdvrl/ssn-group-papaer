"""E147: one gate-only weighted-coactivation partition, not a graph sweep."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=0)
_device, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_device.physical_gpu)):
    raise ValueError("Process visibility and requested GPU differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_device.physical_gpu)

import json
import time
import numpy as np
import torch
from torch.nn import functional as F
import e146_grouped as g

c, native = g.c, g.native
RESULT = c.WB / "results/e147"
RAW = c.ARCHIVE / "e147_gate_group_control"


def proofs():
    return {**g.proofs(), "e147_gate_control.py": c.sha(__file__)}


class Budget(c.Budget):
    def __init__(self):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e147", "gate_group_control", 3600


def self_test():
    q = np.array([[1., 1., 0., 0.], [1., 1., 0., 0.], [0., 0., 1., 1.], [0., 0., 1., 1.]])
    partition, _ = g.greedy(-(q.T @ q)/4, 2)
    assert partition == [[0, 1], [2, 3]]
    design = c.read(g.RESULT / "random_and_sources.json")
    assert len(design["source_maps"]) == 12 and design["independent_source_units"] == 4
    sources = np.array([r["group_sources"] for r in design["source_maps"]])
    assert all(np.all((sources == s).sum(0) == 4) for s in range(3))
    record = {"status": "passed", "CPU_only": True, "source_sha256": proofs(),
              "known_weighted_coactivation_groups": partition, "existing_four_basis_cyclic_balance": True,
              "E146_source_design_sha256": c.sha(g.RESULT / "random_and_sources.json")}
    c.write(RESULT / "self_test.json", record)
    return {"status": "passed"}


@torch.no_grad()
def evaluate(args):
    test = c.read(RESULT / "self_test.json")
    if test["source_sha256"] != proofs() or test["status"] != "passed":
        raise ValueError("Matching known-answer check required")
    previous = c.read(g.RESULT / "manifest.json")
    if previous["status"] != "complete" or previous["source_sha256"] != g.proofs():
        raise ValueError("Sealed E146 required")
    asset = c.read(args.work_root / "assets.json")
    if asset["source_sha256"] != c.code_proof() or c.sha(g.HCAL) != g.HCAL_SHA:
        raise ValueError("Original source/Hcal contract changed")
    design = c.read(g.RESULT / "random_and_sources.json")
    selected = c.read(c.WB / "results/e144/selected.json")["rows"]
    old = c.read(c.WB / "results/e144/manifest.json")
    lock = None
    try:
        with Budget() as budget:
            lock = c.gpu_lock(args.physical_gpu)
            model, teacher, blocks = native.load(argparse.Namespace(experiment="e144"), asset)
            hcal = torch.from_numpy(np.array(np.load(g.HCAL), copy=True)).to("cuda:0").bfloat16()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = blocks["F0"].gate(hcal)
            weight, selected_experts = F.softmax(logits, dim=-1, dtype=torch.float32).topk(8, dim=-1)
            q = torch.zeros((len(hcal), 64), device="cuda:0", dtype=torch.float64)
            q.scatter_(1, selected_experts, weight.bfloat16().double())
            affinity = (q.T @ q / len(q)).cpu().numpy()
            partition, trajectory = g.greedy(-affinity)
            group = {"partition": partition, "trajectory": trajectory, "score": "minus Q.T@Q/N; actual BF16 applied Top8 gate weights; no expert functions",
                     "source_sha256": proofs(), "training_Hcal_sha256": g.HCAL_SHA, "selected_sha256": asset["selected_sha256"],
                     "source_design_sha256": c.sha(g.RESULT / "random_and_sources.json")}
            c.immutable_json(RESULT / "groups.json", group)
            RAW.mkdir(parents=True, exist_ok=True)
            np.save(RAW / "training_gate_affinity.npy", affinity)
            record = {"experiment": "E147", "status": "partial", "source_sha256": proofs(), "groups_sha256": c.sha(RESULT / "groups.json"),
                      "E146_manifest_sha256": c.sha(g.RESULT / "manifest.json"), "selected_sha256": asset["selected_sha256"],
                      "training_gate_affinity": {"path": str(RAW / "training_gate_affinity.npy"), "sha256": c.sha(RAW / "training_gate_affinity.npy")},
                      "raw_batches": []}
            c.write(RESULT / "manifest.json", record)
            del q, weight, logits, hcal
            tokens_old = np.load(c.RECIPE / "held_tokens.npy", mmap_mode="r").reshape(512, 513)
            for batch in range(4):
                budget.check()
                started = time.monotonic()
                tokens = torch.from_numpy(np.stack([tokens_old[r["old_sequence_index"]] for r in selected[16*batch:16*(batch+1)]]).astype(np.int64)).to("cuda:0")
                hidden = g.hidden_only(model, teacher, tokens)
                traces = [c.trace(blocks[f"F{s}"], hidden) for s in range(3)]
                teacher_trace = c.trace(teacher, hidden)
                _, mu = c.cohort(traces)
                pm, _, _ = native.forward(model, c.FixedOutput(mu.bfloat16(), teacher.gate), tokens, hidden, components=False)
                target = tokens[:, 1:]
                info = old["raw_batches"][batch]
                if c.sha(info["path"]) != info["sha256"]:
                    raise ValueError("E144 raw changed")
                with np.load(info["path"], allow_pickle=False) as raw:
                    names = raw["names"].tolist()
                    if not np.array_equal((-pm.gather(-1, target[..., None]).squeeze(-1)).cpu().numpy(), raw["metrics"][names.index("mu"), ..., 0]):
                        raise ValueError("Mu prediction differs from E144")
                    for s in range(3):
                        if not np.array_equal(native.layer_values(traces[s], teacher_trace, mu).cpu().numpy(), raw["layer"][names.index(f"F{s}")]):
                            raise ValueError("Native component/layer endpoint differs")
                metrics, layers = [], []
                average = torch.zeros_like(mu)
                for row in design["source_maps"]:
                    budget.check()
                    sources = np.full(64, -1, dtype=int)
                    for j, members in enumerate(partition):
                        sources[members] = row["group_sources"][j]
                    if np.any(sources < 0):
                        raise ValueError("Source coverage incomplete")
                    op = c.Assembled(blocks["F0"], range(64), [blocks[f"F{s}"].experts[e] for e, s in enumerate(sources)])
                    p, trace, _ = native.forward(model, op, tokens, hidden)
                    for e, s in enumerate(sources):
                        if not torch.equal(trace["components"][e]["component"], traces[s]["components"][e]["component"]):
                            raise ValueError("Actual grouped source product differs")
                    metrics.append(c.prediction_metrics(pm, p, target).cpu().numpy())
                    layers.append(native.layer_values(trace, teacher_trace, mu).cpu().numpy())
                    average += trace["sum64"]/12
                    del p, trace
                balance = float((average-mu).abs().max())
                if balance > 1e-12:
                    raise ValueError("Balanced source mean differs")
                path = RAW / f"batch{batch:02d}.npz"
                if path.exists():
                    raise ValueError("Refusing to overwrite existing E147 raw")
                np.savez_compressed(path, metrics=np.stack(metrics), layer=np.stack(layers))
                record["raw_batches"].append({"path": str(path), "sha256": c.sha(path), "batch": batch,
                                               "seconds": time.monotonic()-started, "balanced_mean_max_abs": balance})
                c.write(RESULT / "manifest.json", record)
                c.emit("E147_batch_complete", batch=batch, seconds=time.monotonic()-started)
                del hidden, traces, teacher_trace, pm, metrics, layers, tokens
            # Read held covariance only after the gate-only partition/predictors are fixed.
            for name in ("cal_gamma", "held_gamma"):
                info = previous[name]
                if c.sha(info["path"]) != info["sha256"]:
                    raise ValueError("Sealed E146 Gamma changed")
                record[name + "_cut"] = g.cut(np.load(info["path"]), partition)
            model.model.layers[9].mlp = teacher
            if c.tensor_hash(teacher.state_dict()) != asset["teacher_block_tensor_sha256"] or c.base.sampled_parameter_hash(model, "model.layers.9.mlp.") != asset["teacher_prefix_sample_hash"]:
                raise ValueError("Frozen public model changed")
            for name, block in blocks.items():
                if c.tensor_hash({"block."+k: v for k, v in block.state_dict().items()}) != asset["sources"][name]["tensor_sha256"]:
                    raise ValueError("Student source changed")
            record.update(status="complete", read_only_source_checks="passed", visible_device_uuid=str(torch.cuda.get_device_properties(0).uuid),
                          peak_allocated_bytes=torch.cuda.max_memory_allocated())
            c.write(RESULT / "manifest.json", record)
    finally:
        if lock is not None:
            lock.close()
    return {"status": "complete"}


def analyze():
    record = c.read(RESULT / "manifest.json")
    if record["status"] != "complete" or record["source_sha256"] != proofs():
        raise ValueError("Sealed E147 required")
    source = c.read(g.RESULT / "manifest.json")
    rows = c.read(c.WB / "results/e144/selected.json")["rows"]
    chunks, old_chunks = [], []
    for current, prior in zip(record["raw_batches"], source["raw_batches"]):
        for info in (current, prior):
            if c.sha(info["path"]) != info["sha256"]:
                raise ValueError("Raw SHA mismatch")
        with np.load(current["path"], allow_pickle=False) as raw:
            chunks.append({k: raw[k].copy() for k in ("metrics", "layer")})
        with np.load(prior["path"], allow_pickle=False) as raw:
            old_chunks.append({k: raw[k].copy() for k in ("metrics", "layer")})
    result = {"experiment": "E147", "status": "complete", "gate_only_minus_cal_gamma": {}, "gate_only_minus_random_mean": {},
              "cal_cut": record["cal_gamma_cut"], "held_cut": record["held_gamma_cut"], "independent_source_units": 4,
              "scope": "Same four source bases and input files, conditional finite cohort; neither training-seed nor random-partition population intervals."}
    for container, column, label in (("metrics", 0, "nll"), ("metrics", 1, "mu_to_variant_kl"), ("layer", 1, "sum64_teacher_sse")):
        a = np.concatenate([r[container] for r in chunks], axis=1).astype(float).mean(2)[..., column].reshape(4, 3, 64).mean(1)
        b = np.concatenate([r[container] for r in old_chunks], axis=1).astype(float).mean(2)[..., column].reshape(4, 4, 3, 64).mean(2)
        result["gate_only_minus_cal_gamma"][label] = g.mc_stats(a-b[0], rows)
        result["gate_only_minus_random_mean"][label] = g.mc_stats(a-b[1:].mean(0), rows)
    c.write(RESULT / "summary.json", result)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("self-test", "evaluate", "analyze"))
    p.add_argument("--physical-gpu", type=int, default=0)
    p.add_argument("--work-root", type=Path, default=Path("/tmp/xiang-moe-20261026/e144145"))
    args = p.parse_args()
    torch.set_num_threads(4)
    print(json.dumps(self_test() if args.mode == "self-test" else evaluate(args) if args.mode == "evaluate" else analyze(), indent=2), flush=True)
