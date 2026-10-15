"""E89 analysis v2 (POST-HOC re-specification after seeing 5 Pythia-410M seeds; see experiments/E89 §2026-10-15 16:10).

Observation that forced it: the heads that correspond functionally across seeds sit in different layers (e.g. the head
shared by induction / antonym ICL / successor is 5.2, 5.4, 4.14, 6.4 in four seeds), so within-layer alignment and
within-layer centring cannot see the correspondence. Everything here is cross-layer.

Usage: e89_analyze2.py [--glob 'hf__pythia-410m*'] [--exclude step,deduped] [--out name] [--pass_metric 0.5]
Readouts
  depth   centre-of-mass layer of |effect| per task; Kendall tau of the task depth order between models
  S       task x task correlation over all heads of globally standardised maps (A half 0 vs B half 1 vs ceiling)
  hub     for each task pair, does the pair share a head among both tasks' top-k (k=3) in a model; consistency across models
  align   cross-layer Hungarian matching of heads on the other tasks' causal profiles (fit half), transfer of the held-out
          task map (other half): correlation over heads and top-1 hit (A's top head maps into B's top-3)
"""
import argparse
import glob
import itertools
import json

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import kendalltau

import mp_common as mc
from e89_analyze import load

DIR = mc.RESULTS / "e89"


def g(x):
    return (x - x.mean()) / (x.std() + 1e-9)


def corr(a, b):
    return float(np.corrcoef(np.ravel(a), np.ravel(b))[0, 1])


def com(m):
    p = np.abs(m).sum(1)
    return float((np.arange(len(p)) * p).sum() / p.sum())


def topk(m, k):
    return set(np.argsort(-m.ravel())[:k].tolist())


def S_of(d, tasks, h, mode="all"):
    return np.corrcoef(np.stack([g(d["maps"][(t, mode)][h]).ravel() for t in tasks]))


def off(S):
    return S[np.triu_indices(len(S), 1)]


def match(FA, FB, layers=None):
    """Hungarian over all heads (cross-layer) or within layer; returns p with B head j <- A head p[j]."""
    n = FA.shape[0]
    C = np.nan_to_num(np.corrcoef(FA, FB)[:n, n:])
    if layers is not None:
        C = np.where(layers[:, None] == layers[None, :], C, -10)
    r, c = linear_sum_assignment(-C)
    p = np.empty(n, int)
    p[c] = r
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="hf__pythia-410m*")
    ap.add_argument("--exclude", default="step,deduped")
    ap.add_argument("--out", default="analysis2_410m")
    ap.add_argument("--pass_metric", type=float, default=0.5)
    ap.add_argument("--k", type=int, default=3)
    a = ap.parse_args()
    files = sorted(f for f in glob.glob(str(DIR / f"{a.glob}.npz")) if not any(x and x in f for x in a.exclude.split(",")))
    names = [f.split("/")[-1][:-4] for f in files]
    D = {n: load(f) for n, f in zip(names, files)}
    tasks = sorted(next(iter(D.values()))["clean"])
    passed = {n: [t for t in tasks if D[n]["clean"][t].mean() > a.pass_metric] for n in names}
    res = {"models": names, "passed": passed, "metric": {n: {t: round(float(D[n]["clean"][t].mean()), 2) for t in tasks} for n in names}}
    pairs = list(itertools.combinations(names, 2))
    rng = np.random.default_rng(0)
    L, H = D[names[0]]["maps"][(tasks[0], "all")].shape[1:]
    layers = np.repeat(np.arange(L), H)

    # depth: centre of mass per task, and whether the task order by depth is shared
    C = {n: {t: com(D[n]["maps"][(t, "all")].mean(0)) for t in passed[n]} for n in names}
    taus = []
    for x, y in pairs:
        ts = [t for t in passed[x] if t in passed[y]]
        taus.append(kendalltau([C[x][t] for t in ts], [C[y][t] for t in ts])[0])
    res["depth"] = {"com": {n: {t: round(v, 1) for t, v in C[n].items()} for n in names},
                    "kendall_task_order_median": float(np.median(taus)), "kendall_q": [float(q) for q in np.quantile(taus, [.1, .9])]}

    # S: task-sharing structure over all heads
    within, cross, null = [], [], []
    for n in names:
        ts = passed[n]
        within.append(corr(off(S_of(D[n], ts, 0)), off(S_of(D[n], ts, 1))))
    for x, y in pairs:
        ts = [t for t in passed[x] if t in passed[y]]
        sx0, sx1, sy0, sy1 = S_of(D[x], ts, 0), S_of(D[x], ts, 1), S_of(D[y], ts, 0), S_of(D[y], ts, 1)
        cross.append(np.mean([corr(off(sx0), off(sy1)), corr(off(sx1), off(sy0))]))
        for _ in range(20):
            p = rng.permutation(len(ts))
            null.append(corr(off(sx0), off(sy1[np.ix_(p, p)])))
    Sm = {}
    for n in names:
        S = (S_of(D[n], tasks, 0) + S_of(D[n], tasks, 1)) / 2
        for i, j in zip(*np.triu_indices(len(tasks), 1)):
            if tasks[i] in passed[n] and tasks[j] in passed[n]:
                Sm.setdefault(f"{tasks[i]}~{tasks[j]}", []).append(S[i, j])
    res["S"] = {"within_med": float(np.median(within)), "cross_med": float(np.median(cross)),
                "cross_q": [float(q) for q in np.quantile(cross, [.1, .9])], "null_q95": float(np.quantile(null, .95)),
                "null_med": float(np.median(null)),
                "pair_mean_sd": {k: [round(float(np.mean(v)), 3), round(float(np.std(v)), 3), len(v)] for k, v in sorted(Sm.items(), key=lambda kv: -np.mean(kv[1]))}}

    # hub: do two tasks share one of their top-k heads, and is that consistent across models
    hub = {}
    for n in names:
        tops = {t: topk(D[n]["maps"][(t, "all")].mean(0), a.k) for t in passed[n]}
        for i, j in itertools.combinations(tasks, 2):
            if i in tops and j in tops:
                hub.setdefault(f"{i}~{j}", []).append(int(len(tops[i] & tops[j]) > 0))
    base = a.k * a.k / (L * H)
    res["hub"] = {"chance_share": round(1 - (1 - a.k / (L * H)) ** a.k, 4),
                  "pairs": {k: [round(float(np.mean(v)), 2), len(v)] for k, v in sorted(hub.items(), key=lambda kv: -np.mean(kv[1]))}}

    # align: cross-layer vs within-layer matching on the other tasks' profiles
    al = {}
    for t in tasks:
        row = {k: [] for k in ("identity", "within_layer", "cross_layer", "cross_layer_assisted")}
        hit = {k: [] for k in row}
        ceil = [corr(g(D[n]["maps"][(t, "all")][0]), g(D[n]["maps"][(t, "all")][1])) for n in names if t in passed[n]]
        for x, y in itertools.permutations(names, 2):
            if t not in passed[x] or t not in passed[y]:
                continue
            others = [u for u in tasks if u != t and u in passed[x] and u in passed[y]]
            F = lambda n, ts: np.stack([g(D[n]["maps"][(u, m)][0]).ravel() for u in ts for m in ("all", "end")], 1)  # noqa: E731
            src, tgt = g(D[x]["maps"][(t, "all")][1]).ravel(), g(D[y]["maps"][(t, "all")][1]).ravel()
            ps = {"identity": np.arange(L * H),
                  "within_layer": match(F(x, others), F(y, others), layers),
                  "cross_layer": match(F(x, others), F(y, others)),
                  "cross_layer_assisted": match(F(x, others + [t]), F(y, others + [t]))}
            ttop = set(np.argsort(-tgt)[:3].tolist())
            s1 = int(np.argmax(src))
            for k, p in ps.items():
                pred = src[p]
                row[k].append(corr(pred, tgt))
                hit[k].append(int(np.where(p == s1)[0][0] in ttop))
        if row["identity"]:
            al[t] = {k: round(float(np.median(v)), 3) for k, v in row.items()}
            al[t].update({f"hit_{k}": round(float(np.mean(v)), 2) for k, v in hit.items()})
            al[t]["ceiling"] = round(float(np.median(ceil)), 3)
            al[t]["chance_hit"] = round(3 / (L * H), 4)
    res["align"] = al
    (DIR / f"{a.out}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ("passed",)}, indent=1))


if __name__ == "__main__":
    main()
