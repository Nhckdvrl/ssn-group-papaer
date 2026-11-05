#!/usr/bin/env python3
"""E174 granularity 2: within-UD-cell permutation null for T_D (CPU only).

For a run pair (A, B): permute B's anchors inside pools (word type x UD cell), so B keeps its
cell -> expert distribution exactly but loses every other cross-run correspondence. Because the
pre-registered pairs are *all* pairs of anchors within each word type, (pi i, pi j) is again a
stored pair, so D_B = C_B - B_B (N1 expectation included) is permuted exactly.

Pools: U = (type, upos); F = (type, upos, prev_upos, next_upos, deprel) with fine cells < 3 anchors
pooled back into a per-(type, upos) remainder pool; T = (type) negative control; I = identity.

Usage: e174_td_null.py TOKENS [N_PERM]  ->  results/e174/td_null_<TOKENS>.json
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
tok = int(float(sys.argv[1]))
N_PERM = int(sys.argv[2]) if len(sys.argv) > 2 else 64
N_BLOCK = 20
MIN_FINE = 3

P = np.load(CAP / "pairs.npz")
pi, pj, ptype = P["i"].astype(np.int64), P["j"].astype(np.int64), P["type"].astype(np.int64)
nT = int(ptype.max()) + 1
N = len(P["anchor_word"])
_, wtype = np.unique(P["anchor_type"], return_inverse=True)
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
A = [ann[int(w)] for w in P["anchor_word"]]
assert (pi < pj).all()
# check: pair type == anchor type
assert (wtype[pi] == wtype[pj]).all()


def enc(keys):
    return np.unique(np.array(keys), return_inverse=True)[1]


upos = [a["upos"] for a in A]
fine = [f'{a["upos"]}|{a["prev_upos"]}|{a["next_upos"]}|{a["deprel"]}' for a in A]
# sanity: UD upos matches pairs.npz anchor_upos
agree = np.mean([u == v for u, v in zip(upos, P["anchor_upos"])])
print(f"UD upos == anchor_upos: {agree:.4f}", flush=True)

poolU = enc([f"{t}#{u}" for t, u in zip(wtype, upos)])
fkey = [f"{t}#{f}" for t, f in zip(wtype, fine)]
fid = enc(fkey)
fcnt = np.bincount(fid)[fid]
poolF = enc([fk if c >= MIN_FINE else f"{t}#{u}#REST" for fk, c, t, u in zip(fkey, fcnt, wtype, upos)])
fine_cov = float((fcnt >= MIN_FINE).mean())
poolT = wtype.copy()
POOLS = {"U": poolU, "F": poolF, "T": poolT}

key_sorted_idx = np.argsort(pi * N + pj)
key_sorted = (pi * N + pj)[key_sorted_idx]


def pair_map(perm):
    a, b = perm[pi], perm[pj]
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    k = lo * N + hi
    pos = np.searchsorted(key_sorted, k)
    assert (key_sorted[pos] == k).all()
    return key_sorted_idx[pos]


def draw_perm(pool, rng):
    n = len(pool)
    perm = np.empty(n, np.int64)
    base = np.lexsort((np.arange(n), pool))
    perm[base] = np.lexsort((rng.random(n), pool))
    assert (pool[perm] == pool).all()
    return perm


rng = np.random.default_rng(174)
maps = {}
pool_info = {}
for name, pool in POOLS.items():
    sz = np.bincount(pool)[pool]
    movable = sz >= 2
    pool_info[name] = {"n_pools": int(pool.max() + 1), "anchors_fixed_frac": float((~movable).mean()),
                       "pairs_both_fixed_frac": float((~movable[pi] & ~movable[pj]).mean())}
    maps[name] = [pair_map(draw_perm(pool, rng)) for _ in range(N_PERM)]
    print(name, pool_info[name], flush=True)
pool_info["F"]["fine_cell_coverage"] = fine_cov
movable_mask = {k: ((np.bincount(p)[p] >= 2)[pi] & (np.bincount(p)[p] >= 2)[pj]) for k, p in POOLS.items()}

# type blocks for jackknife
tblock = np.random.default_rng(1740).permutation(nT) % N_BLOCK
pblock = tblock[ptype]


def cw(x):
    s = np.bincount(ptype, x, nT)
    c = np.bincount(ptype, None, nT)
    return x - (s / np.maximum(c, 1))[ptype]


def load(run):
    Z = np.load(CAP / f"{run}__ckpt_{tok}.npz")
    return np.stack([cw(Z[f"C{l}"].astype(np.float64) - Z[f"B{l}"].astype(np.float64)) for l in range(12)])


d0 = [f"I{i}D0" for i in range(6)]
groups = {"rerun": [("I4D0", "I4D0R")],
          "order": [("I0D0", "I0D1"), ("I1D0", "I1D1")],
          "init": list(itertools.combinations(d0, 2))}
runs = sorted({r for g in groups.values() for p in g for r in p})
M = {r: load(r) for r in runs}
print("loaded", runs, flush=True)

LAY = {"deep": list(range(6, 12)), "shallow": list(range(6)), "L11": [11]}


def blocksum(x):
    return np.bincount(pblock, x, N_BLOCK)


out = {"tokens": tok, "n_perm": N_PERM, "n_pairs": int(len(pi)), "pool_info": pool_info, "results": []}
for g, pairs in groups.items():
    for a, b in pairs:
        XA, XB = M[a], M[b]
        rec = {"group": g, "A": a, "B": b, "pools": {}}
        for pname in ("U", "F", "T"):
            for variant in ("all", "movable"):
                mask = np.ones(len(pi), bool) if variant == "all" else movable_mask[pname]
                per_layer = []
                # per-block sums for jackknife: ab_real, ab_null_mean, aa, bb  (12 x blocks)
                AB, ABN, AA, BB = (np.zeros((12, N_BLOCK)) for _ in range(4))
                nullT = np.zeros((N_PERM, 12))
                for l in range(12):
                    xa, xb = XA[l] * mask, XB[l]
                    aa, bb = blocksum(xa * xa), blocksum(xb * xb * mask)
                    ab = blocksum(xa * xb)
                    abn = np.zeros(N_BLOCK)
                    for p, mp in enumerate(maps[pname]):
                        xbp = xb[mp]
                        s = blocksum(xa * xbp)
                        abn += s / N_PERM
                        # null denominators: permuted B norm on the mask
                        nullT[p, l] = s.sum() / np.sqrt(aa.sum() * (xbp * xbp * mask).sum())
                    AB[l], ABN[l], AA[l], BB[l] = ab, abn, aa, bb
                real = AB.sum(1) / np.sqrt(AA.sum(1) * BB.sum(1))
                r = {}
                for lname, ls in list(LAY.items()) + [(f"L{l}", [l]) for l in range(12)]:
                    rv = float(real[ls].mean())
                    nv = nullT[:, ls].mean(1)
                    # jackknife on excess = real - null_mean (null mean via linear ab average)
                    jk = []
                    for k in range(N_BLOCK):
                        keep = np.arange(N_BLOCK) != k
                        e = [(AB[l, keep].sum() - ABN[l, keep].sum()) / np.sqrt(AA[l, keep].sum() * BB[l, keep].sum()) for l in ls]
                        jk.append(np.mean(e))
                    jk = np.array(jk)
                    se = float(np.sqrt((N_BLOCK - 1) / N_BLOCK * ((jk - jk.mean()) ** 2).sum()))
                    exc = rv - float(nv.mean())
                    r[lname] = {"real": rv, "null_mean": float(nv.mean()), "null_lo": float(np.percentile(nv, 2.5)),
                                "null_hi": float(np.percentile(nv, 97.5)), "excess": exc, "excess_jk_se": se,
                                "excess_frac": exc / rv if rv != 0 else float("nan")}
                rec["pools"][f"{pname}_{variant}"] = r
            d = rec["pools"][f"{pname}_all"]["deep"]
            print(f"{tok} {g:6s} {a}:{b} pool {pname}: deep real {d['real']:.3f} null {d['null_mean']:.3f} [{d['null_lo']:.3f},{d['null_hi']:.3f}] excess {d['excess']:.3f}±{d['excess_jk_se']:.3f} frac {d['excess_frac']:.2f}", flush=True)
        out["results"].append(rec)

# identity check on one pair
xa, xb = M["I0D0"][11], M["I1D0"][11]
out["identity_check"] = float(abs((xa * xb).sum() / np.sqrt((xa * xa).sum() * (xb * xb).sum())
                                  - [r for r in out["results"] if r["A"] == "I0D0" and r["B"] == "I1D0"][0]["pools"]["U_all"]["L11"]["real"]))
(WB / "results/e174").mkdir(exist_ok=True, parents=True)
(WB / f"results/e174/td_null_{tok}.json").write_text(json.dumps(out))
print("saved", flush=True)
