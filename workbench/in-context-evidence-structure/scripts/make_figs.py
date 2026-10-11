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


def marked_fig():
    import json as _j
    meta = {}
    for l in open(ROOT / "data/marked/rows.jsonl"):
        r = _j.loads(l); meta[r["uid"]] = (r["cond"], r["base_id"], r["oracle"]["meta_pB"])
    pats = ["allA", "single_16", "disp_4", "suffix_4", "noise_2__suffix_3", "prefix_8", "suffix_8"]
    names = {"allA": "no\nchange", "single_16": "1 late\nflip", "disp_4": "4 scattered", "suffix_4": "4 at end",
             "noise_2__suffix_3": "3 at end +\n2 scattered", "prefix_8": "8 first\n(stale)", "suffix_8": "8 last"}
    models = ["Qwen3-8B", "Qwen2.5-7B", "Mistral-7B-v0.3"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True, facecolor=SURF)
    for ax, fm, title in ((axes[0], "mag_nat", "Numbers: small / large"), (axes[1], "sst", "Reviews: positive / negative")):
        ax.set_facecolor(SURF)
        orc = {}
        for mi, m in enumerate(models):
            fs = glob.glob(str(ROOT / f"results/marked/{m}.s*.jsonl"))
            if not fs:
                continue
            rec = []
            for f in fs:
                for l in open(f):
                    s = _j.loads(l); c, b, mo = meta[s["uid"]]
                    if not c.startswith(fm):
                        continue
                    p = np.exp(np.array(s["lp"])); p = p / p.sum()
                    rec.append((c.split(":")[1], p[2] + p[3], p[1] + p[3], mo))
            D = pd.DataFrame(rec, columns=["pat", "upper", "newmap", "meta"]).groupby("pat").mean()
            xs = np.arange(len(pats))
            ax.plot(xs + (mi - 1) * 0.08, D.loc[pats, "upper"], marker="o", ms=5, lw=1.6, color="#2a78d6", alpha=0.9,
                    label="writes new format (upper case)" if mi == 0 else None)
            ax.plot(xs + (mi - 1) * 0.08, D.loc[pats, "newmap"], marker="^", ms=5, lw=1.6, color="#eb6834", alpha=0.9,
                    label="uses new mapping" if mi == 0 else None)
            orc = D.loc[pats, "meta"]
        ax.plot(np.arange(len(pats)), orc, color=INK, lw=1.2, ls=(0, (3, 3)), label="Bayes: P(new regime)")
        ax.set_xticks(range(len(pats))); ax.set_xticklabels([names[p] for p in pats], fontsize=7)
        ax.set_title(title, loc="left", fontsize=10, color=INK); ax.set_ylim(-0.02, 1.02)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=7)
    axes[0].set_ylabel("probability at the query", fontsize=8, color=INK)
    axes[0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.text(0.01, 0.01, "New-regime demos are written in upper case AND use the reversed mapping. Lines = 3 models (Qwen3-8B, Qwen2.5-7B, Mistral-7B), 300 bases each.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT / "fig_marked_drift.png", dpi=200); fig.savefig(OUT / "fig_marked_drift.pdf")
    print("saved marked fig")


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "marked":
    marked_fig()


def local_fig():
    import json as _j
    meta = {}
    for l in open(ROOT / "data/local_nat/rows.jsonl"):
        r = _j.loads(l); meta[r["uid"]] = r
    models = ["Qwen3-8B", "Qwen2.5-7B", "Mistral-7B-v0.3"]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.3), sharey=True, facecolor=SURF)
    for ax, m in zip(axes, models):
        ax.set_facecolor(SURF)
        rec = []
        for f in glob.glob(str(ROOT / f"results/local_nat/{m}.s*.jsonl")):
            for l in open(f):
                s = _j.loads(l); r = meta[s["uid"]]
                p = np.exp(np.array(s["lp"])); p = p / p.sum()
                pat = r["cond"].split(":")[1]
                # B = later regime in suffix_8, earlier regime in prefix_8
                p_last = p[r["query_label_B"]] if pat == "suffix_8" else p[r["query_label_A"]]
                pm = r["oracle"]["meta_pB"]; pm_last = pm if pat == "suffix_8" else 1 - pm
                rec.append((pat, r["qrank"], p_last, pm_last))
        D = pd.DataFrame(rec, columns=["pat", "q", "plast", "bayes"])
        D = D[D.pat.isin(["suffix_8", "prefix_8"])].groupby(["pat", "q"]).mean()
        pats = ["suffix_8", "prefix_8"]; lab = {"suffix_8": "mapping 1 → mapping 2", "prefix_8": "mapping 2 → mapping 1"}
        x = np.arange(2); w = 0.36
        ax.bar(x - w / 2, [D.loc[(p, "near"), "plast"] for p in pats], w * 0.92, color="#2a78d6", label="query resembles the last 8 demos")
        ax.bar(x + w / 2, [D.loc[(p, "far"), "plast"] for p in pats], w * 0.92, color="#eb6834", label="query resembles the first 8 demos")
        ax.axhline(D.bayes.mean(), color=INK, lw=1.2, ls=(0, (3, 3)), label="Bayes (both queries)")
        ax.axhline(0.5, color=MUTED, lw=0.8)
        ax.set_xticks(x); ax.set_xticklabels([lab[p] for p in pats], fontsize=8); ax.set_ylim(0, 1)
        ax.set_title(m, loc="left", fontsize=9, color=INK)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=7)
    axes[0].set_ylabel("P(answer follows the LAST 8 demos)", fontsize=8, color=INK)
    axes[0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.text(0.01, 0.01, "Numbers small/large, natural labels; first 8 demos use one mapping, last 8 the reversed one. 300 bases x 2 classes per model.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT / "fig_nearest_not_newest.png", dpi=200); fig.savefig(OUT / "fig_nearest_not_newest.pdf")
    print("saved local fig")


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "local":
    local_fig()
