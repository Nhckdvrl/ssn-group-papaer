#!/usr/bin/env python3
"""Paper F1 (page 1, single column): null-subtracted agreement ladder across three granularities.

x: POS-level route fingerprint / same-form context partition (T_D) / per-token causal role.
y: agreement above the matching null, deep layers L6-11 (E174):
   POS level  - real minus real-A vs N1-router(B)      (coarse_null.json; re-run at 3.2B, others at final)
   T_D        - real minus (form x UPOS) permutation   (td_null_3200000000_summary.json, pool U)
   per-token  - real minus (token id x UPOS) permutation (token_null_3200000000.json, pool LU)
Lines join the means of re-run / data-order / init pairs; dots are individual pairs; bars span pairs.
Variant "_raw" overlays the raw (not null-subtracted) values as thin light lines.

Usage: paper_fig_f1.py  -> results/paper_figs/f1_ladder.{pdf,png}, f1_ladder_raw.{pdf,png}
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]
E = WB / "results/e174"
OUT = WB / "results/paper_figs"
OUT.mkdir(parents=True, exist_ok=True)
G = ("rerun", "order", "init")


def kind(a, b):
    a, b = a.split("@")[0].replace(".npz", "").split("__")[0], b.split("@")[0].replace(".npz", "").split("__")[0]
    return "rerun" if b == a + "R" or a == b + "R" else "order" if a[:2] == b[:2] else "init"


levels = []  # list of {group: [(raw, excess), ...]}
# POS level
d = {}
for r in json.loads((E / "coarse_null.json").read_text())["results"]:
    if r["A"].endswith("@0"):
        continue
    real = np.mean([x["real"] for x in r["layers"]]); nb = np.mean([x["nullB_mean"] for x in r["layers"]])
    d.setdefault(kind(r["A"], r["B"]), []).append((real, real - nb))
levels.append(d)
# T_D
d = {}
for r in json.loads((E / "td_null_3200000000_summary.json").read_text())["results"]:
    x = r["pools"]["U_all"]["deep"]
    d.setdefault(r["group"], []).append((x["real"], x["excess"]))
levels.append(d)
# per-token
d = {}
for r in json.loads((E / "token_null_3200000000.json").read_text())["results"]:
    L = [x for x in r["layers"] if x["layer"] >= 6]
    d.setdefault(kind(r["A"], r["B"]), []).append((np.mean([x["real"] for x in L]), np.mean([x["pools"]["LU"]["excess"] for x in L])))
levels.append(d)

COL = {"rerun": "#1a1a1a", "order": "#4a7fb5", "init": "#c8553d"}
LAB = {"rerun": "re-run", "order": "data order", "init": "initialisation"}
OFF = {"rerun": -0.07, "order": 0.0, "init": 0.07}
XT = ["POS-level\nprofile", "same-form\npartition", "per-token\nrole"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42})


def draw(raw_overlay):
    fig, ax = plt.subplots(figsize=(3.3, 2.25))
    xs = np.arange(3)
    for g in G:
        ex = [np.array([v[1] for v in lv[g]]) for lv in levels]
        rw = [np.array([v[0] for v in lv[g]]) for lv in levels]
        x = xs + OFF[g]
        if raw_overlay:
            ax.plot(x, [r.mean() for r in rw], color=COL[g], lw=0.8, alpha=0.35, ls="--", zorder=1)
        ax.plot(x, [e.mean() for e in ex], color=COL[g], lw=1.4, zorder=3)
        for i, e in enumerate(ex):
            if len(e) > 1:
                ax.vlines(x[i], e.min(), e.max(), color=COL[g], lw=2.6, alpha=0.35, zorder=2)
            ax.scatter(np.full(len(e), x[i]), e, s=7, color=COL[g], zorder=4, linewidths=0)
        ax.text(x[-1] + 0.12, ex[-1].mean(), LAB[g], color=COL[g], va="center", fontsize=7)
    ax.axhline(0, color="#999999", lw=0.6, zorder=0)
    ax.set_xticks(xs, XT)
    ax.set_xlim(-0.3, 2.75)
    top = max(v[0] if raw_overlay else v[1] for lv in levels for g in G for v in lv[g])
    ax.set_ylim(-0.02, top * 1.08)
    ax.set_ylabel("agreement (L6–11)" if raw_overlay else "agreement above null (L6–11)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(pad=0.3)
    name = "f1_ladder_raw" if raw_overlay else "f1_ladder"
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


draw(False)
draw(True)
summ = {lvl: {g: {"excess_mean": float(np.mean([v[1] for v in lv[g]])), "raw_mean": float(np.mean([v[0] for v in lv[g]])),
                  "n_pairs": len(lv[g])} for g in G} for lvl, lv in zip(("pos", "partition", "token"), levels)}
for lvl in summ:
    summ[lvl]["init_over_rerun_excess"] = summ[lvl]["init"]["excess_mean"] / summ[lvl]["rerun"]["excess_mean"]
(OUT / "f1_data.json").write_text(json.dumps(summ, indent=1))
CAP = ("Figure 1: Agreement of expert division between independently trained MoEs, after subtracting the "
       "matching null at each granularity (POS level: a geometry-preserving random router; same-form partition "
       "and per-token role: permutation within UPOS cells, with the token identity kept at the per-token level), "
       "for re-runs of an identical configuration, data-order changes and initialisation changes; dots are pairs, "
       "and untrained models and all nulls sit at 0.")
(OUT / "f1_caption.txt").write_text(CAP + "\nVariant f1_ladder_raw: dashed light lines = raw values before subtraction.\n")
print(json.dumps(summ, indent=1))
