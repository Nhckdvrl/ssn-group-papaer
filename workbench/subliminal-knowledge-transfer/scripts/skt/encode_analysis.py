#!/usr/bin/env python3
"""E04 encoding-layer analysis on common carrier prefixes.

Input: DIR/{base,FF_s1,FG_s1,...}.npy from dump_carrier_dists.py (rows = completion positions, 30 bins).
Outputs (nats, per position, averaged over positions):
  drift_z        = KL(p_z || p_0)                    each teacher's total change on carriers
  shared         = KL(pbar || p_0)                   change common to all configs (format/style)
  r_enc(s)       = mean_z KL(p_{z,s} || pbar_s)       teacher-specific information I(Z;Y|X) within seed set s
  I_B(s)         = mean_B KL(pbar_{.B} || pbar)       language component
  I_A|B(s)       = mean_{A,B} KL(p_{AB} || pbar_{.B}) trigger component given language
  JS_same        = JS(p_{z,s}, p_{z,s'})              same config, different seed  (seed floor)
  JS_cross       = JS(p_{z,s}, p_{z',s'}), z != z'    different config, different seed
Paired permutation test per prefix-position block: is JS_cross > JS_same?
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

EPS = 1e-8


def norm(p):
    p = p.astype(np.float64) + EPS
    return p / p.sum(-1, keepdims=True)


def kl(p, q):
    return (p * (np.log(p) - np.log(q))).sum(-1)


def js(p, q):
    m = 0.5 * (p + q)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--configs", default="FF,FG,MF,MG")
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--out", required=True)
    ap.add_argument("--perm", type=int, default=2000)
    args = ap.parse_args()
    D = Path(args.dir)
    cfgs, seeds = args.configs.split(","), [int(s) for s in args.seeds.split(",")]
    p0 = norm(np.load(D / "base.npy"))
    P = {}
    for c in cfgs:
        for s in seeds:
            f = D / f"{c}_s{s}.npy"
            if f.exists():
                P[(c, s)] = norm(np.load(f))
    idx = np.load(D / "base_index.npy")
    res = {"n_positions": int(len(p0)), "available": sorted(f"{c}_s{s}" for c, s in P)}
    res["drift"] = {f"{c}_s{s}": float(kl(p, p0).mean()) for (c, s), p in P.items()}
    A = {"FF": "F", "FG": "F", "MF": "M", "MG": "M"}
    B = {"FF": "fr", "FG": "de", "MF": "fr", "MG": "de"}
    per_seed = {}
    for s in seeds:
        ps = {c: P[(c, s)] for c in cfgs if (c, s) in P}
        if len(ps) < len(cfgs):
            continue
        pbar = np.mean(list(ps.values()), 0)
        pB = {b: np.mean([ps[c] for c in cfgs if B[c] == b], 0) for b in ("fr", "de")}
        pA = {a: np.mean([ps[c] for c in cfgs if A[c] == a], 0) for a in ("F", "M")}
        per_seed[s] = {
            "shared": float(kl(pbar, p0).mean()),
            "r_enc": float(np.mean([kl(ps[c], pbar) for c in cfgs], 0).mean()),
            "I_B": float(np.mean([kl(pB[b], pbar) for b in pB], 0).mean()),
            "I_A_given_B": float(np.mean([kl(ps[c], pB[B[c]]) for c in cfgs], 0).mean()),
            "I_A": float(np.mean([kl(pA[a], pbar) for a in pA], 0).mean()),
        }
    res["per_seed"] = per_seed
    # seed floor vs cross-config, always across different seeds
    same, cross = [], []
    for (c1, s1), (c2, s2) in itertools.combinations(P, 2):
        if s1 == s2:
            continue
        (same if c1 == c2 else cross).append(js(P[(c1, s1)], P[(c2, s2)]))
    if same and cross:
        same_m, cross_m = np.mean(same, 0), np.mean(cross, 0)   # per position
        # aggregate by prefix (sequence) to respect within-sequence dependence
        seq = idx[:, 0]
        u, inv = np.unique(seq, return_inverse=True)
        d = np.bincount(inv, weights=cross_m - same_m) / np.bincount(inv)
        rng = np.random.default_rng(0)
        obs = d.mean()
        null = np.array([(d * rng.choice([-1, 1], size=len(d))).mean() for _ in range(args.perm)])
        res["JS_same_mean"] = float(same_m.mean())
        res["JS_cross_mean"] = float(cross_m.mean())
        res["cross_minus_same"] = float(obs)
        res["ratio_cross_over_same"] = float(cross_m.mean() / same_m.mean())
        res["perm_p_one_sided"] = float((null >= obs).mean())
        res["n_sequences"] = int(len(u))
    Path(args.out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
