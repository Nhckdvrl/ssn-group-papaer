"""E122/X1: routing geometry, same-input expert functions, held-out substitution effects.

This measures associations, not causal equivalence of expert responsibilities.
Use the original E121 caches. Large tensors stay outside git. Each process owns distinct layers.
"""
import argparse
import hashlib
import json
import os
import platform
import time
from contextlib import ExitStack
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from safetensors import safe_open
from scipy.stats import rankdata

WB = Path(__file__).resolve().parents[1]


def corr(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4 or np.std(a[ok]) < 1e-12 or np.std(b[ok]) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def partial(a, b, cov):
    ok = np.isfinite(a) & np.isfinite(b) & np.isfinite(cov).all(1)
    if ok.sum() < cov.shape[1] + 6:
        return float("nan")
    a, b = rankdata(a[ok]), rankdata(b[ok])
    c = np.column_stack([np.ones(ok.sum()), *[rankdata(v) for v in cov[ok].T]])
    return corr(a - c @ np.linalg.lstsq(c, a, rcond=None)[0],
                b - c @ np.linalg.lstsq(c, b, rcond=None)[0])


def spearman(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    return corr(rankdata(a[ok]), rankdata(b[ok]))


def pair_cov(load, norm, ij):
    i, j = ij
    l, n = np.log(np.maximum(load, 1e-8)), np.log(np.maximum(norm, 1e-8))
    return np.stack([l[i] + l[j], abs(l[i] - l[j]), n[i] + n[j], abs(n[i] - n[j])], 1)


def route_phi(h, gate, device):
    h = h.to(device).float()
    selected = (h @ gate.T).topk(8, -1).indices
    m = torch.zeros(len(h), 64, device=device).scatter_(1, selected, 1)
    loads = m.mean(0)
    mc = m - loads
    s = mc.square().sum(0).sqrt()
    r = (mc.T @ mc) / (s[:, None] * s[None, :]).clamp_min(1e-20)
    invalid = s == 0
    r[invalid, :] = torch.nan
    r[:, invalid] = torch.nan
    return r.cpu().numpy(), loads.cpu().numpy()


def qap(r, f, load, norm, n_perm, rng):
    ij = np.triu_indices(64, 1)
    rv, fv = r[ij], f[ij]
    obs = partial(rv, fv, pair_cov(load, norm, ij))
    if not np.isfinite(obs):
        return {"spearman": spearman(rv, fv), "partial_spearman": obs,
                "qap_p": float("nan"), "null_95": [],
                "pair_coverage": float(np.isfinite(rv).mean()), "n_permutations": 0}
    perms = []
    for _ in range(n_perm):
        p = rng.permutation(64)
        perms.append(partial(rv, f[np.ix_(p, p)][ij], pair_cov(load, norm[p], ij)))
    valid = np.asarray(perms)[np.isfinite(perms)]
    return {"spearman": spearman(rv, fv), "partial_spearman": obs,
            "qap_p": float((1 + (abs(valid) >= abs(obs)).sum()) / (1 + len(valid))),
            "null_95": np.quantile(valid, [.025, .975]).tolist() if len(valid) else [],
            "pair_coverage": float(np.isfinite(rv).mean()), "n_permutations": len(valid)}


def causal_stats(x, y, cov, words, n_boot, rng):
    point = partial(x, y, cov)
    uniq = np.unique(words)
    groups = [np.where(words == w)[0] for w in uniq]
    bs = []
    for _ in range(n_boot):
        ids = np.concatenate([groups[k] for k in rng.integers(0, len(groups), len(groups))])
        bs.append(partial(x[ids], y[ids], cov[ids]))
    b = np.asarray(bs)
    b = b[np.isfinite(b)]
    return {"partial_spearman": point, "ci_word_bootstrap": np.quantile(b, [.025, .975]).tolist() if len(b) else [],
            "spearman": spearman(x, y), "n_items": len(x), "n_words": len(uniq)}


def read_items():
    items = []
    for name in ("pos", "sense"):
        for line in (WB / "results/e121" / f"items_{name}.jsonl").read_text().splitlines():
            row = json.loads(line)
            row["set"] = name
            items.append(row)
    return items


def document_key(item):
    sep = "-" if item["set"] == "pos" else "."
    return item["set"], item["sent"].rsplit(sep, 1)[0]


@torch.no_grad()
def run(a):
    t0 = time.time()
    torch.set_num_threads(4)
    torch.manual_seed(122)
    torch.backends.cuda.matmul.allow_tf32 = False
    device = a.device
    cap = torch.load(a.capture, map_location="cpu", mmap=True, weights_only=False)
    raw = torch.load(a.raw, map_location="cpu", weights_only=False)
    items = read_items()
    posidx = np.array([n for n, it in enumerate(items) if it["set"] == "pos"])
    pos = [items[n] for n in posidx]
    held = np.array([it["split"] == "held" for it in pos])
    words = np.array([it["word"] for it in pos])[held]
    calmeta = np.array(cap["cal_meta"])
    # Captured random positions include preceding context: group entire documents.
    src = np.unique(calmeta[:, 0])
    rng = np.random.default_rng(122)
    sentence_keys = sorted({document_key(items[s]) for s in src})
    shuffled = rng.permutation(len(sentence_keys))
    sentence_half = {sentence_keys[s]: int(i % 2) for i, s in enumerate(shuffled)}
    source_half = {int(s): sentence_half[document_key(items[s])] for s in src}
    half = np.array([source_half[int(s)] for s in calmeta[:, 0]])
    groups = [np.where(half == s)[0] for s in (0, 1)]
    draws = [np.sort(rng.choice(g, min(len(g), a.n_common), replace=False)) for g in groups]
    a.output.mkdir(parents=True, exist_ok=True)
    np.savez(a.output / f"sampling_{a.layers.replace(',', '_')}.npz", source_ids=src, half=half, sample0=draws[0], sample1=draws[1])
    index = json.loads((a.model / "model.safetensors.index.json").read_text())["weight_map"]
    layers = [int(l) for l in a.layers.split(",")]
    needed_shards = {v for k, v in index.items()
                     if any(k.startswith(f"model.layers.{l}.mlp.experts.") for l in layers)}
    with ExitStack() as stack:
        readers = {shard: stack.enter_context(safe_open(str(a.model / shard), framework="pt", device="cpu"))
                   for shard in sorted(needed_shards)}
        for layer in layers:
            tl = time.time()
            gate = cap["gates"][layer].to(device).float()
            hcal = cap["H_cal"][layer]
            route = [route_phi(hcal[g], gate, device) for g in groups]
            rall, lall = route_phi(hcal, gate, device)
            hpos = cap["H_last"][layer][posidx]
            inputs = torch.cat([hcal[d] for d in draws] + [hpos]).to(device, torch.bfloat16)
            allout = []
            for expert in range(64):
                prefix = f"model.layers.{layer}.mlp.experts.{expert}."
                weights = []
                for name in ("gate_proj", "up_proj", "down_proj"):
                    key = prefix + name + ".weight"
                    weights.append(readers[index[key]].get_tensor(key).to(device, torch.bfloat16))
                wg, wu, wd = weights
                y = F.linear(F.silu(F.linear(inputs, wg)) * F.linear(inputs, wu), wd)
                allout.append(y)
            outputs = torch.stack(allout, 1)  # input, expert, hidden
            funcs, norms = [], []
            offset = 0
            for ids in draws:
                chunk = outputs[offset:offset + len(ids)].float()
                norms.append(chunk.norm(dim=-1).mean(0).cpu().numpy())
                unit = F.normalize(chunk, dim=-1)
                funcs.append(torch.bmm(unit, unit.transpose(1, 2)).mean(0).cpu().numpy())
                offset += len(ids)
            yp = outputs[offset:].float()
            assert np.allclose(np.diag(funcs[0]), 1, atol=1e-5)
            ij = np.triu_indices(64, 1)
            row = {"layer": layer, "n_common_each": [len(v) for v in draws],
                   "routing_split_spearman": spearman(route[0][0][ij], route[1][0][ij]),
                   "function_split_spearman": spearman(funcs[0][ij], funcs[1][ij]),
                   "same_half": [qap(route[s][0], funcs[s], route[s][1], norms[s], a.permutations, rng) for s in (0, 1)],
                   "cross_half": [qap(route[s][0], funcs[1-s], route[s][1], norms[1-s], a.permutations, rng) for s in (0, 1)],
                   "causal": {}, "nll_note": "original E121 cache; KL baseline was fp16, self-subtraction is sensitivity only"}
            z = (hpos.to(device).float() @ gate.T).cpu().numpy()
            w = torch.softmax(torch.tensor(z), dim=1).numpy()
            for mode in ("swap9", "swaprand"):
                r = raw[f"L{layer}_{mode}_s0"]
                old, new = r["old"].numpy(), r["new"].numpy()
                idx = torch.arange(len(pos), device=device)
                yo = yp[idx, torch.tensor(old, device=device)]
                yn = yp[idx, torch.tensor(new, device=device)]
                distance = (yo - yn).square().sum(1).sqrt().cpu().numpy()
                cosine_distance = (1 - F.cosine_similarity(yo, yn)).cpu().numpy()
                cov = np.stack([w[np.arange(len(pos)), old], z[np.arange(len(pos)), old] - z[np.arange(len(pos)), new],
                                cap["nll"][posidx].numpy()], 1)[held]
                rd = (1 - rall[old, new])[held]
                dnll = r["dnll"].numpy()[held]
                kl = r["kl"].numpy()[held]
                selfkl = raw[f"L{layer}_self_s0"]["kl"].numpy()[held]
                cc = {}
                for name, x in (("route_distance", rd), ("output_l2", distance[held]), ("output_cosine", cosine_distance[held])):
                    cc[name] = {"kl": causal_stats(x, kl, cov, words, a.bootstrap, rng),
                                "kl_minus_self": causal_stats(x, kl-selfkl, cov, words, a.bootstrap, rng),
                                "dnll": causal_stats(x, dnll, cov, words, a.bootstrap, rng)}
                row["causal"][mode] = cc
            row.update({"elapsed_seconds": time.time()-tl, "total_seconds": time.time()-t0,
                        "hardware": torch.cuda.get_device_name() if device.startswith("cuda") else platform.machine(),
                        "torch": torch.__version__, "pid": os.getpid(), "sampling_seed": 122,
                        "source_item_split_sha256": hashlib.sha256(half.tobytes()).hexdigest(),
                        "expert_identity_permutation_is_not_independent_pair_test": True})
            # Compact results only; matrices aid independent audit, outputs stay transient.
            np.savez(a.output / f"layer{layer}_matrices.npz", R0=route[0][0], R1=route[1][0], Rall=rall,
                     F0=funcs[0], F1=funcs[1], load0=route[0][1], load1=route[1][1], norm0=norms[0], norm1=norms[1])
            (a.output / f"layer{layer}.json").write_text(json.dumps(row, indent=2, allow_nan=True))
            print(json.dumps({"layer": layer, "split_R": row["routing_split_spearman"], "split_F": row["function_split_spearman"],
                              "cross_half": row["cross_half"], "seconds": row["elapsed_seconds"]}), flush=True)
            del outputs, allout, yp, inputs
            if device.startswith("cuda"):
                torch.cuda.empty_cache()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", type=Path, default=Path("/tmp/xiang-moe-20261025/capture.pt"))
    p.add_argument("--raw", type=Path, default=Path("/tmp/xiang-moe-20261025/r3_raw.pt"))
    p.add_argument("--model", type=Path, default=Path("/tmp/xiang-moe-20261025/olmoe"))
    p.add_argument("--output", type=Path, default=WB / "results/e122")
    p.add_argument("--layers", default="9,2")
    p.add_argument("--n-common", type=int, default=1024)
    p.add_argument("--permutations", type=int, default=999)
    p.add_argument("--bootstrap", type=int, default=999)
    p.add_argument("--device", default="cuda")
    run(p.parse_args())
