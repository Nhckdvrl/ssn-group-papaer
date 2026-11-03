#!/usr/bin/env python3
"""E170 figure (2 panels) from committed JSONs.

A  deep layers (L6-11), endpoint: for each linguistic variable, cross-model correlation of the cell-level
   division (X-cells) for different-init vs same-init pairs, with the within-cell residual for comparison.
B  multi-function words, L11: how strongly each run separates the word's grammatical functions in routing
   (mean over 6 trained runs, min-max range), untrained model in grey; sorted; selected words labelled.

Usage: e170_figure.py [en|ja]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = Path(__file__).resolve().parents[1] / "results"
BLUE, ORANGE, GRAY, INK, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#8d8c86", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
TXT = {
    "en": dict(out="e170_figure.png", font=None,
        sup="Which parts of the expert division are shared by every training run?",
        A="A  Division along linguistic labels vs. the rest (deep layers, endpoint)",
        A_x="cross-model correlation", A_init="different init", A_order="same init",
        A_vars=[("upos", "word class of this form"), ("feats", "morphological features"), ("deprel", "dependency relation"),
                ("head_upos", "head word class"), ("next_upos", "next word class"), ("prev_upos", "previous word class"),
                ("genre", "text genre"), ("__resid__", "residual within cells")],
        B="B  Does routing split a word by its grammatical function? (L11)",
        B_y="separation (same-function vs different-function pairs, in sd)", B_x="83 multi-function words, sorted",
        B_tr="6 trained runs (mean, min–max)", B_un="untrained model",
        foot="A: cell = (word form, label pair); bars = corr. of cell means across models; 'residual' = corr. of what is left within cells. "
             "B: functions = UPOS:deprel with ≥15 occurrences; separation = (mean co-routing of same-function pairs − different-function pairs) / sd."),
    "ja": dict(out="e170_figure_ja.png", font="Noto Sans CJK JP",
        sup="エキスパートの分担のうち、どの部分がすべての学習で共有されるか",
        A="A  言語的ラベルに沿った分担 vs それ以外（深い層, 終点）",
        A_x="モデル間相関", A_init="初期化だけ違う", A_order="同じ初期化",
        A_vars=[("upos", "同じ語形の品詞"), ("feats", "形態素特徴"), ("deprel", "係り受け関係"),
                ("head_upos", "主辞の品詞"), ("next_upos", "直後の語の品詞"), ("prev_upos", "直前の語の品詞"),
                ("genre", "ジャンル"), ("__resid__", "ラベルで説明できない残り")],
        B="B  ルーティングは語を文法的機能で分けているか（第 11 層）",
        B_y="分離度（同機能ペア − 異機能ペアの共ルーティング, sd 単位）", B_x="多機能語 83 語（分離度順）",
        B_tr="学習済み 6 本（平均, 最小–最大）", B_un="未学習モデル",
        foot="A：セル =（語形, ラベルの組）。棒 = セル平均のモデル間相関。「残り」= セル内に残る部分のモデル間相関。"
             "B：機能 = UPOS:deprel（各 15 回以上）。分離度 =（同機能ペアの共ルーティング平均 − 異機能ペア）÷ 標準偏差。"),
}
J = json.loads((R / "e170/decomp_3999793152.json").read_text())["vars"]
AMB = json.loads((R / "e170/ambiguous_3999793152.json").read_text())["forms"]
runs = ["I0D0", "I1D0", "I2D0", "I3D0", "I0D1", "I1D1"]
deep = range(6, 12)
band = lambda rec, key: float(np.mean([rec["layers"][l][key] for l in deep]))
LABEL = {"to", "that", "it", "you", "there", "which", "may", "me", "is", "was", "for", "about", "have", "like", "as"}


def style(ax, title):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8.5)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8, fontweight="bold")


def draw(lang):
    t = TXT[lang]
    if t["font"]:
        plt.rcParams["font.family"] = [t["font"], "DejaVu Sans"]
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.2), facecolor=SURF, gridspec_kw={"width_ratios": [1, 1.35]})
    fig.suptitle(t["sup"], x=0.01, ha="left", fontsize=13, color=INK, fontweight="bold")
    ax = axs[0]; style(ax, t["A"])
    names, vi, vo = [], [], []
    for k, lab in t["A_vars"]:
        if k == "__resid__":
            vi.append(band(J["upos+deprel"], "D_init_residcorr")); vo.append(band(J["upos+deprel"], "D_order_residcorr"))
        else:
            vi.append(band(J[k], "D_init_cellcorr")); vo.append(band(J[k], "D_order_cellcorr"))
        names.append(lab)
    y = np.arange(len(names))[::-1]; h = 0.38
    ax.barh(y + h / 2, vo, height=h, color=ORANGE, label=t["A_order"])
    ax.barh(y - h / 2, vi, height=h, color=BLUE, label=t["A_init"])
    for yi, a, b in zip(y, vi, vo):
        ax.text(max(a, b) + 0.02, yi, f"{a / b:.2f}", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=9, color=INK); ax.set_xlim(0, 1.0)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_xlabel(t["A_x"], fontsize=9, color=INK2)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    ax.text(0.99, 0.99, "number = different-init / same-init" if lang == "en" else "数字 = 初期化だけ違う ÷ 同じ初期化", transform=ax.transAxes, ha="right", va="top", fontsize=8, color=INK2)
    ax = axs[1]; style(ax, t["B"])
    forms = sorted(AMB, key=lambda f: -np.mean([AMB[f]["layers"]["11"]["sep"][r] for r in runs]))
    m = np.array([np.mean([AMB[f]["layers"]["11"]["sep"][r] for r in runs]) for f in forms])
    lo = np.array([min(AMB[f]["layers"]["11"]["sep"][r] for r in runs) for f in forms])
    hi = np.array([max(AMB[f]["layers"]["11"]["sep"][r] for r in runs) for f in forms])
    u = np.array([AMB[f]["layers"]["11"]["sep"]["I0D0@0"] for f in forms])
    x = np.arange(len(forms))
    ax.fill_between(x, lo, hi, color=BLUE, alpha=0.18, lw=0)
    ax.plot(x, m, color=BLUE, lw=1.8, label=t["B_tr"])
    ax.plot(x, u, color=GRAY, lw=1.2, ls="--", label=t["B_un"])
    ax.axhline(0, color=GRID, lw=0.8)
    k = 0
    for i, f in enumerate(forms):
        if f in LABEL:
            dy = (9, -13, 22, -26)[k % 4] if m[i] > 0.25 else (-13, -26, 9, 22)[k % 4]
            k += 1
            ax.annotate(f, (i, m[i]), xytext=(0, dy), textcoords="offset points", ha="center", fontsize=8.5, color=INK,
                        arrowprops=dict(arrowstyle="-", color=GRID, lw=0.6))
    ax.set_xticks([]); ax.set_xlabel(t["B_x"], fontsize=9, color=INK2); ax.set_ylabel(t["B_y"], fontsize=8.5, color=INK2)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.legend(loc="upper right", fontsize=8.5, frameon=False)
    fig.text(0.01, 0.01, t["foot"], fontsize=7.3, color=INK2)
    fig.tight_layout(rect=(0, 0.07, 1, 0.94), w_pad=3)
    out = R / "e170" / t["out"]; fig.savefig(out, dpi=170, facecolor=SURF); plt.close(fig); print(out)


for lang in (sys.argv[1:] or ["en", "ja"]):
    draw(lang)
