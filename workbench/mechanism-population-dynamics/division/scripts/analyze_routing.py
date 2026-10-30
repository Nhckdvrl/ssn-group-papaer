#!/usr/bin/env python3
"""E167 R1–R3: cross-model agreement of routing partitions, permutation-invariant.

For two captured checkpoints A, B and each layer pair (la, lb):
  T_ctx : corr of within-type-centred co-routing C over same-type word pairs
          (token identity removed exactly)
  T_D   : same for D = C - E_N1[C] (geometry-preserving null removed)
  T_h   : same for the hidden-state cosine kernel (how similar the representations are)
  T_lex : corr over type pairs of between-type mean co-routing (the "natural" lexical agreement)
CIs: type-cluster bootstrap (1000). Floor: within-type occurrence permutation of B (100).

Usage: analyze_routing.py CAPTURE_DIR OUT_JSON A.npz:B.npz [A.npz:B.npz ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import os
N_BOOT, N_PERM = 1000, int(os.environ.get("E167_NPERM", 100))


def centre_within(x, t, n_types):
    s = np.bincount(t, x, n_types)
    c = np.bincount(t, None, n_types)
    return x - (s / np.maximum(c, 1))[t]


def type_moments(a, b, t, n_types):
    return (np.bincount(t, a * b, n_types), np.bincount(t, a * a, n_types), np.bincount(t, b * b, n_types))


def corr_from(m, w=None):
    ab, aa, bb = (x.sum() for x in m) if w is None else (m[0] @ w, m[1] @ w, m[2] @ w)
    return float(ab / np.sqrt(aa * bb)) if aa > 0 and bb > 0 else float("nan")


def boot_ci(m, n_types, rng):
    ab, aa, bb = m
    W = rng.multinomial(n_types, np.full(n_types, 1 / n_types), size=N_BOOT).T.astype(np.float64)
    vals = (ab @ W) / np.sqrt((aa @ W) * (bb @ W))
    return [float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))]


def perm_null(xa, xb_fn, t, n_types, wtype, rng):
    """Permute occurrences of B within each word type; xb_fn(perm) -> B's pair values under relabelling."""
    n = len(wtype)
    base = np.lexsort((np.arange(n), wtype))
    out = []
    for _ in range(N_PERM):
        perm = np.empty(n, np.int64)
        perm[base] = np.lexsort((rng.random(n), wtype))
        xb = centre_within(xb_fn(perm), t, n_types)
        out.append(corr_from(type_moments(xa, xb, t, n_types)))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def main():
    cap = Path(sys.argv[1])
    out = Path(sys.argv[2])
    specs = [s.split(":") for s in sys.argv[3:]]
    P = np.load(cap / "pairs.npz")
    i, j, t = P["i"], P["j"], P["type"]
    n_types = int(t.max()) + 1
    n_words = len(P["anchor_word"])
    atype = P["anchor_type"]
    _, wtype = np.unique(atype, return_inverse=True)
    lists = [np.where(wtype == k)[0] for k in range(wtype.max() + 1)]
    rng = np.random.default_rng(167)
    results = []
    for a_name, b_name in specs:
        A, B = np.load(cap / a_name), np.load(cap / b_name)
        L = sum(1 for k in A.files if k.startswith("C"))
        rec = {"A": a_name, "B": b_name, "tokens_A": int(A["tokens"]), "tokens_B": int(B["tokens"]), "layers": []}
        for la in range(L):
            lb = la  # primary: same layer (identical architecture)
            row = {"layer": la}
            for name, fa, fb in (("T_ctx", A[f"C{la}"], B[f"C{lb}"]),
                                 ("T_D", A[f"C{la}"] - A[f"B{la}"], B[f"C{lb}"] - B[f"B{lb}"]),
                                 ("T_h", A[f"Kh{la}"], B[f"Kh{lb}"])):
                xa = centre_within(fa.astype(np.float64), t, n_types)
                xb = centre_within(fb.astype(np.float64), t, n_types)
                m = type_moments(xa, xb, t, n_types)
                row[name] = corr_from(m)
                row[name + "_ci"] = boot_ci(m, n_types, rng)
            # permutation floor for T_ctx (cheap version: relabel B's per-word sets)
            SB = B[f"S{lb}"]
            k = SB.shape[1]
            E = int(max(A[f"S{la}"].max(), SB.max())) + 1
            MB = np.zeros((n_words, E), np.float32)
            np.put_along_axis(MB, SB.astype(np.int64), 1.0, 1)
            xa = centre_within(A[f"C{la}"].astype(np.float64), t, n_types)
            row["T_ctx_perm95"] = None if N_PERM == 0 else perm_null(xa, lambda p: (MB[p[i]] * MB[p[j]]).sum(1) / k, t, n_types, wtype, rng)
            # lexical agreement between types (label-free)
            def type_means(S):
                M = np.zeros((n_words, E), np.float32)
                np.put_along_axis(M, S.astype(np.int64), 1.0, 1)
                G = np.zeros((len(lists), E))
                np.add.at(G, wtype, M)
                return G / np.array([len(l) for l in lists])[:, None]
            GA, GB = type_means(A[f"S{la}"]), type_means(SB)
            ua, ub = np.triu_indices(len(lists), 1)
            KA, KB = (GA @ GA.T)[ua, ub] / k, (GB @ GB.T)[ua, ub] / k
            row["T_lex"] = float(np.corrcoef(KA, KB)[0, 1])
            row["null_load_tv"] = [float(A[f"loadtv{la}"]), float(B[f"loadtv{lb}"])]
            rec["layers"].append(row)
        results.append(rec)
        print(a_name, b_name, [round(r["T_D"], 3) for r in rec["layers"]], flush=True)
    out.write_text(json.dumps({"n_pairs": int(len(i)), "n_types": n_types, "results": results}, indent=1))


if __name__ == "__main__":
    main()
