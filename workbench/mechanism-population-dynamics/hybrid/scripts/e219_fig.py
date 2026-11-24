#!/usr/bin/env python3
"""E219 figure: per-layer dNLL when one component's cross-token path is cut in one layer, 10 models as small multiples.
Columns = family (OLMo, Granite, Qwen, distillation, Falcon); top row = recurrent/hybrid member, bottom = reference.
Usage: e219_fig.py SUMMARY_JSON OUT_PNG"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = json.load(open(sys.argv[1]))
GRID = [["H", "GH", "QH", "Llamba", "FH3"], ["T", "GT", "QT", "L1B", "FM"]]
NAME = {"H": "OLMo-Hybrid-7B", "T": "OLMo-3-7B", "GH": "Granite-4.0-H-micro", "GT": "Granite-4.0-micro",
        "QH": "Qwen3.5-4B", "QT": "Qwen3-4B", "Llamba": "Llamba-1B (distilled)", "L1B": "Llama-3.2-1B (teacher)",
        "FH3": "Falcon-H1-3B", "FM": "Falcon-Mamba-7B"}
COL = {"conv": "#2a78d6", "mem": "#eb6834", "attn": "#1baf7a"}
LAB = {"conv": "short conv", "mem": "recurrent state", "attn": "attention"}
YMAX = 1.2
plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#8a8984", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 9.5})
fig, axes = plt.subplots(2, 5, figsize=(14, 5.2), sharey=True)
for r, row in enumerate(GRID):
    for c, m in enumerate(row):
        ax = axes[r][c]; d = S[m]; L = d["n_layers"]
        for comp in ("conv", "mem", "attn"):
            if comp not in d["profile"]:
                continue
            pts = [(l, v) for l, v in enumerate(d["profile"][comp]) if v is not None]
            xs, ys = [p[0] for p in pts], [min(p[1], YMAX) for p in pts]
            sparse = len(pts) < L / 2
            ax.plot(xs, ys, color=COL[comp], lw=2 if not sparse else 1.2, marker="o" if sparse else None, ms=4,
                    label=LAB[comp], solid_capstyle="round", zorder=3 if comp == "conv" else 2)
            clipped = [(l, v) for l, v in pts if v > YMAX]
            if clipped:
                txt = "clipped: " + ", ".join(f"L{l} {v:.2f}" for l, v in clipped)
                ax.text(clipped[-1][0] + 1, YMAX * 0.97, txt, fontsize=7.5, color="#0b0b0b", va="top")
        ax.set_title(NAME[m], color="#0b0b0b")
        ax.set_xlim(-0.5, L - 0.5); ax.set_ylim(-0.05, YMAX)
        ax.axhline(0, color="#d6d5cf", lw=0.8, zorder=1)
        ax.grid(axis="y", color="#ecebe7", lw=0.6); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if c == 0:
            ax.set_ylabel("ΔNLL (nats / token)")
        if r == 1:
            ax.set_xlabel("layer")
h, l = [], []
for ax in axes.flat:
    for hh, ll in zip(*ax.get_legend_handles_labels()):
        if ll not in l:
            h.append(hh); l.append(ll)
fig.legend(h, l, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
fig.text(0.5, -0.01, "One layer, one component: its cross-token path is cut (conv: neighbour taps mean-replaced; state: current token only; "
         "attention: attend to self). Values above 1.2 are clipped and printed.", ha="center", fontsize=8, color="#52514e")
fig.tight_layout(rect=(0, 0.01, 1, 0.95))
fig.savefig(sys.argv[2], dpi=160, bbox_inches="tight", facecolor="#fcfcfb")
