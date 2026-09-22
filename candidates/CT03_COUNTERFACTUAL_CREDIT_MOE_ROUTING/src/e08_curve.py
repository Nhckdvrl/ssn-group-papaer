"""CT03 E08 analysis -- screening curve in EPO's action space. Zero GPU.

Primary metric (frozen in docs/E08_DESIGN.md):

    R_m = max(0, max_{r in TopM_uhat} u_r) / max_r u_r      over cells with max u > 0

The clamp at 0 is the semantics of the decision: if the proxy's top-m contains
only harmful routes, EPO keeps the base route and gains nothing -- it does not
lose. Without it a bad cell would score negative and average like two bad cells.
"""
import argparse, glob, json
from collections import defaultdict
import numpy as np

MS = [1, 2, 4, 8, 16, 32]


def spearman(a, b):
    if len(a) < 3:
        return np.nan
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else np.nan


def boot(per_problem, key, m, B=2000, seed=0):
    ks = sorted(per_problem)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        pick = rng.choice(len(ks), len(ks), replace=True)
        pool = [v for i in pick for v in per_problem[ks[i]][(key, m)]]
        if pool:
            vals.append(np.mean(pool))
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))) \
        if vals else (np.nan, np.nan)


def main(a):
    cells = []
    for f in sorted(glob.glob(a.glob)):
        import torch
        d = torch.load(f, weights_only=False)
        cells += d["cells"]
    print(f"loaded {len(cells)} cells from {a.glob}")

    stats = defaultdict(lambda: defaultdict(list))     # layer -> metric -> list
    perprob = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for c in cells:
        l = c["layer"]
        u = np.array(c["u"]); uh = np.array(c["uhat"])
        stats[l]["n_unique"].append(len(u))
        stats[l]["changed"].append(float(np.mean(c["changed"])))
        stats[l]["rho"].append(spearman(uh, u))
        stats[l]["any_benefit"].append(float(u.max() > 0))
        best = u.max()
        if best <= 0:
            continue
        nben = int((u > 0).sum())
        order = np.argsort(-uh)
        for m in MS:
            sel = order[:m]
            got = max(0.0, float(u[sel].max()))
            for k, v in (("R", got / best),
                         ("recall", float(int(u.argmax()) in sel.tolist())),
                         ("ben_recall", float((u[sel] > 0).sum()) / nben),
                         ("regret", best - got)):
                stats[l][(k, m)].append(v)
                perprob[l][c["pi"]][(k, m)].append(v)

    out = {}
    for l in sorted(stats):
        n = len(stats[l][("R", 1)])
        print(f"\n### L{l}   cells {len(stats[l]['n_unique'])}, "
              f"with a beneficial route {np.mean(stats[l]['any_benefit']):.3f} "
              f"(n={n})   unique/32 {np.mean(stats[l]['n_unique']):.1f}   "
              f"experts changed {np.mean(stats[l]['changed']):.2f}   "
              f"median rho {np.nanmedian(stats[l]['rho']):.3f}")
        print(f"{'m':>4}{'R_m (retained gain)':>22}{'95% CI':>20}"
              f"{'exact-best recall':>19}{'benef. recall':>15}{'regret':>10}"
              f"{'reruns saved':>14}")
        for m in MS:
            v = stats[l][("R", m)]
            if not v:
                continue
            lo, hi = boot(perprob[l], "R", m)
            row = dict(R=float(np.mean(v)), ci=[lo, hi],
                       recall=float(np.mean(stats[l][("recall", m)])),
                       ben_recall=float(np.mean(stats[l][("ben_recall", m)])),
                       regret=float(np.mean(stats[l][("regret", m)])), n=len(v))
            out[f"{l}|{m}"] = row
            nu = np.mean(stats[l]["n_unique"])
            print(f"{m:>4}{row['R']:>22.3f}   [{lo:>6.3f},{hi:>6.3f}]"
                  f"{row['recall']:>19.3f}{row['ben_recall']:>15.3f}"
                  f"{row['regret']:>10.4f}{max(0.0, 1 - m / nu):>13.0%}")

    gate = [m for m in MS if m <= 8
            and all(out.get(f"{l}|{m}", {}).get("R", 0) >= 0.90 for l in (36, 44))]
    print(f"\nGATE (exists m<=8 with R_m>=0.90 at BOTH L36 and L44): "
          f"{'PASS m=' + str(gate[0]) if gate else 'FAIL'}")
    out["_gate"] = gate[0] if gate else None
    out["_meta"] = {str(l): dict(cells=len(stats[l]["n_unique"]),
                                 any_benefit=float(np.mean(stats[l]["any_benefit"])),
                                 n_unique=float(np.mean(stats[l]["n_unique"])),
                                 changed=float(np.mean(stats[l]["changed"])),
                                 rho_med=float(np.nanmedian(stats[l]["rho"])))
                    for l in sorted(stats)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="results/e08_cache_*.pt")
    ap.add_argument("--out", default="results/e08_curve.json")
    main(ap.parse_args())
