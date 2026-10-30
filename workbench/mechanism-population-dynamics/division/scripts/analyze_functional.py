#!/usr/bin/env python3
"""E167 R4/R5 cross-model comparison of functional fingerprints (experts and heads).

Within each layer, units (experts or heads) are matched one-to-one by Hungarian assignment on the
cal split fingerprints and evaluated on the held anchor split (no reuse of the matching data).
Reported per layer:
  matched   : mean held corr of matched pairs
  random    : mean held corr under random one-to-one matching (floor; 200 draws, 95% range)
  reliab_A/B: mean split-half reliability of each unit's own fingerprint (cal vs anchor, same model)
  ratio     : matched / sqrt(reliab_A * reliab_B)  (agreement relative to what measurement allows)
Fingerprint kinds:
  drop  : expert drop dNLL per category   (functional/*.npz drop_fp)
  route : P(expert | category)            (functional/*.npz route_fp, per split)
  habl  : head ablation dNLL per category (heads/*.npz abl_fp)
  hattn : head attention-pattern features per category (heads_attn/*.npz attn_fp; z-scored per column)
Categories with < MIN_TOK tokens in either split are dropped; vectors are centred across units.

Usage: analyze_functional.py KIND DIR OUT_JSON A.npz:B.npz [...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

MIN_TOK = 300


def rowcorr(X, Y):
    X = X - X.mean(1, keepdims=True)
    Y = Y - Y.mean(1, keepdims=True)
    return (X * Y).sum(1) / np.sqrt((X * X).sum(1) * (Y * Y).sum(1) + 1e-30)


def load(kind, path):
    z = np.load(path)
    if kind == "drop":
        fp = z["drop_fp"]  # L,E,2,nc
        keep = (z["cat_counts"] >= MIN_TOK).all(0)
        return fp[..., keep][:, :, 1], fp[..., keep][:, :, 0], int(z["tokens"])  # cal, held(anchor)
    if kind == "habl":
        fp = z["abl_fp"]
        return fp[:, :, 1], fp[:, :, 0], int(z["tokens"])
    if kind == "route":
        r = np.transpose(z["route_fp"], (0, 1, 3, 2))  # L,split,E,nc
        keep = (z["cat_counts"] >= MIN_TOK).all(0)
        r = r[..., keep]
        return r[:, 1], r[:, 0], int(z["tokens"])
    if kind == "hattn":
        fp = z["attn_fp"]  # L,H,2,F*nc ; columns z-scored across heads with cal-split statistics
        nc = z["cat_counts"].shape[1]
        keep = np.tile((z["cat_counts"] >= MIN_TOK).all(0), fp.shape[-1] // nc)
        fp = fp[..., keep]
        mu, sd = fp[:, :, 1].mean(1, keepdims=True), fp[:, :, 1].std(1, keepdims=True) + 1e-6
        return (fp[:, :, 1] - mu) / sd, (fp[:, :, 0] - mu) / sd, int(z["tokens"])
    raise ValueError(kind)


def centre_units(F):
    return F - F.mean(0, keepdims=True)


def main():
    kind, d, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    rng = np.random.default_rng(167)
    res = []
    for spec in sys.argv[4:]:
        a, b = spec.split(":")
        Ac, Ah, ta = load(kind, d / a)
        Bc, Bh, tb = load(kind, d / b)
        rec = {"A": a, "B": b, "tokens_A": ta, "tokens_B": tb, "layers": []}
        for l in range(Ac.shape[0]):
            ac, ah, bc, bh = map(centre_units, (Ac[l], Ah[l], Bc[l], Bh[l]))
            n = ac.shape[0]
            C = np.array([rowcorr(np.repeat(ac[i:i + 1], n, 0), bc) for i in range(n)])  # cal corr matrix
            ri, ci = linear_sum_assignment(-C)
            matched = float(rowcorr(ah[ri], bh[ci]).mean())
            rand = [float(rowcorr(ah, bh[rng.permutation(n)]).mean()) for _ in range(200)]
            relA = float(rowcorr(ac, ah).mean())
            relB = float(rowcorr(bc, bh).mean())
            rec["layers"].append({"layer": l, "matched": matched, "random95": [float(np.percentile(rand, 2.5)), float(np.percentile(rand, 97.5))],
                                  "reliab_A": relA, "reliab_B": relB,
                                  "ratio": matched / np.sqrt(max(relA, 1e-6) * max(relB, 1e-6)),
                                  "per_unit_held": rowcorr(ah[ri], bh[ci]).round(4).tolist()})
        res.append(rec)
        print(a, b, [round(x["matched"], 3) for x in rec["layers"]], flush=True)
    out.write_text(json.dumps({"kind": kind, "results": res}, indent=1))


if __name__ == "__main__":
    main()
