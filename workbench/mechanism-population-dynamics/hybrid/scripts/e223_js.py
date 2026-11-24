#!/usr/bin/env python3
"""E223 step 2: pairwise per-token JS divergence between the 7 dumped models, entropy-binned, plus pre-registered partitions.
Usage: e223_js.py DUMP_DIR OUT_JSON"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import torch

M = ["TF", "MB", "DN", "GLA", "GSA", "HGRN", "RET"]


def main():
    d, out = Path(sys.argv[1]), Path(sys.argv[2])
    meta = {m: np.load(d / f"{m}_meta.npz") for m in M}
    t0 = meta["TF"]["tgt"]
    same = {m: bool(len(meta[m]["tgt"]) == len(t0) and (meta[m]["tgt"] == t0).all()) for m in M}
    print("token ids identical:", same, flush=True)
    assert all(same.values()), "tokenisation differs"
    N = len(t0)
    lps = {m: np.load(d / f"{m}_logp.npy", mmap_mode="r") for m in M}
    pairs = list(itertools.combinations(range(len(M)), 2))
    js = np.zeros((len(pairs), N), np.float32)
    CH = 2048
    for s in range(0, N, CH):
        L = torch.stack([torch.from_numpy(np.asarray(lps[m][s:s + CH])).cuda().float() for m in M])  # [7, c, V]
        P = L.exp()
        for k, (i, j) in enumerate(pairs):
            Mx = 0.5 * (P[i] + P[j]); lm = Mx.clamp_min(1e-30).log()
            js[k, s:s + CH] = (0.5 * (P[i] * (L[i] - lm)).sum(-1) + 0.5 * (P[j] * (L[j] - lm)).sum(-1)).cpu().numpy()
    nll = np.stack([meta[m]["nll"] for m in M]); ent = np.stack([meta[m]["ent"] for m in M])
    mean_ent = ent.mean(0)
    edges = np.quantile(mean_ent, np.linspace(0, 1, 11)); edges[-1] += 1e-6
    bins = [np.where((mean_ent >= edges[b]) & (mean_ent < edges[b + 1]))[0] for b in range(10)]
    mat = np.zeros((7, 7)); matb = np.zeros((10, 7, 7))
    for k, (i, j) in enumerate(pairs):
        mat[i, j] = mat[j, i] = js[k].mean()
        for b, ix in enumerate(bins):
            matb[b, i, j] = matb[b, j, i] = js[k, ix].mean()
    mean_nll = nll.mean(1)
    qual_gap = np.array([abs(mean_nll[i] - mean_nll[j]) for i, j in pairs]); pj = np.array([mat[i, j] for i, j in pairs])
    corr_js_gap = float(np.corrcoef(pj, qual_gap)[0, 1])
    nllcorr = np.corrcoef(nll)

    def mean_pairs(A, idx_pairs):
        return float(np.mean([A[i, j] for i, j in idx_pairs]))

    TF, REC = 0, [1, 2, 3, 4, 5, 6]; CONV, NOCONV = [1, 2], [3, 4, 5, 6]; RET, DD = 6, [1, 2, 3, 4, 5]
    rec_pairs = list(itertools.combinations(REC, 2))
    res_part = {}
    for name, fn in (
        ("P1_TF_apart", lambda A: mean_pairs(A, [(TF, r) for r in REC]) / mean_pairs(A, rec_pairs)),
        ("P2_conv_groups", lambda A: (mean_pairs(A, [(a, b) for a in CONV for b in NOCONV]) /
                                      np.mean([mean_pairs(A, list(itertools.combinations(CONV, 2))),
                                               mean_pairs(A, list(itertools.combinations(NOCONV, 2)))]))),
        ("P3_RET_apart", lambda A: mean_pairs(A, [(RET, r) for r in DD]) / mean_pairs(A, list(itertools.combinations(DD, 2))))):
        overall = fn(mat); per_bin = [fn(matb[b]) for b in range(10)]
        thr = 1.2 if name != "P2_conv_groups" else 1 / 0.8
        res_part[name] = {"ratio_overall": overall, "ratio_per_bin": per_bin, "n_bins_meeting": int(sum(x >= thr for x in per_bin)),
                          "met": bool(sum(x >= thr for x in per_bin) >= 8)}
    # average-linkage clustering (descriptive)
    clusters = [[i] for i in range(7)]; merges = []
    D = mat.copy()
    while len(clusters) > 1:
        best = None
        for a, b in itertools.combinations(range(len(clusters)), 2):
            v = np.mean([D[i, j] for i in clusters[a] for j in clusters[b]])
            if best is None or v < best[0]:
                best = (v, a, b)
        v, a, b = best
        merges.append(([M[i] for i in clusters[a]], [M[i] for i in clusters[b]], float(v)))
        clusters[a] = clusters[a] + clusters[b]; del clusters[b]
    res = {"models": M, "N": int(N), "mean_nll": dict(zip(M, mean_nll.tolist())), "mean_entropy": dict(zip(M, ent.mean(1).tolist())),
           "js_matrix": mat.tolist(), "js_matrix_by_entropy_decile": matb.tolist(), "entropy_edges": edges.tolist(),
           "nll_corr": nllcorr.tolist(), "corr_pairJS_vs_quality_gap": corr_js_gap, "partitions": res_part, "clustering": merges}
    out.write_text(json.dumps(res, indent=1))
    print("mean NLL:", {m: round(x, 3) for m, x in zip(M, mean_nll)})
    print("JS matrix (nats):"); print("      " + " ".join(f"{m:>6s}" for m in M))
    for i, m in enumerate(M):
        print(f"{m:6s}" + " ".join(f"{mat[i, j]:6.3f}" for j in range(7)))
    print("corr(pair JS, |NLL gap|):", round(corr_js_gap, 3))
    for k, v in res_part.items():
        print(k, "overall", round(v["ratio_overall"], 3), "bins meeting", v["n_bins_meeting"], "met", v["met"], [round(x, 2) for x in v["ratio_per_bin"]])
    for mg in merges:
        print("merge", mg)


if __name__ == "__main__":
    main()
