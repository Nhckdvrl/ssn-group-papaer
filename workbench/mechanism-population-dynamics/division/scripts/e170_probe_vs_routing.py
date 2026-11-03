#!/usr/bin/env python3
"""E170 stage 2: "the representation has it" vs "the division of labour uses it".

For every multi-function form (same selection as e170_ambiguous_words.py), layer and model:
  dec_h    : balanced accuracy (5-fold CV, logistic regression) of decoding the function label
             (UPOS:deprel) from the 768-d hidden state at the MoE input  -> is the distinction linearly present
  dec_r    : same from the routing decision (64-d one-hot of the top-8 experts) -> does the division use it
  dec_l    : same from the 64 router logits (what the router could read out)
All minus chance (1 / n_functions). usage = dec_r / dec_h.
Cross-seed: agreement of the per-form usage profile between runs; forms with high dec_h but low dec_r in
every run ("present but not divided"); forms where runs disagree on usage.

Usage: e170_probe_vs_routing.py TOKENS [LAYERS]   -> results/e170/probe_vs_routing_<TOKENS>.json
"""
import json
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
WB = Path(__file__).resolve().parents[1]
AN = Path.home() / "mechpop_cache/e167_analysis"
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3999793152
LAYERS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [2, 5, 8, 11]
TOPK, MIN_OCC, MAX_OCC = 8, 15, 300
runs = ["I0D0", "I1D0", "I2D0", "I3D0", "I0D1", "I1D1", "I0D0@0", "I1D0@0"]
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())


def load(r):
    run, t = (r.split("@")[0], 0) if "@" in r else (r, tok)
    return np.load(AN / f"hidden/{run}__ckpt_{t}.npz")


Z = {r: load(r) for r in runs}
word_idx = Z["I0D0"]["word_idx"]; n_anchor = int(Z["I0D0"]["n_anchor"])
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
print(len(selected), "forms", flush=True)


def dec(X, y):
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced"))
    pred = cross_val_predict(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0))
    return float(balanced_accuracy_score(y, pred))


out = {"tokens": tok, "layers": LAYERS, "forms": {f: {"n": int(len(v[0])), "functions": dict(Counter(v[1].tolist())), "layers": {}} for f, v in selected.items()}}
for l in LAYERS:
    cache = {}
    for r in runs:
        H = Z[r][f"H{l}"][:n_anchor].astype(np.float32); W, b = Z[r][f"W{l}"], Z[r][f"b{l}"]
        cache[r] = (H, W, b)
    for f, (rows, labs) in selected.items():
        chance = 1.0 / len(set(labs))
        rec = {}
        for r in runs:
            H, W, b = cache[r]
            X = H[rows]
            logits = X @ W.T + b
            S = np.argpartition(-logits, TOPK, axis=1)[:, :TOPK]
            M = np.zeros((len(rows), W.shape[0]), np.float32); np.put_along_axis(M, S, 1.0, 1)
            rec[r] = {"dec_h": dec(X, labs) - chance, "dec_r": dec(M, labs) - chance, "dec_l": dec(logits, labs) - chance}
        out["forms"][f]["layers"][l] = rec
    del cache
    # summary for this layer
    tr = runs[:6]
    dh = np.array([[out["forms"][f]["layers"][l][r]["dec_h"] for r in tr] for f in selected])
    dr = np.array([[out["forms"][f]["layers"][l][r]["dec_r"] for r in tr] for f in selected])
    dh0 = np.array([out["forms"][f]["layers"][l]["I0D0@0"]["dec_h"] for f in selected]); dr0 = np.array([out["forms"][f]["layers"][l]["I0D0@0"]["dec_r"] for f in selected])
    usage = dr / np.maximum(dh, 1e-3)
    init = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]; order = [(0, 4), (1, 5)]
    c = lambda A, i, j: np.corrcoef(A[:, i], A[:, j])[0, 1]
    print(f"L{l:2d}: dec_h trained median {np.median(dh.mean(1)):.2f} (untrained {np.median(dh0):.2f}) | dec_r trained {np.median(dr.mean(1)):.2f} (untrained {np.median(dr0):.2f}) | usage median {np.median(usage.mean(1)):.2f} | cross-run corr of dec_r profiles: init {np.mean([c(dr,i,j) for i,j in init]):.2f} order {np.mean([c(dr,i,j) for i,j in order]):.2f}; of usage: init {np.mean([c(usage,i,j) for i,j in init]):.2f} order {np.mean([c(usage,i,j) for i,j in order]):.2f}", flush=True)
    (WB / "results/e170").mkdir(exist_ok=True)
    (WB / f"results/e170/probe_vs_routing_{tok}.json").write_text(json.dumps(out))
# final per-form table at the last layer
l = LAYERS[-1]; tr = runs[:6]
print(f"\nPer form at L{l}: n | dec_h mean[min,max] | dec_r mean[min,max] | usage | untrained dec_h/dec_r")
for f in sorted(selected, key=lambda f: -len(selected[f][0])):
    R = out["forms"][f]["layers"][l]
    dh = [R[r]["dec_h"] for r in tr]; dr = [R[r]["dec_r"] for r in tr]
    print(f"{f:9s} {len(selected[f][0]):4d} | {np.mean(dh):.2f} [{min(dh):.2f},{max(dh):.2f}] | {np.mean(dr):.2f} [{min(dr):.2f},{max(dr):.2f}] | {np.mean(dr)/max(np.mean(dh),1e-3):.2f} | {R['I0D0@0']['dec_h']:.2f}/{R['I0D0@0']['dec_r']:.2f}")
print("saved")
