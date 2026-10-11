"""Is the sentence-level curse predicted by termination geometry or by intrinsic uncertainty?

Outcome: does the segment collapse to an empty hypothesis at beam 64 under RAW scoring?
Predictors: `log p(stop immediately)` (termination geometry, measured before any beam search) and
the frozen human-reference uncertainty `u`. Fitted with statsmodels logit; both predictors are
standardised so the coefficients are comparable.
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "fsmt"
    term = json.load(open(os.path.join(ROOT, "results", "ext", f"termination_{tag}.json")))
    per = term["per_segment"]
    data = os.path.join(ROOT, "data")
    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")]
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]

    gen = None
    for d in ("results/ext/gen", "results/e00/gen"):
        p = os.path.join(ROOT, d, f"{tag}_b64_RAW.jsonl")
        if os.path.exists(p):
            gen = [json.loads(l) for l in open(p, encoding="utf-8")][1:]
            break
    gen.sort(key=lambda r: r["idx"])
    n = len(per["idx"])

    df = pd.DataFrame({
        "empty64": [1.0 if not gen[i]["hyp"].strip() else 0.0 for i in range(n)],
        "log_p_empty": per["log_p_empty"][:n],
        "log_p_greedy": per["log_p_greedy"][:n],
        "u_char": [r["u_char"] for r in unc][:n],
        "u_word": [r["u_word"] for r in unc][:n],
        "ref_words": [len(r.split()) for r in ref_w][:n],
    })
    df["delta_empty"] = df.log_p_empty - df.log_p_greedy

    def z(x):
        return (x - x.mean()) / x.std()

    print(f"== {tag}: P(collapse to empty at beam 64) ==  n={len(df)}, base rate {df.empty64.mean():.3f}")
    models = {
        "u only": ["u_char"],
        "termination only": ["log_p_empty"],
        "both": ["log_p_empty", "u_char"],
        "both + length": ["log_p_empty", "u_char", "ref_words"],
        "delta + u": ["delta_empty", "u_char"],
    }
    out = {}
    for name, cols in models.items():
        X = sm.add_constant(pd.DataFrame({c: z(df[c]) for c in cols}))
        res = sm.Logit(df.empty64, X).fit(disp=0)
        pretty = "  ".join(f"{c}={res.params[c]:+.2f}(p={res.pvalues[c]:.1e})" for c in cols)
        print(f"  {name:18s} pseudo-R2={res.prsquared:.3f}  {pretty}")
        out[name] = {"pseudo_r2": float(res.prsquared),
                     "params": {c: float(res.params[c]) for c in cols},
                     "pvalues": {c: float(res.pvalues[c]) for c in cols}}

    # correlation structure
    print("\n  correlations:")
    for a, b in [("log_p_empty", "u_char"), ("log_p_empty", "ref_words"), ("u_char", "ref_words"),
                 ("log_p_empty", "empty64"), ("u_char", "empty64")]:
        print(f"    {a:12s} vs {b:10s} r = {df[a].corr(df[b]):+.3f}")
    out["correlations"] = {f"{a}~{b}": float(df[a].corr(df[b])) for a, b in
                           [("log_p_empty", "u_char"), ("log_p_empty", "ref_words"),
                            ("u_char", "ref_words"), ("log_p_empty", "empty64"),
                            ("u_char", "empty64")]}
    with open(os.path.join(ROOT, "results", "ext", f"mediation_{tag}.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
