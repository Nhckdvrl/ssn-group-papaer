#!/usr/bin/env python3
"""E176 figure: published readouts x three levels. Points = runs (model level) or run pairs (class / expert level);
step 0 = floor (grey), rerun I4D0/I4D0R = ceiling (red star), order-only pairs (orange), init-only (blue).
-> results/e176/e176_figure.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]
OUT = WB / "results/e176"
S = json.loads((OUT / "summary.json").read_text())
INITS = [f"I{i}D0" for i in range(6)]
rng = np.random.default_rng(0)
EN = {"重现": "reproduces", "部分": "partial", "不重现": "does not reproduce", "训练不改变此量": "training does not move it",
      "地板≈上限，此级不可判": "floor ≈ ceiling", "重跑也低于 .5（读数本身噪声大）": "rerun < .5 (noisy)", "无地板（只报原值）": "no floor"}

fig, axs = plt.subplots(1, 3, figsize=(19, 7), gridspec_kw={"width_ratios": [1.15, 1, 1]})
# ---- A: model level, normalised: step-0 mean = 0, init mean = 1
a = axs[0]
rows = [k for k in ["1", "1k1", "2", "3", "6", "7", "8", "13spec", "13reff", "13iso"] if "floor_mean" in S["model"][k]]
for y, k in enumerate(rows):
    m = S["model"][k]
    f0, mi = m["floor_mean"], m["init_mean"]
    nz = lambda v: (v - f0) / (mi - f0)
    a.scatter([nz(v) for v in m["floor_values"].values()], y + rng.uniform(-.15, .15, len(m["floor_values"])), c="0.6", marker="x", s=22)
    a.scatter([nz(m["values"][r]) for r in INITS], y + rng.uniform(-.15, .15, 6), c="tab:blue", s=16)
    a.scatter([nz(m["values"][r]) for r in ("I0D1", "I1D1")], [y + .25] * 2, c="tab:orange", marker="^", s=22)
    a.scatter([nz(m["values"]["I4D0R"])], [y - .25], c="red", marker="*", s=60)
a.set_yticks(range(len(rows)))
a.set_yticklabels([f"#{k} {S['model'][k]['name'][:46]}\n→ R_m={S['model'][k]['R_m']:.2f}, {EN[S['model'][k]['verdict']]}" for k in rows], fontsize=7)
a.axvline(0, c="0.6", lw=.8, ls=":"); a.axvline(1, c="tab:blue", lw=.8, ls=":")
a.set_xlabel("(value − step-0 mean) / (init mean − step-0 mean)")
a.set_title("A  Model level (one value per run)", loc="left")


def pairs_panel(ax, block, order, title):
    for y, k in enumerate(order):
        c = S[block][k]
        ax.scatter(c["floor"], y + rng.uniform(-.15, .15, len(c["floor"])), c="0.6", marker="x", s=22)
        ax.scatter(c["init"], y + rng.uniform(-.15, .15, len(c["init"])), c="tab:blue", s=16)
        ax.scatter(c["order"], [y + .25] * len(c["order"]), c="tab:orange", marker="^", s=22)
        ax.scatter([c["rerun"]], [y - .25], c="red", marker="*", s=60)
    lab = []
    for k in order:
        c = S[block][k]; q = c["q"]
        lab.append(f"#{k} {c['name'][:44]}\n→ " + (f"q={q:.2f}, " if q == q else "") + EN[c["verdict"]])
    ax.set_yticks(range(len(order))); ax.set_yticklabels(lab, fontsize=7)
    ax.set_xlim(-.6, 1.05); ax.axvline(0, c="0.8", lw=.6)
    ax.set_xlabel("cross-run correlation"); ax.set_title(title, loc="left")


pairs_panel(axs[1], "class", ["1", "3", "6", "7", "8", "13spec", "13iso"], "B  Class level (id-free profiles)")
pairs_panel(axs[2], "expert", ["1", "2", "3", "6", "7", "8"], "C  Expert level (matched, cross-fit)")
h = [plt.Line2D([], [], ls="", marker="o", c="tab:blue", label="init-only (runs / 15 pairs)"),
     plt.Line2D([], [], ls="", marker="^", c="tab:orange", label="order-only (2)"),
     plt.Line2D([], [], ls="", marker="*", c="red", ms=10, label="rerun I4D0/I4D0R (ceiling)"),
     plt.Line2D([], [], ls="", marker="x", c="0.6", label="step 0 (floor)")]
fig.legend(handles=h, loc="lower center", ncol=4, fontsize=8.5, frameon=False)
fig.suptitle("E176  Published single-model MoE readouts on 9 runs: which level survives a change of init seed (anchors, 3.2B tokens, mean over 12 layers)",
             fontsize=10.5)
fig.tight_layout(rect=[0, .05, 1, .96])
fig.savefig(OUT / "e176_figure.png", dpi=150)
print("saved", OUT / "e176_figure.png")
