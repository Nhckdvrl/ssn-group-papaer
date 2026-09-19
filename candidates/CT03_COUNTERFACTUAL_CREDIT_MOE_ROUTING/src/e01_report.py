"""CT03 E01 report -- turns results/e01_records.jsonl into the adjudication table.

Every predictor is expressed as a *predicted dL* (lower = better swap), so the
proxy and the baselines are directly comparable and a positive Spearman always
means "agrees with the exact quantity".
"""

import argparse, json, math
from collections import defaultdict
import numpy as np

PREDICTORS = {
    "px_shared": lambda r: r["px_shared"],
    "px_tok": lambda r: r["px_tok"],
    "router_gap": lambda r: -(r["w_j"] - r["w_i"]),
    "neg_dh_norm": lambda r: -r["dh_norm"],
    "dh_norm": lambda r: r["dh_norm"],
}


def rankdata(a):
    a = np.asarray(a, float)
    o = a.argsort()
    r = np.empty(len(a), float)
    r[o] = np.arange(len(a), dtype=float)
    # average ties
    _, inv, cnt = np.unique(a, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt)); np.add.at(sums, inv, r)
    return (sums / cnt)[inv]


def spearman(x, y):
    if len(x) < 3:
        return float("nan")
    rx, ry = rankdata(x), rankdata(y)
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return float("nan")
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


def cell_stats(groups, exact_key, rng):
    """groups: list of per-token candidate lists (each a list of records)."""
    out = {}
    n_tok = len(groups)
    out["n_tokens"] = n_tok
    out["n_cand"] = sum(len(g) for g in groups)
    if n_tok == 0:
        return out
    ex_all = np.array([r[exact_key] for g in groups for r in g])
    out["beneficial_rate"] = float((ex_all < 0).mean())
    out["exact_median_abs"] = float(np.median(np.abs(ex_all)))
    for name, f in PREDICTORS.items():
        rhos, top1, top3, regret, sign = [], [], [], [], []
        for g in groups:
            ex = np.array([r[exact_key] for r in g])
            pr = np.array([f(r) for r in g])
            rhos.append(spearman(pr, ex))
            best = int(ex.argmin())
            order = pr.argsort()
            top1.append(float(order[0] == best))
            top3.append(float(best in order[:3].tolist()))
            spread = ex.max() - ex.min()
            regret.append(float((ex[order[0]] - ex[best]) / spread) if spread > 0 else 0.0)
            ben = ex < 0
            if ben.any() and (~ben).any():
                sign.append(float(((pr < 0) == ben).mean()))
        rr = np.array([r for r in rhos if not math.isnan(r)])
        out[name] = dict(
            rho_median=float(np.median(rr)) if len(rr) else float("nan"),
            rho_mean=float(rr.mean()) if len(rr) else float("nan"),
            rho_pooled=spearman([f(r) for g in groups for r in g], ex_all),
            top1=float(np.mean(top1)), top3=float(np.mean(top3)),
            norm_regret=float(np.mean(regret)),
            sign_acc=float(np.mean(sign)) if sign else float("nan"),
        )
    # random floor
    t1, t3 = [], []
    for g in groups:
        ex = np.array([r[exact_key] for r in g])
        best = int(ex.argmin())
        order = rng.permutation(len(g))
        t1.append(float(order[0] == best)); t3.append(float(best in order[:3].tolist()))
    out["random"] = dict(top1=float(np.mean(t1)), top3=float(np.mean(t3)),
                         rho_median=0.0)
    return out


def main(a):
    recs = [json.loads(l) for l in open(a.records)]
    rng = np.random.default_rng(0)
    by = defaultdict(lambda: defaultdict(list))
    for r in recs:
        by[(r["stratum"], r["layer"], r["pool"])][(r["q"], r["pos"])].append(r)

    res = {"n_records": len(recs), "exact_key": a.exact, "cells": {}}
    for key, toks in sorted(by.items()):
        res["cells"]["|".join(map(str, key))] = cell_stats(list(toks.values()), a.exact, rng)

    # layer-averaged headline: hard stratum, boundary pool, non-final layers
    layers = sorted({r["layer"] for r in recs})
    nonfinal = [l for l in layers if l < max(layers) - 1]
    head = {}
    for stratum in ("hard", "easy"):
        for pool in ("boundary", "random"):
            cells = [res["cells"][f"{stratum}|{l}|{pool}"] for l in nonfinal
                     if f"{stratum}|{l}|{pool}" in res["cells"]]
            if not cells:
                continue
            head[f"{stratum}|{pool}|nonfinal"] = {
                p: dict(rho_median=float(np.mean([c[p]["rho_median"] for c in cells])),
                        top1=float(np.mean([c[p]["top1"] for c in cells])),
                        top3=float(np.mean([c[p]["top3"] for c in cells])),
                        norm_regret=float(np.mean([c[p]["norm_regret"] for c in cells])))
                for p in list(PREDICTORS) + ["random"] if p in cells[0]
            }
    res["headline_nonfinal_layers"] = nonfinal
    res["headline"] = head

    # cost
    cost = defaultdict(list)
    for r in recs:
        cost[r["layer"]].append(r["exact_batch_s"] / r["n_cand"])
    res["exact_seconds_per_candidate_by_layer"] = {
        str(l): float(np.mean(v)) for l, v in sorted(cost.items())}

    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["headline"], indent=1))
    print("\nexact s/candidate by layer:",
          json.dumps(res["exact_seconds_per_candidate_by_layer"]))
    print(f"\nwrote {a.out}  ({len(recs)} records)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", default="results/e01_records.jsonl")
    ap.add_argument("--exact", default="dL_seq", choices=["dL_seq", "dL_tok"])
    ap.add_argument("--out", default="results/e01_report.json")
    main(ap.parse_args())
