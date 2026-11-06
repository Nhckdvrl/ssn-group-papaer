#!/usr/bin/env python3
"""E173 figure from results/e173/summary.json.
Left: deep (L6-11) T_D at 8e8 per recipe (bar = seed0 vs seed1 pair, tick = the recipe's own step-0 floor),
grey band = baseline 15 only-init pairs (min-max). Right: deep T_D vs tokens per recipe, same band per token count.
Usage: e173_figure.py [L11]   (default deep mean; "L11" plots the last layer instead)
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WB = Path(__file__).resolve().parents[1]
S = json.loads((WB / "results/e173/summary.json").read_text())
KEY = "L11" if len(sys.argv) > 1 and sys.argv[1] == "L11" else "deep"
COL = {"rerun": "#008300", "base": "#52514e", "frz": "#2a78d6", "lb0": "#eb6834", "lb0001": "#e87ba4", "g16": "#1baf7a", "g256": "#eda100", "lb01": "#6250d6",
       "g16r": "#7fd4b5", "g256r": "#f5cd73"}
NAME = {"rerun": "I0D0 rerun (A100)", "base": "baseline", "frz": "(e) frozen router", "lb0": "(a) lb=0", "lb0001": "(a') lb=1e-3", "g16": "(c) 16e top-2",
        "g256": "(d) 256e top-32", "lb01": "(b) lb=0.1", "g16r": "16e rerun", "g256r": "256e rerun"}
rec = {k: v for k, v in S["recipes"].items() if "800000000" in v["routing"]}
rule = S["ruler_15pairs"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.4), gridspec_kw={"width_ratios": [1.1, 1]})
r8 = rule["800000000"][KEY]
a1.axhspan(r8[0], r8[2], color="#d9d8d3", lw=0, zorder=0)
a1.text(max(len(rec), 6) - 0.5, r8[2], "baseline 15 init pairs", ha="right", va="bottom", fontsize=7.5, color="#52514e")
a1.set_xlim(-0.6, max(len(rec), 6) - 0.4)
for i, (k, v) in enumerate(rec.items()):
    t8 = v["routing"]["800000000"]
    a1.bar(i, t8[KEY], width=0.6, color=COL[k], zorder=2)
    if KEY == "L11":
        lo, hi = t8["L11_ci"]
        a1.plot([i, i], [lo, hi], color="#0b0b0b", lw=1, zorder=3)
    if "0" in v["routing"]:
        a1.plot([i - 0.3, i + 0.3], [v["routing"]["0"][KEY]] * 2, color="#0b0b0b", lw=1.5, ls=":", zorder=3)
    top = max(t8[KEY], t8["L11_ci"][1]) if KEY == "L11" else t8[KEY]
    a1.text(i, top + 0.005, f"{t8[KEY]:.2f}", ha="center", va="bottom", fontsize=7.5, color="#0b0b0b")
a1.set_xticks(range(len(rec)), [NAME[k] for k in rec], rotation=25, ha="right")
a1.axhline(0, color="#0b0b0b", lw=0.6)
a1.set_ylabel(f"T_D ({'layer 11' if KEY == 'L11' else 'deep mean L6-11'}), 8e8 tokens")
a1.set_title("Cross-init division agreement by recipe (dotted = own step-0 floor)", fontsize=9, loc="left")
toks = sorted(int(t) for t in rule)
a2.fill_between([t / 1e8 for t in toks], [rule[str(t)][KEY][0] for t in toks], [rule[str(t)][KEY][2] for t in toks], color="#d9d8d3", lw=0)
for k, v in rec.items():
    ts = sorted(int(t) for t in v["routing"] if int(t) > 0)
    a2.plot([t / 1e8 for t in ts], [v["routing"][str(t)][KEY] for t in ts], marker="o", ms=4, lw=2 if k != "base" else 2.5,
            color=COL[k], label=NAME[k])
a2.set_xscale("log", base=2)
a2.set_xticks([1, 2, 4, 8], ["1e8", "2e8", "4e8", "8e8"])
a2.set_xlabel("training tokens")
a2.set_title("Formation curves (band = baseline 15 init pairs)", fontsize=9, loc="left")
a2.legend(frameon=False, fontsize=7.5, loc="upper left")
fig.tight_layout()
out = WB / f"results/e173/recipe_td_{KEY}.png"
fig.savefig(out, dpi=170)
print("saved", out)
