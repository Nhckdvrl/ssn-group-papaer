"""E185 figures.  Card: division/experiments/E185-routing-variance-atlas.md"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import NAMES  # noqa: E402

A = os.path.expanduser("~/mechpop_cache/atlas_e185")
RES = os.path.join(os.path.dirname(__file__), "..", "results", "e185")
DIV = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#e34948"])
SEQ = LinearSegmentedColormap.from_list("seq", ["#fcfcfb", "#2a78d6", "#0b2f5e"])
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
INK, MUTED = "#222222", "#777777"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
M3 = ["qwen3", "gptoss", "olmoe"]
LAB = {"inp": "input id", "prev": "previous id", "nxt": "true next id", "pred": "predicted next id", "pos": "position",
       "seq": "sequence", "corpus": "corpus", "upos": "UPOS", "side": "language side", "lang": "language",
       "script": "script", "sid": "parallel sentence", "inst": "sentence instance", "cls": "token class"}


def lab(k):
    if "|" in k:
        x, s = k.split("|")
        return f"{'+'.join(LAB.get(t, t) for t in x.split(','))} | {'+'.join(LAB.get(t, t) for t in s.split(','))}"
    return LAB.get(k, k)


def share(a):
    return a[..., 0] / a[..., 3]


# 1. D184 factor x layer maps
ROWS = [("marg", f) for f in ["inp", "prev", "nxt", "pred", "pos", "seq", "corpus", "upos"]] + \
       [("cond", f) for f in ["prev|inp", "nxt|inp", "pred|inp", "pos|inp", "seq|inp", "corpus|inp", "upos|inp",
                              "inp|pred", "inp|prev"]]
for m in M3:
    p = f"{A}/d184_{m}.npz"
    if not os.path.exists(p):
        continue
    r = dict(np.load(p))
    T = np.stack([share(r[f"full|{k}|{f}"])[:, 0] for k, f in ROWS])
    B = np.stack([share(r[f"full|{k}|{f}"])[:, 9:].mean(1) for k, f in ROWS])
    Bmin = np.stack([share(r[f"full|{k}|{f}"])[:, 9:].min(1) for k, f in ROWS])
    Bmax = np.stack([share(r[f"full|{k}|{f}"])[:, 9:].max(1) for k, f in ROWS])
    D = T - B
    fig, ax = plt.subplots(1, 3, figsize=(13, 5.2), sharey=True, constrained_layout=True)
    vmax = max(T.max(), B.max())
    for a, Z, t in ((ax[0], T, "trained router T"), (ax[1], B, "load-matched null N_B (mean of 8)")):
        im = a.imshow(Z, aspect="auto", cmap=SEQ, vmin=0, vmax=vmax, interpolation="nearest")
        a.set_title(t, color=INK)
    fig.colorbar(im, ax=ax[:2], shrink=.7, label="share  Î(e;X)/H(e)")
    lim = np.abs(D).max()
    im2 = ax[2].imshow(D, aspect="auto", cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), interpolation="nearest")
    out = (T > Bmax) | (T < Bmin)
    yy, xx = np.where(~out)
    ax[2].scatter(xx, yy, s=4, c=MUTED, marker="o", linewidths=0)
    ax[2].set_title("T − N_B  (dot = T inside the 8-draw range)", color=INK)
    fig.colorbar(im2, ax=ax[2], shrink=.7, label="Δ share")
    ax[0].set_yticks(range(len(ROWS)))
    ax[0].set_yticklabels([lab(f) for _, f in ROWS])
    for a in ax:
        a.set_xlabel("layer")
        a.axhline(7.5, color=INK, lw=.8)
    fig.suptitle(f"E185 D184 routing variance atlas — {NAMES[m]} (English FLORES + UD; top-1 expert)", color=INK)
    fig.savefig(f"{RES}/fig_map_{m}.png", dpi=150)
    plt.close(fig)

# 2. nested map with the cross-fitted estimator: G(X|inp), T - N_B, three models + D180
CF184 = ["seq", "prev", "pred", "nxt", "pos", "corpus", "upos"]
CF180 = ["sid", "inst", "pred", "lang", "script"]
fig, ax = plt.subplots(2, 3, figsize=(13, 6.5), constrained_layout=True)
for j, m in enumerate(M3):
    for i, (data, facs, nb) in enumerate((("d184", CF184, slice(9, 17)), ("d180", CF180, None))):
        p = f"{A}/cf_{data}_{m}.npz"
        a = ax[i, j]
        if not os.path.exists(p):
            a.set_axis_off()
            continue
        r = dict(np.load(p))
        info = json.load(open(f"{A}/cf_{data}_{m}.json"))
        rn = info["routers"]
        iT = rn.index("T")
        if nb is None:
            nb = [rn.index("N_B0")]
        Z = np.stack([r[f][:, iT, 3] - r[f][:, nb, 3].mean(1) for f in facs])
        lim = max(np.abs(Z).max(), 1e-3)
        im = a.imshow(Z, aspect="auto", cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), interpolation="nearest")
        a.set_yticks(range(len(facs)))
        a.set_yticklabels([lab(f) + " | input id" for f in facs])
        a.set_title(f"{NAMES[m]} — {'English, N_B mean of 8' if data == 'd184' else '20 sides, N_B0 x1'}",
                    color=INK)
        a.set_xlabel("layer")
        fig.colorbar(im, ax=a, shrink=.8, label="G_freq,T − G_freq,NB (bit)")
fig.suptitle("E185 nested map: cross-fitted information about the expert beyond the input token id (frequent ids only; T − N_B)",
             color=INK)
fig.savefig(f"{RES}/fig_nested.png", dpi=150)
plt.close(fig)

# 3. residual (b): Delta_obs / Delta_lex / Delta_ctx, T, LET and NON, S and U
M4 = ["qwen3", "qwen3base", "gptoss", "olmoe"]
fig, ax = plt.subplots(4, 4, figsize=(14, 10), constrained_layout=True)
for j, m in enumerate(M4):
    p = f"{RES}/res_b182_{m}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    for i, (g, c, key) in enumerate((("S", "LET", "P1-P2n"), ("S", "NON", "P1-P2n"), ("U", "LET", "P1U-P2U"),
                                     ("U", "NON", "P1U-P2U"))):
        rows = d["groups"][g][c]["0"][key]
        a = ax[i, j]
        x = np.arange(len(rows["d_obs"]))
        for k, col, nm in (("d_obs", CAT[0], "observed Δ"), ("d_lex", CAT[1], "token-id-only Δ_lex"),
                           ("d_ctx", CAT[2], "context Δ_ctx")):
            a.plot(x, rows[k], color=col, lw=2, label=nm)
            a.fill_between(x, rows[k + "_lo"], rows[k + "_hi"], color=col, alpha=.18, lw=0)
        a.axhline(0, color=MUTED, lw=.8)
        a.set_title(f"{NAMES[m]} · {'Serbian' if g == 'S' else 'Uzbek'} · {c}", color=INK)
        if j == 0:
            a.set_ylabel("Δ = D(P1) − D(P2)")
        if i == 3:
            a.set_xlabel("layer")
for a in ax.ravel():
    if a.lines:
        a.legend(frameon=False, fontsize=6)
        break
fig.suptitle("E185 residual (b): script-vs-language contrast split into a token-id-only part and a context part; P1 = same language, other script; P2 = same script, other language "
             "(T, E182 balanced tokens, 95% sentence bootstrap)", color=INK)
fig.savefig(f"{RES}/fig_residual_b.png", dpi=150)
plt.close(fig)

# 4. token context dependence: H_T vs H_NB per id (mid band), D184
fig, ax = plt.subplots(1, 3, figsize=(13, 4.2), constrained_layout=True)
for j, m in enumerate(M3):
    p = f"{A}/tok_d184_{m}.npz"
    pj = f"{RES}/tok_d184_{m}.json"
    if not os.path.exists(p):
        continue
    t = np.load(p)
    d = json.load(open(pj))
    from e185_lib import BANDS
    mid = BANDS[m][1]
    H = t["Hx"][mid].mean(0)
    HT, HB = H[0], H[9:].mean(0)
    a = ax[j]
    a.scatter(HB, HT, s=10, c=CAT[0], alpha=.6, linewidths=0)
    lim = [0, max(HT.max(), HB.max()) + .1]
    a.plot(lim, lim, color=MUTED, lw=.8)
    ids = t["ids"]
    for key in ("most_context_dependent", "least_context_dependent", "T_more_lexical_than_NB"):
        for x in d[key][:3]:
            k = int(np.where(ids == x["id"])[0][0])
            a.annotate(repr(x["str"]), (HB[k], HT[k]), fontsize=7, color=INK, xytext=(3, 2), textcoords="offset points")
    a.set_xlabel("H(e | id), N_B mean (bit)")
    a.set_ylabel("H(e | id), T (bit)")
    a.set_title(f"{NAMES[m]}: {len(ids)} ids (n≥30), mid band", color=INK)
fig.suptitle("E185 context dependence of routing per token id (equal n = 30); below the diagonal = T more lexical "
             "than geometry", color=INK)
fig.savefig(f"{RES}/fig_tokens.png", dpi=150)
plt.close(fig)
print("figures written")
