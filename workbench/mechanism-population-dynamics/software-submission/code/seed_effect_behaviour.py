"""seed_effect_behaviour: initialization main effects on context_trust_1b behavioural readouts across 25 recipes (CPU)."""
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import datadecide as dd
import common as mc
context_trust_1b = mc.RESULTS / "context_trust_1b"


def main():
    recs = sorted({f.stem.split("__")[0] for f in context_trust_1b.glob("*__*.json")})
    recs = [r for r in recs if all((context_trust_1b / f"{r}__{s}.json").exists() for s in dd.SEEDS)]
    C = {(r, s): json.loads((context_trust_1b / f"{r}__{s}.json").read_text())["conditions"] for r in recs for s in dd.SEEDS}
    conds = sorted(C[(recs[0], "default")])
    rng = np.random.default_rng(0)

    def frac_init(Y):
        gm = Y.mean()
        return 25 * ((Y.mean(0) - gm) ** 2).sum() / ((Y - gm) ** 2).sum()
    out = {"n_recipes": len(recs), "conditions": {}}
    offsets = {"D": [], "K": []}
    for c in conds:
        for y, key in (("D", "margin"), ("K", "clean_margin")):
            Y = np.array([[C[(r, s)][c][key] for s in dd.SEEDS] for r in recs])
            f = frac_init(Y)
            null = [frac_init(np.array([rng.permutation(row) for row in Y])) for _ in range(10000)]
            p = float(np.mean(np.array(null) >= f))
            out["conditions"].setdefault(c, {})[y] = {"frac_init": float(f), "p": p,
                                                      "init_offsets": (Y.mean(0) - Y.mean()).tolist()}
            offsets[y].append(Y.mean(0) - Y.mean())
    for y in ("D", "K"):
        out[f"n_sig_{y}"] = int(sum(v[y]["p"] < 0.05 for v in out["conditions"].values()))
        O = np.array(offsets[y])
        out[f"offset_consistency_{y}"] = float(np.nanmean([spearmanr(O[i], O[j])[0] for i, j in itertools.combinations(range(len(O)), 2)]))
    out["decision_D"] = ("init carries behavioural offsets" if out["n_sig_D"] >= 4 else
                         "no init offsets" if out["n_sig_D"] <= 1 else "intermediate")
    (mc.RESULTS / "seed_effect_behaviour").mkdir(exist_ok=True)
    (mc.RESULTS / "seed_effect_behaviour" / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "conditions"}, indent=1))
    for c, v in out["conditions"].items():
        print(f"{c[:42]:42s} D frac {v['D']['frac_init']:.3f} p {v['D']['p']:.4f} | K frac {v['K']['frac_init']:.3f} p {v['K']['p']:.4f}")


if __name__ == "__main__":
    main()
