"""Figures and tables for paper-acl-v3 (all numbers computed from result files).

  Fig 1  fig1_carryover   attention-role vs carrier correspondence by relation between two models (E81, E83, E82)
  Fig 2  fig2_lineage     carriers along a training lineage: Pythia-410M pair (E82) and DataDecide-1B runs (E83)
  Fig 3  fig3_masking     MDA-style data masking on induction heads (E84)
  Tables tab_roles.tex (E35 / E59), tab_lineage.tex (E81), tab_audit.tex (P09 / P11 / P12 / P13)
Usage: figs_v3.py
"""
import glob
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
           "same init.,\nnear-identical\ncorpus": [], "same training\nlineage": []}
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
            rel["same init.,\nnear-identical\ncorpus"].append(pair_stats(E83[a], E83[b]))
    a, b = "pythia__pythia-410m__143000", "pythia__pythia-410m-deduped__143000"
    rel["same init.,\nnear-identical\ncorpus"].append(pair_stats(E81[a], E81[b]))
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
    ax.set_ylim(-0.2, 4.7)
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.legend(loc="upper left", fontsize=5.6, ncol=1, borderaxespad=0.2)
    ax.set_title("a  Pythia-410M and its deduplicated sibling", fontsize=7.2)
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
    ax2.set_xticks(range(len(steps)), [f"{s / 1000:g}k" if s < 60000 else f"{s // 1000}k" for s in steps])
    lab = {"c4-1B": "C4", "dolma1_7-1B": "Dolma", "dolma1_7-no-flan-1B": "Dolma$-$Flan", "dclm-baseline-1B": "DCLM"}
    ax2.set_yticks(range(len(names)), [f"{lab[n.split('/')[0]]} {n.split('/')[1].replace('large-aux-', 's')}" for n in names],
                   fontsize=5.4)
    ax2.set_xlabel("training step (DataDecide-1B, 69k total)")
    ax2.set_title("b  main IOI carrier already the final one (filled)", fontsize=7.2)
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
    axC.legend(loc="upper left", fontsize=5.2, borderaxespad=0.1)
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
    stats = {"fig1": fig1()}
    stats["fig_maps"] = fig_maps()
    stats["fig_classes"] = fig_classes()
    fig2()
    stats["fig3"] = fig3()
    tab_roles()
    tab_lineage()
    tab_pythia()
    tab_reliability()
    stats["fig_scale"] = fig_scale()
    (PAPER / "figures" / "numbers.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
