#!/usr/bin/env python3
"""E170 stage 1: decompose within-word-type routing agreement by linguistic variables (CPU only).

Inputs: E167 routing captures (C, B per layer; pre-registered same-type word pairs) and
results/e167/ud_annotations.json (built by ud_annotate.py, aligned to passages.json words).

For each variable X (upos, deprel, head_upos, prev_upos, next_upos, sent position class, feats, genre,
and upos x X combinations) and each layer:
  within model : R2 of D (within-type-centred N1 residual) on cell means, cells = (type, X_a, X_b) with >= MIN_CELL pairs;
                 leave-one-out R2 as an overfitting check
  cross model  : share = cov(Dcell_A, Dcell_B) / cov(D_A, D_B)   (fraction of reproducible division carried by X)
                 cell_corr = corr(Dcell_A, Dcell_B); resid_corr = corr(D_A - Dcell_A, D_B - Dcell_B)
  label permutation null (within type) for share and R2.
Same for C (token identity removed only). Groups: init-only pairs, order-only pairs, untrained floor pair.

Usage: e170_decompose.py TOKENS [N_PERM]   -> results/e170/decomp_<TOKENS>.json
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
MIN_CELL = 3
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3999793152
N_PERM = int(sys.argv[2]) if len(sys.argv) > 2 else 20

P = np.load(CAP / "pairs.npz")
pi, pj, ptype = P["i"], P["j"], P["type"]
aw = P["anchor_word"]
nT = int(ptype.max()) + 1
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
A = [ann[int(w)] for w in aw]  # per anchor row


def posclass(a):
    return "init" if a["sent_init"] else ("final" if a["sent_final"] else "mid")


VARS = {
    "upos": [a["upos"] for a in A],
    "deprel": [a["deprel"] for a in A],
    "head_upos": [a["head_upos"] for a in A],
    "prev_upos": [a["prev_upos"] for a in A],
    "next_upos": [a["next_upos"] for a in A],
    "sentpos": [posclass(a) for a in A],
    "feats": [a["feats"] for a in A],
    "genre": [a["genre"] for a in A],
    "doc": [a["doc_id"] for a in A],
}
for x in ("deprel", "head_upos", "prev_upos", "next_upos", "feats", "sentpos", "genre"):
    VARS[f"upos+{x}"] = [u + "|" + v for u, v in zip(VARS["upos"], VARS[x])]
ENC = {k: np.unique(np.array(v), return_inverse=True)[1] for k, v in VARS.items()}


def cw(x):
    s = np.bincount(ptype, x, nT)
    c = np.bincount(ptype, None, nT)
    return x - (s / np.maximum(c, 1))[ptype]


def cells_for(lab):
    la, lb = lab[pi], lab[pj]
    lo, hi = np.minimum(la, lb), np.maximum(la, lb)
    key = (ptype.astype(np.int64) * (lab.max() + 1) + lo) * (lab.max() + 1) + hi
    _, cid, cnt = np.unique(key, return_inverse=True, return_counts=True)
    return cid, cnt[cid]


def cell_mean(x, cid, cnt):
    s = np.bincount(cid, x)
    n = np.bincount(cid)
    m = (s / np.maximum(n, 1))[cid]
    m[cnt < MIN_CELL] = 0.0
    loo = np.where(cnt >= MIN_CELL, (s[cid] - x) / np.maximum(n[cid] - 1, 1), 0.0)
    return m, loo


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-30))


def cov(a, b):
    return float(((a - a.mean()) * (b - b.mean())).mean())


def load(run, t):
    Z = np.load(CAP / f"{run}__ckpt_{t}.npz")
    return {l: {"D": cw(Z[f"C{l}"].astype(float) - Z[f"B{l}"].astype(float)), "C": cw(Z[f"C{l}"].astype(float))} for l in range(12)}


groups = {"init": [("I0D0", "I1D0"), ("I0D0", "I2D0"), ("I0D0", "I3D0"), ("I1D0", "I2D0"), ("I1D0", "I3D0"), ("I2D0", "I3D0")],
          "order": [("I0D0", "I0D1"), ("I1D0", "I1D1")]}
runs = sorted({r for g in groups.values() for p in g for r in p})
M = {r: load(r, tok) for r in runs}
F = {r: load(r, 0) for r in ("I0D0", "I1D0")}
rng = np.random.default_rng(170)
# permuted label encodings (within type): permute rows' labels among rows of the same type
order_by_type = np.argsort(np.unique(P["anchor_type"], return_inverse=True)[1], kind="stable")
wtype = np.unique(P["anchor_type"], return_inverse=True)[1]
perm_enc = {}
for k, lab in ENC.items():
    perms = []
    for _ in range(N_PERM):
        perm = np.arange(len(lab))
        for t_id in np.unique(wtype):
            idx = np.where(wtype == t_id)[0]
            perm[idx] = idx[rng.permutation(len(idx))]
        perms.append(lab[perm])
    perm_enc[k] = perms

out = {"tokens": tok, "min_cell": MIN_CELL, "n_perm": N_PERM, "vars": {}}
for k, lab in ENC.items():
    cid, cnt = cells_for(lab)
    coverage = float((cnt >= MIN_CELL).mean())
    pcells = [cells_for(pl) for pl in perm_enc[k]]
    rec = {"coverage": coverage, "layers": []}
    for l in range(12):
        row = {"layer": l}
        for q in ("D", "C"):
            # within-model R2 (mean over the 6 D0/D1 runs) and LOO R2
            r2, r2loo = [], []
            for r in runs:
                x = M[r][l][q]
                m, loo = cell_mean(x, cid, cnt)
                r2.append(float((m * m).sum() / (x * x).sum()))
                r2loo.append(corr(x, loo) ** 2)
            row[f"{q}_R2"] = float(np.mean(r2)); row[f"{q}_R2_loo"] = float(np.mean(r2loo))
            # permutation null for R2 (first run only, cheap)
            x = M[runs[0]][l][q]
            row[f"{q}_R2_perm95"] = float(np.percentile([((cell_mean(x, c, n)[0] ** 2).sum() / (x * x).sum()) for c, n in pcells], 95))
            for g, pairs in list(groups.items()) + [("floor", [("I0D0", "I1D0")])]:
                sh, cc, rc, tot = [], [], [], []
                for a, b in pairs:
                    xa = (F if g == "floor" else M)[a][l][q]; xb = (F if g == "floor" else M)[b][l][q]
                    ma, _ = cell_mean(xa, cid, cnt); mb, _ = cell_mean(xb, cid, cnt)
                    cab = cov(xa, xb)
                    sh.append(cov(ma, mb) / cab if abs(cab) > 1e-12 else float("nan"))
                    cc.append(corr(ma, mb)); rc.append(corr(xa - ma, xb - mb)); tot.append(corr(xa, xb))
                row[f"{q}_{g}_share"] = float(np.nanmean(sh)); row[f"{q}_{g}_cellcorr"] = float(np.mean(cc))
                row[f"{q}_{g}_residcorr"] = float(np.mean(rc)); row[f"{q}_{g}_T"] = float(np.mean(tot))
                if g == "init":
                    xa, xb = M["I0D0"][l][q], M["I1D0"][l][q]
                    cab = cov(xa, xb)
                    row[f"{q}_init_share_perm95"] = float(np.percentile([cov(cell_mean(xa, c, n)[0], cell_mean(xb, c, n)[0]) / cab for c, n in pcells], 95))
        rec["layers"].append(row)
    out["vars"][k] = rec
    deep = lambda key: np.mean([rec["layers"][l][key] for l in range(6, 12)])
    print(f"{k:16s} cov={coverage:.2f} | D: R2 {deep('D_R2'):.3f} (loo {deep('D_R2_loo'):.3f}, perm95 {deep('D_R2_perm95'):.3f}) | share init {deep('D_init_share'):.3f} (perm95 {deep('D_init_share_perm95'):.3f}) order {deep('D_order_share'):.3f} | cellcorr init {deep('D_init_cellcorr'):.3f} order {deep('D_order_cellcorr'):.3f} | residcorr init {deep('D_init_residcorr'):.3f} order {deep('D_order_residcorr'):.3f} | C: R2 {deep('C_R2'):.3f} share init {deep('C_init_share'):.3f}", flush=True)
(WB / "results/e170").mkdir(exist_ok=True)
(WB / f"results/e170/decomp_{tok}.json").write_text(json.dumps(out))
print("saved", WB / f"results/e170/decomp_{tok}.json")
