"""Analyse attn_probe output: how is query->label-token attention organised (position vs similarity)?
usage: analyze_attn.py NPZ"""
import sys
import numpy as np
import statsmodels.api as sm

z = np.load(sys.argv[1])
A, cond, sim, isB = z["A"], z["cond"], z["sim"], z["isB"]          # A: N x L x H x T
N, L, H, T = A.shape
fmt = np.array([c.split(":")[0] for c in cond]); pat = np.array([c.split(":")[1] for c in cond])
pos = np.tile(np.arange(T) / (T - 1), (N, 1))
tot = A.sum(-1)                                                      # N x L x H total attention to label tokens
print("mean total attention from query to all label tokens, by format (max over heads per layer, averaged):")
for f in ("const", "irr5", "rule5"):
    m = fmt == f
    print(f"  {f:6s} top-20 heads mean label-attn {np.sort(tot[m].mean(0).ravel())[-20:].mean():.3f}")

# per head: standardized regression of attention share on position and similarity (within row)
def head_stats(f):
    m = (fmt == f) & (pat == "allA")
    S = A[m] / (A[m].sum(-1, keepdims=True) + 1e-9)                 # share among label tokens
    P = pos[m]; Sm = sim[m]
    Sm = (Sm - np.nanmean(Sm, 1, keepdims=True)) if not np.all(np.isnan(Sm)) else np.zeros_like(P)
    Pc = P - P.mean(1, keepdims=True)
    out = np.zeros((L, H, 2))
    for l in range(L):
        for h in range(H):
            y = S[:, l, h, :]; yc = (y - y.mean(1, keepdims=True)).ravel()
            X = np.c_[Pc.ravel(), np.nan_to_num(Sm).ravel()]
            b, *_ = np.linalg.lstsq(X, yc, rcond=None)
            out[l, h] = b
    return out


W = {f: tot[(fmt == f) & (pat == "allA")].mean(0) for f in ("const", "irr5", "rule5")}
st = {f: head_stats(f) for f in ("const", "irr5", "rule5")}
for f in ("const", "irr5", "rule5"):
    w = W[f]; b = st[f]
    top = np.argsort(w.ravel())[-30:]
    bp = b[..., 0].ravel()[top]; bs = b[..., 1].ravel()[top]
    wt = w.ravel()[top]
    print(f"\n[{f}] top-30 label-attending heads: weighted mean slope on position {np.average(bp, weights=wt):+.4f}, "
          f"on similarity (per matching attr) {np.average(bs, weights=wt):+.4f}")
    for j in top[-8:][::-1]:
        l, h = divmod(j, H)
        print(f"   L{l:02d}H{h:02d} attn {w[l, h]:.3f}  pos-slope {b[l, h, 0]:+.3f}  sim-slope {b[l, h, 1]:+.4f}")

# attention mass on B demos: suffix_4 vs disp_4 (same B count)
print("\nshare of label-attention on B demos (top-30 heads of each format):")
for f in ("const", "irr5", "rule5"):
    top = np.argsort(W[f].ravel())[-30:]
    for p in ("suffix_4", "disp_4", "single_1", "single_16"):
        m = (fmt == f) & (pat == p)
        if m.sum() == 0:
            continue
        S = A[m] / (A[m].sum(-1, keepdims=True) + 1e-9)
        Sf = S.reshape(m.sum(), L * H, T)[:, top, :]
        bmask = isB[m][:, None, :]
        share = (Sf * bmask).sum(-1).mean()
        print(f"  {f:6s} {p:10s} B-share {share:.3f}  (uniform would be {isB[m].mean():.3f})")
