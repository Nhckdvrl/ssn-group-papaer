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
GROUPS = [("Surface pattern", ["stream", "case", "firstlast", "drop"], "#2a78d6", "o"),
          ("Numeric transformation", ["arith", "plus10", "plus1"], "#1baf7a", "s"),
          ("Lexical function", ["letter", "ant_syn", "fr_es", "fr_de"], "#4a3aa7", "D"),
          ("Input-routed mapping", ["parity_nat", "mag_nat", "sst", "condarith"], "#eb6834", "^")]
NAMES = {"stream": "label\nstream", "case": "upper↔\nreverse", "arith": "x±3", "plus10": "x±10", "plus1": "x±1",
         "letter": "next/prev\nletter", "parity_nat": "even/odd\n(flip)", "mag_nat": "small/large\n(flip)",
         "sst": "SST\n(flip)", "condarith": "class-cond.\n±2", "firstlast": "first/last\nletter",
         "drop": "drop first/\nlast", "ant_syn": "antonym↔\nsynonym", "fr_es": "EN→FR↔\nEN→ES", "fr_de": "EN→FR↔\nEN→DE"}
INK, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def main():
    d = pd.concat([pd.read_csv(f) for f in glob.glob(str(ROOT / "results" / "*" / "summary.csv"))
                   if "struct_pilot" not in f and "switch_core" not in f], ignore_index=True)
    d = d[~d.model.str.contains("_s0|_s1|_x4")].drop_duplicates(["model", "fmt"])
    fmts = [f for _, fs, _, _ in GROUPS for f in fs if f in set(d.fmt)]
    fig, axes = plt.subplots(2, 1, figsize=(13, 6.4), sharex=True, facecolor=SURF)
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
    axes[0].legend(handles=handles, frameon=False, fontsize=8, loc="upper right", ncol=4)
    n_models = d.model.nunique()
    fig.text(0.01, 0.005, f"Each point = one model ({n_models} models); bar = median. Paired design, 300 bases per format.",
             fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "fig_structure_selectivity.png", dpi=200); fig.savefig(OUT / "fig_structure_selectivity.pdf")
    print("saved", OUT / "fig_structure_selectivity.png", "models:", sorted(d.model.unique()))


if __name__ == "__main__":
    main()


def regime_map():
    d = pd.concat([pd.read_csv(f) for f in glob.glob(str(ROOT / "results" / "*" / "summary.csv"))
                   if "struct_pilot" not in f and "switch_core" not in f], ignore_index=True)
    d = d[~d.model.str.contains("_s0|_s1|_x4")].drop_duplicates(["model", "fmt"])
    if "recn" not in d:
        print("rerun summaries with recn"); return
    kinds = {"stream": 0, "case": 0, "firstlast": 0, "drop": 0, "arith": 1, "plus10": 1, "plus1": 1,
             "letter": 1, "ant_syn": 1, "fr_es": 1, "fr_de": 1,
             "parity_nat": 2, "mag_nat": 2, "sst": 2, "condarith": 2}
    cols = [("#2a78d6", "o", "surface pattern rule"), ("#1baf7a", "s", "relational / lexical function"),
            ("#eb6834", "^", "input-routed mapping")]
    fig, ax = plt.subplots(figsize=(6.4, 4.8), facecolor=SURF); ax.set_facecolor(SURF)
    ax.axhline(0, color=MUTED, lw=1); ax.axvline(0, color=MUTED, lw=1)
    for f, k in kinds.items():
        x = d[d.fmt == f]
        if x.empty:
            continue
        c, mk, _ = cols[k]
        ax.scatter(x.recn.clip(-0.3, 1.5), x.NDIn.clip(-1.6, 1.8), s=26, color=c, marker=mk, edgecolor=SURF, lw=1, zorder=3)
        ax.annotate(f, (x.recn.median(), x.NDIn.median()), fontsize=7, color=INK, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("positional weighting: (last − first single flip) / |baseline|", fontsize=8, color=INK)
    ax.set_ylabel("noise-direction index (+ normative)", fontsize=8, color=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=7)
    handles = [plt.Line2D([], [], marker=mk, ls="", color=c, markersize=6, label=l) for c, mk, l in cols]
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="upper left")
    ax.text(0.98, 0.04, "recency only", transform=ax.transAxes, ha="right", fontsize=8, color=MUTED)
    ax.text(0.98, 0.94, "change-point-like", transform=ax.transAxes, ha="right", fontsize=8, color=MUTED)
    ax.text(0.02, 0.04, "exchangeable set", transform=ax.transAxes, ha="left", fontsize=8, color=MUTED)
    fig.tight_layout(); fig.savefig(OUT / "fig_regime_map.png", dpi=200); fig.savefig(OUT / "fig_regime_map.pdf")
    print("saved regime map")


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "map":
    regime_map()
