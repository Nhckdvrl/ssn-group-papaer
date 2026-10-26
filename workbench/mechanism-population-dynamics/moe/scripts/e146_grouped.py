"""Conditional E146, one locked 8x8 grouping and three random partitions.

No training; E144 endpoints are reused. Sparse Top-8 products suffice for the
full FP64 expert covariance, without a [64,N,hidden] dense component tensor.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import time
from pathlib import Path

_early = argparse.ArgumentParser(add_help=False)
_early.add_argument("--physical-gpu", type=int, default=0)
_device_args, _ = _early.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_device_args.physical_gpu)):
    raise ValueError("Requested GPU and process visibility differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_device_args.physical_gpu)

import numpy as np
import torch

import e144145_common as c
import e144145_run as native
from e144145_analyze import input_stats, file_groups

RESULT = c.WB / "results/e146"
RAW = c.ARCHIVE / "e146_grouped_recombination"
HCAL = Path("/tmp/xiang-moe-20261025/e134_necessity/public_native_Hcal.npy")
HCAL_SHA = "c91f538cca8793722eaa7e08c11451ed05bb34053c77f37a5e84ebfc892d715f"


def canonical(groups):
    return sorted([sorted(int(e) for e in g) for g in groups], key=lambda g: tuple(g))


def greedy(gamma, final_size=8):
    groups, rounds = [[i] for i in range(len(gamma))], []
    while len(groups[0]) < final_size:
        pool, new, events = canonical(groups), [], []
        while pool:
            choices = [(float(gamma[np.ix_(a, b)].sum()+gamma[np.ix_(b, a)].sum()), tuple(a), tuple(b), i, j)
                       for i, a in enumerate(pool) for j, b in enumerate(pool) if j > i]
            score, a, b, i, j = min(choices)
            new.append(sorted(a+b))
            events.append({"left": list(a), "right": list(b), "ordered_cross_weight": score})
            pool = [g for k, g in enumerate(pool) if k not in (i, j)]
        groups = canonical(new)
        rounds.append(events)
    return groups, rounds


def cut(gamma, groups):
    labels = np.full(len(gamma), -1, dtype=int)
    for g, members in enumerate(groups):
        if np.any(labels[members] != -1):
            raise ValueError("Partition overlaps")
        labels[members] = g
    if np.any(labels < 0):
        raise ValueError("Partition misses experts")
    return float(-gamma[labels[:, None] != labels[None, :]].sum())


def freeze_random():
    rng = np.random.default_rng(14601)
    parts = {f"random{i}": canonical(rng.permutation(64).reshape(8, 8).tolist()) for i in range(3)}
    bases = np.random.default_rng(14602).integers(0, 3, (4, 8))
    design = {"schema": "E146-random-v1", "random_partitions": parts, "group_size": 8, "groups": 8,
              "partition_rng_seed": 14601, "source_rng_seed": 14602, "independent_source_units": 4,
              "bases": bases.tolist(), "source_maps": [{"name": f"base{b}_{s}", "base": b, "shift": s,
                  "group_sources": ((row+s) % 3).tolist()} for b, row in enumerate(bases) for s in range(3)],
              "selected_sha256": c.sha(c.WB / "results/e144/selected.json")}
    c.immutable_json(RESULT / "random_and_sources.json", design)
    return design


@torch.no_grad()
def gamma_from_traces(traces, chunk=512):
    selected = traces[0]["selected"]
    n, topk = selected.shape
    dim = traces[0]["native"].shape[-1]
    experts = traces[0]["q"].shape[-1]
    slots = torch.empty((len(traces), n, topk, dim), dtype=traces[0]["native"].dtype, device=selected.device)
    for s, trace in enumerate(traces):
        if not torch.equal(selected, trace["selected"]):
            raise ValueError("E146 requires the common fixed gate")
        for e, comp in trace["components"].items():
            row = comp["row"]
            matches = selected[row] == e
            if not torch.all(matches.sum(-1) == 1):
                raise ValueError("Incomplete native Top-k component trace")
            rank = matches.long().argmax(-1)
            slots[s, row, rank] = comp["component"]
    gamma = np.zeros((experts, experts), np.float64)
    for start in range(0, n, chunk):
        value = slots[:, start:start+chunk].double()
        value = value-value.mean(0, keepdim=True)
        # Dot each selected pair across source and hidden dimensions, at each h.
        vectors = value.permute(1, 2, 0, 3).reshape(value.shape[1], topk, -1)
        gram = torch.bmm(vectors, vectors.transpose(1, 2)) / len(traces)
        sel = selected[start:start+chunk].cpu().numpy()
        ii = np.broadcast_to(sel[:, :, None], (len(sel), topk, topk))
        jj = np.broadcast_to(sel[:, None, :], (len(sel), topk, topk))
        np.add.at(gamma, (ii.reshape(-1), jj.reshape(-1)), gram.cpu().numpy().reshape(-1))
    gamma /= n
    moments, mu = c.cohort(traces)
    checks = {"symmetry_max_abs": float(np.abs(gamma-gamma.T).max()),
              "trace_minus_C": float(np.trace(gamma)-moments["C"].mean().cpu()),
              "sum_minus_V": float(gamma.sum()-moments["V"].mean().cpu())}
    if max(abs(v) for v in checks.values()) > 1e-10:
        raise ArithmeticError(f"Covariance identities failed: {checks}")
    return gamma, checks, mu


class Budget(c.Budget):
    def __init__(self):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e146", "calibrate_and_evaluate", 10800


def proofs():
    return {**c.code_proof(), "e146_grouped.py": c.sha(__file__)}


class PrefixStop(Exception):
    pass


@torch.no_grad()
def hidden_only(model, teacher, tokens):
    captured = {}
    def collect(module, inputs):
        captured["hidden"] = inputs[0].detach()
        raise PrefixStop()
    model.model.layers[9].mlp = teacher
    handle = teacher.register_forward_pre_hook(collect)
    try:
        try:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                model.model(input_ids=tokens[:, :-1], use_cache=False)
        except PrefixStop:
            pass
    finally:
        handle.remove()
    return captured["hidden"]


@torch.no_grad()
def evaluate(args):
    design = c.read(RESULT / "random_and_sources.json")
    tests = c.read(RESULT / "self_test.json")
    if tests["source_sha256"] != proofs() or tests["status"] != "passed":
        raise ValueError("Matching E146 known-answer tests required")
    asset = c.read(args.work_root / "assets.json")
    if asset["source_sha256"] != c.code_proof() or design["selected_sha256"] != asset["selected_sha256"]:
        raise ValueError("E144 source/input contract changed")
    original = c.read(c.WB / "results/e144/manifest.json")
    if original["status"] != "complete" or original.get("read_only_source_checks") != "passed":
        raise ValueError("Complete E144 endpoints required")
    if c.sha(HCAL) != HCAL_SHA:
        raise ValueError("Original training Hcal8192 differs")
    lock = None
    try:
        with Budget() as budget:
            lock = c.gpu_lock(args.physical_gpu)
            load_args = argparse.Namespace(experiment="e144")
            model, teacher, blocks = native.load(load_args, asset)
            RAW.mkdir(parents=True, exist_ok=True)
            h = torch.from_numpy(np.array(np.load(HCAL), copy=True)).to("cuda:0").bfloat16().reshape(16, 512, 2048)
            ts = [c.trace(blocks[f"F{s}"], h) for s in range(3)]
            cal_gamma, cal_checks, _ = gamma_from_traces(ts)
            del ts, h
            groups, trajectory = greedy(cal_gamma)
            partitions = {"cal_gamma": groups, **design["random_partitions"]}
            grouped = {"partitions": partitions, "calibration_trajectory": trajectory,
                       "calibration_H_sha256": HCAL_SHA, "source_sha256": proofs(),
                       "selected_sha256": design["selected_sha256"],
                       "random_and_sources_sha256": c.sha(RESULT / "random_and_sources.json")}
            c.immutable_json(RESULT / "groups.json", grouped)
            np.save(RAW / "cal_gamma.npy", cal_gamma)
            record = {"experiment": "E146", "status": "partial", "source_sha256": proofs(),
                      "run_git_head": __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                      "asset_preflight_sha256": c.sha(args.work_root / "assets.json"), "selected_sha256": design["selected_sha256"],
                      "groups_sha256": c.sha(RESULT / "groups.json"), "random_and_sources_sha256": c.sha(RESULT / "random_and_sources.json"),
                      "E144_manifest_sha256": c.sha(c.WB / "results/e144/manifest.json"), "cal_gamma_checks": cal_checks,
                      "cal_cuts": {k: cut(cal_gamma, p) for k, p in partitions.items()}, "raw_batches": [],
                      "cal_gamma": {"path": str(RAW / "cal_gamma.npy"), "sha256": c.sha(RAW / "cal_gamma.npy")}}
            c.write(RESULT / "manifest.json", record)
            # All partitions fixed here, before reading any E146 held prediction.
            selected = c.read(c.WB / "results/e144/selected.json")["rows"]
            old_tokens = np.load(c.RECIPE / "held_tokens.npy", mmap_mode="r").reshape(512, 513)
            held_gamma = np.zeros_like(cal_gamma)
            for batch in range(4):
                budget.check()
                start = time.monotonic()
                tokens = torch.from_numpy(np.stack([old_tokens[r["old_sequence_index"]] for r in selected[16*batch:16*(batch+1)]]).astype(np.int64)).to("cuda:0")
                hidden = hidden_only(model, teacher, tokens)
                traces = [c.trace(blocks[f"F{s}"], hidden) for s in range(3)]
                target_trace = c.trace(teacher, hidden)
                gamma, checks, mu = gamma_from_traces(traces)
                held_gamma += gamma/4
                budget.check()
                pm, _, _ = native.forward(model, c.FixedOutput(mu.bfloat16(), teacher.gate), tokens, hidden, components=False)
                target = tokens[:, 1:]
                old_info = original["raw_batches"][batch]
                if c.sha(old_info["path"]) != old_info["sha256"]:
                    raise ValueError("Old E144 raw changed")
                with np.load(old_info["path"], allow_pickle=False) as old:
                    names_old = old["names"].tolist()
                    nll_mu = -pm.gather(-1, target[..., None]).squeeze(-1).cpu().numpy()
                    if not np.array_equal(nll_mu, old["metrics"][names_old.index("mu"), ..., 0]):
                        raise ValueError("Replayed full mu prediction differs from E144")
                    for s in range(3):
                        expected = native.layer_values(traces[s], target_trace, mu).cpu().numpy()
                        if not np.array_equal(expected, old["layer"][names_old.index(f"F{s}")]):
                            raise ValueError("Replayed native component/layer endpoint differs from E144")
                metrics, layer, names = [], [], []
                balance = {}
                for p, partition in partitions.items():
                    mixed_sum = torch.zeros_like(mu)
                    for row in design["source_maps"]:
                        budget.check()
                        sources = np.full(64, -1, dtype=int)
                        for g, members in enumerate(partition):
                            sources[members] = row["group_sources"][g]
                        if np.any(sources < 0):
                            raise ValueError("Incomplete source coverage")
                        experts = [blocks[f"F{s}"].experts[e] for e, s in enumerate(sources)]
                        op = c.Assembled(blocks["F0"], range(64), experts)
                        pred, trace, _ = native.forward(model, op, tokens, hidden)
                        for e, s in enumerate(sources):
                            if not torch.equal(trace["components"][e]["component"], traces[s]["components"][e]["component"]):
                                raise ValueError("Grouped actual product differs from own native source")
                        metrics.append(c.prediction_metrics(pm, pred, target).cpu().numpy())
                        layer.append(native.layer_values(trace, target_trace, mu).cpu().numpy())
                        names.append(p+"/"+row["name"])
                        mixed_sum += trace["sum64"] / 12
                        del pred, trace
                    balance[p] = float((mixed_sum-mu).abs().max())
                    if balance[p] > 1e-12:
                        raise ArithmeticError("Cyclic grouped source mean differs from mu")
                path = RAW / f"batch{batch:02d}.npz"
                if path.exists():
                    raise ValueError("Refusing to replace an existing E146 raw batch")
                np.savez_compressed(path, names=np.array(names), metrics=np.stack(metrics), layer=np.stack(layer),
                                    metric_fields=np.array(c.METRICS), layer_fields=np.array(native.LAYER_FIELDS))
                record["raw_batches"].append({"path": str(path), "sha256": c.sha(path), "batch": batch,
                                               "seconds": time.monotonic()-start, "balance_max_abs": balance, "gamma_checks": checks})
                c.write(RESULT / "manifest.json", record)
                c.emit("E146_held_batch_complete", batch=batch, seconds=time.monotonic()-start, peak_gb=torch.cuda.max_memory_allocated()/1e9)
                del traces, target_trace, metrics, layer, pm, hidden, tokens
            np.save(RAW / "held_gamma.npy", held_gamma)
            record["held_gamma"] = {"path": str(RAW / "held_gamma.npy"), "sha256": c.sha(RAW / "held_gamma.npy")}
            record["held_cuts"] = {k: cut(held_gamma, p) for k, p in partitions.items()}
            model.model.layers[9].mlp = teacher
            for name, block in blocks.items():
                if c.tensor_hash({"block."+k: v for k, v in block.state_dict().items()}) != asset["sources"][name]["tensor_sha256"]:
                    raise ValueError("Source parameters mutated")
            if c.tensor_hash(teacher.state_dict()) != asset["teacher_block_tensor_sha256"] or c.base.sampled_parameter_hash(model, "model.layers.9.mlp.") != asset["teacher_prefix_sample_hash"]:
                raise ValueError("Public frozen model mutated")
            record.update(status="complete", read_only_source_checks="passed", visible_device_uuid=str(torch.cuda.get_device_properties(0).uuid),
                          peak_allocated_bytes=torch.cuda.max_memory_allocated())
            c.write(RESULT / "manifest.json", record)
    finally:
        if lock is not None:
            lock.close()
    return {"status": record["status"], "experiment": "E146"}


def mc_stats(values, rows):
    values = np.asarray(values, np.float64)
    if values.shape != (4, 64):
        raise ValueError("Exactly four independent grouped-source basis vectors")
    result = input_stats(values.mean(0), rows, 146001)
    result["source_base_points"] = values.mean(1).tolist()
    result["source_mc_se"] = float(values.mean(1).std(ddof=1)/2)
    groups = file_groups(rows)
    rng, samples = np.random.default_rng(146002), []
    for _ in range(1000):
        sources = rng.integers(0, 4, 4)
        inputs = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        samples.append(float(values[np.ix_(sources, inputs)].mean()))
    result["crossed_file_source_ci95"] = np.quantile(samples, [.025, .975]).tolist()
    return result


def analyze():
    record = c.read(RESULT / "manifest.json")
    if record["status"] != "complete" or record["source_sha256"] != proofs():
        raise ValueError("Complete frozen E146 raw required")
    rows = c.read(c.WB / "results/e144/selected.json")["rows"]
    chunks = []
    for r in record["raw_batches"]:
        if c.sha(r["path"]) != r["sha256"]:
            raise ValueError("E146 raw SHA differs")
        with np.load(r["path"], allow_pickle=False) as raw:
            chunks.append({k: np.array(raw[k]) for k in raw.files})
    pred = np.concatenate([r["metrics"] for r in chunks], axis=1).astype(float).mean(2).reshape(4, 4, 3, 64, 4).mean(2)
    layer = np.concatenate([r["layer"] for r in chunks], axis=1).mean(2).reshape(4, 4, 3, 64, 5).mean(2)
    old_manifest = c.read(c.WB / "results/e144/manifest.json")
    old_pred, old_layer = [], []
    for r in old_manifest["raw_batches"]:
        if c.sha(r["path"]) != r["sha256"]:
            raise ValueError("E144 endpoint raw changed")
        with np.load(r["path"], allow_pickle=False) as raw:
            names = raw["names"].tolist()
            indices = [names.index(f"F{s}") for s in range(3)]
            old_pred.append(raw["metrics"][indices].astype(float).mean(0).mean(1))
            old_layer.append(raw["layer"][indices].mean(0).mean(1))
    bp, bl = np.concatenate(old_pred), np.concatenate(old_layer)
    parts = list(c.read(RESULT / "groups.json")["partitions"])
    result = {"experiment": "E146", "status": "complete", "independent_source_units": 4, "partitions": {}, "cal_minus_random": {},
              "manifest_sha256": c.sha(RESULT / "manifest.json"), "scope": "Fixed three students, four source basis vectors, three random partitions; crossed intervals are not training-seed population intervals."}
    arrays = {"delta_nll": pred[..., 0]-bp[None, None, :, 0], "delta_mu_to_variant_kl": pred[..., 1]-bp[None, None, :, 1],
              "delta_sum64_teacher_sse": layer[..., 1]-bl[None, None, :, 1], "delta_native_teacher_sse": layer[..., 0]-bl[None, None, :, 0]}
    for i, p in enumerate(parts):
        result["partitions"][p] = {"cal_cut": record["cal_cuts"][p], "held_cut": record["held_cuts"][p],
                                   **{k: mc_stats(v[i], rows) for k, v in arrays.items()}}
    for name, comparator in [(p, i) for i, p in enumerate(parts[1:], 1)] + [("random_mean", None)]:
        result["cal_minus_random"][name] = {k: mc_stats(v[0]-(v[comparator] if comparator is not None else v[1:].mean(0)), rows) for k, v in arrays.items()}
    c.write(RESULT / "summary.json", result)
    return {"status": "complete", "partitions": {p: {"cal_cut": d["cal_cut"], "held_cut": d["held_cut"], "delta_nll": d["delta_nll"]["point"],
              "delta_kl": d["delta_mu_to_variant_kl"]["point"]} for p, d in result["partitions"].items()}}


def self_test():
    torch.set_num_threads(1)
    torch.manual_seed(146)
    from transformers import OlmoeConfig
    from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock
    cfg = OlmoeConfig(hidden_size=8, intermediate_size=8, num_experts=4, num_experts_per_tok=2, norm_topk_prob=False)
    blocks = [OlmoeSparseMoeBlock(cfg).eval() for _ in range(3)]
    for b in blocks[1:]:
        b.gate.weight.data.copy_(blocks[0].gate.weight)
    h = torch.randn(2, 3, 8)
    ts = [c.trace(b, h) for b in blocks]
    gamma, checks, _ = gamma_from_traces(ts, chunk=2)
    dense = torch.zeros(3, 4, 6, 8, dtype=torch.float64)
    for s, t in enumerate(ts):
        for e, comp in t["components"].items():
            dense[s, e, comp["row"]] = comp["component"].double()
    delta = dense-dense.mean(0)
    truth = torch.einsum("sehd,sfhd->ef", delta, delta).numpy()/18
    np.testing.assert_allclose(gamma, truth, rtol=1e-12, atol=1e-14)
    assert abs(cut(gamma, [[i] for i in range(4)])-(np.trace(gamma)-gamma.sum())) < 1e-12
    assert cut(gamma, [list(range(4))]) == 0
    known = np.kron(np.eye(4), np.array([[1., -1.], [-1., 1.]]))
    group, rounds = greedy(known, 2)
    assert group == [[0, 1], [2, 3], [4, 5], [6, 7]] and cut(known, group) == 0
    # Full enumeration tests the group cut expectation, separate from greedy.
    u = np.array([[1., -1., 2., -2.], [-1., 1., -2., 2.], [0., 0., 0., 0.]])
    gm = u.T @ u / 3
    partition = [[0, 1], [2, 3]]
    risks = [(u[a, partition[0]].sum()+u[b, partition[1]].sum())**2 for a, b in itertools.product(range(3), repeat=2)]
    assert abs(np.mean(risks)-cut(gm, partition)) < 1e-12
    result = {"status": "passed", "CPU_only": True, "source_sha256": proofs(), "checks": {
        "sparse_FP64_gamma_matches_dense_truth": True, "gamma_C_V_identities": checks,
        "singleton_whole_endpoints": True, "greedy_known_negative_pairs": True, "grouped_source_enumeration": True}}
    c.write(RESULT / "self_test.json", result)
    return {"status": "passed", "checks": result["checks"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("prepare", "self-test", "evaluate", "analyze"))
    p.add_argument("--physical-gpu", type=int, default=0)
    p.add_argument("--work-root", type=Path, default=Path("/tmp/xiang-moe-20261026/e144145"))
    args = p.parse_args()
    torch.set_num_threads(4)
    result = freeze_random() if args.mode == "prepare" else self_test() if args.mode == "self-test" else evaluate(args) if args.mode == "evaluate" else analyze()
    print(json.dumps({"status": "design_frozen", "partitions": len(result["random_partitions"])} if args.mode == "prepare" else result, indent=2), flush=True)
