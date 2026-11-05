#!/usr/bin/env python3
"""E174 granularity 3: within-cell permutation null for the per-token causal-role readout (CPU only).

Readout = token_roles.py compare "matched": experts' per-token dNLL vectors; Hungarian on one half of
the windows, mean matched correlation on the other half, both directions averaged.
Null: B's token axis permuted inside pools x half (pools from automatic spaCy tags, e174_tag_windows.py):
  U  = (upos, word-initial)
  F  = (upos, word-initial, prev_upos, next_upos, dep), cells < 3 tokens fall back to their U pool
  LU = (token id, upos)
Row statistics of B within a half are permutation-invariant, so B is standardised once per half.
Jackknife: 16 window blocks (8 per half), excess recomputed with N_JK_PERM permutations each.

Usage: e174_token_null.py TOKENS LAYERS A:B [A:B ...]  -> results/e174/token_null_<TOKENS>.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

WB = Path(__file__).resolve().parents[1]
TR = Path.home() / "mechpop_cache/e167_analysis/token_roles"
TAGS = Path.home() / "mechpop_cache/e174/window_tags.npz"
tok = sys.argv[1]
layers = [int(x) for x in sys.argv[2].split(",")]
specs = [s.split(":") for s in sys.argv[3:]]
N_PERM, N_JK_PERM, N_BLK, MIN_FINE = 32, 4, 16, 3

T = np.load(TAGS)
W, S = T["upos"].shape
ids = T["ids"][:, :S]
half = (np.arange(W) >= W // 2)[:, None].repeat(S, 1)  # False = first half
wblk = (np.arange(W)[:, None] // (W // N_BLK)).repeat(S, 1)


def enc(*cols):
    k = np.stack([c.reshape(-1).astype(np.int64) for c in cols], 1)
    return np.unique(k, axis=0, return_inverse=True)[1].reshape(-1)


poolU = enc(T["upos"], T["init"])
fine = enc(T["upos"], T["init"], T["prev"], T["nxt"], T["dep"])
fcnt = np.bincount(fine)[fine]
poolF = enc(np.where(fcnt >= MIN_FINE, fine, -1 - poolU), np.zeros_like(fine))
poolLU = enc(ids, T["upos"])
POOLS = {"U": poolU, "F": poolF, "LU": poolLU}
hflat = half.reshape(-1)
info = {}
for k, p in POOLS.items():
    q = enc(p, hflat)
    sz = np.bincount(q)[q]
    info[k] = {"n_pools": int(q.max() + 1), "tokens_fixed_frac": float((sz < 2).mean())}
info["F"]["fine_cell_coverage"] = float((fcnt >= MIN_FINE).mean())
print(info, flush=True)


def draw_perm(pool, rng):
    n = len(pool)
    perm = np.empty(n, np.int64)
    base = np.lexsort((np.arange(n), pool))
    perm[base] = np.lexsort((rng.random(n), pool))
    return perm


rng = np.random.default_rng(1741)
PERMS = {k: [draw_perm(enc(p, hflat), rng) for _ in range(N_PERM)] for k, p in POOLS.items()}


def zrows(X):
    X = X - X.mean(1, keepdims=True)
    return X / (np.sqrt((X * X).sum(1, keepdims=True)) + 1e-30)


def matched(DA, DB, cols_fit, cols_ev):
    """DA, DB: E x (W*S). Hungarian on fit columns, mean corr on eval columns."""
    za_f, zb_f = zrows(DA[:, cols_fit]), zrows(DB[:, cols_fit])
    za_e, zb_e = zrows(DA[:, cols_ev]), zrows(DB[:, cols_ev])
    ri, ci = linear_sum_assignment(-(za_f @ zb_f.T))
    return float(((za_e[ri] * zb_e[ci]).sum(1)).mean())


def readout(DA, DB, keep=None):
    h = hflat if keep is None else hflat[keep]
    if keep is not None:
        DA, DB = DA[:, keep], DB[:, keep]
    c1, c2 = np.flatnonzero(~h), np.flatnonzero(h)
    return 0.5 * (matched(DA, DB, c1, c2) + matched(DA, DB, c2, c1))


out = {"tokens": tok, "layers": layers, "n_perm": N_PERM, "pool_info": info, "results": []}
for a, b in specs:
    A, B = np.load(TR / f"{a}__ckpt_{tok}.npz"), np.load(TR / f"{b}__ckpt_{tok}.npz")
    rec = {"A": a, "B": b, "layers": []}
    for l in layers:
        DA = A[f"D{l}"].astype(np.float32).reshape(A[f"D{l}"].shape[0], -1)
        DB = B[f"D{l}"].astype(np.float32).reshape(B[f"D{l}"].shape[0], -1)
        real = readout(DA, DB)
        row = {"layer": l, "real": real, "pools": {}}
        for pname, perms in PERMS.items():
            nv = np.array([readout(DA, DB[:, p]) for p in perms])
            jk = []
            for k in range(N_BLK):
                keep = wblk.reshape(-1) != k
                r_k = readout(DA, DB, keep)
                n_k = np.mean([readout(DA, DB[:, p], keep) for p in perms[:N_JK_PERM]])
                jk.append(r_k - n_k)
            jk = np.array(jk)
            se = float(np.sqrt((N_BLK - 1) / N_BLK * ((jk - jk.mean()) ** 2).sum()))
            row["pools"][pname] = {"null_mean": float(nv.mean()), "null_lo": float(np.percentile(nv, 2.5)),
                                   "null_hi": float(np.percentile(nv, 97.5)), "excess": real - float(nv.mean()),
                                   "excess_jk_se": se, "excess_frac": (real - float(nv.mean())) / real,
                                   "null_draws": nv.round(5).tolist()}
        rec["layers"].append(row)
        print(tok, a, b, l, f"real {real:.3f}", {k: (round(v['null_mean'], 3), round(v['excess'], 3), round(v['excess_jk_se'], 3)) for k, v in row["pools"].items()}, flush=True)
    out["results"].append(rec)
(WB / "results/e174").mkdir(exist_ok=True, parents=True)
(WB / f"results/e174/token_null_{tok}.json").write_text(json.dumps(out))
print("saved", flush=True)
