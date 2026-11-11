"""E187 混杂审计 (gain attribution): how many post-attention RMSNorm gain entries are ~0, and how much of the
effective router of layer l (W_l diag g_l) sits on dims where the partner layer's gain is tiny (x_hat poorly
recoverable from fp16 h there).  Writes results/e187/gaindiag.json."""
import json, os
import numpy as np
C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
sm = np.load(f"{C}/w_instruct/small.npz"); W = sm["gate"].astype(np.float64); g = sm["post_ln"].astype(np.float64)
out = {"n_small_1e-3": [int((np.abs(g[l]) < 1e-3).sum()) for l in range(48)],
       "n_small_1e-2": [int((np.abs(g[l]) < 1e-2).sum()) for l in range(48)], "pairs": []}
for lag in (12, 24, 1):
    for l in range(6, 42 - lag + 1):
        m = l + lag
        if m > 41:
            continue
        We = W[l] * g[l]; Wc = We - We.mean(0)
        e = (Wc ** 2).sum(0); bad = np.abs(g[m]) < 1e-3
        Wm = W[m] * g[m]; Wmc = Wm - Wm.mean(0); e2 = (Wmc ** 2).sum(0); bad2 = np.abs(g[l]) < 1e-3
        out["pairs"].append(dict(l=l, m=m, lag=lag, energy_l_on_tiny_gm=float(e[bad].sum() / e.sum()),
                                 energy_m_on_tiny_gl=float(e2[bad2].sum() / e2.sum()), gain_ratio_med=float(np.median(g[l] / g[m]))))
json.dump(out, open(f"{RES}/gaindiag.json", "w"), indent=0)
print(out["n_small_1e-3"]); print(max(p["energy_l_on_tiny_gm"] for p in out["pairs"]), max(p["energy_m_on_tiny_gl"] for p in out["pairs"]))
