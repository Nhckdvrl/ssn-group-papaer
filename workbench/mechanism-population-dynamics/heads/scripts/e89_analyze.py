"""E89 analysis: is the division of labour among heads reproduced across retrainings? Protocol: experiments/E89-*.md.

Usage: e89_analyze.py [--glob 'hf__pythia-410m*'] [--out name]
All cross-model statistics use independent prompt halves (model A half 0 vs model B half 1 and vice versa), so that the
within-model split-half value is the measurement ceiling at the same noise level.
"""
import argparse
import glob
import itertools
import json

import numpy as np
from scipy.optimize import linear_sum_assignment

import mp_common as mc

DIR = mc.RESULTS / "e89"
MODES = ("all", "end")


def load(path, tasks=None):
    z = np.load(path)
    ts = sorted({k.split("__")[0] for k in z.files if k.endswith("__clean")})
    out = {"clean": {}, "maps": {}, "roles": {}}
    for t in ts:
        if tasks and t not in tasks:
            continue
        half = z[f"{t}__half"]
        out["clean"][t] = z[f"{t}__clean"]
        for m in MODES:
            e = z[f"{t}__{m}"].astype(np.float32)
            out["maps"][(t, m)] = np.stack([e[half == 0].mean(0), e[half == 1].mean(0)])  # [2, L, H]
    for k in z.files:
        if k.startswith("role__"):
            out["roles"][k[6:]] = z[k]  # [2, L, H]
    return out


NORM = "z"


def zl(x):
    """Remove each task's layer profile: within-layer z-score (NORM z) or within-layer centring (NORM c, keeps
    magnitudes so layers where the task has real effects dominate)."""
    mu = x.mean(1, keepdims=True)
    if NORM == "c":
        return (x - mu) / (x.std() + 1e-9)
    return (x - mu) / (x.std(1, keepdims=True) + 1e-9)


def corr(a, b):
    a, b = np.ravel(a), np.ravel(b)
    return float(np.corrcoef(a, b)[0, 1])


def sharing(M, tasks, mode, h):
    X = np.stack([zl(M[(t, mode)][h]).ravel() for t in tasks])
    return np.corrcoef(X)


def offdiag(S):
    return S[np.triu_indices(len(S), 1)]


def layer_profile(M, t, mode, h):
    return np.abs(M[(t, mode)][h]).sum(1)


def align_layer(FA, FB):
    """FA, FB [H, F] features of one layer -> permutation p with B[j] matched to A[p[j]]."""
    C = np.corrcoef(FA, FB)[:FA.shape[0], FA.shape[0]:]
    C = np.nan_to_num(C)
    r, c = linear_sum_assignment(-C)
    p = np.empty(FB.shape[0], int)
    p[c] = r
    return p


def feats(M, roles, tasks, h, kind):
    """Per-layer head features [L, H, F] from the given tasks (both modes) or from attention roles."""
    if kind == "roles":
        arrs = [zl(roles[k][h]) for k in sorted(roles)]
    else:
        arrs = [zl(M[(t, m)][h]) for t in tasks for m in MODES]
    return np.stack(arrs, -1)


def transfer(A, B, t, ftasks, kind, mode="all", rng=None):
    """Predict B's held-out map of task t (half 1) from A's (half 1) after per-layer alignment fitted on half 0."""
    MA, MB = A["maps"], B["maps"]
    L, H = MA[(t, mode)].shape[1:]
    if kind == "identity":
        P = [np.arange(H)] * L
    elif kind == "random":
        P = [rng.permutation(H) for _ in range(L)]
    else:
        FA = feats(MA, A["roles"], ftasks, 0, kind)
        FB = feats(MB, B["roles"], ftasks, 0, kind)
        P = [align_layer(FA[l], FB[l]) for l in range(L)]
    pa = zl(MA[(t, mode)][1])
    pred = np.stack([pa[l][P[l]] for l in range(L)])
    return corr(pred, zl(MB[(t, mode)][1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="hf__pythia-410m*")
    ap.add_argument("--exclude", default="step,deduped")
    ap.add_argument("--out", default="analysis_410m")
    ap.add_argument("--min_metric", type=float, default=1.0)
    ap.add_argument("--min_rel", type=float, default=0.6)
    ap.add_argument("--norm", default="z")
    a = ap.parse_args()
    global NORM
    NORM = a.norm
    files = sorted(f for f in glob.glob(str(DIR / f"{a.glob}.npz")) if not any(x and x in f for x in a.exclude.split(",")))
    names = [f.split("/")[-1][:-4] for f in files]
    D = {n: load(f) for n, f in zip(names, files)}
    tasks_all = sorted({t for d in D.values() for t in d["clean"]})
    res = {"models": names, "per_task": {}}
    # positive controls: clean metric and split-half reliability (Spearman-Brown) of each task map
    keep = []
    for t in tasks_all:
        mets = [float(D[n]["clean"][t].mean()) for n in names]
        rel = {m: [corr(D[n]["maps"][(t, m)][0], D[n]["maps"][(t, m)][1]) for n in names] for m in MODES}
        sb = {m: [2 * r / (1 + r) for r in v] for m, v in rel.items()}
        ok = min(mets) > a.min_metric and np.median(sb["all"]) >= a.min_rel
        res["per_task"][t] = {"metric_min": min(mets), "metric_med": float(np.median(mets)),
                              "rel_sb_all_med": float(np.median(sb["all"])), "rel_sb_end_med": float(np.median(sb["end"])),
                              "kept": bool(ok)}
        if ok:
            keep.append(t)
    res["tasks"] = keep
    pairs = list(itertools.combinations(names, 2))
    rng = np.random.default_rng(0)
    # R1 layer profiles
    r1 = {}
    for t in keep:
        within = [corr(layer_profile(D[n]["maps"], t, "all", 0), layer_profile(D[n]["maps"], t, "all", 1)) for n in names]
        cross = [np.mean([corr(layer_profile(D[x]["maps"], t, "all", 0), layer_profile(D[y]["maps"], t, "all", 1)),
                          corr(layer_profile(D[x]["maps"], t, "all", 1), layer_profile(D[y]["maps"], t, "all", 0))]) for x, y in pairs]
        r1[t] = {"within": float(np.median(within)), "cross": float(np.median(cross))}
    res["R1_layer_profile"] = r1
    # R2 task-sharing structure
    r2 = {}
    for mode in MODES:
        S = {n: [sharing(D[n]["maps"], keep, mode, h) for h in (0, 1)] for n in names}
        within = [corr(offdiag(S[n][0]), offdiag(S[n][1])) for n in names]
        cross = [np.mean([corr(offdiag(S[x][0]), offdiag(S[y][1])), corr(offdiag(S[x][1]), offdiag(S[y][0]))]) for x, y in pairs]
        null = []
        for x, y in pairs[:20]:
            for _ in range(50):
                p = rng.permutation(len(keep))
                null.append(corr(offdiag(S[x][0]), offdiag(S[y][1][np.ix_(p, p)])))
        mean_S = np.mean([np.mean([S[n][0], S[n][1]], 0) for n in names], 0)
        r2[mode] = {"within_med": float(np.median(within)), "cross_med": float(np.median(cross)),
                    "cross_q": [float(q) for q in np.quantile(cross, [.1, .9])], "null_q95": float(np.quantile(null, .95)),
                    "ratio": float(np.median(cross) / np.median(within)),
                    "mean_S": {f"{keep[i]}~{keep[j]}": round(float(mean_S[i, j]), 3) for i, j in zip(*np.triu_indices(len(keep), 1))},
                    "pair_sd_across_models": {f"{keep[i]}~{keep[j]}": round(float(np.std([np.mean([S[n][0][i, j], S[n][1][i, j]]) for n in names])), 3)
                                              for i, j in zip(*np.triu_indices(len(keep), 1))}}
    res["R2_sharing"] = r2
    # R3 leave-one-task-out alignment transfer
    r3 = {}
    for t in keep:
        others = [u for u in keep if u != t]
        row = {k: [] for k in ("identity", "random", "roles", "loto", "assisted")}
        for x, y in pairs:
            for A, B in ((D[x], D[y]), (D[y], D[x])):
                row["identity"].append(transfer(A, B, t, others, "identity"))
                row["random"].append(np.mean([transfer(A, B, t, others, "random", rng=rng) for _ in range(5)]))
                row["roles"].append(transfer(A, B, t, others, "roles"))
                row["loto"].append(transfer(A, B, t, others, "tasks"))
                row["assisted"].append(transfer(A, B, t, keep, "tasks"))
        ceil = [corr(zl(D[n]["maps"][(t, "all")][0]), zl(D[n]["maps"][(t, "all")][1])) for n in names]
        r3[t] = {k: float(np.median(v)) for k, v in row.items()}
        r3[t]["ceiling_split_half"] = float(np.median(ceil))
    res["R3_transfer"] = r3
    out = DIR / f"{a.out}.json"
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ("R2_sharing",)}, indent=1))
    for mode in MODES:
        print(mode, {k: v for k, v in r2[mode].items() if k not in ("mean_S", "pair_sd_across_models")})


if __name__ == "__main__":
    main()
