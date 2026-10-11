"""lockin_datadecide analysis: lock-in timing of the init-set layout (DataDecide 1B early checkpoints)."""
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import datadecide as dd
import common as mc
crossing_1b = mc.RESULTS / "crossing_1b"
RECS = ("dolma1_7-1B", "c4-1B", "dclm-baseline-1B")
STEPS = (2500, 10000)


def main():
    maps = lambda f: json.loads(f.read_text())["maps"]
    final = {(r, s): maps(crossing_1b / f"{r}__{s}.json") for r in RECS for s in dd.SEEDS}
    out = {"steps": {}}
    # positive control: on the final step, this 3-recipe subset reproduces SI - SD > 0.1
    for step in STEPS + ("final",):
        E = final if step == "final" else {(r, s): maps(crossing_1b / f"{r}__{s}__step{step}.json") for r in RECS for s in dd.SEEDS}
        row = {}
        for m in ("M1", "M2", "M4"):
            V = {k: np.ravel(v[m]) for k, v in E.items()}
            g = {"SI": [], "SD": [], "DD": []}
            for a, b in itertools.combinations(sorted(E), 2):
                c = "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
                g[c].append(float(spearmanr(V[a], V[b])[0]))
            lock = [float(spearmanr(V[k], np.ravel(final[k][m]))[0]) for k in E] if step != "final" else None
            row[m] = {k: float(np.mean(v)) for k, v in g.items()}
            row[m]["SI_minus_SD"] = row[m]["SI"] - row[m]["SD"]
            row[m]["pairs"] = g
            if lock:
                row[m]["lock_mean"] = float(np.mean(lock))
        out["steps"][str(step)] = row
    out["positive_control_final"] = {m: out["steps"]["final"][m]["SI_minus_SD"] > 0.1 for m in ("M1", "M2", "M4")}
    rel = [json.loads((crossing_1b / f"{r}__{s}__step{st}.json").read_text())["reliability_M2"] for r in RECS for s in dd.SEEDS for st in STEPS]
    out["positive_control_reliability_M2_min"] = float(min(rel))
    dec = {}
    for m in ("M1", "M2", "M4"):
        s25, s10 = out["steps"]["2500"][m], out["steps"]["10000"][m]
        dec[m] = ("early lock-in" if s25["SI_minus_SD"] > 0.1 and s25["lock_mean"] >= 0.5 else
                  "gradual" if s10["SI_minus_SD"] > 0.1 else "late")
    out["decision"] = dec
    (mc.RESULTS / "lockin_datadecide").mkdir(exist_ok=True)
    (mc.RESULTS / "lockin_datadecide" / "analysis.json").write_text(json.dumps(out, indent=1))
    for st, row in out["steps"].items():
        print(st, {m: {k: round(v, 3) for k, v in r.items() if k != "pairs"} for m, r in row.items()})
    print("positive control (final subset):", out["positive_control_final"], "| M2 reliability min:",
          round(out["positive_control_reliability_M2_min"], 3), "| decision:", dec)


if __name__ == "__main__":
    main()
