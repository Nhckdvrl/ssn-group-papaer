#!/usr/bin/env python3
"""E167/E168 preliminary-results figure (4 panels) from the committed result JSONs.

A  expert division beyond token identity and geometry (T_D) by layer at 3.2B tokens:
   only-init pairs (mean, min-max band), only-order pairs (ceiling), untrained floor
B  formation: T_D of L5 and L11 over training tokens, only-init vs only-order
C  resolution hierarchy (deep layers L6-L11): only-init / only-order ratio for four readouts
D  depth profile: experts (routing T_D ratio, 3.2B) vs attention heads (attention-pattern
   fingerprint excess over the untrained floor, ratio, 1.6B)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = Path(__file__).resolve().parents[1] / "results"
OUT = R / "e167" / "prelim_figure.png"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8d8c86"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
DEEP = list(range(6, 12))


def j(p):
    return json.loads((R / p).read_text())


def pairs(path, tok, kind):
    d = j(path)["results"]
    out = []
    for r in d:
        a, b = r["A"].split("__")[0], r["B"].split("__")[0]
        if r.get("tokens_A", tok) != tok:
            continue
        same_init = a[:2] == b[:2]
        if kind == "init" and not same_init and a[2:] == "D0" and b[2:] == "D0":
            out.append(r)
        if kind == "order" and same_init:
            out.append(r)
    return out


def style(ax, title):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=9.5, color=INK, pad=6)


fig, axs = plt.subplots(2, 2, figsize=(10.5, 7.2), facecolor=SURF)
L = np.arange(12)

# A
ax = axs[0, 0]
style(ax, "A  Expert division after removing word identity & geometry (3.2B)")
ini = pairs("e167/routing_3200000000.json", 3200000000, "init")
odr = pairs("e167/routing_3200000000.json", 3200000000, "order")
I = np.array([[l["T_D"] for l in r["layers"]] for r in ini])
O = np.array([[l["T_D"] for l in r["layers"]] for r in odr])
F = np.array([l["T_D"] for l in [r for r in j("e167/routing_3200000000.json")["results"] if r["tokens_A"] == 0][0]["layers"]])
ax.fill_between(L, I.min(0), I.max(0), color=BLUE, alpha=0.15, lw=0)
ax.plot(L, I.mean(0), color=BLUE, lw=2, marker="o", ms=4)
ax.plot(L, O.mean(0), color=ORANGE, lw=2, marker="o", ms=4)
ax.plot(L, F, color=GRAY, lw=1.5, ls="--")
ax.text(11.15, I.mean(0)[-1], f"different init\n({len(ini)} pairs)", color=INK, fontsize=8, va="center")
ax.text(11.15, O.mean(0)[-1], f"same init,\ndata order only\n({len(odr)} pairs)", color=INK, fontsize=8, va="center")
ax.text(11.15, F[-1], "untrained\nfloor", color=INK2, fontsize=8, va="center")
ax.set_xlim(-0.3, 13.6)
ax.set_xticks(L)
ax.set_xlabel("layer", fontsize=8, color=INK2)
ax.set_ylabel("T_D (corr. of context partition, null-removed)", fontsize=8, color=INK2)

# B
ax = axs[0, 1]
style(ax, "B  Formation over training (L5 dotted, L11 solid)")
toks = [25e6, 200e6, 400e6, 800e6, 1.6e9, 3.2e9]
for layer, ls in ((11, "-"), (5, ":")):
    vi, vo = [], []
    for t in toks:
        s = j(f"e167/routing_summary_{int(t)}.json")
        vi.append(s["init"]["T_D"][layer])
        vo.append(s["order"]["T_D"][layer])
    ax.plot(toks, vi, color=BLUE, lw=2, ls=ls, marker="o", ms=4)
    ax.plot(toks, vo, color=ORANGE, lw=2, ls=ls, marker="o", ms=4)
    ax.text(3.6e9, vi[-1], f"diff. init, L{layer}", color=INK, fontsize=8, va="center")
    ax.text(3.6e9, vo[-1], f"same init, L{layer}", color=INK, fontsize=8, va="center")
ax.set_xscale("log")
ax.set_xlim(2e7, 1.4e10)
ax.set_xlabel("training tokens", fontsize=8, color=INK2)
ax.set_ylabel("T_D", fontsize=8, color=INK2)

# C
ax = axs[1, 0]
style(ax, "C  What repeats across inits? (L6-11, ratio to ceiling)")
rs = j("e167/functional_route_summary_800000000.json")
dr = j("e167/functional_drop_summary_800000000.json")
td = j("e167/routing_summary_3200000000.json")
tk = j("e168/token_roles_final_partial.json")["results"]
tk_o = [r for r in tk if r["A"][:2] == r["B"][:2]]
tk_i = [r for r in tk if r["A"][:2] != r["B"][:2]]
lay = lambda r: {x["layer"]: x["matched"] for x in r["layers"]}
tk_ratio = np.mean([np.mean([lay(r)[l] for r in tk_i]) / lay(tk_o[0])[l] for l in DEEP])
items = [
    ("which word classes an expert serves\n(routing profile, 800M)", np.mean([rs["init"]["matched"][l] / rs["order"]["matched"][l] for l in DEEP])),
    ("how contexts of a word are split\n(T_D, null-removed, 3.2B)", np.mean([td["init"]["T_D"][l] / td["order"]["T_D"][l] for l in DEEP])),
    ("damage profile over word classes\n(expert drop, 800M; 3 vs 1 pairs)", np.mean([dr["init"]["matched"][l] / dr["order"]["matched"][l] for l in DEEP])),
    ("which exact predictions need it\n(token-level drop, final; 6 vs 1 pairs)", tk_ratio),
]
y = np.arange(len(items))[::-1]
ax.barh(y, [v for _, v in items], color=BLUE, height=0.55)
for yi, (lab, v) in zip(y, items):
    ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=8.5, color=INK)
ax.set_yticks(y)
ax.set_yticklabels([lab for lab, _ in items], fontsize=7.5, color=INK)
ax.set_xlim(0, 1.15)
ax.axvline(1.0, color=GRAY, lw=1, ls="--")
ax.text(1.01, y[-1] - 0.45, "ceiling", fontsize=7.5, color=INK2, ha="left")
ax.grid(axis="y", visible=False)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_xlabel("ratio", fontsize=8, color=INK2)

# D
ax = axs[1, 1]
style(ax, "D  Experts vs attention heads by depth (ratio to ceiling)")
exp_ratio = [td["init"]["T_D"][l] / td["order"]["T_D"][l] for l in L]
hs = j("e167/functional_hattn_summary_1600000000.json")
floor = [x["matched"] for x in j("e167/functional_hattn_floor_t0.json")["results"][0]["layers"]]
h_ratio = [(hs["init"]["matched"][l] - floor[l]) / (hs["order"]["matched"][l] - floor[l]) for l in L]
ax.plot(L[1:], exp_ratio[1:], color=BLUE, lw=2, marker="o", ms=4)
ax.plot(L[1:], h_ratio[1:], color=AQUA, lw=2, marker="s", ms=4)
ax.text(11.15, exp_ratio[-1] + 0.06, "experts\n(routing T_D, 3.2B)", color=INK, fontsize=8, va="center")
ax.text(11.15, h_ratio[-1] - 0.08, "attention heads\n(pattern, 1.6B,\nfloor-removed)", color=INK, fontsize=8, va="center")
ax.set_xlim(0.7, 13.6)
ax.set_ylim(0, 1.0)
ax.set_xticks(L[1:])
ax.set_xlabel("layer (L0 omitted: near-zero denominators)", fontsize=8, color=INK2)
ax.set_ylabel("ratio", fontsize=8, color=INK2)

fig.text(0.01, 0.008, "Small OLMoE-style MoE (12 layers, 64 experts, top-8, ~150M active); 6 independent inits + 2 same-init/different-order runs; Dolma v1.7.\n"
         "T_D: within-word-type co-routing correlation after removing an expert-geometry-preserving null (N1). Ceiling = same init, data order only.",
         fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.045, 1, 1), h_pad=2.5, w_pad=3)
fig.savefig(OUT, dpi=170, facecolor=SURF)
print(OUT)
print({lab.split("\n")[0]: round(float(v), 3) for lab, v in items})
print("expert ratio", [round(x, 2) for x in exp_ratio], "head ratio", [round(x, 2) for x in h_ratio])
