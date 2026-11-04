#!/usr/bin/env python3
"""Preliminary-results figure v4 (2026-11-04, after E171): v3 plus the exact-rerun pair (I4D0, I4D0R) as the
reproducibility ceiling in panels A, B, C.

A  expert division beyond token identity and geometry (T_D) by layer, 3.2B (15 + 2 pairs)
B  formation at L11 and L0: shallow init imprint washes out, deep one persists
C  resolution hierarchy (deep layers, endpoint; ratio different-init / same-init)
D  same geometry, different cut (L11, 3.2B)
E  which linguistic distinctions carry the reproducible division (E170 stage 1, deep layers):
   cell-level reproducibility ratio per variable vs the within-cell residual
F  multi-function words (E170 stage 1b, L11): per-run separation of a word's contexts by grammatical
   function; words whose function is determined by the left context vs by the right context

Usage: prelim_figure_v4.py [en|ja]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = Path(__file__).resolve().parents[1] / "results"
BLUE, ORANGE, AQUA, GRAY, RED = "#2a78d6", "#eb6834", "#1baf7a", "#8d8c86", "#c0392b"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
DEEP = list(range(6, 12))
L = np.arange(12)
RUNS = ["I0D0", "I1D0", "I2D0", "I3D0", "I0D1", "I1D1"]
WORDS = ["you", "it", "which", "there", "to", "that", "me", "on", "have", "like", "as", "what", "is", "are", "was", "be", "for", "with", "about", "so"]
VARS = ["upos", "feats", "deprel", "next_upos", "head_upos", "prev_upos", "sentpos", "genre"]

TXT = {
    "en": dict(out="prelim_figure_v4.png", font=None,
        sup="Do independently trained MoEs divide labour among experts the same way?  (6 runs differing only in init; 2 runs differing only in data order; 1 identical-config re-run)",
        A="A  Expert division, \"natural\" agreement removed (3.2B tokens)", A_y="agreement (corr.; word identity\nand geometry removed)", A_x="layer",
        A_init="different init\n({n} pairs, mean & range)", A_order="same init, different order\n({n} pairs)", A_floor="untrained", A_rerun="identical config, re-run\n(1 pair; training non-determinism)",
        B="B  Over training: deep imprint stays, shallow washes out", B_x="training tokens", B_y="agreement",
        B_lab={"o11": "same init, L11", "i11": "diff. init, L11", "o0": "same init, L0", "i0": "diff. init, L0", "r11": "re-run, L11", "r0": "re-run, L0"}, B_gap="gap .12–.17\nfrom 400M on", ticks=["25M", "200M", "800M", "3.2B"],
        C="C  What repeats? (deep layers, 3.2B)", C_items=["which word classes an expert serves", "damage pattern over word classes", "how contexts of a word are split", "which exact token predictions need it"], C_x="different-init / same-init (orange: / identical-config re-run)",
        D="D  Same geometry, different cut (L11)", D_y="cross-model correlation", D_cats=["hidden-state\ngeometry", "routing (word\nidentity removed)", "routing beyond\ngeometry null"], D_groups=["different init", "same init", "untrained"],
        E="E  Which distinctions carry the reproducible split? (deep layers)", E_x="reproducibility of the split organised by the variable\n(different-init / same-init)",
        E_items={"upos": "word class of the form", "feats": "morphological features", "deprel": "dependency relation", "next_upos": "next word's class", "head_upos": "head's class", "prev_upos": "previous word's class", "sentpos": "sentence position", "genre": "genre"},
        E_resid="within-cell residual", E_share="share carried",
        F="F  Multi-function words: do all runs split them the same way? (L11)", F_y="separation of contexts by\ngrammatical function", F_left="function set by left context", F_right="function set by right context", F_untr="untrained",
        foot=("Small OLMoE-style MoE (12 layers, 64 experts, top-8, ~150M active params, Dolma 4B tokens). Agreement = correlation of how contexts of the same word are routed, minus a random "
              "router that keeps the router's geometry.\nA, B, D: 3.2B tokens. C, E, F: endpoint. E: UD English EWT annotations; cells = (word form, value pair). F: dots = 6 trained runs, hollow = untrained; "
              "left/right from a classifier predicting the function from left-only or right-only context.")),
    "ja": dict(out="prelim_figure_v4_ja.png", font="Noto Sans CJK JP",
        sup="独立に学習した MoE は、エキスパートの役割を同じように分けるか（初期化だけ違う 6 本；同じ初期化でデータ順だけ違う 2 本；同一設定の再実行 1 本）",
        A="A  「当たり前の一致」を除いた分担の一致（層ごと, 32 億）", A_y="一致度（相関；単語の同一性と\n隠れ状態の幾何による分を除去）", A_x="層",
        A_init="初期化だけ違う\n（{n} ペア, 平均と範囲）", A_order="同じ初期化, データ順だけ違う\n（{n} ペア）", A_floor="未学習", A_rerun="完全に同一の設定で再実行\n（1 ペア；学習の非決定性）",
        B="B  学習中の推移：深い層の初期化の痕跡は残り、浅い層のは消える", B_x="学習トークン数", B_y="一致度",
        B_lab={"o11": "同じ初期化, 第 11 層", "i11": "初期化だけ違う, 第 11 層", "o0": "同じ初期化, 第 0 層", "i0": "初期化だけ違う, 第 0 層", "r11": "再実行, 第 11 層", "r0": "再実行, 第 0 層"}, B_gap="差 .12–.17\n（4 億以降一定）", ticks=["2500万", "2億", "8億", "32億"],
        C="C  何が再現されるか（深い層, 32 億）", C_items=["どの品詞を担当するか", "品詞ごとの損傷パターン", "同じ単語の文脈をどう分けるか", "どの具体的なトークンの予測で必要か"], C_x="初期化だけ違う ÷ 同じ初期化（橙：÷ 同一設定の再実行）",
        D="D  幾何は同じ、切り方は違う（第 11 層）", D_y="モデル間相関", D_cats=["隠れ状態の幾何", "ルーティング\n（単語の同一性を除去）", "ルーティング\n（幾何ヌルを除去）"], D_groups=["初期化だけ違う", "同じ初期化", "未学習"],
        E="E  再現される分け方は、どの区別に沿っているか（深い層）", E_x="その区別で区切った分け方の再現性（初期化だけ違う ÷ 同じ初期化）",
        E_items={"upos": "語形の品詞", "feats": "形態素特徴", "deprel": "係り受け関係", "next_upos": "直後の語の品詞", "head_upos": "主辞の品詞", "prev_upos": "直前の語の品詞", "sentpos": "文中位置", "genre": "ジャンル"},
        E_resid="区別で説明できない残差", E_share="担う割合",
        F="F  多機能語：どの学習も同じように分けるか（第 11 層）", F_y="文法的機能による\n文脈の分離度", F_left="機能が左文脈で決まる語", F_right="機能が右文脈で決まる語", F_untr="未学習",
        foot=("小型 OLMoE 型 MoE（12 層・各層 64 エキスパート・top-8・アクティブ約 1.5 億パラメータ, Dolma 40 億トークン）。一致度 = 同じ単語の文脈ごとの振り分けの相関から、ルーターの幾何を保ったランダムなルーターの分を差し引いたもの。\n"
              "A–D：32 億トークン；E・F：終点。再実行 = 同じ初期化 seed・同じデータ順・同じコードと同型 GPU。E：UD English EWT の注釈、格 = (語形, 値の組)。F：点 = 学習済み 6 本、白抜き = 未学習；左／右は左文脈のみ・右文脈のみから機能を予測する分類器による。")),
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
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=9.8, color=INK, pad=7, fontweight="bold")


# ---- data ----
ini = pairs("e167/routing_3200000000.json", 3200000000, "init"); odr = pairs("e167/routing_3200000000.json", 3200000000, "order")
I = np.array([[l["T_D"] for l in r["layers"]] for r in ini]); O = np.array([[l["T_D"] for l in r["layers"]] for r in odr])
F = np.array([l["T_D"] for l in [r for r in j("e167/routing_3200000000.json")["results"] if r["tokens_A"] == 0][0]["layers"]])
toks = [25e6, 200e6, 400e6, 800e6, 1.6e9, 3.2e9]
S = {t: j(f"e167/routing_summary_{int(t)}.json") for t in toks}
B = {k: [S[t][g]["T_D"][l] for t in toks] for k, (g, l) in {"o11": ("order", 11), "i11": ("init", 11), "o0": ("order", 0), "i0": ("init", 0)}.items()}
rs = j("e167/functional_route_summary_3999793152.json"); dr = j("e167/functional_drop_summary_3999793152.json"); tdf = j("e167/routing_summary_3999793152.json")
tk = j("e168/token_roles_final.json")["results"]
tk_o = [r for r in tk if r["A"][:2] == r["B"][:2]]; tk_i = [r for r in tk if r["A"][:2] != r["B"][:2] and r["A"][2:4] == "D0" and r["B"][2:4] == "D0"]
lay = lambda r: {x["layer"]: x["matched"] for x in r["layers"]}
deep_ratio = lambda s, key: np.mean([s["init"][key][l] / s["order"][key][l] for l in DEEP])
C_vals = [deep_ratio(rs, "matched"), deep_ratio(dr, "matched"), deep_ratio(tdf, "T_D"), np.mean([np.mean([lay(r)[l] for r in tk_i]) / np.mean([lay(r)[l] for r in tk_o]) for l in DEEP])]
# E171: exact re-run pair (I4D0, I4D0R) as the ceiling; same-init / different-init references at 3.2B from results/e171
E171 = Path(R / "e171")
def e171(path, key, name_filter):
    out = {}
    for r in j(path)["results"]:
        a, b = r["A"].split("__")[0], r["B"].split("__")[0]
        if r.get("tokens_A", 3200000000) != 3200000000:
            continue
        out.setdefault(name_filter(a, b), []).append([x[key] for x in r["layers"]])
    return {k: np.mean(v, 0) for k, v in out.items()}
kind = lambda a, b: "rerun" if b.endswith("R") or a.endswith("R") and a[:4] == b[:4] else ("order" if a[:2] == b[:2] else "init")
kind = lambda a, b: "rerun" if (a + b).count("R") == 1 and a[:4] == b[:4] else ("order" if a[:2] == b[:2] else "init")
RT = e171("e171/routing.json", "T_D", kind)
RR = {r["tokens_A"]: [x["T_D"] for x in r["layers"]] for r in j("e171/routing.json")["results"] if kind(r["A"].split("__")[0], r["B"].split("__")[0]) == "rerun"}
FR = e171("e171/functional_route.json", "matched", kind)
TKR = {k: v for k, v in e171("e171/token_roles.json", "matched", kind).items()}
tk_layers = [x["layer"] for x in j("e171/token_roles.json")["results"][0]["layers"]]
deep_tk = lambda v: np.mean([v[i] for i, l in enumerate(tk_layers) if l in DEEP])
C_rerun = [np.mean(FR["init"][6:]) / np.mean(FR["rerun"][6:]), None, np.mean(RT["init"][6:]) / np.mean(RT["rerun"][6:]), deep_tk(TKR["init"]) / deep_tk(TKR["rerun"])]
try:
    FD = e171("e171/functional_drop.json", "matched", kind)
    if "rerun" in FD and "init" in FD:
        C_rerun[1] = np.mean(FD["init"][6:]) / np.mean(FD["rerun"][6:])
except FileNotFoundError:
    pass
print("C (÷ same-init)", [round(v, 2) for v in C_vals], "C (÷ re-run)", [None if v is None else round(v, 2) for v in C_rerun])
s32 = S[3.2e9]
Dvals = {g: [s32[g]["T_h"][11], s32[g]["T_ctx"][11], s32[g]["T_D"][11]] for g in ("init", "order", "floor_t0")}
DEC = j("e170/decomp_3999793152.json")["vars"]
band = lambda rec, key: np.mean([rec["layers"][l][key] for l in DEEP])
E_cell = {v: band(DEC[v], "D_init_cellcorr") / band(DEC[v], "D_order_cellcorr") for v in VARS}
E_share = {v: band(DEC[v], "D_init_share") for v in VARS}
E_resid = np.mean([band(DEC[v], "D_init_residcorr") / band(DEC[v], "D_order_residcorr") for v in VARS])
AMB = j("e170/ambiguous_3999793152.json")["forms"]
CTX = j("e170/context_predictability_3999793152.json")["forms"]
F_rows = []
for w in WORDS:
    if w not in AMB or w not in CTX:
        continue
    sep = [AMB[w]["layers"]["11"]["sep"][r] for r in RUNS]; untr = AMB[w]["layers"]["11"]["sep"]["I0D0@0"]
    left = CTX[w]["bacc_left"] - CTX[w]["chance_bacc"]; right = CTX[w]["bacc_right"] - CTX[w]["chance_bacc"]
    F_rows.append((w, sep, untr, left >= right))
F_rows.sort(key=lambda r: -np.mean(r[1]))


def draw(lang):
    t = TXT[lang]
    if t["font"]:
        plt.rcParams["font.family"] = [t["font"], "DejaVu Sans"]
    fig, axs = plt.subplots(2, 3, figsize=(16.5, 8.6), facecolor=SURF)
    fig.suptitle(t["sup"], x=0.01, ha="left", fontsize=12.5, color=INK, fontweight="bold")
    # A
    ax = axs[0, 0]; style(ax, t["A"])
    ax.fill_between(L, I.min(0), I.max(0), color=BLUE, alpha=0.15, lw=0)
    ax.plot(L, I.mean(0), color=BLUE, lw=2, marker="o", ms=3.5); ax.plot(L, O.mean(0), color=ORANGE, lw=2, marker="o", ms=3.5); ax.plot(L, F, color=GRAY, lw=1.4, ls="--")
    ax.plot(L, RT["rerun"], color=AQUA, lw=2, marker="o", ms=3.5)
    ax.text(11.3, RT["rerun"][-1] + 0.02, t["A_rerun"], color=INK, fontsize=7.8, va="center")
    ax.text(11.3, O.mean(0)[-1] - 0.025, t["A_order"].format(n=len(odr)), color=INK, fontsize=7.8, va="center")
    ax.text(11.3, I.mean(0)[-1] - 0.03, t["A_init"].format(n=len(ini)), color=INK, fontsize=7.8, va="center")
    ax.text(11.3, F[-1] + 0.01, t["A_floor"], color=INK2, fontsize=7.8, va="center")
    ax.set_xlim(-0.3, 16.5); ax.set_xticks(L); ax.set_xlabel(t["A_x"], fontsize=8.5, color=INK2); ax.set_ylabel(t["A_y"], fontsize=8.5, color=INK2)
    # B
    ax = axs[0, 1]; style(ax, t["B"])
    B["r11"] = [RR[int(x)][11] for x in toks]; B["r0"] = [RR[int(x)][0] for x in toks]
    for k, col, ls in (("r11", AQUA, "-"), ("o11", ORANGE, "-"), ("i11", BLUE, "-"), ("r0", AQUA, "--"), ("o0", ORANGE, "--"), ("i0", BLUE, "--")):
        ax.plot(toks, B[k], color=col, lw=2, ls=ls, marker="o", ms=3.5)
        dy = {"r11": 0.022, "o11": -0.012, "r0": 0.03, "o0": 0.0, "i0": -0.028}.get(k, 0)
        ax.text(toks[-1] * 1.25, B[k][-1] + dy, t["B_lab"][k], color=INK, fontsize=7.6, va="center")
    ax.annotate("", xy=(3.2e9, B["i11"][-1]), xytext=(3.2e9, B["o11"][-1]), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
    ax.text(2.1e9, (B["i11"][-1] + B["o11"][-1]) / 2, t["B_gap"], fontsize=7.6, color=INK2, ha="right", va="center")
    ax.set_xscale("log"); ax.set_xlim(1.6e7, 6e10); ax.set_ylim(0, 1.0); ax.set_xticks([25e6, 200e6, 800e6, 3.2e9]); ax.set_xticklabels(t["ticks"]); ax.minorticks_off()
    ax.set_xlabel(t["B_x"], fontsize=8.5, color=INK2); ax.set_ylabel(t["B_y"], fontsize=8.5, color=INK2)
    # C
    ax = axs[0, 2]; style(ax, t["C"])
    y = np.arange(4)[::-1]
    ax.barh(y + 0.17, C_vals, color=BLUE, height=0.32)
    for yi, v in zip(y, C_vals):
        ax.text(v + 0.02, yi + 0.17, f"{v:.2f}", va="center", fontsize=8.5, color=INK, fontweight="bold")
    for yi, v in zip(y, C_rerun):
        if v is None:
            ax.text(0.02, yi - 0.17, "(re-run denominator not computed)" if lang == "en" else "（再実行の分母は未計算）", va="center", fontsize=7, color=INK2)
            continue
        ax.barh(yi - 0.17, v, color=ORANGE, height=0.32)
        ax.text(v + 0.02, yi - 0.17, f"{v:.2f}", va="center", fontsize=8.5, color=INK, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(t["C_items"], fontsize=8.3, color=INK); ax.set_xlim(0, 1.15); ax.set_ylim(-0.6, 3.6)
    ax.axvline(1.0, color=GRAY, lw=1, ls="--"); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID, lw=0.8); ax.set_xlabel(t["C_x"], fontsize=8.5, color=INK2)
    # D
    ax = axs[1, 0]; style(ax, t["D"])
    x = np.arange(3); w = 0.26
    for off, g, col, lab in ((-w, "init", BLUE, t["D_groups"][0]), (0, "order", ORANGE, t["D_groups"][1]), (w, "floor_t0", GRAY, t["D_groups"][2])):
        vals = Dvals[g]; ax.bar(x + off, vals, width=w - 0.03, color=col, label=lab)
        for xi, v in zip(x, vals):
            ax.text(xi + off, max(v, 0) + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.set_xticks(x); ax.set_xticklabels(t["D_cats"], fontsize=8.3, color=INK); ax.set_ylim(0, 1.18); ax.set_ylabel(t["D_y"], fontsize=8.5, color=INK2)
    ax.legend(loc="upper right", fontsize=7.8, frameon=False)
    # E
    ax = axs[1, 1]; style(ax, t["E"])
    order_v = sorted(VARS, key=lambda v: E_cell[v])
    y = np.arange(len(order_v))
    ax.barh(y, [E_cell[v] for v in order_v], color=BLUE, height=0.6)
    for yi, v in zip(y, order_v):
        ax.text(E_cell[v] + 0.015, yi, f"{E_cell[v]:.2f}   ({t['E_share']} {E_share[v]:.2f})", va="center", fontsize=7.8, color=INK)
    ax.axvline(E_resid, color=RED, lw=1.4, ls="--"); ax.text(E_resid, len(order_v) - 0.35, f" {t['E_resid']} {E_resid:.2f}", color=RED, fontsize=7.8, va="center")
    ax.set_yticks(y); ax.set_yticklabels([t["E_items"][v] for v in order_v], fontsize=8.3, color=INK); ax.set_xlim(0, 1.3); ax.set_ylim(-0.6, len(order_v) - 0.2)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID, lw=0.8); ax.set_xlabel(t["E_x"], fontsize=8.5, color=INK2)
    # F
    ax = axs[1, 2]; style(ax, t["F"])
    xs = np.arange(len(F_rows))
    for xi, (wd, sep, untr, left) in zip(xs, F_rows):
        col = BLUE if left else ORANGE
        ax.scatter(np.full(6, xi) + np.linspace(-0.18, 0.18, 6), sep, s=16, color=col, zorder=3)
        ax.scatter([xi], [untr], s=22, facecolor="white", edgecolor=INK2, lw=0.9, zorder=4)
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xticks(xs); ax.set_xticklabels([r[0] for r in F_rows], fontsize=8.3, rotation=45, ha="right", color=INK)
    ax.set_ylabel(t["F_y"], fontsize=8.5, color=INK2); ax.set_ylim(-0.3, 1.7)
    ax.scatter([], [], s=16, color=BLUE, label=t["F_left"]); ax.scatter([], [], s=16, color=ORANGE, label=t["F_right"]); ax.scatter([], [], s=22, facecolor="white", edgecolor=INK2, label=t["F_untr"])
    ax.legend(loc="upper right", fontsize=7.8, frameon=False)
    fig.text(0.01, 0.006, t["foot"], fontsize=7.2, color=INK2)
    fig.tight_layout(rect=(0, 0.05, 1, 0.965), h_pad=2.6, w_pad=2.4)
    out = R / "e167" / t["out"]
    fig.savefig(out, dpi=165, facecolor=SURF); plt.close(fig); print(out)


for lang in (sys.argv[1:] or ["en", "ja"]):
    draw(lang)
print("E cell ratios", {k: round(v, 2) for k, v in E_cell.items()}, "resid", round(E_resid, 2))
print("F", [(r[0], round(float(np.mean(r[1])), 2), r[3]) for r in F_rows])
