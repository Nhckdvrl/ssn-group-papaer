"""Within-class loss change by continuation ambiguity A (IN targets only).
A = number of distinct tokens that followed earlier occurrences of the current context token x_t
(prefix positions < t); A = 0 means x_t never occurred before. usage: explore_ambiguity.py PAIRS..."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_p0 import boot, fmt, ROOT

DOMS = ["pg19", "wikipedia", "python"]


def amb(ids):
    S, L = ids.shape
    A = np.zeros((S, L - 1), np.int32)
    for s in range(S):
        x = ids[s]; foll = {}
        for t in range(L - 1):                 # target is x[t+1], column t
            c = x[t]
            A[s, t] = len(foll.get(c, ()))
            if t >= 1:
                foll.setdefault(x[t - 1], set()).add(c)
    return A


def within(tag, d, cin):
    nll = np.load(f"{ROOT}/scores/{tag}/{d}.npy")
    lp = np.where(cin, np.load(f"{ROOT}/scores/{tag}/{d}_lpin.npy"), np.load(f"{ROOT}/scores/{tag}/{d}_lpout.npy"))
    return nll + lp            # nll - gate, gate = -lp


A = {}; C = {}
for d in DOMS:
    A[d] = amb(np.load(f"{ROOT}/data/pack_{d}.npz")["ids"])
    C[d] = np.load(f"{ROOT}/data/tags_{d}.npz")["rep"] >= 1
bins = [(0, 0), (1, 1), (2, 2), (3, 4), (5, 9), (10, 10 ** 6)]
for pair in sys.argv[1:]:
    a, b = pair.split(",")
    W = np.concatenate([within(a, d, C[d]) - within(b, d, C[d]) for d in DOMS])
    Aa = np.concatenate([A[d] for d in DOMS]); cin = np.concatenate([C[d] for d in DOMS])
    print(f"== within-class Δ ({a} - {b}) on IN targets by ambiguity A")
    for lo, hi in bins:
        m = cin & (Aa >= lo) & (Aa <= hi)
        print(f"  A in [{lo},{hi if hi < 10**6 else 'inf'}]  share {m.sum() / cin.sum():.3f}  {fmt(boot(W, m))}")
