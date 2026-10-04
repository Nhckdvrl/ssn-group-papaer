"""sgd_temperature: batch size vs inheritance, at step 2000 of the same LR schedule. For bs in (16, 64, 512): same-seed c4-papers
within-layer similarity (inheritance, seeds 1-3), same-seed same-corpus order-only similarity (seed 1, c4, order 1 vs
101), and different-seed same-corpus similarity (baseline). bs64 values come from the standard runs' step-2000 measures."""
import itertools
import json

import numpy as np

import common as mc
from similarity import within_matrix

D = mc.RESULTS / "controlled"


def at2000(name):
    f = D / f"{name}.json"
    if not f.exists():
        return None
    m = json.loads(f.read_text())["measures"]
    return m.get("2000")


def main():
    out = {}
    conds = {"bs16": ("_bs16_st2000", 1e-3 / 16), "bs64": ("", 1e-3 / 64), "bs512": ("_bs512_st2000", 1e-3 / 512),
             "lr3e-3": ("_lr0.003_st2000", 3e-3 / 64), "lr3e-4": ("_lr0.0003_st2000", 3e-4 / 64)}
    for bs, (suf, temp) in conds.items():
        R = {(i, c): at2000(f"S_i{i}_{c}_o{i}{suf}") for i in (1, 2, 3) for c in ("c4", "papers")}
        R = {k: v for k, v in R.items() if v}
        order = at2000(f"S_i1_c4_o101{suf}")
        row = {"n_runs": len(R), "lr_over_b": temp}
        for m in ("M1", "M2"):
            ok = lambda v: m != "M1" or v["M1_max"] > 0.3
            si = [within_matrix([R[(i, "c4")][m], R[(i, "papers")][m]])[0, 1] for i in (1, 2, 3)
                  if (i, "c4") in R and (i, "papers") in R and ok(R[(i, "c4")]) and ok(R[(i, "papers")])]
            sd = [within_matrix([R[(i, c)][m], R[(j, c)][m]])[0, 1] for c in ("c4", "papers")
                  for i, j in itertools.combinations((1, 2, 3), 2) if (i, c) in R and (j, c) in R and ok(R[(i, c)]) and ok(R[(j, c)])]
            od = (within_matrix([R[(1, "c4")][m], order[m]])[0, 1]
                  if order and (1, "c4") in R and ok(order) and ok(R[(1, "c4")]) else None)
            row[m] = {"inherit_c4_papers": float(np.mean(si)) if si else None, "per_seed": [round(float(x), 3) for x in si],
                      "diff_seed": float(np.mean(sd)) if sd else None, "order_only": None if od is None else float(od)}
        out[bs] = row
        print(f"{bs:7s} LR/B {temp:.1e}", " | ".join(f"{m}: inherit {r['inherit_c4_papers']} {r['per_seed']} order-only {r['order_only']} diff-seed {r['diff_seed']}"
                                       for m, r in ((m, row[m]) for m in ("M1", "M2"))), flush=True)
    (mc.RESULTS / "sgd_temperature.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
