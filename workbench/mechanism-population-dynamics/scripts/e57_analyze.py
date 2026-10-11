"""E57: within-layer SI / SD by size x training step (early checkpoints) next to the E45 final step, same 6 recipes."""
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

PLAN = json.loads((mc.CACHE / "datadecide" / "e45_plan.json").read_text())
SIZES = ("10M", "20M", "60M", "150M", "300M", "750M")
STEPS = (1250, 2500, 3750)


def within(a, b):
    return float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))


def cell(M, recs, m, rng):
    keys = [k for k in M if k[0] in recs and (m != "M1" or M[k]["M1_max"] > 0.3)]
    V = {k: np.array(M[k]["maps"][m]) for k in keys}
    sims = {(a, b): within(V[a], V[b]) for a, b in itertools.combinations(keys, 2)}
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    g = {c: [v for p, v in sims.items() if cls(*p) == c] for c in ("SI", "SD", "DD")}
    if not g["SI"] or not g["SD"]:
        return None
    boots = []
    for _ in range(300):
        w = rng.choice(recs, len(recs))
        cnt = {r: int((w == r).sum()) for r in recs}
        si = [v for p, v in sims.items() if cls(*p) == "SI" for _ in range(cnt[p[0][0]] * cnt[p[1][0]])]
        sd = [v for p, v in sims.items() if cls(*p) == "SD" for _ in range(cnt[p[0][0]] * cnt[p[1][0]])]
        if si and sd:
            boots.append(np.mean(si) - np.mean(sd))
    return {"SI": float(np.mean(g["SI"])), "SD": float(np.mean(g["SD"])), "n_models": len(keys),
            "diff": float(np.mean(g["SI"]) - np.mean(g["SD"])), "ci95": np.percentile(boots, [2.5, 97.5]).tolist()}


def main():
    rng = np.random.default_rng(0)
    out = {}
    for size in SIZES:
        recs = PLAN[size]["recipes"][:6]
        fin = PLAN[size]["step"]
        for step in STEPS + (fin,):
            if step == fin:
                files = [f for f in (mc.RESULTS / "e45").glob(f"{size}__*.json")]
                M = {tuple(f.stem.split("__")[1:]): json.loads(f.read_text()) for f in files}
            else:
                files = list((mc.RESULTS / "e57").glob(f"{size}@{step}__*.json"))
                M = {tuple(f.stem.split("__")[1:]): json.loads(f.read_text()) for f in files}
            M = {k: v for k, v in M.items() if k[0] in recs}
            if len(M) < 18:
                continue
            row = {"frac": step / fin}
            for m in ("M1", "M2", "M4"):
                row[m] = cell(M, recs, m, rng)
            out[f"{size}@{step}"] = row
            print(f"{size:5s} step {step:6d} ({step / fin:5.1%}) " + " | ".join(
                f"{m} SI {r['SI']:.2f} SD {r['SD']:.2f} [{r['ci95'][0]:.2f},{r['ci95'][1]:.2f}]" if r else f"{m} –"
                for m, r in ((m, row[m]) for m in ("M1", "M2", "M4"))), flush=True)
    (mc.RESULTS / "e57" / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
