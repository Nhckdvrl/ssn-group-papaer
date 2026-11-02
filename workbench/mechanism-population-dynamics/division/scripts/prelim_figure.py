#!/usr/bin/env python3
"""E167/E168 preliminary-results figure (4 panels) from the committed result JSONs.

A  expert division beyond token identity and geometry (T_D) by layer at 3.2B tokens:
   only-init pairs (mean, min-max band), only-order pairs (ceiling), untrained floor
B  formation: T_D of the last layer over training, only-init vs only-order (3.2B and earlier, 15 pairs)
C  resolution hierarchy (deep layers L6-L11, endpoint): only-init / only-order ratio for four readouts,
   ordered coarse to fine
D  depth profile: experts (routing T_D ratio, 3.2B) vs attention heads (attention-pattern fingerprint
   excess over the untrained floor, ratio, 1.6B), grouped into shallow / middle / deep layers

Usage: prelim_figure.py [en|ja]   (default: both)
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
BANDS = [(1, 4), (5, 8), (9, 11)]
L = np.arange(12)

TXT = {
    "en": dict(
        out="prelim_figure.png", font=None,
        sup="Do independently trained MoEs divide labour among experts the same way?",
        A="A  Expert division, \"natural\" agreement removed",
        A_y="agreement (corr.; word identity\nand geometry removed)", A_x="layer",
        A_init="different init only\n({n} pairs, mean & range)", A_order="same init, data order only\n= ceiling ({n} pairs)",
        A_floor="untrained models\n= floor",
        B="B  Over training (last layer)", B_x="training tokens", B_y="agreement",
        B_init="different init", B_order="same init (ceiling)", B_ratio="{p:.0%} of ceiling",
        ticks=["25M", "200M", "800M", "3.2B"],
        C="C  What repeats? (deep layers)",
        C_items=["which word classes an expert serves", "damage pattern over word classes",
                 "how contexts of the same word are split", "which exact token predictions need it"],
        C_coarse="coarse", C_fine="fine", C_ceiling="ceiling", C_x="ratio to ceiling",
        D="D  Experts vs heads: opposite depth trends", D_y="ratio to ceiling",
        D_bands=["shallow\n(L1-4)", "middle\n(L5-8)", "deep\n(L9-11)"], D_exp="experts", D_head="attention heads",
        D_dots="dots: single layers",
        foot=("Small OLMoE-style MoE (12 layers, 64 experts, top-8, ~150M active params, Dolma). 6 runs differing only in init "
              "+ 2 runs with the same init and a different data order (ceiling).\n"
              "Agreement = correlation of how contexts of the same word are routed, minus a random router that keeps the "
              "router's geometry. Ratio = different-init pairs / ceiling pairs.\n"
              "A, B, D(experts): 3.2B tokens (15 pairs). C: endpoint 4.0B tokens (6 vs 2 pairs). D(heads): attention patterns "
              "by word class, 1.6B, untrained floor removed."),
    ),
    "ja": dict(
        out="prelim_figure_ja.png", font="Noto Sans CJK JP",
        sup="独立に学習した MoE は、エキスパートの役割を同じように分けるか",
        A="A  「当たり前の一致」を除いた分担の一致（層ごと）",
        A_y="一致度（相関；単語の同一性と\n隠れ状態の幾何による分を除去）", A_x="層",
        A_init="初期化だけ違う\n（{n} ペア, 平均と範囲）", A_order="データ順だけ違う\n= 上限の目安（{n} ペア）",
        A_floor="未学習モデル同士\n= 下限",
        B="B  学習中の推移（最終層）", B_x="学習トークン数", B_y="一致度",
        B_init="初期化だけ違う", B_order="データ順だけ違う（上限）", B_ratio="上限の {p:.0%}",
        ticks=["2500万", "2億", "8億", "32億"],
        C="C  何が再現されるか（深い層, 上限比）",
        C_items=["どの品詞を担当するか", "品詞ごとの損傷パターン",
                 "同じ単語の文脈をどう分けるか", "どの具体的なトークンの予測で必要か"],
        C_coarse="粗い", C_fine="細かい", C_ceiling="上限", C_x="上限比",
        D="D  エキスパートとヘッド：深さで逆の傾向", D_y="上限比",
        D_bands=["浅い層\n(1–4)", "中間層\n(5–8)", "深い層\n(9–11)"], D_exp="エキスパート", D_head="注意ヘッド",
        D_dots="点：各層の値",
        foot=("小型 OLMoE 型 MoE（12 層・各層 64 エキスパート・top-8・アクティブ約 1.5 億パラメータ, Dolma）。"
              "初期化だけ違う 6 本 ＋ 同じ初期化でデータ順だけ違う 2 本（上限の目安）。\n"
              "一致度 = 同じ単語の文脈ごとの振り分けの相関から、ルーターの幾何を保ったランダムなルーターの分を差し引いたもの。"
              "上限比 = 初期化だけ違うペア ÷ データ順だけ違うペア。\n"
              "A・B・D（エキスパート）：32 億トークン（15 ペア）。C：終点 40 億トークン（6 ペア対 2 ペア）。"
              "D（ヘッド）：品詞ごとの注意パターン, 16 億トークン, 未学習の分を除去。"),
    ),
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


# ---- data (language independent) ----
ini = pairs("e167/routing_3200000000.json", 3200000000, "init")
odr = pairs("e167/routing_3200000000.json", 3200000000, "order")
I = np.array([[l["T_D"] for l in r["layers"]] for r in ini])
O = np.array([[l["T_D"] for l in r["layers"]] for r in odr])
F = np.array([l["T_D"] for l in [r for r in j("e167/routing_3200000000.json")["results"] if r["tokens_A"] == 0][0]["layers"]])

toks = [25e6, 200e6, 400e6, 800e6, 1.6e9, 3.2e9]
B_i = [j(f"e167/routing_summary_{int(t)}.json")["init"]["T_D"][11] for t in toks]
B_o = [j(f"e167/routing_summary_{int(t)}.json")["order"]["T_D"][11] for t in toks]

rs = j("e167/functional_route_summary_3999793152.json")
dr = j("e167/functional_drop_summary_3999793152.json")
tdf = j("e167/routing_summary_3999793152.json")
tk = j("e168/token_roles_final.json")["results"]
tk_o = [r for r in tk if r["A"][:2] == r["B"][:2]]
tk_i = [r for r in tk if r["A"][:2] != r["B"][:2] and r["A"][2:4] == "D0" and r["B"][2:4] == "D0"]
lay = lambda r: {x["layer"]: x["matched"] for x in r["layers"]}
deep_ratio = lambda s, key: np.mean([s["init"][key][l] / s["order"][key][l] for l in DEEP])
C_vals = [
    deep_ratio(rs, "matched"),
    deep_ratio(dr, "matched"),
    deep_ratio(tdf, "T_D"),
    np.mean([np.mean([lay(r)[l] for r in tk_i]) / np.mean([lay(r)[l] for r in tk_o]) for l in DEEP]),
]

td = j("e167/routing_summary_3200000000.json")
exp_ratio = np.array([td["init"]["T_D"][l] / td["order"]["T_D"][l] for l in L])
hs = j("e167/functional_hattn_summary_1600000000.json")
floor = [x["matched"] for x in j("e167/functional_hattn_floor_t0.json")["results"][0]["layers"]]
h_ratio = np.array([(hs["init"]["matched"][l] - floor[l]) / (hs["order"]["matched"][l] - floor[l]) for l in L])


def draw(lang):
    t = TXT[lang]
    if t["font"]:
        plt.rcParams["font.family"] = [t["font"], "DejaVu Sans"]
    fig, axs = plt.subplots(2, 2, figsize=(11.5, 8.2), facecolor=SURF)
    fig.suptitle(t["sup"], x=0.01, ha="left", fontsize=13, color=INK, fontweight="bold")

    # A
    ax = axs[0, 0]
    style(ax, t["A"])
    ax.fill_between(L, I.min(0), I.max(0), color=BLUE, alpha=0.15, lw=0)
    ax.plot(L, I.mean(0), color=BLUE, lw=2, marker="o", ms=4)
    ax.plot(L, O.mean(0), color=ORANGE, lw=2, marker="o", ms=4)
    ax.plot(L, F, color=GRAY, lw=1.5, ls="--")
    ax.text(11.3, O.mean(0)[-1], t["A_order"].format(n=len(odr)), color=INK, fontsize=8.5, va="center")
    ax.text(11.3, I.mean(0)[-1] - 0.01, t["A_init"].format(n=len(ini)), color=INK, fontsize=8.5, va="center")
    ax.text(11.3, F[-1] + 0.01, t["A_floor"], color=INK2, fontsize=8.5, va="center")
    ax.set_xlim(-0.3, 15.2)
    ax.set_xticks(L)
    ax.set_xlabel(t["A_x"], fontsize=9, color=INK2)
    ax.set_ylabel(t["A_y"], fontsize=9, color=INK2)

    # B
    ax = axs[0, 1]
    style(ax, t["B"])
    ax.plot(toks, B_o, color=ORANGE, lw=2, marker="o", ms=5)
    ax.plot(toks, B_i, color=BLUE, lw=2, marker="o", ms=5)
    ax.text(toks[-1] * 1.25, B_o[-1], t["B_order"], color=INK, fontsize=8.5, va="center")
    ax.text(toks[-1] * 1.25, B_i[-1], t["B_init"], color=INK, fontsize=8.5, va="center")
    for k in (2, 5):  # 400M and 3.2B
        ax.annotate(t["B_ratio"].format(p=B_i[k] / B_o[k]), (toks[k], B_i[k]), xytext=(7, -15),
                    textcoords="offset points", ha="left", fontsize=8.5, color=BLUE)
    ax.set_xscale("log")
    ax.set_xlim(1.6e7, 3.0e10)
    ax.set_ylim(0, 0.5)
    ax.set_xticks([25e6, 200e6, 800e6, 3.2e9])
    ax.set_xticklabels(t["ticks"])
    ax.minorticks_off()
    ax.set_xlabel(t["B_x"], fontsize=9, color=INK2)
    ax.set_ylabel(t["B_y"], fontsize=9, color=INK2)

    # C
    ax = axs[1, 0]
    style(ax, t["C"])
    y = np.arange(4)[::-1]
    ax.barh(y, C_vals, color=BLUE, height=0.55)
    for yi, v in zip(y, C_vals):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(t["C_items"], fontsize=9, color=INK)
    ax.set_xlim(0, 1.18)
    ax.set_ylim(-0.6, 3.75)
    ax.axvline(1.0, color=GRAY, lw=1, ls="--")
    ax.text(1.0, 3.5, t["C_ceiling"], fontsize=8.5, color=INK2, ha="center")
    ax.annotate("", xy=(1.11, -0.3), xytext=(1.11, 3.3), arrowprops=dict(arrowstyle="->", color=INK2, lw=1))
    ax.text(1.13, 3.3, t["C_coarse"], fontsize=8.5, color=INK2, va="center")
    ax.text(1.13, -0.3, t["C_fine"], fontsize=8.5, color=INK2, va="center")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_xlabel(t["C_x"], fontsize=9, color=INK2)

    # D
    ax = axs[1, 1]
    style(ax, t["D"])
    x = np.arange(len(BANDS))
    w = 0.36
    for off, vals, col, lab in ((-w / 2, exp_ratio, BLUE, t["D_exp"]), (w / 2, h_ratio, AQUA, t["D_head"])):
        means = [vals[a:b + 1].mean() for a, b in BANDS]
        ax.bar(x + off, means, width=w - 0.03, color=col, label=lab)
        for xi, (a, b) in zip(x, BANDS):
            pts = vals[a:b + 1]
            ax.scatter(np.full(len(pts), xi + off), pts, s=14, color="white", edgecolor=INK2, lw=0.8, zorder=3)
        for xi, m in zip(x, means):
            ax.text(xi + off, 0.02, f"{m:.2f}", ha="center", va="bottom", fontsize=8.5, color="white", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(t["D_bands"], fontsize=9, color=INK)
    ax.scatter([], [], s=14, color="white", edgecolor=INK2, lw=0.8, label=t["D_dots"])
    ax.set_ylim(0, 1.12)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_ylabel(t["D_y"], fontsize=9, color=INK2)
    ax.legend(loc="upper center", fontsize=8.5, frameon=False, ncol=3, handletextpad=0.4, columnspacing=1.2,
              bbox_to_anchor=(0.5, 1.02))

    fig.text(0.01, 0.008, t["foot"], fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.075, 1, 0.97), h_pad=3, w_pad=3)
    out = R / "e167" / t["out"]
    fig.savefig(out, dpi=170, facecolor=SURF)
    plt.close(fig)
    print(out)


for lang in (sys.argv[1:] or ["en", "ja"]):
    draw(lang)
print({k: round(float(v), 3) for k, v in zip(TXT["en"]["C_items"], C_vals)})
print("bands experts", [round(exp_ratio[a:b + 1].mean(), 2) for a, b in BANDS],
      "heads", [round(h_ratio[a:b + 1].mean(), 2) for a, b in BANDS])
