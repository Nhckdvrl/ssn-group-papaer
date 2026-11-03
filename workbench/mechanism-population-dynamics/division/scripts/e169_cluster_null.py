#!/usr/bin/env python3
"""E169: cluster (k-means) null for cross-seed routing agreement, from the hidden-state captures (CPU).

Per model and layer: fit k-means (K = n_experts) on cal-word hidden states with several seeds, in
(i) the raw 768-d space and (ii) the model's own router read-out subspace; assign every pre-registered
anchor word its 8 nearest centroids; build the co-routing kernel on E167's same-type word pairs and
centre within type. Then the usual T statistic (cross-model correlation):
  T_router_km (same model, router vs k-means), T_km_self (same model, two k-means seeds),
  T_km_cross (two models' k-means), T_ctx recomputed from H/W/b (check vs routing capture),
  T_Dkm (router residual against the k-means expectation), and T_D from the routing capture for reference.

Usage: e169_cluster_null.py TOKENS [N_SEEDS] [K]   -> results/e169/cluster_null_<TOKENS>.json
"""
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

WB = Path(__file__).resolve().parents[1]
AN = Path.home() / "mechpop_cache/e167_analysis"
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3999793152
N_SEEDS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
K = int(sys.argv[3]) if len(sys.argv) > 3 else 64
TOPK = 8

P = np.load(AN / "routing/pairs.npz")
pi, pj, ptype, aw = P["i"], P["j"], P["type"], P["anchor_word"]
nT = int(ptype.max()) + 1


def cw(x):
    s = np.bincount(ptype, x, nT); c = np.bincount(ptype, None, nT)
    return x - (s / np.maximum(c, 1))[ptype]


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-30))


def kernel(S, E):
    M = np.zeros((S.shape[0], E), np.float32)
    np.put_along_axis(M, S, 1.0, 1)
    return (M[pi] * M[pj]).sum(1) / S.shape[1]


def readout(W):
    Wc = W - W.mean(0, keepdims=True)
    U, s, Vt = np.linalg.svd(Wc, full_matrices=False)
    r = int((s > 1e-6 * s[0]).sum())
    return Vt[:r].T


def topk_nearest(X, centers, k):
    d = (X * X).sum(1, keepdims=True) - 2 * X @ centers.T + (centers * centers).sum(1)[None]
    return np.argpartition(d, k, axis=1)[:, :k]


groups = {"init": [("I0D0", "I1D0"), ("I0D0", "I2D0"), ("I0D0", "I3D0"), ("I1D0", "I2D0"), ("I1D0", "I3D0"), ("I2D0", "I3D0")],
          "order": [("I0D0", "I0D1"), ("I1D0", "I1D1")], "floor": [("I0D0", "I1D0")]}
runs = sorted({r for g in ("init", "order") for p in groups[g] for r in p})
out = {"tokens": tok, "n_seeds": N_SEEDS, "K": K, "layers": []}
# load everything once (kernels only; hidden states dropped after use)
store = {}
for r in runs + ["I0D0@0", "I1D0@0"]:
    run, t = (r.split("@")[0], 0) if "@" in r else (r, tok)
    Z = np.load(AN / f"hidden/{run}__ckpt_{t}.npz")
    rows = {int(w): n for n, w in enumerate(Z["word_idx"])}
    sel = np.array([rows[int(w)] for w in aw]); n_anchor = int(Z["n_anchor"])
    R = np.load(AN / f"routing/{run}__ckpt_{t}.npz")
    store[r] = {"Z": Z, "sel": sel, "cal": np.arange(n_anchor, len(Z["word_idx"])), "R": R}
    print("loaded", r, flush=True)

import os
LAYERS = [int(x) for x in os.environ.get("E169_LAYERS", ",".join(map(str, range(12)))).split(",")]
SUFFIX = os.environ.get("E169_SUFFIX", "")
for l in LAYERS:
    t0 = time.time()
    per = {}
    for r in runs + ["I0D0@0", "I1D0@0"]:
        S = store[r]; Z = S["Z"]
        H = Z[f"H{l}"].astype(np.float32); W, b = Z[f"W{l}"], Z[f"b{l}"]
        Ha, Hc = H[S["sel"]], H[S["cal"]]
        E = W.shape[0]
        scores = Ha @ W.T + b
        Sr = np.argpartition(-scores, TOPK, axis=1)[:, :TOPK]
        Cr = cw(kernel(Sr, E).astype(float))
        Ccap = cw(S["R"][f"C{l}"].astype(float)); Bcap = cw(S["R"][f"B{l}"].astype(float))
        rec = {"C_router": Cr, "C_cap": Ccap, "D_cap": Ccap - Bcap, "check_corr_recompute_vs_capture": corr(Cr, Ccap)}
        V = readout(W)
        for space, Xa, Xc in (("raw", Ha, Hc), ("readout", Ha @ V, Hc @ V)):
            kms = []
            sizes = []
            for s in range(N_SEEDS):
                km = KMeans(n_clusters=K, n_init=1, random_state=1000 + s, max_iter=100).fit(Xc)
                Sk = topk_nearest(Xa, km.cluster_centers_.astype(np.float32), TOPK)
                kms.append(cw(kernel(Sk, K).astype(float)))
                sizes.append(np.bincount(km.labels_, minlength=K).max() / (len(Xc) / K))
            rec[space] = {"km": kms, "maxload": float(np.mean(sizes))}
        per[r] = rec
    row = {"layer": l, "recompute_check": {r: per[r]["check_corr_recompute_vs_capture"] for r in per}}
    for space in ("raw", "readout"):
        sp = {"maxload": float(np.mean([per[r][space]["maxload"] for r in runs]))}
        sp["T_router_km"] = float(np.mean([corr(per[r]["C_router"], k) for r in runs for k in per[r][space]["km"]]))
        sp["T_km_self"] = float(np.mean([corr(a, b) for r in runs for a, b in itertools.combinations(per[r][space]["km"], 2)]))
        for g, pairs in groups.items():
            key = lambda x: f"{x}@0" if g == "floor" else x
            sp[f"T_km_cross_{g}"] = float(np.mean([corr(a, b) for x, y in pairs for a in per[key(x)][space]["km"] for b in per[key(y)][space]["km"]]))
            sp[f"T_ctx_{g}"] = float(np.mean([corr(per[key(x)]["C_router"], per[key(y)]["C_router"]) for x, y in pairs]))
            sp[f"T_D_{g}"] = float(np.mean([corr(per[key(x)]["D_cap"], per[key(y)]["D_cap"]) for x, y in pairs]))
            dk = lambda r: per[r]["C_router"] - np.mean(per[r][space]["km"], 0)
            sp[f"T_Dkm_{g}"] = float(np.mean([corr(dk(key(x)), dk(key(y))) for x, y in pairs]))
            sp[f"T_router_km_{g}"] = float(np.mean([corr(per[key(x)]["C_router"], k) for x, y in pairs for k in per[key(x)][space]["km"]])) if g == "floor" else None
        row[space] = sp
    out["layers"].append(row)
    s = row["raw"]; t = row["readout"]
    print(f"L{l:2d} ({time.time()-t0:.0f}s) check {np.mean(list(row['recompute_check'].values())):.3f} | raw: km_self {s['T_km_self']:.3f} km_cross init {s['T_km_cross_init']:.3f} order {s['T_km_cross_order']:.3f} floor {s['T_km_cross_floor']:.3f} | router_km {s['T_router_km']:.3f} | T_ctx init {s['T_ctx_init']:.3f} order {s['T_ctx_order']:.3f} | T_D init {s['T_D_init']:.3f} order {s['T_D_order']:.3f} | T_Dkm init {s['T_Dkm_init']:.3f} order {s['T_Dkm_order']:.3f} floor {s['T_Dkm_floor']:.3f} || readout: km_self {t['T_km_self']:.3f} km_cross init {t['T_km_cross_init']:.3f} order {t['T_km_cross_order']:.3f} router_km {t['T_router_km']:.3f} T_Dkm init {t['T_Dkm_init']:.3f} order {t['T_Dkm_order']:.3f}", flush=True)
    (WB / "results/e169").mkdir(exist_ok=True)
    (WB / f"results/e169/cluster_null_{tok}{SUFFIX}.json").write_text(json.dumps(out))
print("saved")
