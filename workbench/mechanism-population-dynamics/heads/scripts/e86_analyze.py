"""E86 (with E85): do exact reruns keep the strongest induction head, and do reruns / random masks keep the role map?

Usage: e86_analyze.py -> results/e85/e86_analysis.json + printed table (protocol: experiments/E85-*.md, E86 section)
"moved": the original strongest induction head scores below 0.9 of the other run's strongest.
Role-map correspondence = within-layer Spearman of a head-score map, averaged over layers (as in the paper), at step 3000.
"""
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

E46 = mc.RESULTS / "e46"
OUT = mc.RESULTS / "e85"
NAMES = {"rerun": "L_i{i}_c4_o1_rerun1_st3000", "mask0": "L_i{i}_c4_o1_st3000_maskrandom0.1_500-2000",
         "mask1": "L_i{i}_c4_o1_st3000_maskrandom0.1_500-2000_ms1"}


def load(name):
    f = E46 / f"{name}.json"
    return json.loads(f.read_text())["measures"]["3000"] if f.exists() else None


def corr(A, B):
    A, B = np.array(A), np.array(B)
    return float(np.nanmean([spearmanr(A[l], B[l])[0] for l in range(A.shape[0])]))


def best(M):
    M = np.array(M)
    return np.unravel_index(M.argmax(), M.shape)


def main():
    base = {i: load(f"L_i{i}_c4_o1_st3000") for i in range(1, 16)}
    base = {i: b for i, b in base.items() if b}
    rows = []
    for i, b in base.items():
        for cond, pat in NAMES.items():
            d = load(pat.format(i=i))
            if d is None:
                continue
            o = best(b["M1"])
            rows.append({"init": i, "cond": cond, "swap": bool(best(d["M1"]) != o),
                         "orig_rel": float(np.array(d["M1"])[o] / np.max(d["M1"])),
                         "r_M1": corr(b["M1"], d["M1"]), "r_M2": corr(b["M2"], d["M2"]), "r_M3": corr(b["M3"], d["M3"]),
                         "copy_ratio": d["copy_gain"] / b["copy_gain"]})
    unrel = [{"r_M1": corr(base[i]["M1"], base[j]["M1"]), "r_M2": corr(base[i]["M2"], base[j]["M2"]),
              "r_M3": corr(base[i]["M3"], base[j]["M3"])} for i in base for j in base if i < j]
    res = {"rows": rows, "unrelated": {k: float(np.mean([u[k] for u in unrel])) for k in ("r_M1", "r_M2", "r_M3")},
           "n_unrelated_pairs": len(unrel)}
    for grp, conds in (("rerun", ("rerun",)), ("mask", ("mask0", "mask1"))):
        g = [r for r in rows if r["cond"] in conds]
        if g:
            res[grp] = {"n": len(g), "swap_rate": float(np.mean([r["swap"] for r in g])),
                        "moved_rate": float(np.mean([r["orig_rel"] < 0.9 for r in g])),
                        **{k: float(np.mean([r[k] for r in g])) for k in ("r_M1", "r_M2", "r_M3", "copy_ratio")},
                        "copy_min": float(min(r["copy_ratio"] for r in g)), "copy_max": float(max(r["copy_ratio"] for r in g))}
    if "rerun" in res and "mask" in res:
        a, m = res["rerun"]["swap_rate"], res["mask"]["swap_rate"]
        res["decision"] = "mask >> rerun" if a <= m / 2 else ("comparable" if a >= 0.75 * m else "in between")
    (OUT / "e86_analysis.json").write_text(json.dumps(res, indent=1))
    for r in rows:
        print(f"init {r['init']:2d} {r['cond']:6s} swap {int(r['swap'])} orig {r['orig_rel']:.2f} rM1 {r['r_M1']:.2f} rM2 {r['r_M2']:.2f} rM3 {r['r_M3']:.2f} copy {r['copy_ratio']:.2f}")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
