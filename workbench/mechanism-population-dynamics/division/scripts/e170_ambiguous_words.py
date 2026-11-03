#!/usr/bin/env python3
"""E170 stage 1b: for multi-function word forms, does every run split the word's contexts by grammatical
function, and do different runs split them the same way? Uses ALL anchor occurrences (hidden-state
captures from capture_hidden.py; routing recomputed from H, W, b on CPU), not only the pre-registered sample.

Function of an occurrence = UPOS:deprel (coarse). A form qualifies if it has >= 2 functions with >= MIN_OCC
occurrences each among anchor words; occurrences of other functions are dropped.
Per form, layer, model:
  sep      : separation of co-routing C between same-function pairs and different-function pairs
             (mean difference / sd of C)  -> does this run use the distinction to divide labour
  fkernel  : function-level kernel = mean C per (function_a, function_b) cell
Cross-model (init / order / floor groups):
  T_fun    : corr of function-level kernels (do runs agree on which functions go together / apart)
  T_resid  : corr of within-cell residuals (agreement beyond the function distinction)
  T_all    : corr of the full within-form-centred kernel
Usage: e170_ambiguous_words.py TOKENS [MIN_OCC] [LAYERS]   -> results/e170/ambiguous_<TOKENS>.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
AN = Path.home() / "mechpop_cache/e167_analysis"
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3999793152
MIN_OCC = int(sys.argv[2]) if len(sys.argv) > 2 else 15
LAYERS = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [2, 5, 8, 11]
TOPK = 8
MAX_OCC = 300  # cap per function to bound pair counts
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
groups = {"init": [("I0D0", "I1D0"), ("I0D0", "I2D0"), ("I0D0", "I3D0"), ("I1D0", "I2D0"), ("I1D0", "I3D0"), ("I2D0", "I3D0")],
          "order": [("I0D0", "I0D1"), ("I1D0", "I1D1")], "floor": [("I0D0@0", "I1D0@0")]}
runs = ["I0D0", "I1D0", "I2D0", "I3D0", "I0D1", "I1D1", "I0D0@0", "I1D0@0"]


def load(r):
    run, t = (r.split("@")[0], 0) if "@" in r else (r, tok)
    return np.load(AN / f"hidden/{run}__ckpt_{t}.npz")


Z = {r: load(r) for r in runs}
word_idx = Z["I0D0"]["word_idx"]; n_anchor = int(Z["I0D0"]["n_anchor"])
# routing top-k for every anchor word, once per model and layer (reads each H array once)
S = {r: {} for r in runs}
for r in runs:
    for l in LAYERS:
        H = Z[r][f"H{l}"][:n_anchor].astype(np.float32)
        sc = H @ Z[r][f"W{l}"].T + Z[r][f"b{l}"]
        S[r][l] = np.argpartition(-sc, TOPK, axis=1)[:, :TOPK].astype(np.int16)
        del H, sc
    print("routed", r, flush=True)
E = Z["I0D0"]["W0"].shape[0]

forms = defaultdict(list)
for row in range(n_anchor):
    a = ann[int(word_idx[row])]
    forms[a["form"].lower()].append((row, f"{a['upos']}:{a['deprel']}"))
rng = np.random.default_rng(170)
selected = {}
for f, occ in forms.items():
    cnt = Counter(fn for _, fn in occ)
    keep = [fn for fn, c in cnt.items() if c >= MIN_OCC]
    if len(keep) < 2:
        continue
    rows, labs = [], []
    for fn in keep:
        rr = [r for r, x in occ if x == fn]
        if len(rr) > MAX_OCC:
            rr = sorted(rng.choice(rr, MAX_OCC, replace=False).tolist())
        rows += rr; labs += [fn] * len(rr)
    selected[f] = (np.array(rows), np.array(labs))
print(len(selected), "multi-function forms;", sum(len(v[0]) for v in selected.values()), "occurrences", flush=True)


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float("nan")


out = {"tokens": tok, "min_occ": MIN_OCC, "layers": LAYERS, "forms": {}}
for f, (rows, labs) in sorted(selected.items(), key=lambda kv: -len(kv[1][0])):
    n = len(rows); ii, jj = np.triu_indices(n, 1)
    same = labs[ii] == labs[jj]
    ulab = sorted(set(labs)); lid = np.array([ulab.index(x) for x in labs])
    cell = np.minimum(lid[ii], lid[jj]) * len(ulab) + np.maximum(lid[ii], lid[jj])
    ncell = np.maximum(np.bincount(cell), 1)
    rec = {"n": int(n), "functions": {u: int((labs == u).sum()) for u in ulab}, "layers": {}}
    for l in LAYERS:
        per = {}
        for r in runs:
            M = np.zeros((n, E), np.float32); np.put_along_axis(M, S[r][l][rows].astype(np.int64), 1.0, 1)
            C = (M[ii] * M[jj]).sum(1) / TOPK
            Cc = C - C.mean()
            fk = np.bincount(cell, Cc) / ncell
            per[r] = {"C": Cc, "fcell": fk[cell], "sep": float((C[same].mean() - C[~same].mean()) / (C.std() + 1e-9))}
        row = {"sep": {r: per[r]["sep"] for r in runs}}
        for g, pairs in groups.items():
            row[f"T_all_{g}"] = float(np.mean([corr(per[a]["C"], per[b]["C"]) for a, b in pairs]))
            row[f"T_fun_{g}"] = float(np.mean([corr(per[a]["fcell"], per[b]["fcell"]) for a, b in pairs]))
            row[f"T_resid_{g}"] = float(np.mean([corr(per[a]["C"] - per[a]["fcell"], per[b]["C"] - per[b]["fcell"]) for a, b in pairs]))
        rec["layers"][l] = row
    out["forms"][f] = rec
    l = LAYERS[-1]; row = rec["layers"][l]
    seps = [row["sep"][r] for r in runs[:6]]
    print(f"{f:10s} n={n:4d} fn={len(ulab)} | L{l}: sep trained {np.mean(seps):.2f} [{min(seps):.2f},{max(seps):.2f}] untrained {row['sep']['I0D0@0']:.2f} | T_fun init {row['T_fun_init']:.2f} order {row['T_fun_order']:.2f} floor {row['T_fun_floor']:.2f} | T_resid init {row['T_resid_init']:.2f} order {row['T_resid_order']:.2f} | T_all init {row['T_all_init']:.2f} order {row['T_all_order']:.2f}", flush=True)
(WB / "results/e170").mkdir(exist_ok=True)
(WB / f"results/e170/ambiguous_{tok}.json").write_text(json.dumps(out))
print("saved")
