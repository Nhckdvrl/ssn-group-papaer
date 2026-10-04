"""pythia_small analysis: Pythia std/deduped (shared init) vs PolyPythias seeds; 160M data-seed vs weight-seed."""
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import common as mc
D = mc.RESULTS / "pythia_small"


def main():
    out = {"a": {}, "b": {}, "pc": {}}
    for size in ("70m", "160m", "410m"):
        names = ["std", "deduped"] + [f"seed{k}" for k in range(1, 10)]
        M = {n: json.loads((D / f"pythia-{size}-{n}.json").read_text()) for n in names}
        out["pc"][size] = {"rel_M2_min": min(m["reliability_M2"] for m in M.values()),
                           "n_M1max_over_0.3": sum(m["M1_max"] > 0.3 for m in M.values()), "n": len(M)}
        row = {}
        for m in ("M1", "M2", "M3", "M4"):
            V = {n: np.ravel(M[n]["maps"][m]) for n in names}
            si = float(spearmanr(V["std"], V["deduped"])[0])
            sd = [float(spearmanr(V[a], V[b])[0]) for a, b in itertools.combinations([n for n in names if n != "deduped"], 2)]
            dd = [float(spearmanr(V["deduped"], V[f"seed{k}"])[0]) for k in range(1, 10)]
            row[m] = {"SI": si, "SD_mean": float(np.mean(sd)), "SD_p95": float(np.percentile(sd, 95)),
                      "SD_max": float(np.max(sd)), "DD_mean": float(np.mean(dd)),
                      "SI_percentile_in_SD": float((np.array(sd) < si).mean() * 100),
                      "replicates": bool(si > np.percentile(sd, 95) and si - np.mean(sd) > 0.1)}
        out["a"][size] = row
    # (b) 160M: same init / different order vs different init / same order vs both differ
    names = ["std", "deduped", "data-seed1", "data-seed2", "data-seed3", "weight-seed1", "weight-seed2", "weight-seed3"] + \
            [f"seed{k}" for k in range(1, 10)]
    M = {n: json.loads((D / f"pythia-160m-{n}.json").read_text()) for n in names}
    groups = {"same_init_diff_order": list(itertools.combinations(["std", "data-seed1", "data-seed2", "data-seed3"], 2)),
              "diff_init_same_order": list(itertools.combinations(["std", "weight-seed1", "weight-seed2", "weight-seed3"], 2)),
              "both_differ": list(itertools.combinations([f"seed{k}" for k in range(1, 10)], 2)),
              "same_init_diff_data": [("deduped", x) for x in ("std", "data-seed1", "data-seed2", "data-seed3")]}
    for m in ("M1", "M2", "M3", "M4"):
        V = {n: np.ravel(M[n]["maps"][m]) for n in names}
        g = {k: [float(spearmanr(V[a], V[b])[0]) for a, b in prs] for k, prs in groups.items()}
        r = {k: {"mean": float(np.mean(v)), "min": float(np.min(v)), "max": float(np.max(v)), "n": len(v)} for k, v in g.items()}
        diff = r["same_init_diff_order"]["mean"] - r["diff_init_same_order"]["mean"]
        hi = lambda k: r[k]["mean"] > r["both_differ"]["mean"] + 0.1
        r["decision"] = ("init (not order)" if diff > 0.1 else "order" if -diff > 0.1 else
                         "both" if hi("same_init_diff_order") and hi("diff_init_same_order") else "undecidable")
        out["b"][m] = r
    (mc.RESULTS / "pythia_small" / "analysis.json").write_text(json.dumps(out, indent=1))
    for size, row in out["a"].items():
        print(size, out["pc"][size], {m: (round(v["SI"], 3), round(v["SD_mean"], 3), round(v["SD_p95"], 3), v["replicates"])
                                      for m, v in row.items()})
    for m, r in out["b"].items():
        print("160m", m, {k: round(v["mean"], 3) for k, v in r.items() if k != "decision"}, r["decision"])


if __name__ == "__main__":
    main()
