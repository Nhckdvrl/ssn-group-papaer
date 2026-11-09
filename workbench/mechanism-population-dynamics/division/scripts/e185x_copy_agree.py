"""E185 residual follow-up: do Qwen3-30B-A3B's weight-copy layers (l, l+12) route the same tokens to the 'same'
(gate-row-matched) experts?  Experts of layer m are matched to layer l by Hungarian assignment on |cos| of router rows.
Readout: per-token top-1 agreement under the matching, and top-8 set overlap, for the trained router on the E184 English
store (~85k tokens), vs. the same for lags 11 and 13 (non-copies) and vs chance (matched-load expectation).
Writes results/e185/residual_qwen3_copy_agree.json"""
import json, os
import numpy as np
from scipy.optimize import linear_sum_assignment

W = np.load("/home/xiang/mechpop_cache/e179/qwen3/gateW.npy").astype(np.float64)
W /= np.linalg.norm(W, axis=2, keepdims=True)
A = np.load("/home/xiang/mechpop_cache/e184/qwen3/topk.npy", mmap_mode="r")
L, E = 48, 128
T = {l: np.asarray(A[l, :, 0, :]).astype(np.int64) for l in range(L)}


def agree(l, m):
    C = np.abs(W[l] @ W[m].T)
    r, c = linear_sum_assignment(-C)
    perm = np.empty(E, np.int64); perm[c] = r                     # expert of m -> matched expert of l
    t1l, t1m = T[l][:, 0], perm[T[m][:, 0]]
    pl = np.bincount(t1l, minlength=E) / t1l.size; pm = np.bincount(t1m, minlength=E) / t1m.size
    sl = np.zeros((t1l.size, E), bool); sl[np.arange(t1l.size)[:, None], T[l]] = True
    ov = sl[np.arange(t1l.size)[:, None], perm[T[m]]].mean()
    return float((t1l == t1m).mean()), float((pl * pm).sum()), float(ov), float(C[r, c].mean())


out = {}
for lag in (12, 11, 13, 24, 1):
    rows = []
    for l in range(0, L - lag):
        a, ch, ov, cs = agree(l, l + lag)
        rows.append(dict(l=l, top1=a, chance=ch, top8_overlap=ov, matched_cos=cs))
    out[str(lag)] = rows
    inblk = [r for r in rows if 6 <= r["l"] and r["l"] + lag <= 41]
    print(lag, "in-block mean top1 %.3f chance %.3f top8 %.3f cos %.2f" % tuple(
        np.mean([r[k] for r in inblk]) for k in ("top1", "chance", "top8_overlap", "matched_cos")))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e185",
                                 "residual_qwen3_copy_agree.json"), "w"), indent=1)
for r in out["12"]:
    print(r["l"], "->", r["l"] + 12, "top1 %.3f (chance %.3f) top8 %.3f" % (r["top1"], r["chance"], r["top8_overlap"]))
