"""Readout for probe_order: per (task, n, gap) candidate-renormalised P(correct), argmax accuracy.
Also for recency with n >= 2: share of candidate mass on the *first* occurrence (primacy) vs last.
usage: analyze_probe_order.py TAG [TAG ...]
"""
import json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(tag):
    return [json.loads(l) for l in open(f"{ROOT}/results/probe_order/{tag}.jsonl")]


def summarize(rows):
    out = {}
    for r in rows:
        lp = np.array(r["lp_cands"]); p = np.exp(lp - lp.max()); p /= p.sum()
        key = (r["task"], r["n"], r["gap"])
        out.setdefault(key, []).append((p[r["correct"]], float(np.argmax(p) == r["correct"]), p[0], lp[r["correct"]]))
    return {k: np.array(v) for k, v in out.items()}


tags = sys.argv[1:]
S = {t: summarize(load(t)) for t in tags if os.path.exists(f"{ROOT}/results/probe_order/{t}.jsonl")}
for task in ("reassign", "keyed"):
    print(f"== {task}: candidate-renormalised P(correct) [chance = 1/n]  (acc)")
    keys = sorted({k for s in S.values() for k in s if k[0] == task}, key=lambda k: (k[1], k[2]))
    print(f"{'n':>2s} {'gap':>4s} " + " ".join(f"{t:>14s}" for t in S))
    for k in keys:
        cells = []
        for t, s in S.items():
            v = s.get(k)
            cells.append(f"{v[:, 0].mean():.2f} ({v[:, 1].mean():.2f})" if v is not None else "-")
        print(f"{k[1]:>2d} {k[2]:>4d} " + " ".join(f"{c:>14s}" for c in cells))
print("== reassign n>=2: mass on FIRST occurrence (primacy) — pooled over gaps")
for t, s in S.items():
    row = []
    for n in (2, 4, 8):
        v = np.concatenate([s[k] for k in s if k[0] == "reassign" and k[1] == n])
        row.append(f"n={n}: last {v[:, 0].mean():.2f} first {v[:, 2].mean():.2f}")
    print(f"{t:>10s}  " + " | ".join(row))
