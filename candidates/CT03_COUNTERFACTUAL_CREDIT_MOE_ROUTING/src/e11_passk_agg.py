"""CT03 E11 -- pass@K table from the e11_passk shards. Zero GPU.

Unbiased estimator: pass@k for a problem with c of n correct samples is
1 - C(n-c, k)/C(n, k), i.e. the probability that k draws without replacement
are all wrong, subtracted from 1. Averaging the per-problem estimate is what
makes pass@k at k<n usable at all; the plug-in "any of the first k" is biased
and throws away most of the samples.

CIs are paired bootstraps over PROBLEMS, the unit of independence -- samples
within a problem are not exchangeable across problems.
"""
import argparse, glob, json
from math import comb
import numpy as np


def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def main(a):
    rows, arms, meta = [], None, None
    for f in sorted(glob.glob(a.glob)):
        d = json.load(open(f))
        arms = arms or d["arms"]
        meta = meta or dict(n_samples=d["n_samples"], temp=d["temp"],
                            top_p=d["top_p"])
        assert d["arms"] == arms and d["n_samples"] == meta["n_samples"], f
        rows += [{k: v for k, v in r.items() if k != "completions"}
                 for r in d["rows"]]
    rows.sort(key=lambda r: r["pi"])
    n = meta["n_samples"]
    ks = [k for k in (1, 2, 4, 8, 16, 32, 64) if k <= n]
    print(f"n={len(rows)} problems x {n} samples  T={meta['temp']} "
          f"top_p={meta['top_p']}  arms {arms}")
    print(f"{'k':>3}  " + "  ".join(f"{a_:>12}" for a_ in arms) +
          "        diff              95% CI")
    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, len(rows), (a.B, len(rows)))
    tab = {}
    for k in ks:
        est = {arm: np.array([pass_at_k(n, r[arm]["c"], k) for r in rows])
               for arm in arms}
        line = f"{k:>3}  " + "  ".join(f"{est[a_].mean():12.4f}" for a_ in arms)
        row = {arm: float(est[arm].mean()) for arm in arms}
        if len(arms) == 2:
            d = est[arms[1]] - est[arms[0]]
            bs = d[boot_idx].mean(1)
            lo, hi = np.percentile(bs, [2.5, 97.5])
            line += f"    {d.mean():+.4f}   [{lo:+.4f},{hi:+.4f}]"
            row.update(diff=float(d.mean()), ci=[float(lo), float(hi)])
        tab[k] = row
        print(line)
    json.dump(dict(table=tab, n_problems=len(rows), arms=arms, **meta),
              open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="results/e11_passk_s*.json")
    ap.add_argument("--out", default="results/e11_passk_table.json")
    ap.add_argument("--B", type=int, default=5000)
    main(ap.parse_args())
