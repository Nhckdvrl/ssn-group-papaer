#!/usr/bin/env python3
"""Paper F4 (double column): do published single-checkpoint expert readouts survive a change of seed? (E176)

Three columns = levels; rows = readouts (short names); one marker per run pair:
  dot = init pair (15), triangle = data-order pair (2), star = re-run (1), cross = step-0 (untrained) pair.
Model level : |value_A - value_B| / |init mean - step-0 mean| (pairwise analogue of R_m; small = reproduced; log x).
Class level : Spearman rho of the expert-index-free profile between the two runs.
Expert level: rho after Hungarian matching of experts (cross-fitted over document halves).
No verdict text in the figure; q and R_m are explained in the caption.

Usage: paper_fig_f4.py -> results/paper_figs/f4_readouts.{pdf,png}
"""
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]
S = json.loads((WB / "results/e176/summary.json").read_text())
OUT = WB / "results/paper_figs"
OUT.mkdir(parents=True, exist_ok=True)

SHORT = {
    "model": {"1": "saturation, top-8", "1k1": "saturation, top-1", "2": "co-activation ≥ .5",
              "3": "max domain lift", "6": "UPOS routing entropy", "7": "word-form purity",
              "13spec": "DBES S_spec", "13reff": "DBES R_eff", "13iso": "DBES S_iso", "8": "Spec_POS"},
    "class": {"1": "saturation by UPOS", "3": "deviation by layer × genre", "6": "entropy by UPOS",
              "7": "purity by word form", "13spec": "S_spec by genre", "13iso": "S_iso by genre pair",
              "8": "Spec_POS by UPOS"},
    "expert": {"1": "saturation", "2": "co-activation matrix", "3": "domain lift", "6": "P(expert | UPOS)",
               "7": "top-10 word forms", "8": "KL(P(c|e) ‖ P(c))"},
}
TITLE = {"model": "model level", "class": "class level", "expert": "expert level"}
XLAB = {"model": "|Δ| / training effect", "class": "Spearman ρ", "expert": "ρ after matching"}
C = {"init": "#c8553d", "order": "#4a7fb5", "rerun": "#1a1a1a", "floor": "#8c8c8c"}
MK = {"init": ("o", 9), "order": ("^", 16), "rerun": ("*", 34), "floor": ("x", 12)}

INIT = [f"I{i}D0" for i in range(6)]
ORDER = [("I0D0", "I0D1"), ("I1D0", "I1D1")]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42})
rows = {lev: [k for k in SHORT[lev] if k in S[lev]] for lev in SHORT}
fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.6), gridspec_kw={"width_ratios": [1, 1, 1]})
rng = np.random.default_rng(0)
data_out = {}
for ax, lev in zip(axes, ("model", "class", "expert")):
    ks = rows[lev]
    for yi, k in enumerate(ks):
        y = len(ks) - 1 - yi
        c = S[lev][k]
        if lev == "model":
            v, fv = c["values"], c["floor_values"]
            gap = abs(c["init_mean"] - c["floor_mean"])
            pts = {"init": [abs(v[a] - v[b]) / gap for a, b in itertools.combinations(INIT, 2)],
                   "order": [abs(v[a] - v[b]) / gap for a, b in ORDER],
                   "rerun": [abs(v["I4D0"] - v["I4D0R"]) / gap],
                   "floor": [abs(fv[a] - fv[b]) / gap for a, b in itertools.combinations(sorted(fv), 2)]}
            pts = {g: [max(x, 1e-3) for x in p] for g, p in pts.items()}
        else:
            pts = {"init": c["init"], "order": c["order"], "rerun": [c["rerun"]], "floor": c["floor"] or []}
        data_out[f"{lev}/{k}"] = pts
        for g in ("floor", "init", "order", "rerun"):
            p = np.asarray(pts[g], float)
            if not len(p):
                continue
            jit = rng.uniform(-0.12, 0.12, len(p)) if len(p) > 2 else np.zeros(len(p))
            m, s = MK[g]
            ax.scatter(p, y + jit, marker=m, s=s, color=C[g], linewidths=0.7 if m == "x" else 0,
                       alpha=0.75 if g in ("init", "floor") else 1, zorder=3 if g != "floor" else 2)
    ax.set_yticks(range(len(ks)), [SHORT[lev][k] for k in reversed(ks)])
    ax.set_ylim(-0.6, len(ks) - 0.4)
    ax.set_title(TITLE[lev], fontsize=7.5, pad=3)
    ax.set_xlabel(XLAB[lev])
    if lev == "model":
        ax.set_xscale("log")
        ax.set_xlim(8e-4, 3)
    else:
        ax.set_xlim(-0.15, 1.05)
    ax.grid(axis="y", color="#eeeeee", lw=0.5, zorder=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
# one shared legend, bottom
from matplotlib.lines import Line2D  # noqa: E402
h = [Line2D([], [], marker=MK[g][0], ls="", color=C[g], markersize=(4 if g != "rerun" else 6.5), markeredgewidth=0.8)
     for g in ("init", "order", "rerun", "floor")]
fig.legend(h, ["initialisation pair", "data-order pair", "re-run", "untrained pair"], loc="lower center",
           ncol=4, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(pad=0.3, rect=(0, 0.06, 1, 1))
fig.savefig(OUT / "f4_readouts.pdf")
fig.savefig(OUT / "f4_readouts.png", dpi=300)
(OUT / "f4_data.json").write_text(json.dumps(data_out, indent=1))
CAP = ("Figure 4: Published single-checkpoint readouts of expert behaviour (rows) recomputed on nine runs, at the "
       "model level (pairwise difference relative to the training effect, i.e. init mean minus untrained mean; "
       "R_m = range over six initialisations / training effect), the class level (correlation of expert-index-free "
       "profiles) and the expert level (correlation after matching experts); one marker per run pair, and "
       "q = (ρ_init − ρ_untrained) / (ρ_re-run − ρ_untrained) is the fraction of the re-run ceiling that an "
       "initialisation change retains.")
(OUT / "f4_caption.txt").write_text(CAP + "\n")
print("saved")
