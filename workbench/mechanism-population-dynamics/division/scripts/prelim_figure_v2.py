#!/usr/bin/env python3
"""Revised preliminary figure (2026-11-03 review): drops the head panel (its 'opposite trend' is produced
entirely by the single-pair untrained floor) and shows instead the two findings that survived review.

A  expert division beyond token identity and geometry (T_D) by layer at 3.2B tokens (unchanged)
B  formation at two depths: last layer (L11) and first layer (L0); only-init vs only-order. The
   shallow initialisation imprint washes out, the deep one stays (.12-.17 gap from 400M on).
C  resolution hierarchy (deep layers, endpoint) (unchanged)
D  same geometry, different cut: hidden-state geometry agreement (T_h), raw routing agreement with word
   identity removed (T_ctx), and the geometry-null residual (T_D), L11, 3.2B, for only-init / only-order /
   untrained pairs.

Usage: prelim_figure_v2.py [en|ja]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = Path(__file__).resolve().parents[1] / "results"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8d8c86"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
DEEP = list(range(6, 12))
L = np.arange(12)

TXT = {
    "en": dict(out="prelim_figure_v2.png", font=None,
        sup="Do independently trained MoEs divide labour among experts the same way?",
        A="A  Expert division, \"natural\" agreement removed (3.2B tokens)",
        A_y="agreement (corr.; word identity\nand geometry removed)", A_x="layer",
        A_init="different init only\n({n} pairs, mean & range)", A_order="same init, data order only\n({n} pairs)", A_floor="untrained models",
        B="B  Over training: deep imprint stays, shallow imprint washes out", B_x="training tokens", B_y="agreement",
        B_lab={"o11": "same init, L11", "i11": "different init, L11", "o0": "same init, L0", "i0": "different init, L0"},
        B_gap="gap .12–.17\nfrom 400M on", ticks=["25M", "200M", "800M", "3.2B"],
        C="C  What repeats? (deep layers, endpoint)",
        C_items=["which word classes an expert serves", "damage pattern over word classes",
                 "how contexts of the same word are split", "which exact token predictions need it"],
        C_x="different-init / same-init ratio",
        D="D  Same geometry, different cut (L11, 3.2B)", D_y="cross-model correlation",
        D_cats=["hidden-state\ngeometry", "routing\n(word identity removed)", "routing beyond\ngeometry null"],
        D_groups=["different init", "same init", "untrained"],
        foot=("Small OLMoE-style MoE (12 layers, 64 experts, top-8, ~150M active params, Dolma). 6 runs differing only in init "
              "+ 2 runs with the same init and a different data order.\nAgreement = correlation of how contexts of the same word are routed, "
              "minus a random router that keeps the router's geometry. A, B, D: 3.2B tokens (15 + 2 pairs). C: endpoint 4.0B tokens (6 vs 2 pairs).")),
    "ja": dict(out="prelim_figure_v2_ja.png", font="Noto Sans CJK JP",
        sup="独立に学習した MoE は、エキスパートの役割を同じように分けるか",
        A="A  「当たり前の一致」を除いた分担の一致（層ごと, 32 億トークン）",
        A_y="一致度（相関；単語の同一性と\n隠れ状態の幾何による分を除去）", A_x="層",
        A_init="初期化だけ違う\n（{n} ペア, 平均と範囲）", A_order="同じ初期化, データ順だけ違う\n（{n} ペア）", A_floor="未学習モデル同士",
        B="B  学習中の推移：深い層の初期化の痕跡は残り、浅い層のは消える", B_x="学習トークン数", B_y="一致度",
        B_lab={"o11": "同じ初期化, 第 11 層", "i11": "初期化だけ違う, 第 11 層", "o0": "同じ初期化, 第 0 層", "i0": "初期化だけ違う, 第 0 層"},
        B_gap="差 .12–.17\n（4 億以降一定）", ticks=["2500万", "2億", "8億", "32億"],
        C="C  何が再現されるか（深い層, 終点）",
        C_items=["どの品詞を担当するか", "品詞ごとの損傷パターン", "同じ単語の文脈をどう分けるか", "どの具体的なトークンの予測で必要か"],
        C_x="初期化だけ違う ÷ 同じ初期化",
        D="D  幾何は同じ、切り方は違う（第 11 層, 32 億）", D_y="モデル間相関",
        D_cats=["隠れ状態の幾何", "ルーティング\n（単語の同一性を除去）", "ルーティング\n（幾何ヌルを除去）"],
        D_groups=["初期化だけ違う", "同じ初期化", "未学習"],
        foot=("小型 OLMoE 型 MoE（12 層・各層 64 エキスパート・top-8・アクティブ約 1.5 億パラメータ, Dolma）。初期化だけ違う 6 本 ＋ 同じ初期化でデータ順だけ違う 2 本。\n"
              "一致度 = 同じ単語の文脈ごとの振り分けの相関から、ルーターの幾何を保ったランダムなルーターの分を差し引いたもの。A・B・D：32 億トークン（15＋2 ペア）。C：終点 40 億（6 対 2 ペア）。")),
}


def j(p):
    return json.loads((R / p).read_text())


def pairs(path, tok, kind):
    out = []
    for r in j(path)["results"]:
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
    ax.tick_params(colors=INK2, labelsize=8.5)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8, fontweight="bold")


ini = pairs("e167/routing_3200000000.json", 3200000000, "init")
odr = pairs("e167/routing_3200000000.json", 3200000000, "order")
I = np.array([[l["T_D"] for l in r["layers"]] for r in ini])
O = np.array([[l["T_D"] for l in r["layers"]] for r in odr])
flo = [r for r in j("e167/routing_3200000000.json")["results"] if r["tokens_A"] == 0][0]["layers"]
F = np.array([l["T_D"] for l in flo])
toks = [25e6, 200e6, 400e6, 800e6, 1.6e9, 3.2e9]
S = {t: j(f"e167/routing_summary_{int(t)}.json") for t in toks}
B = {k: [S[t][g]["T_D"][l] for t in toks] for k, (g, l) in {"o11": ("order", 11), "i11": ("init", 11), "o0": ("order", 0), "i0": ("init", 0)}.items()}
rs = j("e167/functional_route_summary_3999793152.json"); dr = j("e167/functional_drop_summary_3999793152.json"); tdf = j("e167/routing_summary_3999793152.json")
tk = j("e168/token_roles_final.json")["results"]
tk_o = [r for r in tk if r["A"][:2] == r["B"][:2]]
tk_i = [r for r in tk if r["A"][:2] != r["B"][:2] and r["A"][2:4] == "D0" and r["B"][2:4] == "D0"]
lay = lambda r: {x["layer"]: x["matched"] for x in r["layers"]}
deep_ratio = lambda s, key: np.mean([s["init"][key][l] / s["order"][key][l] for l in DEEP])
C_vals = [deep_ratio(rs, "matched"), deep_ratio(dr, "matched"), deep_ratio(tdf, "T_D"),
          np.mean([np.mean([lay(r)[l] for r in tk_i]) / np.mean([lay(r)[l] for r in tk_o]) for l in DEEP])]
s32 = S[3.2e9]
Dvals = {g: [s32[g]["T_h"][11], s32[g]["T_ctx"][11], s32[g]["T_D"][11]] for g in ("init", "order", "floor_t0")}


def draw(lang):
    t = TXT[lang]
    if t["font"]:
        plt.rcParams["font.family"] = [t["font"], "DejaVu Sans"]
    fig, axs = plt.subplots(2, 2, figsize=(11.5, 8.4), facecolor=SURF)
    fig.suptitle(t["sup"], x=0.01, ha="left", fontsize=13, color=INK, fontweight="bold")
    ax = axs[0, 0]; style(ax, t["A"])
    ax.fill_between(L, I.min(0), I.max(0), color=BLUE, alpha=0.15, lw=0)
    ax.plot(L, I.mean(0), color=BLUE, lw=2, marker="o", ms=4)
    ax.plot(L, O.mean(0), color=ORANGE, lw=2, marker="o", ms=4)
    ax.plot(L, F, color=GRAY, lw=1.5, ls="--")
    ax.text(11.3, O.mean(0)[-1], t["A_order"].format(n=len(odr)), color=INK, fontsize=8.5, va="center")
    ax.text(11.3, I.mean(0)[-1] - 0.01, t["A_init"].format(n=len(ini)), color=INK, fontsize=8.5, va="center")
    ax.text(11.3, F[-1] + 0.01, t["A_floor"], color=INK2, fontsize=8.5, va="center")
    ax.set_xlim(-0.3, 15.5); ax.set_xticks(L); ax.set_xlabel(t["A_x"], fontsize=9, color=INK2); ax.set_ylabel(t["A_y"], fontsize=9, color=INK2)
    ax = axs[0, 1]; style(ax, t["B"])
    for k, col, ls in (("o11", ORANGE, "-"), ("i11", BLUE, "-"), ("o0", ORANGE, "--"), ("i0", BLUE, "--")):
        ax.plot(toks, B[k], color=col, lw=2, ls=ls, marker="o", ms=4)
        ax.text(toks[-1] * 1.25, B[k][-1] + (0.012 if k == "o0" else -0.012 if k == "i0" else 0), t["B_lab"][k], color=INK, fontsize=8.2, va="center")
    ax.annotate("", xy=(3.2e9, B["i11"][-1]), xytext=(3.2e9, B["o11"][-1]), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
    ax.text(2.0e9, (B["i11"][-1] + B["o11"][-1]) / 2, t["B_gap"], fontsize=8.2, color=INK2, ha="right", va="center")
    ax.set_xscale("log"); ax.set_xlim(1.6e7, 4.5e10); ax.set_ylim(0, 0.9)
    ax.set_xticks([25e6, 200e6, 800e6, 3.2e9]); ax.set_xticklabels(t["ticks"]); ax.minorticks_off()
    ax.set_xlabel(t["B_x"], fontsize=9, color=INK2); ax.set_ylabel(t["B_y"], fontsize=9, color=INK2)
    ax = axs[1, 0]; style(ax, t["C"])
    y = np.arange(4)[::-1]
    ax.barh(y, C_vals, color=BLUE, height=0.55)
    for yi, v in zip(y, C_vals):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(t["C_items"], fontsize=9, color=INK); ax.set_xlim(0, 1.15); ax.set_ylim(-0.6, 3.6)
    ax.axvline(1.0, color=GRAY, lw=1, ls="--"); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_xlabel(t["C_x"], fontsize=9, color=INK2)
    ax = axs[1, 1]; style(ax, t["D"])
    x = np.arange(3); w = 0.26
    for off, g, col, lab in ((-w, "init", BLUE, t["D_groups"][0]), (0, "order", ORANGE, t["D_groups"][1]), (w, "floor_t0", GRAY, t["D_groups"][2])):
        vals = Dvals[g]
        ax.bar(x + off, vals, width=w - 0.03, color=col, label=lab)
        for xi, v in zip(x, vals):
            ax.text(xi + off, max(v, 0) + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_xticks(x); ax.set_xticklabels(t["D_cats"], fontsize=9, color=INK); ax.set_ylim(0, 1.15)
    ax.set_ylabel(t["D_y"], fontsize=9, color=INK2)
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)
    fig.text(0.01, 0.008, t["foot"], fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.06, 1, 0.97), h_pad=3, w_pad=3)
    out = R / "e167" / t["out"]
    fig.savefig(out, dpi=170, facecolor=SURF); plt.close(fig); print(out)


for lang in (sys.argv[1:] or ["en", "ja"]):
    draw(lang)
print("C", [round(float(v), 3) for v in C_vals], "D", {g: [round(v, 3) for v in Dvals[g]] for g in Dvals})
