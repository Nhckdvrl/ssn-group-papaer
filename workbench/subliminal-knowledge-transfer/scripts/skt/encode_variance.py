#!/usr/bin/env python3
"""E04: exact rule-vs-seed decomposition of teacher information on common carrier prefixes.

With teachers indexed by (rule z, seed s) and uniform weights, the chain rule of mutual information gives,
per position x and with KL to arithmetic means:
    I(teacher; Y | x) = I(rule; Y | x) + I(seed; Y | x, rule)
    mean_{z,s} KL(p_zs || pbar) = mean_z KL(pbar_z || pbar) + mean_{z,s} KL(p_zs || pbar_z)
The between-rule term is biased upward by finite seeds; with n seeds per rule (small-divergence / ANOVA
approximation): sigma2_seed ~= within * n/(n-1), sigma2_rule ~= between - within/(n-1).
CIs: bootstrap over the 5,000 prefix sequences (positions within a sequence are not independent).

    python encode_variance.py --dir DISTS --configs FF,FG,MF,MG --seeds 1,2,3 --out OUT.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

EPS = 1e-8


def load(d, n):
    p = np.load(Path(d) / f"{n}.npy").astype(np.float64) + EPS
    return p / p.sum(-1, keepdims=True)


def kl(p, q):
    return (p * (np.log(p) - np.log(q))).sum(-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--configs", default="FF,FG,MF,MG")
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfgs, S = a.configs.split(","), [int(s) for s in a.seeds.split(",")]
    n = len(S)
    P = {(c, s): load(a.dir, f"{c}_s{s}") for c in cfgs for s in S}
    idx = np.load(Path(a.dir) / "base_index.npy")
    _, inv = np.unique(idx[:, 0], return_inverse=True)
    cnt = np.bincount(inv)
    pc = {c: np.mean([P[(c, s)] for s in S], 0) for c in cfgs}
    pbar = np.mean(list(pc.values()), 0)
    total = np.mean([kl(P[k], pbar) for k in P], 0)
    within = np.mean([kl(P[(c, s)], pc[c]) for c in cfgs for s in S], 0)
    between = np.mean([kl(pc[c], pbar) for c in cfgs], 0)
    seed_c, rule_c = within * n / (n - 1), between - within / (n - 1)
    rng = np.random.default_rng(0)
    seqs = {k: np.bincount(inv, weights=v) / cnt for k, v in
            dict(total=total, within=within, between=between, sigma_seed=seed_c, sigma_rule=rule_c).items()}
    out = {"n_positions": int(len(total)), "n_sequences": int(len(cnt)), "configs": cfgs, "seeds": S}
    B = [rng.integers(0, len(cnt), len(cnt)) for _ in range(a.boot)]
    for k, sv in seqs.items():
        bs = [sv[b].mean() for b in B]
        out[k] = [float(sv.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    share = [seqs["sigma_rule"][b].mean() / (seqs["sigma_rule"][b].mean() + seqs["sigma_seed"][b].mean()) for b in B]
    out["rule_share"] = [float(seqs["sigma_rule"].mean() / (seqs["sigma_rule"].mean() + seqs["sigma_seed"].mean())),
                         float(np.percentile(share, 2.5)), float(np.percentile(share, 97.5))]
    pos = idx[:, 1]
    for name, m in (("pos0", pos == 0), ("pos_ge1", pos >= 1)):
        r, s = rule_c[m].mean(), seed_c[m].mean()
        out[f"{name}_rule_seed_share"] = [float(r), float(s), float(r / (r + s))]
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
