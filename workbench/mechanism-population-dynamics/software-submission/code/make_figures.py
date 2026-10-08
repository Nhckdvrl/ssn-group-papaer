"""Figures for the ACL version of the paper (outputs/figures/*.pdf), drawn from finished analyses only.
  fig1_hook        crossing_1b (which-head agreement among all 75 1B models, ordered by seed) + habit_templates (Flan effect by template)
  fig2_innate      crossing_sizes / pythia_small / pythia_large (agreement by size), seed_identification (seed identification), coordinates_vs_content / more_roles (coordinates vs content)
  fig3_critical    controlled_pretraining / controlled_pretraining (branching), lockin_pythia / controlled_pretraining / pythia_large (lock-in during training)
  fig4_flan        habit_templates (Flan effect by template), flan_layout (head layout and habit map with / without Flan)
  fig4_question    (appendix) habit_sizes + habit_templates (sizes), habit_pretraining (pretraining), habit_olmo2_public (OLMo 2 mid-training), habit_popqa / habit_nqswap (other datasets)
  fig5_content     content_vs_function_words (content vs function words; per-pair file written by content_vs_function_words.py)
  figA_temperature sgd_temperature / its larger-batch runs + crossing_sizes (appendix)
  figA_warmup      warmup_window (appendix: warm-up length and optimizer reset)
Sizes are the printed sizes (column 3.03 in, text 6.3 in), fonts are Liberation Serif / Mono (TrueType, Times metrics;
embedded as Type 42, as aclpubcheck rejects Type 3 fonts), colours are Okabe-Ito: shared initialization = vermillion, shared corpus = green."""
import glob
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np

import common as mc
R = mc.RESULTS
OUT = mc.WB / "outputs" / "figures"
COL, TXT = 3.03, 6.3
SEED, ACQ, OTHER, PYTH, BLUE, SKY = "#D55E00", "#009E73", "#8C8C8C", "#7B5EA7", "#0072B2", "#56B4E9"
LIGHT, INK, GRID, CP = "#CFCFCF", "#262626", "#E9E9E9", "#FBE3D6"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Liberation Serif", "DejaVu Serif"],
    "font.monospace": ["Liberation Mono", "DejaVu Sans Mono"], "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Serif", "mathtext.it": "Liberation Serif:italic", "mathtext.bf": "Liberation Serif:bold",
    "font.size": 7.5, "axes.titlesize": 7.5, "axes.labelsize": 7.3, "xtick.labelsize": 6.6, "ytick.labelsize": 6.6,
    "legend.fontsize": 6.4, "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.4,
    "ytick.major.size": 2.4, "xtick.minor.size": 1.3, "ytick.minor.size": 1.3, "xtick.major.pad": 1.8,
    "ytick.major.pad": 1.8, "lines.linewidth": 1.25, "lines.markersize": 3.6, "lines.markeredgewidth": 0.5,
    "pdf.fonttype": 42, "axes.titlepad": 4, "axes.labelpad": 2, "axes.axisbelow": True,
    "axes.titlelocation": "left", "axes.titleweight": "bold"})


def save(fig, name):
    """Saved at exactly the figure size, which is the printed size: \\includegraphics[width=\\columnwidth] or
    [width=\\textwidth] then applies no scaling, so the 6-7.5 pt fonts print at their nominal size."""
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=250)
    plt.close(fig)


def axes_in(fig, l, b, w, h):
    """Add axes at a position given in inches from the lower-left corner."""
    W, H = fig.get_size_inches()
    return fig.add_axes([l / W, b / H, w / W, h / H])


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, lw=0.5, zorder=0)


def logx_params(ax, ticks=(1e7, 1e8, 1e9, 1e10)):
    ax.set_xscale("log")
    ax.set_xticks(list(ticks))
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v / 1e6:g}M" if v < 1e9 else f"{v / 1e9:g}B"))
    ax.xaxis.set_minor_formatter(mt.NullFormatter())


def pct(ax):
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{100 * v:g}%"))
    ax.xaxis.set_minor_formatter(mt.NullFormatter())


def title(ax, letter, text, x=-0.02):
    ax.set_title(f"({letter}) {text}", fontsize=7.3, loc="left", x=x)


def line(ax, x, y, color, marker="o", ls="-", **kw):
    ax.plot(x, y, ls=ls, color=color, marker=marker, mec="white", mew=0.5, zorder=3, **kw)


def tag(ax, x, y, s, color, ha="left", va="center", size=6.4, **kw):
    ax.text(x, y, s, color=color, ha=ha, va=va, fontsize=size, **kw)


# ---------------------------------------------------------------- Fig 1
SEEDS_1B = ["default", "large-aux-2", "large-aux-3"]
MINUS = "−"


def signed(v):
    return f"{v:+.2f}".replace("-", MINUS)


def fig1_hook():
    """(a) Which-head agreement between all 75 1B models (3 seeds x 25 corpora), ordered by seed then corpus, mean of
    the induction, previous-token and retrieval maps (induction only for models with an induction head). The six runs
    with an unlisted initialization (paper Appendix A) are kept and marked; the printed means exclude them. (b) habit_templates: Flan - no-Flan
    effect on context trust by template (1B, mean +- SE over seeds)."""
    from similarity import within_matrix
    files = {}
    for s in SEEDS_1B:
        for f in sorted(glob.glob(str(R / "crossing_1b" / f"*-1B__{s}.json"))):
            if "step" not in f:
                files[(f.split("/")[-1].split("-1B__")[0], s)] = f
    corpora = sorted({c for c, _ in files if all((c, s) in files for s in SEEDS_1B)})
    keys = [(c, s) for s in SEEDS_1B for c in corpora]
    J = [json.loads(open(files[k]).read()) for k in keys]
    Ms = []
    for m in ("M1", "M2", "M4"):
        W = within_matrix([j["maps"][m] for j in J])
        if m == "M1":
            ok = np.array([j["M1_max"] > 0.3 for j in J])
            W[~ok, :] = np.nan
            W[:, ~ok] = np.nan
        Ms.append(W)
    S = np.nanmean(np.stack(Ms), 0)
    np.fill_diagonal(S, np.nan)
    n = len(corpora)
    bad = [i for i, k in enumerate(keys) if k in mc.UNVERIFIED_1B]
    good = [i for i in range(3 * n) if i not in bad]
    si = np.nanmean([S[i, j] for i in good for j in good if i // n == j // n and i != j])
    sd = np.nanmean([S[i, j] for i in good for j in good if i // n != j // n and i % n == j % n])

    fig = plt.figure(figsize=(COL, 3.3))
    fig.text(0.0, 3.25 / 3.3, "(a) Which head takes a role, 75 models at 1B", fontsize=7.4, fontweight="bold", va="top")
    ax = axes_in(fig, 0.2, 1.36, 1.68, 1.68)
    cmap = plt.get_cmap("magma").copy()
    cmap.set_bad("#F2F2F2")
    im = ax.imshow(S, cmap=cmap, vmin=0, vmax=0.5, interpolation="nearest")
    for b in (n, 2 * n):
        ax.axhline(b - 0.5, color="white", lw=0.9)
        ax.axvline(b - 0.5, color="white", lw=0.9)
    for i in bad:  # runs whose initialization differs from their seed label (verified from weights, App. A)
        ax.plot([-1.9], [i], marker=">", color=INK, ms=2.5, clip_on=False, mew=0)
    ax.set_xticks([n / 2 - 0.5 + i * n for i in range(3)], [f"init. {i + 1}" for i in range(3)])
    ax.set_yticks([n / 2 - 0.5 + i * n for i in range(3)], [f"init. {i + 1}" for i in range(3)], rotation=90, va="center")
    ax.xaxis.tick_top()
    ax.tick_params(length=0, pad=1.5, labelsize=6.6)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.text(0.5, -0.025, f"{n} pretraining corpora per initialization", transform=ax.transAxes, ha="center", va="top", fontsize=6.3,
            color="#555555")
    cax = axes_in(fig, 1.94, 1.36, 0.07, 1.68)
    cb = fig.colorbar(im, cax=cax)
    cb.set_ticks([0, 0.25, 0.5], labels=["0", "0.25", "0.5"])
    cb.outline.set_linewidth(0.4)
    cb.ax.tick_params(labelsize=6, length=1.8, width=0.5, pad=1)
    cb.set_label("which-head agreement", fontsize=6.3, labelpad=1.5)
    tx = 2.38 / COL
    for y, head, v, col in ((2.98, "same init.,\nother corpus", f"{si:.2f}", SEED),
                            (2.33, "other init.,\nsame corpus", signed(sd), OTHER)):
        fig.text(tx, y / 3.3, head, fontsize=6.4, va="top", linespacing=1.1)
        fig.text(tx, (y - 0.27) / 3.3, v, fontsize=11, va="top", color=col, fontweight="bold")
    fig.add_artist(plt.Line2D([tx + 0.012], [1.565 / 3.3], marker=">", color=INK, ms=2.8, mew=0, transform=fig.transFigure))
    fig.text(tx + 0.035, 1.6 / 3.3, "initialized\ndifferently\n(App. A)", fontsize=5.9, va="top", color="#555555",
             linespacing=1.1)
    # (b) the two levels of a role map, mean over the nine roles (more_roles analysis: within-layer and layer-profile)
    more_roles = json.loads((R / "more_roles" / "analysis.json").read_text())
    roles = [k for k in more_roles if isinstance(more_roles[k], dict) and "SI" in more_roles[k]]
    val = lambda c, q: float(np.mean([more_roles[r][c][q] for r in roles]))
    fig.text(0.0, 1.06 / 3.3, "(b) Layer vs. head within the layer (9 roles)", fontsize=7.4, fontweight="bold", va="top")
    ax = axes_in(fig, 0.98, 0.3, 1.97, 0.64)
    groups = [("layer_profile", "which layer"), ("within", "which head\nin the layer")]
    pairs = [("SI", "same init., other corpus", SEED), ("SD", "other init., same corpus", OTHER),
             ("DD", "both different", LIGHT)]
    for gi, (q, _) in enumerate(groups):
        for pi, (c, _, col) in enumerate(pairs):
            yy = (1 - gi) * 1.0 + (1 - pi) * 0.26
            v = val(c, q)
            ax.barh(yy, v, height=0.22, color=col, zorder=2)
            s = "0.00" if abs(v) < 0.005 else signed(v) if v < 0 else f"{v:.2f}"
            ax.text(max(v, 0) + 0.012, yy, s, va="center", fontsize=5.8, color=col if col != LIGHT else "#777777")
    ax.set_yticks([1.0, 0.0], [g[1] for g in groups], fontsize=6.4)
    ax.tick_params(axis="y", length=0)
    ax.axvline(0, color=INK, lw=0.6)
    ax.spines["left"].set_visible(False)
    grid(ax, "x")
    ax.set_xlim(-0.05, 0.75)
    ax.set_ylim(-0.42, 1.42)
    ax.set_xlabel("agreement between two models", fontsize=6.6)
    for pi, (c, lab, col) in enumerate(pairs):  # legend in the empty lower right, aligned with the bars
        yy = (1 - pi) * 0.26
        ax.barh(yy, 0.03, left=0.42, height=0.16, color=col, zorder=2)
        ax.text(0.465, yy, lab, fontsize=5.8, ha="left", va="center", color=INK)
    save(fig, "fig1_hook")
    return dict(n_corpora=n, same_seed=round(si, 3), same_corpus=round(sd, 3), n_bad=len(bad))


# ---------------------------------------------------------------- Fig 2
DD_PARAMS = {"4M": 3.7e6, "6M": 6e6, "8M": 8.5e6, "10M": 9.9e6, "14M": 14.4e6, "16M": 16e6, "20M": 19.1e6, "60M": 57e6,
             "90M": 97.9e6, "150M": 151e6, "300M": 320e6, "530M": 530e6, "750M": 750e6, "1B@7500": 1.18e9}
PYTHIA_PARAMS = {"70m": 19e6, "160m": 85e6, "410m": 302e6, "1b": 805e6, "1.4b": 1.21e9, "6.9b": 6.44e9, "12b": 11.3e9}


def pythia_within():
    from similarity import within_matrix
    out = {}
    for s in PYTHIA_PARAMS:
        for d in ("pythia_small", "pythia_large"):
            a, b = R / d / f"pythia-{s}-std.json", R / d / f"pythia-{s}-deduped.json"
            if a.exists() and b.exists():
                A, B = json.loads(a.read_text()), json.loads(b.read_text())
                v = [within_matrix([A["maps"][m], B["maps"][m]])[0, 1] for m in ("M1", "M2", "M4")
                     if m != "M1" or (A["M1_max"] > 0.3 and B["M1_max"] > 0.3)]
                out[s] = float(np.mean(v))
    return out


def fig2_innate():
    d = json.loads((R / "crossing_sizes" / "analysis.json").read_text())
    S = [s for s in DD_PARAMS if s in d]
    mean_c = lambda s, c: np.mean([d[s][m]["within_layer"][c] for m in ("M1", "M2", "M4") if d[s][m]["decidable"]])
    H = 1.86
    fig = plt.figure(figsize=(TXT, H))
    # (a)
    ax = axes_in(fig, 0.4, 0.33, 1.6, 1.3)
    grid(ax)
    pw = pythia_within()
    line(ax, [PYTHIA_PARAMS[s] for s in pw], list(pw.values()), PYTH, marker="D", ls="--", ms=3.1, lw=1.0)
    line(ax, [DD_PARAMS[s] for s in S], [mean_c(s, "SI") for s in S], SEED)
    line(ax, [DD_PARAMS[s] for s in S], [mean_c(s, "SD") for s in S], OTHER, ms=3.0)
    tag(ax, 1.6e10, 0.76, "Pythia, same init.\n(Pile vs. dedup.)", PYTH, ha="right", va="top", size=6.1)
    tag(ax, 3e6, 0.3, "DataDecide:\nsame init.,\nother corpus", SEED, va="center", size=6.1)
    tag(ax, 1.8e9, -0.085, "other init., same corpus", OTHER, ha="right", size=6.1)
    ax.axhline(0, color=INK, lw=0.5)
    logx_params(ax)
    ax.set_xlim(2.5e6, 2.0e10)
    ax.set_ylim(-0.13, 0.8)
    ax.set_xlabel("parameters")
    ax.set_ylabel("which-head agreement")
    title(ax, "a", "Agreement by model size", x=-0.2)
    # (b)
    ax = axes_in(fig, 2.5, 0.33, 1.2, 1.3)
    grid(ax)
    e = json.loads((R / "seed_identification.json").read_text())
    S2 = [s for s in DD_PARAMS if s in e]
    early = json.loads((R / "seed_identification_early.json").read_text())
    ep = {}
    for k, v in early.items():
        s, _ = k.split("@")
        if v["frac"] < 0.06 and s in DD_PARAMS and (s not in ep or v["frac"] < ep[s][0]):
            ep[s] = (v["frac"], v["accuracy"])
    ax.plot([DD_PARAMS[s] for s in S2], [e[s]["all"]["chance"] for s in S2], ":", color=INK, lw=0.8)
    line(ax, [DD_PARAMS[s] for s in S2], [e[s]["all"]["accuracy"] for s in S2], SEED)
    ax.plot([DD_PARAMS[s] for s in ep], [v[1] for v in ep.values()], "o", mfc="white", mec=SEED, mew=0.9, ms=4.4, zorder=4)
    tag(ax, 3.5e6, 0.25, "chance", INK, size=6.1)
    ax.plot([1.3e8], [0.64], "o", color=SEED, mec="white", ms=3.6)
    tag(ax, 1.75e8, 0.64, "end of\ntraining", SEED, size=6.0)
    ax.plot([1.3e8], [0.47], "o", mfc="white", mec=SEED, mew=0.9, ms=4.4)
    tag(ax, 1.75e8, 0.47, "at 3–5%", SEED, size=6.0)
    logx_params(ax, (1e7, 1e8, 1e9))
    ax.set_xlim(2.5e6, 2.2e9)
    ax.set_ylim(0, 1.06)
    ax.yaxis.set_major_formatter(mt.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("parameters")
    ax.set_ylabel("initialization identified")
    title(ax, "b", "Identifying the initialization", x=-0.3)
    # (c)
    ax = axes_in(fig, 4.9, 0.33, 1.33, 1.3)
    m43 = json.loads((R / "coordinates" / "analysis.json").read_text())["metrics"]
    more_roles = json.loads((R / "more_roles" / "analysis.json").read_text())
    roles = [k for k in more_roles if isinstance(more_roles[k], dict) and "SI" in more_roles[k]]
    rows = [("which head (9 roles)", {c: np.mean([more_roles[r][c]["within"] for r in roles]) for c in ("SI", "SD", "DD")}),
            ("residual dimensions", m43["resid_index_corr"]), ("outlier dimensions", m43["massive_dims_jaccard"]),
            ("residual stream", m43["resid_cka"]), ("head outputs", m43["head_out_cka_best"]),
            ("MLP neurons", m43["neuron_best_corr"])]
    y = np.array([6.4, 5.5, 4.6, 2.6, 1.7, 0.8])
    grid(ax, "x")
    ax.axvline(0, color=INK, lw=0.6)
    for yi, (_, r) in zip(y, rows):
        a, b = r["SI"] - r["DD"], r["SD"] - r["DD"]
        ax.plot([min(a, b, 0), max(a, b, 0)], [yi, yi], color=LIGHT, lw=0.8, zorder=1)
        ax.plot(b, yi, "o", color=ACQ, mec="white", ms=4.6, zorder=3)
        ax.plot(a, yi, "o", color=SEED, mec="white", ms=4.6, zorder=4)
    ax.set_yticks(y, [r[0] for r in rows], fontsize=6.2)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.03, 0.37)
    ax.set_ylim(0.3, 7.6)
    import matplotlib.transforms as mtr
    tr = mtr.blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(-0.04, 7.25, "index-aligned", transform=tr, ha="right", va="center", fontsize=6.2, fontstyle="italic")
    ax.text(-0.04, 3.45, "unit-invariant", transform=tr, ha="right", va="center", fontsize=6.2, fontstyle="italic")
    ax.plot(0.22, 2.6, "o", color=SEED, mec="white", ms=4.6)
    tag(ax, 0.24, 2.6, "shared init.", SEED, size=6.0)
    ax.plot(0.22, 1.7, "o", color=ACQ, mec="white", ms=4.6)
    tag(ax, 0.24, 1.7, "shared corpus", ACQ, size=6.0)
    ax.set_xlabel("gain over unrelated models")
    title(ax, "c", "What the initialization shares", x=-0.82)
    save(fig, "fig2_innate")


# ---------------------------------------------------------------- Fig 3
def fig3_critical():
    import re
    d = json.loads((R / "controlled" / "analysis.json").read_text())
    H = 3.3
    fig = plt.figure(figsize=(COL, H))
    ax = axes_in(fig, 0.5, 1.95, 2.45, 1.08)
    grid(ax)
    ax.axvspan(100, 250, color=CP, lw=0, zorder=0)
    for pat, col, mk in (("eps0.1$", SKY, "^"), ("eps1$", BLUE, "s"), ("tocode", SEED, "o")):
        pts = {}
        for k, v in d["D"].items():
            mm = re.search(r"_b(\d+)_", k)
            if mm and re.search(pat, k):
                vals = [v[m][1] for m in ("M1", "M2") if m in v]
                if vals:
                    pts.setdefault(int(mm.group(1)), []).append(np.mean(vals))
        if pat == "tocode":  # step 0 = the same seed trained on code from scratch, vs. natural text (controlled_pretraining)
            controlled_pairs = json.loads((R / "controlled_corpus_pairs.json").read_text())
            pts[0] = [np.mean([controlled_pairs[m]["SI_code"] for m in ("M1", "M2")])]
        else:
            eps = pat.strip("eps$")
            pts[0] = [np.mean([v[m][1] for m in ("M1", "M2") if m in v]) for k, v in d["C"].items() if k.endswith(f"_eps{eps}")]
        ks = sorted(pts)
        line(ax, [max(k, 40) for k in ks], [np.mean(pts[k]) for k in ks], col, marker=mk, ms=3.3)
    rr = np.mean([np.mean([v[m][1] for m in ("M1", "M2") if m in v]) for k, v in d["C"].items() if k.endswith("rerun1")])
    ax.axhline(rr, color=INK, ls=":", lw=0.8)
    tag(ax, 8800, rr + 0.075, "exact rerun", INK, size=6.0, ha="right")
    L = json.loads((R / "controlled_large_model.json").read_text())
    lv = {40: np.mean(list(L["L_i1_code_o1"].values())), 100: np.mean(list(L["L_i1_c4_o1_b100_tocode_too300"].values())),
          1000: np.mean(list(L["L_i1_c4_o1_b1000_tocode_too1200"].values()))}
    ax.plot(list(lv), list(lv.values()), "o", mfc="white", mec=SEED, mew=0.9, ms=4.4, zorder=4)
    tag(ax, 48, 0.6, "noise 10%", SKY, size=6.0)
    tag(ax, 140, 0.2, "noise as large\nas the weights", BLUE, size=6.0)
    tag(ax, 2600, 0.6, "switch to code", SEED, size=6.0, ha="center")
    tag(ax, 158, -0.12, "1–2.5%", "#B5532A", size=5.6, ha="center", va="center")
    ax.set_xscale("log")
    ax.minorticks_off()
    ax.set_xticks([40, 100, 250, 1000, 4000], ["0", "1%", "2.5%", "10%", "40%"])
    ax.set_xlim(32, 9500)
    ax.set_ylim(-0.25, 1.1)
    ax.set_xlabel("when the intervention happens (share of training)")
    ax.set_ylabel("agreement with\nthe uninterrupted run")
    title(ax, "a", "Intervening in controlled pretraining", x=-0.2)
    ax = axes_in(fig, 0.5, 0.33, 2.45, 1.08)
    grid(ax)
    ax.axvspan(0.01, 0.025, color=CP, lw=0, zorder=0)
    lockin_pythia = json.loads((R / "lockin_pythia" / "analysis.json").read_text())
    c = lockin_pythia["70m"]["S_prev"]["mean_curve"]
    st = [int(s) for s in c if int(s) > 0]
    ax.plot([s / 143000 for s in st], [c[str(s)] for s in st], "-", color=BLUE, lw=1.3, zorder=3)
    runs = [v for v in d["lockin"].values() if "M2" in next(iter(v.values()))]
    st = sorted({int(s) for v in runs for s in v})
    ax.plot([s / 10000 for s in st], [np.mean([v[str(s)]["M2"] for v in runs if str(s) in v]) for s in st], "-",
            color=SEED, lw=1.3, zorder=3)
    pythia_large = json.loads((R / "pythia_large_analysis.json").read_text())["12b@3000"]["to_own_final"]
    ax.plot([3000 / 143000], [np.mean(list(pythia_large.values()))], "*", color=PYTH, ms=8.5, mec="white", mew=0.5, zorder=5)
    tag(ax, 0.00105, 0.8, "Pythia-70M\n(10 inits.)", BLUE, size=6.0)
    tag(ax, 0.0125, 0.33, "controlled", SEED, size=6.0)
    tag(ax, 0.03, 0.6, "Pythia-12B", PYTH, size=6.0)
    ax.set_xscale("log")
    ax.set_xlim(8e-4, 1.15)
    pct(ax)
    ax.set_ylim(0, 1.06)
    ax.set_xlabel("share of training")
    ax.set_ylabel("agreement with\nthe final layout")
    title(ax, "b", "Most of the layout is in place by 2–4%", x=-0.2)
    save(fig, "fig3_critical")


# ---------------------------------------------------------------- Fig 4
def fig4_question():
    habit_sizes = json.loads((R / "habit_sizes" / "analysis.json").read_text())
    habit_templates = json.loads((R / "habit_templates" / "analysis.json").read_text())["cells"]
    H = 1.86
    fig = plt.figure(figsize=(TXT, H))
    ax = axes_in(fig, 0.36, 0.33, 1.98, 1.3)
    grid(ax)
    sizes = list(habit_sizes) + ["1B"]
    get = lambda s, c: (habit_sizes[s]["cells"][c] if s != "1B" else habit_templates[c])
    for j, (c, lab, col, mk) in enumerate((("QA", "Question: … Answer:", ACQ, "o"), ("QA_short", "Q: … A:", OTHER, "s"),
                                           ("novel", "Query: … Response:", "#BDBDBD", "^"))):
        x = np.arange(len(sizes)) + (j - 1) * 0.24
        ax.errorbar(x, [get(s, c)["delta"] for s in sizes], [get(s, c)["se"] for s in sizes], fmt=mk, color=col, ms=3.4,
                    mec="white", mew=0.4, elinewidth=0.6, capsize=0, zorder=3, label=lab)
    ax.axhline(0, color=INK, lw=0.5)
    ax.set_xticks(range(len(sizes)), sizes, fontsize=6.2)
    ax.set_xlim(-0.5, len(sizes) - 0.5)
    ax.set_xlabel("model size")
    ax.set_ylabel("added context trust (nats)")
    ax.legend(loc="upper left", handletextpad=0.1, borderaxespad=0.1, labelspacing=0.25,
              prop={"family": "monospace", "size": 5.7})
    ax.set_ylim(-1.0, 4.6)
    title(ax, "a", "At every size from 60M to 1B", x=-0.15)
    ax = axes_in(fig, 2.72, 0.33, 1.15, 1.3)
    grid(ax)
    habit_pretraining = json.loads((R / "habit_pretraining" / "analysis.json").read_text())["steps"]
    st = sorted(habit_pretraining, key=int)
    fr = np.array([int(s) / 69369 for s in st])
    for key, col, mk, ls, dx in (("FE_c1", ACQ, "o", "-", 1.0), ("decl", OTHER, "s", "--", 1.06)):
        ax.errorbar(fr * dx, [habit_pretraining[s][key]["delta"] for s in st], [habit_pretraining[s][key]["se"] for s in st], fmt=mk + ls, color=col,
                    ms=3.2, mec="white", mew=0.4, lw=1.0, elinewidth=0.6, capsize=0, zorder=3)
    tag(ax, 0.03, 3.85, "question", ACQ, size=6.1)
    tag(ax, 0.25, -1.35, "declarative", OTHER, size=6.1)
    ax.axhline(0, color=INK, lw=0.5)
    ax.set_xscale("log")
    pct(ax)
    ax.set_xticks([0.036, 0.1, 0.3, 1.0], ["3.6%", "10%", "30%", "100%"])
    ax.set_xlim(0.026, 1.4)
    ax.set_xlabel("share of pretraining (1B)")
    ax.set_ylim(-1.7, 4.6)
    title(ax, "b", "From 3.6% of training", x=-0.12)
    ax = axes_in(fig, 4.28, 0.33, 0.62, 1.3)
    grid(ax)
    habit_olmo2_public = json.loads((R / "habit_olmo2_public" / "analysis.json").read_text())["partA"]
    s1 = [v["FE_c1"] for v in habit_olmo2_public["stage1"].values()]
    s2 = [v["FE_c1"] for v in habit_olmo2_public["stage2_final"].values()]
    ax.plot([0, 1], [np.mean(s1), np.mean(s2)], "-", color=LIGHT, lw=1.0, zorder=1)
    ax.plot(np.zeros(3) + np.array([-0.08, 0, 0.08]), s1, "o", color=OTHER, mec="white", ms=4.2, zorder=3)
    ax.plot(np.ones(3) + np.array([-0.08, 0, 0.08]), s2, "o", color=ACQ, mec="white", ms=4.2, zorder=3)
    ax.axhline(0, color=INK, lw=0.5)
    ax.set_xticks([0, 1], ["before", "after"])
    ax.set_xlim(-0.5, 1.5)
    ax.set_xlabel("FLAN mid-training")
    ax.set_ylabel("trust gain (nats)")
    ax.set_ylim(-1.0, 3.0)
    title(ax, "c", "OLMo 2", x=-0.5)
    ax = axes_in(fig, 5.47, 0.33, 0.76, 1.3)
    grid(ax, "x")
    habit_popqa = json.loads((R / "habit_popqa" / "analysis.json").read_text())
    habit_nqswap = json.loads((R / "habit_nqswap" / "analysis.json").read_text())
    rows = [("PopQA\nquestion", habit_popqa["FE"], ACQ), ("PopQA\ndeclarative", habit_popqa["decl"], LIGHT),
            ("NQ-Swap\nDataDecide", habit_nqswap["datadecide_1B"]["effects"]["Question_vs_Q"], ACQ),
            ("NQ-Swap\nOLMo 2", habit_nqswap["olmo2_midtraining"]["effects"]["Question_vs_Q"], ACQ)]
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1]["delta"] for r in rows], 0.62, color=[r[2] for r in rows], zorder=2)
    ax.errorbar([r[1]["delta"] for r in rows], y, xerr=[r[1]["se"] for r in rows], fmt="none", ecolor="#555555",
                elinewidth=0.6, capsize=1.2, capthick=0.6, zorder=3)
    ax.axvline(0, color=INK, lw=0.6)
    ax.set_yticks(y, [r[0] for r in rows], fontsize=6.0, linespacing=1.0)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.7, 2.7)
    ax.set_xlabel("effect (nats)")
    title(ax, "d", "Other datasets", x=-0.75)
    save(fig, "fig4_question")


# ---------------------------------------------------------------- Fig 4 (main text): the Flan case study
def fig4_flan():
    """(a) habit_templates: Flan - no-Flan effect on context trust by template (1B, mean +- SE over initializations).
    (b) flan_layout: which-head agreement (mean over nine roles) of same-initialization Flan / no-Flan pairs, of
    same-initialization pairs of other Dolma 1.7 ablations, and of different-initialization pairs.
    (c) flan_layout: which-head agreement of the declarative retrieval map and of the Question: habit map (QA - declarative
    attention to the context entity) among the Flan models, same vs. different initialization."""
    e = json.loads((R / "habit_templates" / "analysis.json").read_text())["cells"]
    a = json.loads((R / "flan_layout" / "analysis.json").read_text())
    H = 2.55
    fig = plt.figure(figsize=(COL, H))
    cells = [("QA", "Question: … Answer:"), ("Q_only", "Question: …"), ("A_only", "Answer:"),
             ("QA_short", "Q: … A:"), ("novel", "Query: … Response:")]
    ax = axes_in(fig, 1.17, 1.5, 1.8, 0.78)
    title(ax, "a", "Trust added by Flan, by template", x=-0.62)
    y = np.arange(len(cells))[::-1]
    ax.barh(y, [e[k]["delta"] for k, _ in cells], color=[ACQ if k in ("QA", "Q_only") else LIGHT for k, _ in cells],
            height=0.66, zorder=2)
    ax.errorbar([e[k]["delta"] for k, _ in cells], y, xerr=[e[k]["se"] for k, _ in cells], fmt="none", ecolor="#555555",
                elinewidth=0.6, capsize=1.4, capthick=0.6, zorder=3)
    ax.set_yticks(y, [lab for _, lab in cells], fontsize=6.1, family="monospace")
    ax.tick_params(axis="y", length=0)
    ax.axvline(0, color=INK, lw=0.6)
    ax.spines["left"].set_visible(False)
    grid(ax, "x")
    ax.set_xlabel("nats", fontsize=6.6, labelpad=1)
    ax.set_xlim(-0.6, 3.4)
    # (b)
    lay = a["layout_flan_vs_other"]
    m = lambda k: float(np.mean([v[k][0] for v in lay.values()]))
    ax = axes_in(fig, 0.36, 0.3, 1.02, 0.78)
    title(ax, "b", "Head layout, 9 roles", x=-0.34)
    vals = [("Flan vs.\nno Flan", m("flan_vs_noflan"), SEED), ("other\nablations", m("flan_vs_flan"), SEED),
            ("other\ninit.", m("other_seed"), OTHER)]
    x = np.arange(3)
    ax.bar(x, [v[1] for v in vals], color=[v[2] for v in vals], width=0.62, zorder=2)
    for xi, (_, v, col) in zip(x, vals):
        ax.text(xi, max(v, 0) + 0.015, "0.00" if abs(v) < 0.005 else f"{v:.2f}".replace("-", MINUS), ha="center",
                va="bottom", fontsize=5.8, color=col)
    ax.set_xticks(x, [v[0] for v in vals], fontsize=5.8)
    ax.tick_params(axis="x", length=0)
    ax.axhline(0, color=INK, lw=0.6)
    grid(ax)
    ax.set_ylim(-0.06, 0.6)
    ax.set_ylabel("which-head agreement", fontsize=6.4)
    # (c) POST-HOC flan_layout: the Flan-specific part of the habit (Question: minus Q:) in attention to the context entity
    h = a["posthoc_template_contrast"]["question_minus_q"]
    ax = axes_in(fig, 1.98, 0.3, 0.99, 0.78)
    title(ax, "c", "Top-10 retrieval heads", x=-0.34)
    vals = [("heads", h["share_expected"], LIGHT), ("attention\nto entity", h["top10_share_of_entity_attention"], OTHER),
            ("added by\nFlan", h["share_top10_retrieval"], ACQ)]
    ax.bar(range(3), [v[1] for v in vals], color=[v[2] for v in vals], width=0.6, zorder=2)
    for xi, (_, v, col) in enumerate(vals):
        ax.text(xi, v + 0.012, f"{100 * v:.0f}%", ha="center", va="bottom", fontsize=5.8,
                color=col if col != LIGHT else "#777777")
    ax.set_xticks(range(3), [v[0] for v in vals], fontsize=5.8)
    ax.tick_params(axis="x", length=0)
    ax.axhline(0, color=INK, lw=0.6)
    grid(ax)
    ax.set_ylim(0, 0.4)
    ax.yaxis.set_major_formatter(mt.PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("their share of", fontsize=6.2)
    save(fig, "fig4_flan")


# ---------------------------------------------------------------- Fig 5
def fig5_content():
    from scipy.stats import spearmanr
    fw = json.loads((R / "corpus_distance" / "function_words.json").read_text())["by_size"]
    P = json.loads((R / "corpus_distance" / "function_words_pairs.json").read_text())
    H = 1.72
    fig = plt.figure(figsize=(COL, H))
    ax = axes_in(fig, 0.42, 0.42, 0.98, 1.05)
    grid(ax)
    pts = np.array([(v["cw"], v["fw"], np.mean(list(v["inherit"].values()))) for v in P.values() if v["disjoint"] and v["inherit"]])
    ax.scatter(pts[:, 0], pts[:, 2], s=6, color=SEED, alpha=0.7, lw=0, zorder=3)
    b = np.polyfit(pts[:, 0], pts[:, 2], 1)
    xx = np.linspace(pts[:, 0].min(), pts[:, 0].max(), 10)
    ax.plot(xx, np.polyval(b, xx), color=INK, lw=0.8, zorder=4)
    rho = spearmanr(pts[:, 0], pts[:, 2])[0]
    tag(ax, 0.97, 0.96, f"ρ = {rho:.2f}".replace("-", MINUS), INK, ha="right", va="top", size=6.4, transform=ax.transAxes)
    ax.set_xlabel("content-word distance (JS)")
    ax.set_ylabel("same-seed agreement")
    title(ax, "a", "1B, no shared sources", x=-0.35)
    ax = axes_in(fig, 1.92, 0.42, 1.06, 1.05)
    grid(ax)
    order = [s for s in ["90M", "150M", "300M", "530M", "750M", "1B@7500", "1B"] if s in fw]
    x = np.arange(len(order))
    for off, key, col, mk in ((-0.14, "partial_cw_given_fw", SEED, "o"), (0.14, "partial_fw_given_cw", OTHER, "s")):
        vals = [[-fw[s][m][key] for m in fw[s]] for s in order]
        ax.errorbar(x + off, [np.mean(v) for v in vals], [[np.mean(v) - min(v) for v in vals], [max(v) - np.mean(v) for v in vals]],
                    fmt=mk, color=col, ms=3.4, mec="white", mew=0.4, elinewidth=0.6, capsize=0, zorder=3)
    ax.axhline(0, color=INK, lw=0.5)
    tag(ax, -0.35, 0.9, "content words", SEED, size=6.1)
    tag(ax, -0.35, -0.64, "function words", OTHER, size=6.1)
    ax.set_xticks(x, [s.replace("@7500", "†") for s in order], rotation=45, fontsize=5.9)
    ax.set_xlim(-0.5, len(order) - 0.5)
    ax.set_ylabel("−partial ρ with agreement")
    ax.set_ylim(-0.78, 1.02)
    title(ax, "b", "Only content words matter", x=-0.3)
    save(fig, "fig5_content")


# ---------------------------------------------------------------- Appendix: SGD temperature
DD_RECIPE = {"4M": (32, 1.4e-2), "6M": (32, 1.2e-2), "8M": (32, 1.1e-2), "10M": (32, 1.0e-2), "14M": (32, 9.2e-3),
             "16M": (32, 8.9e-3), "20M": (64, 8.4e-3), "60M": (96, 5.8e-3), "90M": (160, 4.9e-3), "150M": (192, 4.2e-3),
             "300M": (320, 3.3e-3), "530M": (448, 2.8e-3), "750M": (576, 2.5e-3), "1B@7500": (704, 2.1e-3)}


def figA_temperature():
    e = json.loads((R / "sgd_temperature.json").read_text())
    d = json.loads((R / "crossing_sizes" / "analysis.json").read_text())
    tok = {"bs16": 16 * 512, "bs64": 64 * 512, "bs512": 512 * 512, "lr3e-3": 64 * 512, "lr3e-4": 64 * 512}
    lr = {"bs16": 1e-3, "bs64": 1e-3, "bs512": 1e-3, "lr3e-3": 3e-3, "lr3e-4": 3e-4}
    H = 1.65
    fig = plt.figure(figsize=(COL, H))
    ax = axes_in(fig, 0.42, 0.36, 1.05, 1.0)
    grid(ax)
    pts = sorted((lr[k] / tok[k], v["M2"]["inherit_c4_papers"], v["M2"]["order_only"], k) for k, v in e.items()
                 if v["M2"]["inherit_c4_papers"] is not None)
    line(ax, [p[0] for p in pts], [p[2] for p in pts], BLUE, marker="s", ms=3.2)
    line(ax, [p[0] for p in pts], [p[1] for p in pts], SEED, ms=3.2)
    tag(ax, pts[0][0], 0.9, "other batch order", BLUE, size=5.8, ha="left")
    tag(ax, pts[0][0], 0.33, "C4 vs. papers", SEED, size=5.8, ha="left")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.minorticks_off()
    ax.set_xlabel("LR per batch token")
    ax.set_ylabel("same-seed agreement")
    ax.set_ylim(-0.05, 1.02)
    title(ax, "a", "Controlled models", x=-0.35)
    ax = axes_in(fig, 1.85, 0.36, 1.12, 1.0)
    grid(ax)
    S = [s for s in DD_RECIPE if s in d]
    x = [DD_RECIPE[s][1] / (DD_RECIPE[s][0] * 2048) for s in S]
    y = [np.mean([d[s][m]["within_layer"]["SI"] for m in ("M1", "M2", "M4") if d[s][m]["decidable"]]) for s in S]
    ax.plot(x, y, "o", color=SEED, mec="white", ms=3.6)
    for xi, yi, s in zip(x, y, S):
        if s in ("4M", "60M", "300M", "1B@7500"):
            tag(ax, xi, yi + 0.035, s.replace("@7500", ""), INK, size=5.6, ha="center", va="bottom")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.minorticks_off()
    ax.set_xlabel("LR per batch token")
    ax.set_ylim(-0.05, 0.5)
    title(ax, "b", "DataDecide sizes", x=-0.2)
    save(fig, "figA_temperature")


# ---------------------------------------------------------------- Appendix: warm-up and optimizer state (warmup_window)
def figA_warmup():
    """warmup_window: agreement of the final layout with the uninterrupted run after noise as large as the weights at step k,
    against the learning already applied before step k (cumulative learning rate in units of the peak rate), for the
    300-step and 1000-step warm-ups; crosses: branches whose AdamW state was reset."""
    d = json.loads((R / "warmup_window.json").read_text())
    mean = lambda v: float(np.mean([np.mean(list(x.values())) for x in v.values()]))
    import controlled_pretraining
    cum = lambda k, w: sum(controlled_pretraining.lr_at(s, 1e-3, w) for s in range(k)) / 1e-3
    fig = plt.figure(figsize=(COL, 1.75))
    ax = axes_in(fig, 0.5, 0.36, 2.45, 1.25)
    grid(ax)
    for w, col, mk in ((300, BLUE, "s"), (1000, SKY, "o")):
        sec = d[f"warm{w}"]["noise"]
        ks = sorted(sec, key=int)
        line(ax, [cum(int(k), w) for k in ks], [mean(sec[k]) for k in ks], col, marker=mk, ms=3.4)
        for k in ks[:2]:  # the first two intervention points (1% and 2.5% of training)
            ax.text(cum(int(k), w) * 1.12, mean(sec[k]) - 0.06, f"{int(k) / 100:g}%", fontsize=5.6, color=col)
    ro = d["reset_opt"]
    ax.plot([cum(int(k), 300) for k in ro], [mean(ro[k]) for k in ro], "x", color=SEED, ms=4.5, mew=1.0, zorder=5)
    tag(ax, 2400, 0.42, "warm-up 300 steps", BLUE, size=6.0, ha="right")
    tag(ax, 2400, 0.31, "warm-up 1000 steps", SKY, size=6.0, ha="right")
    tag(ax, 2400, 0.20, "× optimizer state reset", SEED, size=6.0, ha="right")
    ax.set_xscale("log")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("learning before the intervention (cumulative LR / peak LR)")
    ax.set_ylabel("agreement with\nthe uninterrupted run")
    save(fig, "figA_warmup")


if __name__ == "__main__":
    import sys
    fns = {f.__name__: f for f in (fig1_hook, fig2_innate, fig3_critical, fig4_flan, fig4_question, fig5_content,
                                       figA_temperature, figA_warmup)}
    for name in (sys.argv[1:] or fns):
        print(name, fns[name]())
