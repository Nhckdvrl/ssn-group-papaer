"""Figures and tables for paper-acl-v3 (all numbers computed from result files).

  Fig 1  fig1_carryover   attention-role vs carrier correspondence by relation between two models (E81, E83, E82)
  Fig 2  fig2_lineage     carriers along a training lineage: Pythia-410M pair (E82) and DataDecide-1B runs (E83)
  Fig 3  fig3_masking     identical reruns and data masking on induction heads (E84-E86)
  Tables tab_roles.tex (E35 / E59), tab_lineage.tex (E81), tab_audit.tex (P09 / P11 / P12 / P13)
Usage: figs_v3.py
"""
import glob
import itertools
import json
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import mp_common as mc  # noqa: E402
from e81_analyze import SB, top, within  # noqa: E402

R = mc.RESULTS
PAPER = R.parent / "paper-acl-v3"
OUT = PAPER / "figures"
COL, TXT = 3.03, 6.3
ROLE, CARR, OTHER, INK, GRID = "#0072B2", "#D55E00", "#8C8C8C", "#262626", "#E9E9E9"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Liberation Serif", "DejaVu Serif"], "font.size": 7.5,
    "axes.titlesize": 7.5, "axes.labelsize": 7.3, "xtick.labelsize": 6.6, "ytick.labelsize": 6.6, "legend.fontsize": 6.4,
    "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.4, "ytick.major.size": 2.4,
    "lines.linewidth": 1.2, "lines.markersize": 3.4, "pdf.fonttype": 42, "axes.titlepad": 4, "axes.labelpad": 2,
    "axes.axisbelow": True, "axes.titlelocation": "left", "axes.titleweight": "bold"})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=250)
    plt.close(fig)


def npz(path):
    z = np.load(path)
    return {k: z[k] for k in z.files}


def pair_stats(x, y):
    """END->IO attention correspondence and reliability-corrected single-head ablation correspondence."""
    rel = lambda d, k: SB(within(d[k][0], d[k][1]))  # noqa: E731
    att = within(x["att_io"].mean(0), y["att_io"].mean(0))
    ab = within(x["abl"].mean(0), y["abl"].mean(0)) / np.sqrt(max(rel(x, "abl"), 1e-3) * max(rel(y, "abl"), 1e-3))
    return att, min(ab, 1.0)


# ---------------------------------------------------------------- Fig 1
def fig1():
    E81 = {f.split("/")[-1][:-4]: npz(f) for f in glob.glob(str(R / "e81" / "*.npz"))}
    E83 = {f.split("/")[-1][:-4]: npz(f) for f in glob.glob(str(R / "e83" / "*step69369*.npz"))}
    dd = {k: v for k, v in E81.items() if k.startswith("dd__")}
    rel = {"different\ninitialization": [], "same init.,\ndifferent corpus": [],
           "same init.,\nclosely related\ncorpus": [], "same training\nlineage": []}
    keys = sorted(dd)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ca, sa = a.split("__")[1], a.split("seed-")[1]
            cb, sb = b.split("__")[1], b.split("seed-")[1]
            if sa != sb:
                rel["different\ninitialization"].append(pair_stats(dd[a], dd[b]))
            elif ca != cb:
                rel["same init.,\ndifferent corpus"].append(pair_stats(dd[a], dd[b]))
    for s in ("default", "large-aux-2", "large-aux-3"):  # Flan ablation: ~1.5% of the corpus removed
        a, b = f"dd__DataDecide-dolma1_7-1B__step69369-seed-{s}", f"dd__DataDecide-dolma1_7-no-flan-1B__step69369-seed-{s}"
        if a in E83 and b in E83:
            rel["same init.,\nclosely related\ncorpus"].append(pair_stats(E83[a], E83[b]))
    a, b = "pythia__pythia-410m__143000", "pythia__pythia-410m-deduped__143000"
    rel["same init.,\nclosely related\ncorpus"].append(pair_stats(E81[a], E81[b]))
    O = "hf__OLMo-2-0425-1B__"
    lineage = [("pythia__pythia-410m__66000", "pythia__pythia-410m__143000")]
    lineage += [(O + "stage1-step1907359-tokens4001B", O + f"stage2-ingredient{i}-step23852-tokens51B") for i in (1, 2, 3)]
    lineage += [("hf__OLMo-2-0425-1B-SFT__main", "hf__OLMo-2-0425-1B-DPO__main"),
                ("hf__OLMo-2-0425-1B-DPO__main", "hf__OLMo-2-0425-1B-Instruct__main")]
    for a, b in lineage:
        rel["same training\nlineage"].append(pair_stats(E81[a], E81[b]))
    fig = plt.figure(figsize=(COL, 2.2))
    ax = fig.add_axes([0.13, 0.27, 0.85, 0.56])
    x = np.arange(len(rel))
    for j, (lab, col) in enumerate((("attention role (which head attends to the IO name)", ROLE),
                                     ("causal carrier (which head's ablation hurts IOI)", CARR))):
        m = [np.mean([p[j] for p in v]) for v in rel.values()]
        lo = [np.min([p[j] for p in v]) for v in rel.values()]
        hi = [np.max([p[j] for p in v]) for v in rel.values()]
        xs = x + (j - 0.5) * 0.36
        ax.bar(xs, m, 0.34, color=col, label=lab, zorder=2)
        ax.errorbar(xs, m, yerr=[np.array(m) - lo, np.array(hi) - m], fmt="none", ecolor=INK, lw=0.6, capsize=1.2, zorder=3)
    ax.set_xticks(x, list(rel), fontsize=5.9)
    ax.set_ylim(-0.1, 1.08)
    ax.axhline(0, color=INK, lw=0.5)
    ax.set_ylabel("head-map correspondence")
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.legend(loc="lower left", fontsize=5.9, handlelength=1.0, bbox_to_anchor=(-0.02, 1.0), ncol=1)
    save(fig, "fig1_carryover")
    return {k.replace("\n", " "): {"n": len(v), "attention": float(np.mean([p[0] for p in v])),
                                    "carrier": float(np.mean([p[1] for p in v]))} for k, v in rel.items()}


# ---------------------------------------------------------------- Fig 2
def fig2():
    a = json.loads((R / "e82" / "analysis.json").read_text())
    c = json.loads((R / "e83" / "analysis.json").read_text())
    fig = plt.figure(figsize=(TXT, 1.75))
    ax = fig.add_axes([0.07, 0.24, 0.40, 0.62])
    for m, col, lab in (("pythia-410m", CARR, "410M: own final carriers"), ("pythia-410m-deduped", "#E69F00", "410M-dedup: own final carriers")):
        rows = a["runs"][m]["rows"]
        st = sorted(int(s) for s in rows)
        ax.plot(st, [rows[str(s)]["top3_overlap_final"] for s in st], "-o", color=col, label=lab)
    sib = a["siblings"]["pythia-410m vs pythia-410m-deduped"]
    st = sorted(int(s) for s in sib)
    ax.plot(st, [sib[str(s)]["top3_overlap"] for s in st], "--s", color=OTHER, label="410M vs 410M-dedup: shared carriers")
    ax.set_xscale("log")
    ax.set_xlabel("training step (Pythia, 143k total)")
    ax.set_ylabel("top-3 IOI heads in common")
    ax.set_yticks([0, 1, 2, 3])
    ax.set_ylim(-0.2, 3.6)
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.text(70000, 3.25, "410M", color=CARR, fontsize=6.0, ha="center")
    ax.text(2.6e4, 0.68, "410M-dedup.", color="#E69F00", fontsize=6.0, ha="center")
    ax.text(1.5e5, 0.2, "shared by the two siblings", color=OTHER, fontsize=6.0, ha="right")
    ax.set_title("a  Pythia-410M siblings: final carriers in place", fontsize=7.0)
    ax2 = fig.add_axes([0.57, 0.24, 0.41, 0.62])
    runs = c["runs"]
    names = sorted(runs, key=lambda k: (k.split("/")[0], k.split("/")[1]))
    steps = sorted({int(s) for r in runs.values() for s in r["traj"]})
    M = np.full((len(names), len(steps)), np.nan)
    for i, n in enumerate(names):
        fin = runs[n]["traj"][str(max(steps))][0] if str(max(steps)) in runs[n]["traj"] else None
        for j, s in enumerate(steps):
            t = runs[n]["traj"].get(str(s))
            if t:
                M[i, j] = 1.0 if t[0] == fin else 0.0
    cmap = matplotlib.colors.ListedColormap(["#F2F2F2", CARR])
    cmap.set_bad("white")
    ax2.imshow(np.ma.masked_invalid(M), aspect="auto", cmap=cmap, vmin=0, vmax=1)
    for i in range(len(names) + 1):
        ax2.axhline(i - 0.5, color="white", lw=0.6)
    for j in range(len(steps) + 1):
        ax2.axvline(j - 0.5, color="white", lw=0.6)
    for i, n in enumerate(names):
        ax2.plot(steps.index(runs[n]["selection"]), i, marker="v", ms=2.6, color=INK, mec="none")
    ax2.set_xticks(range(len(steps)), [f"{s / 1000:g}k" if s < 60000 else f"{s // 1000}k" for s in steps])
    lab = {"c4-1B": "C4", "dolma1_7-1B": "Dolma", "dolma1_7-no-flan-1B": "Dolma$-$Flan", "dclm-baseline-1B": "DCLM"}
    ax2.set_yticks(range(len(names)), [f"{lab[n.split('/')[0]]} {n.split('/')[1].replace('large-aux-', 's')}" for n in names],
                   fontsize=5.4)
    ax2.set_xlabel("training step (DataDecide-1B, 69k total)")
    ax2.set_title("b  DataDecide-1B: main carrier is already the final one (filled)", fontsize=7.0)
    for sp in ax2.spines.values():
        sp.set_visible(False)
    save(fig, "fig2_lineage")


# ---------------------------------------------------------------- Fig 3
def fig3():
    E46 = R / "e46"
    names = {"base": "L_i{i}_c4_o1_st3000", "rerun": "L_i{i}_c4_o1_rerun1_st3000",
             "random": "L_i{i}_c4_o1_st3000_maskrandom0.1_500-2000", "repeat": "L_i{i}_c4_o1_st3000_maskrepeat0.1_500-2000"}
    load = lambda n: json.loads((E46 / f"{n}.json").read_text()) if (E46 / f"{n}.json").exists() else None  # noqa: E731
    steps = ["750", "1000", "1500", "2000", "3000"]
    xs = [int(s) for s in steps]
    fig = plt.figure(figsize=(TXT, 1.7))
    axA = fig.add_axes([0.07, 0.25, 0.25, 0.6])
    axB = fig.add_axes([0.40, 0.25, 0.25, 0.6])
    axC = fig.add_axes([0.73, 0.25, 0.25, 0.6])
    cols = {"repeat": CARR, "random": "#E69F00", "rerun": OTHER}
    labels = {"repeat": "mask most repetitive 10%", "random": "mask random 10%", "rerun": "rerun (no mask)"}
    out = {}
    for cond in ("rerun", "random", "repeat"):
        T, C = [], []
        for i in (1, 2, 3):
            b, d = load(names["base"].format(i=i)), load(names[cond].format(i=i))
            if not (b and d):
                continue
            M = np.array(b["measures"]["3000"]["M1"])
            tgt = np.unravel_index(M.argmax(), M.shape)
            T.append([np.array(d["measures"][s]["M1"])[tgt] / max(np.array(b["measures"][s]["M1"])[tgt], 1e-3) for s in steps])
            C.append([d["measures"][s]["copy_gain"] / b["measures"][s]["copy_gain"] for s in steps])
        for ax, Y in ((axA, np.array(T)), (axB, np.array(C))):
            ax.plot(xs, Y.mean(0), "-o", color=cols[cond], label=labels[cond], zorder=3)
            ax.fill_between(xs, Y.min(0), Y.max(0), color=cols[cond], alpha=0.15, lw=0, zorder=2)
        out[cond] = {"T": np.array(T).mean(0).round(3).tolist(), "C": np.array(C).mean(0).round(3).tolist(), "n": len(T)}
    for ax, t in ((axA, "a  base run's induction head"), (axB, "b  copying ability")):
        ax.axvspan(500, 2000, color="#F4E1D2", lw=0, zorder=0)
        ax.axhline(1, color=INK, lw=0.5)
        ax.set_ylim(0, 1.4)
        ax.set_xticks([1000, 2000, 3000])
        ax.set_xlabel("training step")
        ax.set_title(t, fontsize=6.9)
    axA.set_ylabel("relative to unmasked run")
    axB.legend(loc="lower right", fontsize=5.6)
    for n, ls, lab in ((names["base"].format(i=2), "-", "unmasked"), (names["random"].format(i=2), "--", "random 10% masked")):
        d = load(n)
        for (l, h), col in (((7, 9), CARR), ((8, 1), ROLE)):
            axC.plot(xs, [np.array(d["measures"][s]["M1"])[l, h] for s in steps], ls, marker="o", color=col,
                     label=f"head {l}.{h}, {lab}")
    axC.axvspan(500, 2000, color="#F4E1D2", lw=0, zorder=0)
    axC.set_ylim(0, 0.85)
    axC.set_xticks([1000, 2000, 3000])
    axC.set_xlabel("training step")
    axC.set_ylabel("induction score")
    axC.set_title("c  two candidates (initialization 2)", fontsize=6.9)
    axC.legend(loc="lower right", fontsize=5.0, borderaxespad=0.1, handlelength=1.6)
    save(fig, "fig3_masking")
    return out


# ---------------------------------------------------------------- Fig: shared coordinate system (E35 maps)
def fig_maps():
    """69 x 69 within-layer correspondence of head-role maps (mean of 4 roles), sorted by initialization."""
    bad = set(json.loads((R / "e35_verified.json").read_text())["excluded"])
    seeds = ("default", "large-aux-2", "large-aux-3")
    recs = sorted({f.split("/")[-1].split("-1B__")[0] for f in glob.glob(str(R / "e35" / "*-1B__*.json")) if "step" not in f})
    keys = [(r, sd) for sd in seeds for r in recs if f"{r}|{sd}" not in bad and (R / "e35" / f"{r}-1B__{sd}.json").exists()]
    maps = {k: json.loads((R / "e35" / f"{k[0]}-1B__{k[1]}.json").read_text())["maps"] for k in keys}
    n = len(keys)
    C = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            v = np.mean([within(np.array(maps[keys[i]][m]), np.array(maps[keys[j]][m])) for m in ("M1", "M2", "M3", "M4")])
            C[i, j] = C[j, i] = v
    fig = plt.figure(figsize=(COL, 2.35))
    ax = fig.add_axes([0.13, 0.05, 0.66, 0.84])
    off = C.copy()
    np.fill_diagonal(off, np.nan)
    im = ax.imshow(np.ma.masked_invalid(off), cmap="Blues", vmin=0, vmax=0.6, interpolation="nearest")
    b = [sum(k[1] == sd for k in keys) for sd in seeds]
    edges = np.cumsum([0] + b)
    for e in edges[1:-1]:
        ax.axhline(e - 0.5, color=INK, lw=0.4)
        ax.axvline(e - 0.5, color=INK, lw=0.4)
    mids = [(edges[k] + edges[k + 1]) / 2 - 0.5 for k in range(3)]
    ax.set_xticks(mids, ["init. A", "init. B", "init. C"], fontsize=6.2)
    ax.set_yticks(mids, ["init. A", "init. B", "init. C"], fontsize=6.2, rotation=90, va="center")
    ax.tick_params(length=0)
    ax.xaxis.tick_top()
    for sp in ax.spines.values():
        sp.set_visible(False)
    cax = fig.add_axes([0.83, 0.2, 0.03, 0.55])
    cb = fig.colorbar(im, cax=cax)
    cb.ax.tick_params(labelsize=5.6)
    cb.set_label("which-head correspondence", fontsize=6.0)
    save(fig, "fig_maps")
    same = [C[i, j] for i in range(n) for j in range(i + 1, n) if keys[i][1] == keys[j][1]]
    diff = [C[i, j] for i in range(n) for j in range(i + 1, n) if keys[i][1] != keys[j][1]]
    return {"n_models": n, "same_init_mean": float(np.mean(same)), "diff_init_mean": float(np.mean(diff)),
            "same_init_min": float(np.min(same)), "diff_init_max": float(np.max(diff))}


# ---------------------------------------------------------------- Fig: same class, different member (Pythia-410M pair)
def fig_classes():
    a = npz(R / "e81" / "pythia__pythia-410m__143000.npz")
    b = npz(R / "e81" / "pythia__pythia-410m-deduped__143000.npz")
    da, db = a["dla"].mean(0), b["dla"].mean(0)
    heads = list(dict.fromkeys(top(da) + top(db)))
    fig = plt.figure(figsize=(COL, 1.45))
    ax = fig.add_axes([0.12, 0.27, 0.86, 0.6])
    x = np.arange(len(heads))
    ax.bar(x - 0.19, [da[h] for h in heads], 0.36, color=CARR, label="Pythia-410M", zorder=2)
    ax.bar(x + 0.19, [db[h] for h in heads], 0.36, color="#E69F00", label="Pythia-410M-deduped", zorder=2)
    ax.set_xticks(x, [f"{l}.{h}" for l, h in heads], fontsize=6.2)
    ax.set_ylabel("direct effect on IOI")
    ax.set_xlabel("head (layer.head)", labelpad=1)
    ax.axhline(0, color=INK, lw=0.5)
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.legend(loc="upper right", fontsize=5.8)
    save(fig, "fig_classes")
    return {f"{l}.{h}": [float(da[l, h]), float(db[l, h])] for l, h in heads}


# ---------------------------------------------------------------- Tables
def fig_scale():
    a = json.loads((R / "e45" / "analysis.json").read_text())
    sizes = ["4M", "6M", "8M", "10M", "14M", "16M", "20M", "60M", "90M", "150M", "300M", "530M", "750M"]
    num = lambda z: float(z[:-1]) * (1e6 if z.endswith("M") else 1e9)  # noqa: E731
    v = json.loads((R / "e35_verified.json").read_text())["agreement"]
    fig = plt.figure(figsize=(COL, 1.55))
    ax = fig.add_axes([0.13, 0.25, 0.84, 0.6])
    out = {}
    for m, lab, col in (("M1", "induction", ROLE), ("M2", "previous token", CARR)):
        xs = [num(z) for z in sizes if m in a[z]] + [1e9]
        si = [a[z][m]["within_layer"]["SI"] for z in sizes if m in a[z]] + [v[m]["SI"]]
        dd = [a[z][m]["within_layer"]["DD"] for z in sizes if m in a[z]] + [v[m]["DD"]]
        ax.plot(xs, si, "-o", color=col, label=f"{lab}: same initialization")
        ax.plot(xs, dd, "--", color=col, lw=0.9, label=f"{lab}: different initialization")
        out[m] = {"sizes": sizes + ["1B"], "SI": si, "DD": dd}
    ax.set_xscale("log")
    ax.set_xlabel("parameters (DataDecide)")
    ax.set_ylabel("which-head corresp.")
    ax.axhline(0, color=INK, lw=0.5)
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.legend(loc="upper left", fontsize=5.3, ncol=1)
    save(fig, "fig_scale")
    return out


def tab_pythia():
    a = json.loads((R / "e73" / "analysis.json").read_text())
    rows = []
    for z, lab in (("160m", "160M"), ("410m", "410M"), ("1b", "1B"), ("1.4b", "1.4B"), ("6.9b", "6.9B"), ("12b", "12B")):
        x = a[z]["by_kind"]["deduped"]
        rows.append(f"{lab} & {a[z]['reference']['top'][0]} & {'yes' if x['ref_top1_in_target_top3'] else 'no'} & "
                    f"{int(round(x['ref_top3_overlap'] * 3))}/3 & {x['transfer3']:.2f} \\\\")
    tex = ("\\begin{tabular}{lcccc}\n\\toprule\nSize & \\makecell{main carrier\\\\(standard)} & \\makecell{also in sibling's\\\\top three} & "
           "\\makecell{top-3\\\\shared} & transfer \\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (PAPER / "tables" / "tab_pythia.tex").write_text(tex)


def tab_reliability():
    rel = json.loads((R / "e81" / "analysis.json").read_text())["reliability"]
    groups = {"DataDecide-1B (9 models)": [k for k in rel if k.startswith("dd__")],
              "Pythia-410M": ["pythia__pythia-410m__143000"],
              "OLMo-2-1B (pretraining end)": ["hf__OLMo-2-0425-1B__stage1-step1907359-tokens4001B"]}
    cols = [("ind", "induction"), ("att_io", "END$\\to$IO"), ("abl", "ablation"), ("dla", "DLA (rank)"), ("dla_pearson", "DLA (value)")]
    rows = []
    for g, ks in groups.items():
        ks = [k for k in ks if k in rel]
        rows.append(g + " & " + " & ".join(f"{np.mean([rel[k][c] for k in ks]):.2f}" for c, _ in cols) + " \\\\")
    tex = ("\\begin{tabular}{l" + "c" * len(cols) + "}\n\\toprule\n& " + " & ".join(n for _, n in cols) + " \\\\\n\\midrule\n"
           + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (PAPER / "tables" / "tab_reliability.tex").write_text(tex)


def fig_distance():
    """1B siblings: corpus distance (unigram Jensen-Shannon) vs which-head correspondence (mean over 3 roles, 3 seeds)."""
    dist = json.loads((R / "e60" / "recipe_distance.json").read_text())["pairs"]
    bad = set(json.loads((R / "e35_verified.json").read_text())["excluded"])
    seeds = ("default", "large-aux-2", "large-aux-3")
    recs = sorted({f.split("/")[-1].split("-1B__")[0] for f in glob.glob(str(R / "e35" / "*-1B__*.json")) if "step" not in f})
    maps = {(r, sd): json.loads((R / "e35" / f"{r}-1B__{sd}.json").read_text())["maps"] for r in recs for sd in seeds
            if f"{r}|{sd}" not in bad and (R / "e35" / f"{r}-1B__{sd}.json").exists()}
    xs, ys = [], []
    for a, b in itertools.combinations(recs, 2):
        key = f"{a}|{b}" if f"{a}|{b}" in dist else f"{b}|{a}"
        if key not in dist:
            continue
        v = [np.mean([within(np.array(maps[(a, sd)][m]), np.array(maps[(b, sd)][m])) for m in ("M1", "M2", "M4")])
             for sd in seeds if (a, sd) in maps and (b, sd) in maps]
        if v:
            xs.append(dist[key]["js_uni"])
            ys.append(float(np.mean(v)))
    from scipy.stats import spearmanr
    rho = spearmanr(xs, ys)[0]
    fig = plt.figure(figsize=(COL, 1.55))
    ax = fig.add_axes([0.14, 0.25, 0.83, 0.62])
    ax.scatter(xs, ys, s=5, color=ROLE, alpha=0.7, lw=0, zorder=3)
    ax.set_xscale("log")
    ax.set_xlabel("corpus distance (unigram Jensen--Shannon)")
    ax.set_ylabel("which-head corresp.")
    ax.grid(color=GRID, lw=0.5, zorder=0)
    ax.text(0.97, 0.92, f"Spearman $\\rho$ = {rho:.2f}, {len(xs)} corpus pairs", transform=ax.transAxes, ha="right", fontsize=6.0)
    save(fig, "fig_distance")
    return {"rho": float(rho), "n": len(xs), "range": [float(min(ys)), float(max(ys))]}


def tab_classes():
    a = json.loads((R / "e75" / "analysis.json").read_text())
    rows = []
    def row(name, prof, h, classes):
        rows.append(f"{name} & \\head{{{h}}} & {prof['dla']:.2f} & {prof['att_s2']:.2f} & ${prof['ov_copy']:.2f}$ & "
                    f"{len(classes['NM'])} & {len(classes['NNM'])} \\\\")
    for size, lab in (("160m", "160M"), ("410m", "410M")):
        d = a[size]
        tgt = "deduped"
        # standard model: its strongest S2-attending, negative-copy head among its reference heads
        refp = d[tgt]["ref_heads_profile"]
        h = max(refp, key=lambda k: refp[k]["ref"]["dla"] if refp[k]["ref"]["ov_copy"] < 0 else -9)
        row(f"Pythia-{lab}", refp[h]["ref"], h, d["ref_classes"])
        for t, tl in (("deduped", f"Pythia-{lab}-dedup."), ("seed1", f"Pythia-{lab} seed 1")):
            if t not in d:
                continue
            op = d[t]["target_own_profile"]
            h = max(op, key=lambda k: op[k]["target"]["dla"] if op[k]["target"]["ov_copy"] < 0 else -9)
            row(tl, op[h]["target"], h, d[t]["classes"])
    tex = ("\\begin{tabular}{llccccc}\n\\toprule\n& \\multicolumn{4}{c}{subject-suppression head} & \\makecell{name\\\\movers} & "
           "\\makecell{negative\\\\name movers} \\\\\n\\cmidrule(lr){2-5}\nModel & head & effect & \\makecell{attn.\\\\to S2} & \\makecell{name\\\\copy} & & \\\\\n"
           "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (PAPER / "tables" / "tab_classes.tex").write_text(tex)


def tab_mapping():
    a = json.loads((R / "e75" / "analysis.json").read_text())
    ro = {"160m": json.loads((R / "e75" / "role_only_160m.json").read_text()),
          "410m": json.loads((R / "e75" / "role_only_410m.json").read_text())}
    tr = json.loads((R / "e75" / "type_rule_posthoc.json").read_text())
    cols = [("160m", "deduped", "160m-deduped"), ("410m", "deduped", "410m-deduped"), ("410m", "seed1", "410m-seed1")]
    def get(size, t, key):
        return a[size][t]["sets"][key]["ratio_total"]
    rows = [("Same head index", [get(s, t, "index") for s, t, _ in cols]),
            ("Nearest attention / OV profile", [ro[s][t]["ratio"] if t in ro[s] else None for s, t, _ in cols]),
            ("Class rule (attention and OV sign)", [tr[k]["ratio"] for _, _, k in cols]),
            ("Profile with the target's causal readout", [get(s, t, "profile_map") for s, t, _ in cols])]
    fmt = lambda v: "--" if v is None else f"{v:.2f}".replace("-", "$-$")  # noqa: E731
    body = "\n".join(f"{n} & " + " & ".join(fmt(v) for v in vals) + " \\\\" for n, vals in rows)
    tex = ("\\begin{tabular}{lccc}\n\\toprule\n& \\multicolumn{2}{c}{same initialization} & \\makecell{different\\\\initialization} \\\\\n"
           "\\cmidrule(lr){2-3}\\cmidrule(lr){4-4}\nMapping & 160M-dedup. & 410M-dedup. & 410M seed 1 \\\\\n\\midrule\n" + body
           + "\n\\bottomrule\n\\end{tabular}\n")
    (PAPER / "tables" / "tab_mapping.tex").write_text(tex)


def tab_roles():
    e59 = json.loads((R / "e59" / "analysis.json").read_text())
    names = [("M1", "Induction"), ("M2", "Previous token"), ("M3", "Attention sink"), ("M4", "Knowledge retrieval"),
             ("R1", "Duplicate token"), ("R2", "Current token"), ("R3", "Two tokens back"), ("R4", "Delimiter"),
             ("R5", "OV copying (weights only)")]
    rows = []
    for k, n in names:
        d = e59[k]
        rows.append(f"{n} & {d['SI']['within']:.2f} & {d['SD']['within']:.2f} & {d['DD']['within']:.2f} & "
                    f"{d['SI']['layer_profile']:.2f} / {d['DD']['layer_profile']:.2f} \\\\")
    tex = ("\\begin{tabular}{lcccc}\n\\toprule\n& \\multicolumn{3}{c}{which head within the layer} & which layer \\\\\n"
           "\\cmidrule(lr){2-4}\\cmidrule(lr){5-5}\nRole & \\makecell{same init.\\\\diff.\\ corpus} & "
           "\\makecell{diff.\\ init.\\\\same corpus} & \\makecell{both\\\\differ} & \\makecell{same init.\\ /\\\\both differ} \\\\\n\\midrule\n"
           + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (PAPER / "tables" / "tab_roles.tex").write_text(tex)


def tab_lineage():
    a = json.loads((R / "e81" / "analysis.json").read_text())["B"]
    order = [("stage1 -> stage2 i1 @5B", "Pretraining end $\\to$ midtraining, 5B tokens"),
             ("stage1 -> stage2 i1 end", "Pretraining end $\\to$ midtraining mix 1, 51B"),
             ("stage1 -> stage2 i2 end", "Pretraining end $\\to$ midtraining mix 2, 51B"),
             ("stage1 -> stage2 i3 end", "Pretraining end $\\to$ midtraining mix 3, 51B"),
             ("SFT -> DPO", "SFT $\\to$ DPO"), ("DPO -> Instruct", "DPO $\\to$ Instruct"),
             ("pythia-410m 66k -> 143k", "Pythia-410M step 66k $\\to$ 143k")]
    rows = []
    for k, n in order:
        c = a[k]
        rows.append(f"{n} & {c['att_io']['r']:.2f} & {min(c['abl']['corrected'], 1.0):.2f} & {c['top3_overlap_dla']}/3 & "
                    f"{min(c['additive_transfer_abl'], 1.0):.2f} & {c['top3_dla'][1][0]} \\\\")
    s = a["SIBLING pythia-410m std vs dedup"]
    rows.append("\\midrule\n" + f"Pythia-410M vs.\\ its deduplicated sibling & {s['att_io']['r']:.2f} & {s['abl']['corrected']:.2f} & "
                f"{s['top3_overlap_dla']}/3 & {s['additive_transfer_abl']:.2f} & {s['top3_dla'][1][0]} \\\\")
    tex = ("\\begin{tabular}{lccccc}\n\\toprule\n& \\makecell{attention\\\\role} & \\makecell{ablation\\\\map} & "
           "\\makecell{top-3\\\\carriers} & transfer & \\makecell{main\\\\carrier} \\\\\n\\midrule\n" + "\n".join(rows)
           + "\n\\bottomrule\n\\end{tabular}\n")
    (PAPER / "tables" / "tab_lineage.tex").write_text(tex)


def main():
    fig_schematic_grids()
    fig1_dots()
    stats = {"fig_maps": fig_maps()}
    fig_heatmaps()
    fig2()
    stats["fig3"] = fig_competition()
    tab_roles()
    tab_lineage()
    tab_pythia()
    tab_reliability()
    stats["fig_scale"] = fig_scale()
    stats["fig_distance"] = fig_distance()
    tab_classes()
    tab_mapping()
    (PAPER / "figures" / "numbers.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))



# ---------------------------------------------------------------- Fig 1: schematic of the three relations
def fig_schematic():
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig = plt.figure(figsize=(COL, 2.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    def box(x, y, w, h, text, fc, fs=5.6, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=INK, lw=0.6))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")

    def arrow(x0, y0, x1, y1, col=INK, style="-|>", ls="-"):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=5, lw=0.6, color=col, linestyle=ls))

    def label(x, y, text, src, ysrc=None):
        ax.text(x, y, text, ha="center", va="center", fontsize=5.6, style="italic")
        ax.text(x, y - 0.42 if ysrc is None else ysrc, src, ha="center", va="center", fontsize=4.6, color=OTHER)
    INIT, RUN, DESC = "#DCE9F5", "#F7F7F7", "#FBE3D6"
    box(0.25, 5.55, 2.85, 0.75, "initialization A", INIT, bold=True)
    box(0.15, 3.95, 1.2, 0.72, "corpus X", RUN)
    box(2.0, 3.95, 1.2, 0.72, "corpus Y", RUN)
    arrow(1.1, 5.55, 0.75, 4.67)
    arrow(2.25, 5.55, 2.6, 4.67)
    box(4.1, 5.55, 1.45, 0.75, "init. B", INIT, bold=True)
    box(4.22, 3.95, 1.2, 0.72, "corpus X", RUN)
    arrow(4.82, 5.55, 4.82, 4.67)
    arrow(1.38, 4.31, 1.97, 4.31, col=ROLE, style="<|-|>", ls="--")
    arrow(3.23, 4.31, 4.19, 4.31, col=OTHER, style="<|-|>", ls="--")
    box(0.15, 2.45, 1.2, 0.7, "midtraining", DESC)
    box(0.15, 1.1, 1.2, 0.8, "SFT, DPO,\ninstruct", DESC)
    arrow(0.75, 3.95, 0.75, 3.15)
    arrow(0.75, 2.45, 0.75, 1.9)
    label(1.68, 4.82, "siblings", "DataDecide, Pythia", ysrc=3.68)
    label(3.71, 4.82, "unrelated", "DataDecide", ysrc=3.68)
    label(2.5, 1.85, "descendants", "OLMo 2, Pythia")
    ax.text(2.75, 0.45, "controlled pretraining: interventions within a run", fontsize=4.6, color=OTHER, ha="center")
    rows = ["layer of a role", "algorithm", "which head\nhas a role", "which heads\ncarry a task"]
    cols = ["unrelated", "siblings", "descen-\ndants"]
    val = [[1, 1, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1]]
    x0, xs, y0, ys = 7.35, 0.92, 4.95, 1.13
    ax.text(x0 + xs, 6.3, "carries over to", ha="center", fontsize=5.8, fontweight="bold")
    for j, c in enumerate(cols):
        ax.text(x0 + j * xs, 5.75, c, ha="center", va="center", fontsize=5.1)
    for i, r in enumerate(rows):
        y = y0 - i * ys
        ax.text(x0 - 0.5, y, r, ha="right", va="center", fontsize=5.3)
        col = CARR if i == 3 else ROLE
        for j in range(3):
            ax.scatter([x0 + j * xs], [y], s=24, color=col if val[i][j] else "white", edgecolors=col, linewidths=0.8, zorder=3)
    save(fig, "fig0_schematic")


def fig_schematic_grids():
    """Fig 1: three relations drawn as pairs of [layer x head] grids; blue = a head role, orange = the task carrier."""
    from matplotlib.patches import FancyBboxPatch, Rectangle
    LIGHT = "#E6E9EC"
    fig = plt.figure(figsize=(COL, 1.22))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 30.3)
    ax.set_ylim(2.8, 15.0)
    ax.axis("off")
    c = 1.02  # cell size
    model1 = {"role": [(0, 2), (2, 0)], "carrier": [(1, 3)]}
    second = {"unrelated": {"role": [(0, 0), (2, 3)], "carrier": [(1, 1)]},
              "siblings": {"role": [(0, 2), (2, 0)], "carrier": [(1, 1)]},
              "descendants": {"role": [(0, 2), (2, 0)], "carrier": [(1, 3)]}}
    titles = {"unrelated": ("Unrelated", "different initialization"),
              "siblings": ("Siblings", "same init., other data"),
              "descendants": ("Descendants", "continued training")}

    def grid(x0, y0, m):
        for li in range(3):
            for hj in range(4):
                fc = LIGHT
                if (li, hj) in m["role"]:
                    fc = ROLE
                if (li, hj) in m["carrier"]:
                    fc = CARR
                ax.add_patch(Rectangle((x0 + hj * c, y0 + (2 - li) * c), c * 0.88, c * 0.88, fc=fc, ec="none"))
    for k, rel in enumerate(("unrelated", "siblings", "descendants")):
        x = 0.25 + k * 10.0
        ax.add_patch(FancyBboxPatch((x, 3.0), 9.6, 11.7, boxstyle="round,pad=0,rounding_size=0.6",
                                    fc="#F7F8FA", ec="#D5D9DE", lw=0.5))
        ax.text(x + 4.8, 13.6, titles[rel][0], ha="center", va="center", fontsize=7.2, fontweight="bold")
        ax.text(x + 4.8, 12.35, titles[rel][1], ha="center", va="center", fontsize=5.9, color=INK)
        grid(x + 0.45, 7.7, model1)
        grid(x + 5.15, 7.7, second[rel])
        ax.text(x + 0.45 + 2.0, 6.8, "model 1", ha="center", va="center", fontsize=5.4, color=OTHER)
        ax.text(x + 5.15 + 2.0, 6.8, "model 2", ha="center", va="center", fontsize=5.4, color=OTHER)
        same_role = second[rel]["role"] == model1["role"]
        same_carr = second[rel]["carrier"] == model1["carrier"]
        ax.text(x + 4.8, 5.15, ("same" if same_role else "different") + " role heads", ha="center", va="center", fontsize=6.0,
                color=ROLE, fontweight="bold" if same_role else "normal")
        ax.text(x + 4.8, 3.95, ("same" if same_carr else "different") + " carriers", ha="center", va="center", fontsize=6.0,
                color=CARR, fontweight="bold" if same_carr else "normal")
    save(fig, "fig0_schematic")


def fig1_dots():
    """Fig 2 (redesign): per-pair dots and mean bars for attention-role vs carrier correspondence by relation."""
    E81 = {f.split("/")[-1][:-4]: npz(f) for f in glob.glob(str(R / "e81" / "*.npz"))}
    E83 = {f.split("/")[-1][:-4]: npz(f) for f in glob.glob(str(R / "e83" / "*step69369*.npz"))}
    dd = {k: v for k, v in E81.items() if k.startswith("dd__")}
    rel = {"same training\nlineage": [], "same init.,\nclosely related\ndata": [], "same init.,\ndifferent\ncorpus": [],
           "different\ninitialization": []}
    keys = sorted(dd)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ca, sa = a.split("__")[1], a.split("seed-")[1]
            cb, sb = b.split("__")[1], b.split("seed-")[1]
            if sa != sb:
                rel["different\ninitialization"].append(pair_stats(dd[a], dd[b]))
            elif ca != cb:
                rel["same init.,\ndifferent\ncorpus"].append(pair_stats(dd[a], dd[b]))
    for s in ("default", "large-aux-2", "large-aux-3"):
        a, b = f"dd__DataDecide-dolma1_7-1B__step69369-seed-{s}", f"dd__DataDecide-dolma1_7-no-flan-1B__step69369-seed-{s}"
        if a in E83 and b in E83:
            rel["same init.,\nclosely related\ndata"].append(pair_stats(E83[a], E83[b]))
    rel["same init.,\nclosely related\ndata"].append(pair_stats(E81["pythia__pythia-410m__143000"], E81["pythia__pythia-410m-deduped__143000"]))
    O = "hf__OLMo-2-0425-1B__"
    lineage = [("pythia__pythia-410m__66000", "pythia__pythia-410m__143000")]
    lineage += [(O + "stage1-step1907359-tokens4001B", O + f"stage2-ingredient{i}-step23852-tokens51B") for i in (1, 2, 3)]
    lineage += [("hf__OLMo-2-0425-1B-SFT__main", "hf__OLMo-2-0425-1B-DPO__main"), ("hf__OLMo-2-0425-1B-DPO__main", "hf__OLMo-2-0425-1B-Instruct__main")]
    for a, b in lineage:
        rel["same training\nlineage"].append(pair_stats(E81[a], E81[b]))
    fig = plt.figure(figsize=(COL, 1.85))
    ax = fig.add_axes([0.14, 0.25, 0.84, 0.64])
    rng = np.random.default_rng(0)
    for k, (name, pairs) in enumerate(rel.items()):
        for j, col in enumerate((ROLE, CARR)):
            v = np.array([p[j] for p in pairs])
            x = k + (j - 0.5) * 0.36
            ax.bar(x, v.mean(), 0.32, color=col, alpha=0.25, zorder=1)
            ax.plot([x - 0.16, x + 0.16], [v.mean()] * 2, color=col, lw=1.4, zorder=3)
            ax.scatter(x + rng.uniform(-0.09, 0.09, len(v)), v, s=5, color=col, lw=0, zorder=4)
            ax.text(x, v.max() + 0.045, f"{v.mean():.2f}", ha="center", fontsize=5.6, color=col, fontweight="bold")
    ax.set_xticks(range(len(rel)), list(rel), fontsize=5.8)
    ax.set_ylim(-0.25, 1.15)
    ax.set_yticks([0, 0.5, 1.0])
    ax.axhline(0, color=INK, lw=0.5)
    ax.set_ylabel("correspondence of head maps")
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.text(0.02, 1.06, "which head attends to the IO", transform=ax.transAxes, color=ROLE, fontsize=6.2, fontweight="bold")
    ax.text(0.52, 1.06, "which head carries IOI (causal)", transform=ax.transAxes, color=CARR, fontsize=6.2, fontweight="bold")
    save(fig, "fig1_carryover")


def fig_heatmaps():
    """Sec 4: Pythia-410M and its deduplicated sibling, END->IO attention and DLA, carriers boxed."""
    from matplotlib.patches import Rectangle
    a = npz(R / "e81" / "pythia__pythia-410m__143000.npz")
    b = npz(R / "e81" / "pythia__pythia-410m-deduped__143000.npz")
    lo, hi = 9, 22
    fig = plt.figure(figsize=(COL, 2.2))
    vmax_att = max(a["att_io"].mean(0)[lo:hi].max(), b["att_io"].mean(0)[lo:hi].max())
    vmax_dla = max(a["dla"].mean(0)[lo:hi].max(), b["dla"].mean(0)[lo:hi].max())
    for r, (key, cmap, vmax, lab) in enumerate((("att_io", "Blues", vmax_att, "attention END$\\to$IO"),
                                                 ("dla", "Oranges", vmax_dla, "direct effect on IOI"))):
        for cidx, (d, name) in enumerate(((a, "Pythia-410M"), (b, "Pythia-410M-dedup."))):
            ax = fig.add_axes([0.1 + cidx * 0.45, 0.52 - r * 0.43, 0.4, 0.37])
            M = d[key].mean(0)[lo:hi]
            ax.imshow(np.clip(M, 0, None), cmap=cmap, vmin=0, vmax=vmax, aspect="auto", interpolation="nearest")
            for (l, h) in top(d["dla"].mean(0)):
                if lo <= l < hi:
                    ax.add_patch(Rectangle((h - 0.5, l - lo - 0.5), 1, 1, fill=False, ec=INK, lw=0.9))
            ax.set_xticks([0, 15], ["0", "15"] if r == 1 else ["", ""], fontsize=5.4)
            ax.set_yticks([0, hi - lo - 1], [str(lo), str(hi - 1)], fontsize=5.4)
            if r == 0:
                ax.set_title(name, fontsize=6.6, fontweight="normal", loc="center")
            if cidx == 0:
                ax.set_ylabel(lab, fontsize=6.0)
            if r == 1:
                ax.set_xlabel("head", fontsize=5.6, labelpad=-4)
            for sp in ax.spines.values():
                sp.set_visible(False)
    save(fig, "fig_classes")


def fig_competition():
    """Sec 6 (E84-E86): which candidate becomes the strongest induction head is not reproducible; the role map is."""
    import e86_analyze as e86
    E46 = R / "e46"
    full = lambda n: json.loads((E46 / f"{n}.json").read_text())["measures"] if (E46 / f"{n}.json").exists() else None  # noqa: E731
    pats = {"base": "L_i{i}_c4_o1_st3000", **e86.NAMES, "repeat": "L_i{i}_c4_o1_st3000_maskrepeat0.1_500-2000"}
    steps = ["100", "250", "500", "750", "1000", "1500", "2000", "3000"]
    xs = [int(s) for s in steps]
    MASK = "#E69F00"
    fig = plt.figure(figsize=(TXT, 1.72))
    axA = fig.add_axes([0.055, 0.25, 0.19, 0.6])
    axB = fig.add_axes([0.305, 0.25, 0.2, 0.6])
    axC = fig.add_axes([0.575, 0.25, 0.16, 0.6])
    axD = fig.add_axes([0.80, 0.25, 0.19, 0.6])
    # a: one initialization, two identical runs
    b, r = full(pats["base"].format(i=12)), full(pats["rerun"].format(i=12))
    for (l, h), col in (((7, 2), CARR), ((8, 3), ROLE)):
        for d, ls, mk in ((b, "-", "o"), (r, "--", "s")):
            axA.plot(xs, [np.array(d[s]["M1"])[l, h] for s in steps], ls, marker=mk, ms=2.4, color=col)
    axA.text(110, 0.72, "head 8.3, runs 1 and 2", color=ROLE, fontsize=5.8)
    axA.text(110, 0.62, "head 7.2, run 1", color=CARR, fontsize=5.8)
    axA.text(2000, 0.06, "7.2, run 2", color=CARR, fontsize=5.8, ha="center")
    axA.set_xscale("log")
    axA.set_xticks([100, 1000, 3000], ["100", "1k", "3k"])
    axA.set_ylim(-0.03, 0.8)
    axA.set_ylabel("induction score")
    axA.set_xlabel("training step")
    axA.set_title("a  two identical runs", fontsize=6.9)
    # b: original strongest head in the other run, per initialization
    rows = []
    for i in range(1, 16):
        bm = full(pats["base"].format(i=i))
        if bm is None:
            continue
        o = e86.best(bm["3000"]["M1"])
        for cond in ("rerun", "mask0", "mask1"):
            d = full(pats[cond].format(i=i))
            if d is not None:
                D = np.array(d["3000"]["M1"])
                rows.append((i, cond, D[o] / D.max()))
    for cond, col, mk, dx, lab in (("rerun", INK, "o", -0.18, "identical rerun"), ("mask0", MASK, "^", 0.06, "random 10% mask"),
                                   ("mask1", MASK, "^", 0.22, None)):
        v = [(i + dx, x) for i, c, x in rows if c == cond]
        axB.scatter(*zip(*v), s=7, marker=mk, color=col, lw=0, label=lab, zorder=3)
    axB.axhline(1, color=GRID, lw=0.8, zorder=0)
    axB.axhline(0.9, color=OTHER, lw=0.5, ls=":", zorder=0)
    axB.set_xticks([1, 5, 10, 15])
    axB.set_xlabel("initialization")
    axB.set_ylabel("first run's head / strongest")
    axB.set_ylim(-0.05, 1.08)
    axB.legend(loc="lower left", fontsize=5.4, handletextpad=0.1, borderaxespad=0.1)
    axB.set_title("b  strongest head, 15 initializations", fontsize=6.9)
    # c: role maps reproduce
    res = json.loads((R / "e85" / "e86_analysis.json").read_text())
    groups = (("rerun", ("rerun",)), ("random\nmask", ("mask0", "mask1")))
    for k, (name, conds) in enumerate(groups):
        for j, (key, col) in enumerate((("r_M1", ROLE), ("r_M2", "#56B4E9"))):
            v = np.array([x[key] for x in res["rows"] if x["cond"] in conds])
            x0 = k + (j - 0.5) * 0.36
            axC.bar(x0, v.mean(), 0.32, color=col, alpha=0.25)
            axC.plot([x0 - 0.16, x0 + 0.16], [v.mean()] * 2, color=col, lw=1.3)
            axC.scatter(x0 + np.random.default_rng(k * 2 + j).uniform(-0.09, 0.09, len(v)), v, s=4, color=col, lw=0, zorder=3)
    for j, (key, col) in enumerate((("r_M1", ROLE), ("r_M2", "#56B4E9"))):
        x0 = 2 + (j - 0.5) * 0.36
        axC.plot([x0 - 0.16, x0 + 0.16], [res["unrelated"][key]] * 2, color=col, lw=1.3)
    axC.text(0.25, 1.08, "induction", color=ROLE, fontsize=5.6, ha="center")
    axC.text(1.8, 1.08, "previous token", color="#56B4E9", fontsize=5.6, ha="center")
    axC.set_xticks([0, 1, 2], ["rerun", "random\nmask", "other\ninit."], fontsize=5.8)
    axC.set_ylim(-0.1, 1.15)
    axC.set_yticks([0, 0.5, 1])
    axC.axhline(0, color=INK, lw=0.5)
    axC.set_ylabel("role-map correspondence")
    axC.set_title("c  role maps", fontsize=6.9)
    # d: copying ability, relative to the first run
    for cond, col, inits, lab in (("rerun", INK, range(1, 16), "rerun"), ("mask0", MASK, range(1, 16), "random 10%"),
                                  ("repeat", CARR, (1, 2, 3), "most repetitive 10%")):
        Y = []
        for i in inits:
            bm, d = full(pats["base"].format(i=i)), full(pats[cond].format(i=i))
            if bm is None or d is None:
                continue
            Y.append([d[s]["copy_gain"] / bm[s]["copy_gain"] for s in steps[4:]])
        Y = np.array(Y)
        axD.plot(xs[4:], Y.mean(0), "-o", ms=2.4, color=col, label=lab, zorder=3)
        if cond == "repeat":
            axD.fill_between(xs[4:], Y.min(0), Y.max(0), color=col, alpha=0.15, lw=0)
    axD.axvspan(500, 2000, color="#F4E1D2", lw=0, zorder=0)
    axD.axhline(1, color=INK, lw=0.5)
    axD.set_ylim(0, 1.6)
    axD.set_xlim(900, 3100)
    axD.set_xticks([1000, 2000, 3000], ["1k", "2k", "3k"])
    axD.text(1450, 1.45, "masking window", color="#B5835A", fontsize=5.6, ha="center")
    axD.set_xlabel("training step")
    axD.set_ylabel("copying rel. to first run")
    axD.legend(loc="lower right", fontsize=5.2, handlelength=1.2, borderaxespad=0.1)
    axD.set_title("d  copying ability", fontsize=6.9)
    save(fig, "fig3_masking")
    return {"rows": [(i, c, round(float(x), 3)) for i, c, x in rows]}


if __name__ == "__main__":
    main()
