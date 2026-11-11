"""E186 figures: one factor x layer map per model, one training-time figure.  Card: division/experiments/E186-atlas-capture-breadth.md"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import NAMES, BANDS, E186_OLMOE  # noqa: E402

A = os.environ.get("E186_A6", os.path.expanduser("~/mechpop_cache/atlas_e186"))
RES = os.environ.get("E186_RES", os.path.join(os.path.dirname(__file__), "..", "results", "e186"))
DIV = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#e34948"])
SEQ = LinearSegmentedColormap.from_list("seq", ["#fcfcfb", "#2a78d6", "#0b2f5e"])
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
INK, MUTED = "#222222", "#777777"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
LAB = {"inp": "input id", "prev": "previous id", "nxt": "true next id", "pred": "predicted next id", "pos": "position",
       "seq": "sequence", "corpus": "corpus", "upos": "UPOS", "lang": "language", "script": "script",
       "sid": "parallel sentence", "inst": "sentence instance"}


def lab(k):
    if "|" in k:
        x, s = k.split("|")
        return f"{'+'.join(LAB.get(t, t) for t in x.split(','))} | {'+'.join(LAB.get(t, t) for t in s.split(','))}"
    return LAB.get(k, k)


def share(a):
    return a[..., 0] / a[..., 3]


def ridx(rn):
    return rn.index("T"), [i for i, n in enumerate(rn) if n.startswith("N_A")], \
        [i for i, n in enumerate(rn) if n.startswith("N_B")]


def ld(prefix, m):
    p = f"{A}/{prefix}_{m}.npz"
    if not os.path.exists(p):
        return None, None
    return dict(np.load(p)), json.load(open(f"{A}/{prefix}_{m}.json"))


ROWS = [("marg", f) for f in ["inp", "prev", "nxt", "pred", "pos", "seq", "corpus", "upos"]] + \
       [("cond", f) for f in ["prev|inp", "nxt|inp", "pred|inp", "pos|inp", "seq|inp", "corpus|inp", "upos|inp",
                              "inp|pred", "inp|prev"]]
GROWS = [("cf_d184", f) for f in ["seq", "prev", "pred", "nxt", "pos", "corpus", "upos"]] + \
        [("cf_d180", f) for f in ["sid", "inst", "pred", "lang", "script"]]
for m in ["phimoe", "mixtral", "dsv2lite"] + E186_OLMOE:
    r, info = ld("d184", m)
    if r is None:
        continue
    iT, iA, iB = ridx(info["routers"])
    T = np.stack([share(r[f"full|{k}|{f}"])[:, iT] for k, f in ROWS])
    B3 = np.stack([share(r[f"full|{k}|{f}"])[:, iB] for k, f in ROWS])
    B, Bmin, Bmax = B3.mean(2), B3.min(2), B3.max(2)
    fig = plt.figure(figsize=(13, 9), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[17, 12])
    ax = [fig.add_subplot(gs[0, i]) for i in range(3)]
    vmax = max(T.max(), B.max())
    for a, Z, t in ((ax[0], T, "trained router T"), (ax[1], B, "load-matched null N_B (mean of 8)")):
        im = a.imshow(Z, aspect="auto", cmap=SEQ, vmin=0, vmax=vmax, interpolation="nearest")
        a.set_title(t, color=INK)
    fig.colorbar(im, ax=ax[:2], shrink=.7, label="share  Î(e;X)/H(e)")
    D = T - B
    lim = max(np.abs(D).max(), 1e-6)
    im2 = ax[2].imshow(D, aspect="auto", cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), interpolation="nearest")
    yy, xx = np.where(~((T > Bmax) | (T < Bmin)))
    ax[2].scatter(xx, yy, s=4, c=MUTED, marker="o", linewidths=0)
    ax[2].set_title("T − N_B  (dot = T inside the 8-draw range)", color=INK)
    fig.colorbar(im2, ax=ax[2], shrink=.7, label="Δ share")
    ax[0].set_yticks(range(len(ROWS)))
    ax[0].set_yticklabels([lab(f) for _, f in ROWS])
    for a in ax:
        a.xaxis.set_major_locator(MaxNLocator(integer=True))
        a.set_xlabel("MoE layer")
        a.axhline(7.5, color=INK, lw=.8)
        if a is not ax[0]:
            a.set_yticks([])
    # G_freq panel
    gT, gB, gmin, gmax, ylab = [], [], [], [], []
    for pre, f in GROWS:
        c, ci = ld(pre, m)
        if c is None:
            continue
        jT, _, jB = ridx(ci["routers"])
        G = c[f][..., 3]
        gT.append(G[:, jT]); gB.append(G[:, jB].mean(1)); gmin.append(G[:, jB].min(1)); gmax.append(G[:, jB].max(1))
        ylab.append(("EN " if pre == "cf_d184" else "ML ") + lab(f) + " | input id")
    if gT:
        axg = fig.add_subplot(gs[1, :])
        gT, gB, gmin, gmax = map(np.stack, (gT, gB, gmin, gmax))
        Dg = gT - gB
        lim = max(np.abs(Dg).max(), 1e-6)
        im3 = axg.imshow(Dg, aspect="auto", cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), interpolation="nearest")
        yy, xx = np.where(~((gT > gmax) | (gT < gmin)))
        axg.scatter(xx, yy, s=5, c=MUTED, marker="o", linewidths=0)
        axg.set_yticks(range(len(ylab)))
        axg.set_yticklabels(ylab)
        axg.set_xlabel("MoE layer")
        axg.set_title("cross-fitted G_freq(X | input id): T − N_B mean (bits; lower bound, detection limit ≈ .08 bit; "
                      "dot = T inside the 8-draw range; EN = English view, ML = 20 FLORES sides)", color=INK)
        fig.colorbar(im3, ax=axg, shrink=.8, label="Δ bits")
    fig.suptitle(f"E186 routing variance atlas — {NAMES[m]} (top-1 expert)", color=INK)
    fig.savefig(f"{RES}/fig_map_{m}.png", dpi=140)
    plt.close(fig)
    print("map", m, flush=True)

# training-time figure
summ = json.load(open(f"{RES}/summary.json"))
tt = summ.get("training", {})
xs = {"olmoe0924_s5k": 20, "olmoe0924_s20k": 83, "olmoe0924_s80k": 335, "olmoe0924_s320k": 1342,
      "olmoe0924_s1220k": 5117, "olmoe0924_main": 7000}
XL = {"olmoe0924_s5k": "20B", "olmoe0924_s20k": "83B", "olmoe0924_s80k": "335B", "olmoe0924_s320k": "1.3T",
      "olmoe0924_s1220k": "5.1T", "olmoe0924_main": "rel."}
ks = [k for k in E186_OLMOE if k in tt]
if ks:
    x = np.array([xs[k] for k in ks])
    fig, ax = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    a = ax[0, 0]
    rat = np.array([tt[k]["ratio_tokfactors_mid"] for k in ks])
    for i, nm in enumerate(["input", "previous", "true next", "pred. next", "UPOS"]):
        a.plot(x, rat[:, i], "-o", ms=3, color=CAT[i], label=nm)
    a.axhline(1, color=MUTED, lw=.6, ls="--")
    a.set_title("vocabulary sharpening: mid-band share T / N_B", color=INK)
    a.legend(frameon=False, fontsize=7)
    a = ax[0, 1]
    a.plot(x, [tt[k]["Gsid_mid_T"] for k in ks], "-o", ms=3, color=CAT[0], label="parallel sentence | input: T")
    a.plot(x, [tt[k]["Gsid_mid_NB"] for k in ks], "--o", ms=3, color=CAT[0], alpha=.5, label="… N_B mean")
    a.plot(x, [tt[k]["Glang_mid_T"] for k in ks], "-o", ms=3, color=CAT[1], label="language | input: T")
    a.set_title("given the token: content vs language (G_freq, mid band, bits)", color=INK)
    a.legend(frameon=False, fontsize=7)
    a = ax[1, 0]
    a.plot(x, [tt[k]["l0_prev_over_inp_T"] for k in ks], "-o", ms=3, color=CAT[2], label="T")
    a.plot(x, [tt[k]["l0_prev_over_inp_NB"] for k in ks], "--o", ms=3, color=CAT[2], alpha=.5, label="N_B mean")
    a.axhline(1, color=MUTED, lw=.6, ls="--")
    a.set_title("layer 0: share(previous id) / share(input id)", color=INK)
    a.legend(frameon=False, fontsize=7)
    ax2 = a.twinx()
    ax2.plot(x, [tt[k]["acc"] for k in ks], ":", color=MUTED)
    ax2.set_ylabel("English next-token accuracy (dotted)", color=MUTED)
    a = ax[1, 1]
    ks2 = [k for k in ks if "sat_T" in tt[k]]
    for i, k in enumerate(ks2):
        a.plot(tt[k]["sat_T"], "-", color=CAT[i % 6], label=f"T {NAMES[k].replace('OLMoE-0924 ', '')}")
        a.plot(tt[k]["sat_NF"], ":", color=CAT[i % 6])
    a.set_title("top-k overlap with release (solid T, dotted fixed random N_F)", color=INK)
    a.set_xlabel("layer")
    a.legend(frameon=False, fontsize=6)
    for a in (ax[0, 0], ax[0, 1], ax[1, 0]):
        a.set_xscale("log")
        a.set_xticks(x)
        a.set_xticklabels([XL[k] for k in ks])
        a.minorticks_off()
        a.set_xlabel("training tokens (log)")
    fig.suptitle("E186 training-time axis — OLMoE-1B-7B-0924 checkpoints (FLORES + UD; top-1 expert)", color=INK)
    fig.savefig(f"{RES}/fig_training.png", dpi=150)
    plt.close(fig)
    print("training fig", flush=True)
