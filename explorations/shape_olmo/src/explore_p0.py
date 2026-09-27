"""Exploratory cuts of P0 scores (no new model calls). usage: explore_p0.py TAG_T TAG_H"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tag import FAMILIES, CONTENT, FUNCTION, PROSE
from analyze_p0 import boot, fmt, DOMS, ROOT

tt, th = sys.argv[1], sys.argv[2]
L = {d: (np.load(f"{ROOT}/scores/{tt}/{d}.npy"), np.load(f"{ROOT}/scores/{th}/{d}.npy"),
         np.load(f"{ROOT}/data/tags_{d}.npz")) for d in DOMS}

print("== 1. reuse split per domain: Delta on rep=0 | rep=1 | rep>=2 | rep>=8  (share of tokens with rep>=2)")
for d, (a, b, t) in L.items():
    D = a - b; r = t["rep"]
    cells = [boot(D, r == 0), boot(D, r == 1), boot(D, r >= 2), boot(D, r >= 8)]
    print(f"{d:10s} " + " | ".join(f"{c[0]:+.4f} [{c[1]:+.3f},{c[2]:+.3f}]" for c in cells) + f"  (rep>=2 share {(r >= 2).mean():.2f})")

print("== 2. prose content vs function, overall and within rep=0 / rep>=2")
pd_ = [d for d in DOMS if d in PROSE]
cat = lambda xs: np.concatenate(xs, 0)
D = cat([L[d][0] - L[d][1] for d in pd_]); p1 = cat([L[d][2]["pos1"] for d in pd_]); r = cat([L[d][2]["rep"] for d in pd_])
fid = lambda S: [FAMILIES.index(f) for f in S]
con, fun = np.isin(p1, fid(CONTENT)), np.isin(p1, fid(FUNCTION))
for name, m in (("all", np.ones_like(r, bool)), ("rep=0", r == 0), ("rep=1", r == 1), ("rep>=2", r >= 2)):
    c, f = boot(D, con & m), boot(D, fun & m)
    print(f"{name:7s} content {fmt(c)} | function {fmt(f)}")
print("   share of function tokens with rep>=1:", round(float((r[fun] >= 1).mean()), 3),
      " content:", round(float((r[con] >= 1).mean()), 3))

print("== 3. Delta by difficulty (bins of mean NLL of the two models), pooled all domains")
A = cat([L[d][0] for d in DOMS]); B = cat([L[d][1] for d in DOMS]); R = cat([L[d][2]["rep"] for d in DOMS])
M = (A + B) / 2
edges = [0, 0.01, 0.1, 0.5, 1, 2, 4, 8, 100]
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (M >= lo) & (M < hi)
    m0 = m & (R == 0); m2 = m & (R >= 2)
    print(f"meanNLL [{lo:5.2f},{hi:5.2f}) share {m.mean():.3f}  Delta {boot(A - B, m)[0]:+.4f} | rep=0 {boot(A - B, m0)[0]:+.4f} (n={m0.sum()}) | rep>=2 {boot(A - B, m2)[0]:+.4f} (n={m2.sum()})")
