"""CT03 E03.7 -- separate the INTERACTION gap from the ESTIMATION gap.

Write the exact utilities as  u = u_par + u_perp,  where u_par = A z*_exact is
the part a scalar router can express and u_perp is the pair/set-specific
residual. Then two different quantities have been conflated:

  G_int = 1 - R2_exact               how much is simply not expressible
  G_est                              how badly we estimate the expressible part

The decisive number is rho(u_hat, u_par). If it jumps far above
rho(u_hat, u_exact), then non-additive interaction is what limits the proxy.
If it barely moves, the first-order estimator is missing the representable
component itself, and interaction is not the story.

Zero GPU: reuses results/e036_proxy.jsonl and results/c0_eval_base_pairs.jsonl.
"""
import argparse, json, sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e035_integrability import fit_potentials
from e01_report import spearman


def main(a):
    prox, exact = defaultdict(dict), defaultdict(dict)
    for r in map(json.loads, open(a.proxy)):
        prox[(r["q"], r["layer"], r["pos"])][(r["i"], r["j"])] = -r["px"]
    for r in map(json.loads, open(a.exact)):
        exact[(r["q"], r["layer"], r["pos"])][(r["i"], r["j"])] = -r["dL"]
    keys = [k for k in prox if k in exact and set(prox[k]) == set(exact[k])
            and len(prox[k]) >= 8]

    per = defaultdict(list)
    for k in keys:
        pk = sorted(prox[k])
        uh = np.array([prox[k][p] for p in pk])
        ue = np.array([exact[k][p] for p in pk])
        _, _, r2e, pred_e, _ = fit_potentials([(i, j, exact[k][(i, j)]) for i, j in pk])
        per[k[1]].append(dict(
            r2_exact=r2e,
            rho_u=spearman(uh, ue),            # proxy vs full exact utility
            rho_par=spearman(uh, pred_e),      # proxy vs its EXPRESSIBLE part
            ceiling=float(np.sqrt(max(r2e, 0.0))),
            perp_share=1 - r2e))

    print(f"tokens: {len(keys)}\n")
    print("Interaction gap vs estimation gap")
    print(f"{'layer':>6}{'n':>5}{'1-R2(int)':>11}{'ceiling':>9}"
          f"{'rho(u_hat,u)':>14}{'rho(u_hat,u_par)':>18}{'lift':>8}{'est gap':>9}")
    out = {}
    for l in sorted(per):
        v = per[l]
        g = lambda key: float(np.median([x[key] for x in v]))
        row = dict(n=len(v), perp=g("perp_share"), ceiling=g("ceiling"),
                   rho_u=g("rho_u"), rho_par=g("rho_par"))
        row["lift"] = row["rho_par"] - row["rho_u"]
        # how far the proxy is from perfectly recovering the expressible part
        row["est_gap"] = 1.0 - row["rho_par"]
        out[str(l)] = row
        print(f"{l:>6}{row['n']:>5}{row['perp']:>11.3f}{row['ceiling']:>9.3f}"
              f"{row['rho_u']:>14.3f}{row['rho_par']:>18.3f}"
              f"{row['lift']:>+8.3f}{row['est_gap']:>9.3f}")
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
    print("\nReading: a large positive 'lift' means non-additive interaction is what"
          "\nlimits the proxy. A lift near zero means the first-order estimator is"
          "\nmissing the representable component itself.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--proxy", default="results/e036_proxy.jsonl")
    ap.add_argument("--exact", default="results/c0_eval_base_pairs.jsonl")
    ap.add_argument("--out", default="results/e037_gaps.json")
    main(ap.parse_args())
