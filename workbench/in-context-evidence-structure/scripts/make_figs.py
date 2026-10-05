"""Figure: per-format structure selectivity across models (global rules vs relational functions vs
input-routed mappings).  Reads results/*/summary.csv (summarize_switch.py outputs)."""
import glob
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figs"; OUT.mkdir(parents=True, exist_ok=True)
GROUPS = [("Global rule", ["stream", "case"], "#2a78d6", "o"),
          ("Relational function", ["arith", "plus10", "plus1", "letter"], "#1baf7a", "s"),
          ("Input-routed mapping", ["parity_nat", "mag_nat", "sst", "condarith"], "#eb6834", "^")]
NAMES = {"stream": "label\nstream", "case": "upper↔\nreverse", "arith": "x±3", "plus10": "x±10", "plus1": "x±1",
         "letter": "next/prev\nletter", "parity_nat": "even/odd\n(flip)", "mag_nat": "small/large\n(flip)",
         "sst": "SST\n(flip)", "condarith": "class-cond.\n±2"}
INK, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def main():
    d = pd.concat([pd.read_csv(f) for f in glob.glob(str(ROOT / "results" / "*" / "summary.csv"))
                   if "struct_pilot" not in f and "switch_core" not in f], ignore_index=True)
    d = d[~d.model.str.contains("_s0|_s1|_x4")].drop_duplicates(["model", "fmt"])
    fmts = [f for _, fs, _, _ in GROUPS for f in fs if f in set(d.fmt)]
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True, facecolor=SURF)
    for ax, col, title in ((axes[0], "CSIn", "Clustering selectivity (0 = exchangeable set, 1 = Bayes oracle)"),
                           (axes[1], "NDIn", "Noise-direction index (+ = normative, − = opposite to oracle)")):
        ax.set_facecolor(SURF)
        ax.axhline(0, color=MUTED, lw=1); ax.axhline(1, color=MUTED, lw=1, ls=(0, (3, 3)))
        for gname, fs, colr, mk in GROUPS:
            for f in fs:
                if f not in fmts:
                    continue
                x = fmts.index(f)
                v = d[d.fmt == f][col].values
                jit = np.linspace(-0.18, 0.18, len(v)) if len(v) > 1 else [0]
                ax.scatter(x + np.array(jit), v, s=36, color=colr, marker=mk, edgecolor=SURF, linewidth=1.5, zorder=3)
                ax.plot([x - 0.28, x + 0.28], [np.median(v)] * 2, color=INK, lw=2, zorder=4)
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=8)
    axes[1].set_xticks(range(len(fmts))); axes[1].set_xticklabels([NAMES[f] for f in fmts], fontsize=8)
    handles = [plt.Line2D([], [], marker=mk, ls="", color=c, markersize=7, label=g) for g, _, c, mk in GROUPS]
    axes[0].legend(handles=handles, frameon=False, fontsize=8, loc="upper right", ncol=3)
    n_models = d.model.nunique()
    fig.text(0.01, 0.005, f"Each point = one model ({n_models} models); bar = median. Paired design, 300 bases per format.",
             fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "fig_structure_selectivity.png", dpi=200); fig.savefig(OUT / "fig_structure_selectivity.pdf")
    print("saved", OUT / "fig_structure_selectivity.png", "models:", sorted(d.model.unique()))


if __name__ == "__main__":
    main()
