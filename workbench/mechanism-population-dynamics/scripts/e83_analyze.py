"""E83 analysis: P1 (main carrier chosen at emergence persists) and P2 (sibling sharing decided at emergence).

Usage: e83_analyze.py -> results/e83/analysis.json + printed verdicts
"""
import glob
import itertools
import json
import re

import numpy as np

import mp_common as mc
from e81_analyze import top, within

OUT = mc.RESULTS / "e83"
RECS = ("c4-1B", "dolma1_7-1B", "dolma1_7-no-flan-1B", "dclm-baseline-1B")
SEEDS = ("default", "large-aux-2", "large-aux-3")


def load():
    D, LD = {}, {}
    for f in glob.glob(str(OUT / "dd__*.npz")):
        _, model, rev = f.split("/")[-1][:-4].split("__")
        st, sd = re.match(r"step(\d+)-seed-(.+)", rev).groups()
        z = np.load(f)
        D[(model.replace("DataDecide-", ""), sd, int(st))] = {k: z[k] for k in z.files}
        LD[(model.replace("DataDecide-", ""), sd, int(st))] = json.loads(open(f[:-4] + ".json").read())["logit_diff"]
    return D, LD


def main():
    D, LD = load()
    runs = {}
    for r in RECS:
        for s in SEEDS:
            steps = sorted(st for (rr, ss, st) in D if rr == r and ss == s)
            if 69369 not in steps:
                continue
            sel = next((st for st in steps if LD[(r, s, st)] > 1), None)
            fin = top(D[(r, s, 69369)]["dla"].mean(0))
            traj = {st: [f"{l}.{h}" for l, h in top(D[(r, s, st)]["dla"].mean(0))] for st in steps}
            if sel is None:
                runs[f"{r}/{s}"] = {"selection": None, "traj": traj}
                continue
            st_top = top(D[(r, s, sel)]["dla"].mean(0))
            runs[f"{r}/{s}"] = {"selection": sel, "ld_at_selection": LD[(r, s, sel)],
                                "main_at_selection": f"{st_top[0][0]}.{st_top[0][1]}", "main_final": f"{fin[0][0]}.{fin[0][1]}",
                                "P1_main_kept": st_top[0] == fin[0], "top3_overlap_sel_final": len(set(st_top) & set(fin)),
                                "traj": traj, "ld": {st: LD[(r, s, st)] for st in steps}}
    ok = [v for v in runs.values() if v.get("selection")]
    p1 = sum(v["P1_main_kept"] and v["top3_overlap_sel_final"] >= 2 for v in ok)
    pairs = []
    for s in SEEDS:
        for a, b in itertools.combinations(RECS, 2):
            ra, rb = runs.get(f"{a}/{s}"), runs.get(f"{b}/{s}")
            if not (ra and rb and ra.get("selection") and rb.get("selection")):
                continue
            sel_shared = ra["main_at_selection"] == rb["main_at_selection"]
            fin_shared = ra["main_final"] == rb["main_final"]
            fa, fb = D[(a, s, 69369)], D[(b, s, 69369)]
            pairs.append({"seed": s, "pair": f"{a} vs {b}", "shared_at_selection": sel_shared, "shared_final": fin_shared,
                          "attio_final": within(fa["att_io"].mean(0), fb["att_io"].mean(0))})
    p2 = np.mean([p["shared_at_selection"] == p["shared_final"] for p in pairs]) if pairs else None
    res = {"runs": runs, "pairs": pairs, "P1": {"n_runs": len(ok), "n_kept": int(p1), "holds": p1 >= 9},
           "P2": {"n_pairs": len(pairs), "agreement": None if p2 is None else float(p2), "holds": p2 is not None and p2 >= 0.8}}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in runs.items():
        print(k, "selection", v.get("selection"), "main", v.get("main_at_selection"), "-> final", v.get("main_final"),
              "kept", v.get("P1_main_kept"), "top3 overlap", v.get("top3_overlap_sel_final"))
        print("    traj", v["traj"])
    for p in pairs:
        print(p)
    print("P1", res["P1"], "\nP2", res["P2"])


if __name__ == "__main__":
    main()
