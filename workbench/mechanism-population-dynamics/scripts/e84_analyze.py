"""E84 analysis: relocation vs suppression after MDA-style masking (protocol: experiments/E84-*.md).

Usage: e84_analyze.py -> results/e84/analysis.json + printed table
T = target head's induction score / base;  B = best head score / base best;  C = copy_gain / base copy_gain.
Target = base's top induction head at the final step (3000).
"""
import json

import numpy as np

import mp_common as mc

E46 = mc.RESULTS / "e46"
OUT = mc.RESULTS / "e84"
STEPS = ("750", "1000", "1500", "2000", "3000")
NAMES = {"base": "L_i{i}_c4_o1_st3000", "rerun": "L_i{i}_c4_o1_rerun1_st3000",
         "random": "L_i{i}_c4_o1_st3000_maskrandom0.1_500-2000", "repeat": "L_i{i}_c4_o1_st3000_maskrepeat0.1_500-2000"}


def load(name):
    f = E46 / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def head(M):
    M = np.array(M)
    i = np.unravel_index(M.argmax(), M.shape)
    return (int(i[0]), int(i[1])), float(M.max())


def main():
    res = {}
    for i in (1, 2, 3):
        base = load(NAMES["base"].format(i=i))
        if base is None:
            continue
        bm = base["measures"]
        tgt, bbest = head(bm["3000"]["M1"])
        res[i] = {"target": f"{tgt[0]}.{tgt[1]}", "base_best": bbest, "base_gain": bm["3000"]["copy_gain"], "conds": {}}
        for cond in ("rerun", "random", "repeat"):
            d = load(NAMES[cond].format(i=i))
            if d is None:
                continue
            m = d["measures"]
            traj = {}
            for s in STEPS:
                if s not in m or s not in bm:
                    continue
                M = np.array(m[s]["M1"])
                h, best = head(M)
                bh, bb = head(bm[s]["M1"])
                traj[s] = {"T": float(M[tgt] / np.array(bm[s]["M1"])[tgt]) if np.array(bm[s]["M1"])[tgt] > 0.05 else None,
                           "B": best / bb if bb > 0.05 else None,
                           "C": m[s]["copy_gain"] / bm[s]["copy_gain"] if bm[s]["copy_gain"] > 0.1 else None,
                           "best_head": f"{h[0]}.{h[1]}", "base_best_head": f"{bh[0]}.{bh[1]}"}
            res[i]["conds"][cond] = {"traj": traj, "masked": d.get("masked"), "threshold": d.get("mask_threshold")}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1))
    for i, r in res.items():
        print(f"init {i}: target {r['target']} base best {r['base_best']:.2f} base gain {r['base_gain']:.2f}")
        for cond, c in r["conds"].items():
            f = c["traj"].get("3000")
            if f:
                print(f"  {cond:7s} @3000 T {f['T'] and round(f['T'], 2)} B {f['B'] and round(f['B'], 2)} C {f['C'] and round(f['C'], 2)} "
                      f"best {f['best_head']} (base {f['base_best_head']}) masked {c['masked']}")
            print("          traj", {s: (v["best_head"], v["T"] and round(v["T"], 2), v["C"] and round(v["C"], 2)) for s, v in c["traj"].items()})
    # decision readouts
    rep = [r["conds"]["repeat"]["traj"].get("3000") for r in res.values() if "repeat" in r["conds"]]
    rer = [r["conds"]["rerun"]["traj"].get("3000") for r in res.values() if "rerun" in r["conds"]]
    rep, rer = [x for x in rep if x], [x for x in rer if x]
    if rep:
        reloc = sum((x["T"] or 1) <= 0.7 and (x["B"] or 0) >= 0.9 and (x["C"] or 0) >= 0.9 for x in rep)
        supp = sum((x["C"] or 1) <= 0.9 and (x["B"] or 1) <= 0.9 for x in rep)
        print(f"\nrepeat: relocation in {reloc}/{len(rep)}, suppression in {supp}/{len(rep)}")
    if rer:
        moved = sum(x["best_head"] != x["base_best_head"] or (x["T"] or 1) <= 0.7 for x in rer)
        print(f"rerun: target moved / weakened in {moved}/{len(rer)}")


if __name__ == "__main__":
    main()
