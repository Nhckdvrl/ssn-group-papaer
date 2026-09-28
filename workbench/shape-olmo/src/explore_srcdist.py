"""Delta for repeated-4-gram targets by distance to the most recent earlier occurrence of that 4-gram.
T = SWA(4096)+full, H = GDN+full: if T's reuse advantage comes from its SWA layers, it should shrink
when the source is > 4096 tokens back. usage: explore_srcdist.py TAG_T TAG_H"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_p0 import boot, fmt, DOMS, ROOT

N = 4
tt, th = sys.argv[1], sys.argv[2]
Ds, dist = [], []
for d in DOMS:
    ids = np.load(f"{ROOT}/data/pack_{d}.npz")["ids"]
    D = np.load(f"{ROOT}/scores/{tt}/{d}.npy") - np.load(f"{ROOT}/scores/{th}/{d}.npy")
    S, L = ids.shape
    dd = np.full((S, L - 1), -1, np.int32)
    for s in range(S):
        x = ids[s]; last = {}
        for t in range(N - 1, L):
            key = tuple(x[t - N + 1:t + 1])
            if t >= 1 and key in last:
                dd[s, t - 1] = t - last[key]      # target index t -> nll column t-1
            last[key] = t
    Ds.append(D); dist.append(dd)
D = np.concatenate(Ds); dd = np.concatenate(dist)
print(f"repeated-{N}-gram targets: {(dd > 0).sum()} of {dd.size}")
for lo, hi in ((1, 64), (64, 512), (512, 2048), (2048, 4096), (4096, 6144), (6144, 8192)):
    print(f"source distance [{lo:5d},{hi:5d})  Delta {fmt(boot(D, (dd >= lo) & (dd < hi)))}")
print(f"not a repeated-{N}-gram               Delta {fmt(boot(D, dd < 0))}")
