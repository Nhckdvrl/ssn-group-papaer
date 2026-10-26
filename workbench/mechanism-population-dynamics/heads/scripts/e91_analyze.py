"""E91 analysis: per-head sharpness trajectories before the spikes, against the two control runs.

Usage: e91_analyze.py -> prints, per outlier window, loss and the heads whose sharpness (spread_max / spread_mean /
entropy) departs most from the controls' range, with their role (previous-token score, layer); writes results/e91/analysis.json
"""
import glob
import json
import re

import numpy as np

import mp_common as mc

DIR = mc.RESULTS / "e91"
HUB = {"pythia-410m-seed3": ["6.12", "4.6", "10.11"], "pythia-410m-seed4": ["5.11", "4.1"],
       "pythia-410m": ["5.2"], "pythia-410m-seed1": ["5.4"]}
WINDOWS = {"pythia-410m-seed3": (60000, 76000), "pythia-410m-seed4": (110000, 124000)}
CONTROLS = ("pythia-410m", "pythia-410m-seed1")


def load():
    R = {}
    for f in glob.glob(str(DIR / "*.json")):
        if "analysis" in f:
            continue
        m = re.match(r"(.+)__step(\d+)\.json", f.split("/")[-1])
        R.setdefault(m.group(1), {})[int(m.group(2))] = json.loads(open(f).read())
    return R


def main():
    R = load()
    out = {}
    for run, (a, b) in WINDOWS.items():
        if run not in R:
            continue
        steps = sorted(s for s in R[run] if a <= s <= b)
        ctrl = [R[c][s] for c in CONTROLS if c in R for s in R[c] if a <= s <= b]
        print(f"\n== {run} window {a}-{b}; controls: {len(ctrl)} checkpoints")
        rows = []
        for k in ("spread_max", "spread_mean", "entropy"):
            # control range per layer (head identities differ across runs, so compare against the controls' per-layer max/min)
            C = np.stack([np.array(c[k]) for c in ctrl]) if ctrl else None
            hi = C.max((0, 2)) if C is not None else None
            lo = C.min((0, 2)) if C is not None else None
            for s in steps:
                M = np.array(R[run][s][k])
                if k == "entropy":
                    exc = (lo[:, None] - M) if lo is not None else -M  # lower entropy than any control head in that layer
                else:
                    exc = (M - hi[:, None]) if hi is not None else M
                i = int(np.argmax(exc))
                l, h = divmod(i, M.shape[1])
                rows.append({"step": s, "measure": k, "head": f"{l}.{h}", "excess": round(float(exc.ravel()[i]), 3),
                             "value": round(float(M[l, h]), 3), "prev": round(R[run][s]["prev"][l][h], 3)})
        for s in steps:
            r = R[run][s]
            hubs = " ".join(f"{hh}:spr={r['spread_max'][int(hh.split('.')[0])][int(hh.split('.')[1])]:.1f}/"
                            f"ent={r['entropy'][int(hh.split('.')[0])][int(hh.split('.')[1])]:.2f}" for hh in HUB[run])
            top = [x for x in rows if x["step"] == s]
            print(f"{s:>7} loss={r['lm_loss']:.3f} outmax={r['max_out_logit']:.1f} | hubs {hubs} | "
                  + " ".join(f"{x['measure'][:7]}:{x['head']}(+{x['excess']:.2f},prev={x['prev']:.2f})" for x in top))
        out[run] = rows
    for c in CONTROLS:
        if c in R:
            print(f"\n== control {c}")
            for s in sorted(R[c]):
                r = R[c][s]
                l, h = map(int, HUB[c][0].split("."))
                print(f"{s:>7} loss={r['lm_loss']:.3f} outmax={r['max_out_logit']:.1f} hub {HUB[c][0]} spr={r['spread_max'][l][h]:.1f} ent={r['entropy'][l][h]:.2f} "
                      f"| global max spread {np.max(r['spread_max']):.1f} at {int(np.argmax(r['spread_max']))//16}.{int(np.argmax(r['spread_max']))%16}")
    (DIR / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
