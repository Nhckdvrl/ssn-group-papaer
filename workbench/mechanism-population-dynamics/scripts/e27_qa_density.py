"""E27: recipe QA-format density (E23 S3) vs format effect (E26 cells) across 25 DataDecide recipes. CPU only.
Protocol: experiments/E27-*.md.  Usage: e27_qa_density.py
"""
import json

import numpy as np
from scipy.stats import spearmanr

import dd_common as dd
import e18_trait as e18
import mp_common as mc
from e21_e22_corpus import partial_spearman

E26 = mc.RESULTS / "e26"
CTX = ("c1", "cK", "cP", "cF")


def effects(d, R, items=None):
    kn = items if items is not None else d["known"]
    cats = sorted({r["cat"] for r in R})
    by = {c: [i for i in kn if R[i]["cat"] == c] for c in cats}
    m = {c: float(np.mean([np.mean(np.array(v)[ix]) for ix in by.values() if len(ix) >= 10]))
         for c, v in d["cells"].items()}
    avg = lambda x: (m[f"{x}_decl"] + m[f"{x}_qa"]) / 2
    return {"FE_c1": m["c1_qa"] - m["c1_decl"], "FE": float(np.mean([m[f"{c}_qa"] - m[f"{c}_decl"] for c in CTX])),
            "count": avg("cK") - avg("c1")}


def main():
    R = e18.rows()
    S = json.loads((mc.RESULTS / "e23" / "recipe_stats.json").read_text())
    K = {}
    rows = {}
    for name in S:
        fs = [E26 / f"{name}-1B__{s}.json" for s in dd.SEEDS]
        fs = [f for f in fs if f.exists()] if all(f.exists() for f in fs) else [E26 / f"{name}-1B__default.json"]
        if not fs[0].exists():
            continue
        ds = [json.loads(f.read_text()) for f in fs]
        ef = [effects(d, R) for d in ds]
        rows[name] = {k: float(np.mean([e[k] for e in ef])) for k in ef[0]}
        rows[name]["n_seeds"] = len(ds)
        c20 = [json.loads((mc.RESULTS / "e20" / (f.name)).read_text())["conditions"] for f in fs]
        K[name] = float(np.mean([np.mean([v["clean_margin"] for v in c.values()]) for c in c20]))
    names = sorted(rows)
    s3 = np.log(np.array([S[n]["QA_per_1k"] for n in names]) + 1e-3)
    s1 = np.array([S[n]["S1"] for n in names])
    fe = np.array([rows[n]["FE_c1"] for n in names])
    cnt = np.array([rows[n]["count"] for n in names])
    kk = np.array([K[n] for n in names])
    rng = np.random.default_rng(0)
    rho = spearmanr(s3, fe)[0]
    p = float(np.mean([abs(spearmanr(rng.permutation(s3), fe)[0]) >= abs(rho) for _ in range(10000)]))
    out = {"n_recipes": len(names), "rho_logS3_FEc1": float(rho), "perm_p": p,
           "rho_logS3_FE_all_ctx": float(spearmanr(s3, [rows[n]["FE"] for n in names])[0]),
           "rho_logS3_count": float(spearmanr(s3, cnt)[0]), "rho_S1_FEc1": float(spearmanr(s1, fe)[0]),
           "partial_logS3_FEc1_given_K": partial_spearman(s3, fe, [kk]), "per_recipe": rows}
    (mc.RESULTS / "e27").mkdir(exist_ok=True)
    (mc.RESULTS / "e27" / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "per_recipe"}, indent=1))


if __name__ == "__main__":
    main()
