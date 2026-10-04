"""crossing_sizes analysis: SI / SD / DD layout similarity per DataDecide size (+ 1B five-init at step 7500)."""
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import common as mc
D = mc.RESULTS / "crossing_sizes"
SIZES = ("4M", "6M", "8M", "10M", "14M", "16M", "20M", "60M", "90M", "150M", "300M", "530M", "750M", "1B@7500")
# exclusion fixed before analysis: its step0 shards differ from the other small-aux-2 1B models
EXCLUDE = {("1B@7500", "fineweb-pro", "small-aux-2")}
PARAMS = {"4M": 3.7e6, "6M": 6e6, "8M": 8.5e6, "10M": 9.9e6, "14M": 14.4e6, "16M": 16e6, "20M": 19.1e6, "60M": 57e6,
          "90M": 97.9e6, "150M": 151e6, "300M": 320e6, "530M": 530e6, "750M": 750e6, "1B@7500": 1.18e9}


def within(a, b):
    return float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))


def main():
    out = {}
    rng = np.random.default_rng(0)
    for size in SIZES:
        files = sorted(D.glob(f"{size}__*.json"))
        M = {tuple(f.stem.split("__")[1:]): json.loads(f.read_text()) for f in files
             if (size, *f.stem.split("__")[1:]) not in EXCLUDE}
        recs = sorted({r for r, _ in M})
        seeds = sorted({s for _, s in M})
        recs = [r for r in recs if sum((r, s) in M for s in seeds) >= 2]
        keys = [k for k in M if k[0] in recs]
        if len(recs) < 3:
            continue
        row = {"n_models": len(keys), "n_recipes": len(recs), "seeds": seeds,
               "pc_rel_M2": float(np.mean([M[k]["reliability_M2"] for k in keys])),
               "frac_M1max_over_0.3": float(np.mean([M[k]["M1_max"] > 0.3 for k in keys]))}
        cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
        for m in ("M1", "M2", "M3", "M4"):
            V = {k: np.array(M[k]["maps"][m]) for k in keys}
            sims = {(a, b): (spearmanr(V[a].ravel(), V[b].ravel())[0], within(V[a], V[b]))
                    for a, b in itertools.combinations(keys, 2)}
            g = {c: [v for p, v in sims.items() if cls(*p) == c] for c in ("SI", "SD", "DD")}
            boots = []
            for _ in range(500):
                w = rng.choice(recs, len(recs))
                cnt = {r: int((w == r).sum()) for r in recs}
                gg = {"SI": [], "SD": []}
                for (a, b), v in sims.items():
                    c = cls(a, b)
                    if c in gg and cnt[a[0]] and cnt[b[0]]:
                        gg[c] += [v[0]] * (cnt[a[0]] * cnt[b[0]])
                if gg["SI"] and gg["SD"]:
                    boots.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
            r = {c: float(np.mean([x[0] for x in v])) for c, v in g.items() if v}
            rw = {c: float(np.mean([x[1] for x in v])) for c, v in g.items() if v}
            ci = np.percentile(boots, [2.5, 97.5]).tolist() if boots else [None, None]
            decidable = not (m == "M1" and row["frac_M1max_over_0.3"] < 2 / 3)
            row[m] = {"full": r, "within_layer": rw, "SI_minus_SD": r["SI"] - r["SD"], "ci95": ci,
                      "decidable": decidable,
                      "init_determined": bool(decidable and r["SI"] - r["SD"] > 0.1 and ci[0] is not None and ci[0] > 0)}
        out[size] = row
    out["trend"] = {}
    for m in ("M1", "M2", "M4"):
        pts = [(np.log(PARAMS[s]), out[s][m]["SI_minus_SD"]) for s in SIZES if s in out and out[s][m]["decidable"]]
        if len(pts) >= 4:
            out["trend"][m] = {"spearman_logparams": float(spearmanr(*zip(*pts))[0]), "n_sizes": len(pts)}
    (D / "analysis.json").write_text(json.dumps(out, indent=1))
    for s in SIZES:
        if s in out:
            r = out[s]
            print(f"{s:8s} n={r['n_models']:3d} relM2={r['pc_rel_M2']:.3f} M1>0.3={r['frac_M1max_over_0.3']:.2f} | " +
                  " | ".join(f"{m} SI {r[m]['full']['SI']:.2f} SD {r[m]['full']['SD']:.2f} wSI {r[m]['within_layer']['SI']:.2f} "
                             f"wSD {r[m]['within_layer']['SD']:.2f} {'✓' if r[m]['init_determined'] else ('–' if not r[m]['decidable'] else '✗')}"
                             for m in ("M1", "M2", "M4")))
    print("trend", out["trend"])


if __name__ == "__main__":
    main()
