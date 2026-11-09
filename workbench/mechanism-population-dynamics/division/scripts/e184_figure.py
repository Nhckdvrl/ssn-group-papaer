#!/usr/bin/env python3
"""E184 tables + figures from results/e184/<model>.json.  Usage: e184_figure.py [models...]
Writes results/e184/tables.md, summary.json, fig_claim{1,2,3,4}.png (T vs N_A / N_B by layer, three models)."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WB = Path(__file__).resolve().parents[1]
OUT = WB / "results/e184"
MODELS = sys.argv[1:] or ["qwen3", "gptoss", "olmoe"]
NAME = {"qwen3": "Qwen3-30B-A3B", "gptoss": "GPT-OSS-20B", "olmoe": "OLMoE-1B-7B-0125-Inst"}
CLAIMS = [("1", "flores", "R1 token-id purity − id-shuffle floor", "lexical / token-id experts"),
          ("2", "ud", "Spec_POS − UPOS-shuffle floor", "POS specialisation"),
          ("3", "flores", "rep1 − random-pair floor", "adjacent tokens share expert"),
          ("4", "flores", "ΔG = G(pred next) − G(input), bits", "deep layers route by predicted next token")]
SECOND = [("2w", "ud", "Spec_POS − within-token-id UPOS shuffle"), ("4n", "flores", "ΔG' = G(true next) − G(input)"),
          ("1", "ud", "R1 on UD"), ("3", "ud", "rep1 on UD"), ("4", "ud", "ΔG on UD")]
R = {m: json.load(open(OUT / f"{m}.json")) for m in MODELS if (OUT / f"{m}.json").exists()}
MODELS = [m for m in MODELS if m in R]


def J(o, c):
    r = {k: np.array(v, dtype=float) for k, v in o["readouts"].items() if isinstance(v, list)}
    if c == "1":
        return r["R1"] - r["R1_floor"]
    if c == "2":
        return r["R2"] - r["R2_floor"]
    if c == "2w":
        return r["R2"] - r["R2w_floor"]
    if c == "3":
        return r["R3"] - r["R3_floor"]
    if c == "4":
        return r["G_pred"] - r["G_in"]
    if c == "4n":
        return r["G_nxt"] - r["G_in"]


def fam(Jm, D):
    return Jm[:, 0], Jm[:, 1:1 + D], Jm[:, 1 + D:1 + 2 * D]


def f3(x):
    return f"{x:.3f}"


def rng(a):
    return f"{a.mean():.3f} [{a.min():.3f}, {a.max():.3f}]"


lines = ["# E184 tables（自动生成：`scripts/e184_figure.py`；数据 `results/e184/<model>.json`）", ""]
summary = {}
# ---------------------------------------------------------------- verdict table
lines += ["## 1. 结论级判决（主语料、主读数；逐层 above / within / below / split 计数；⌈2L/3⌉ 门槛）", "",
          "| 结论 | " + " | ".join(NAME[m] for m in MODELS) + " |", "|---|" + "---|" * len(MODELS)]
for c, corp, desc, short in CLAIMS:
    row = f"| {c} {short}（{corp}） |"
    for m in MODELS:
        v = R[m][corp]["verdicts"][c]
        h = [R[m][corp][f"half{i}"]["verdicts"][c]["verdict"] for i in (0, 1)]
        star = "" if all(x == v["verdict"] for x in h) else "*"
        cn = v["counts"]
        extra = (f"; 中位 T−max = {v['ratio_above_median']:.3f} bit" if c == "4" else f"; 中位 T/max = {v['ratio_above_median']:.2f}") if v["verdict"].startswith("survives") else ""
        row += f" **{v['verdict']}**{star}（above {cn['above']} / within {cn['within']} / below {cn['below']} / split {cn['split']}，L={len(v['classes'])}{extra}） |"
        summary.setdefault(m, {})[f"{c}_{corp}"] = {"verdict": v["verdict"], "counts": cn, "halves": h,
                                                     "ratio": v["ratio_above_median"]}
    lines.append(row)
lines += ["", "\\* = 两个语料半（序列 id 奇 / 偶）中至少一半的判决与全量不同。", ""]
lines += ["### 次级判决（预登记的次读数与 UD 复核）", "", "| 读数 | " + " | ".join(NAME[m] for m in MODELS) + " |",
          "|---|" + "---|" * len(MODELS)]
for c, corp, desc in SECOND:
    row = f"| {c}（{corp}）{desc} |"
    for m in MODELS:
        v = R[m][corp]["verdicts"][c]
        h = [R[m][corp][f"half{i}"]["verdicts"][c]["verdict"] for i in (0, 1)]
        star = "" if all(x == v["verdict"] for x in h) else "*"
        cn = v["counts"]
        row += f" {v['verdict']}{star}（{cn['above']}/{cn['within']}/{cn['below']}/{cn['split']}） |"
        summary[m][f"{c}_{corp}"] = {"verdict": v["verdict"], "counts": cn, "halves": h}
    lines.append(row)
lines += ["", "括号内为 above / within / below / split 层数。", ""]

# ---------------------------------------------------------------- key numbers at representative layers
lines += ["## 2. 代表层数值（l* = ⌊L/2⌋ 与末层；T vs 零模型 8-draw 均值 [min, max]）", ""]
for c, corp, desc, short in CLAIMS + [("2w", "ud", "Spec_POS − within-id floor", "")]:
    lines += [f"### 结论 {c}：{desc}（{corp}）", "", "| 模型 | 层 | T | N_A | N_B | T/mean(N_B) | 原值 T / N_B 均值 | 地板 T |",
              "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        D = R[m]["meta"]["draws"]
        o = R[m][corp]
        Jm = J(o, c)
        T, NA, NB = fam(Jm, D)
        L = len(T)
        raw = {"1": "R1", "2": "R2", "2w": "R2", "3": "R3", "4": "G_pred"}[c]
        flo = {"1": "R1_floor", "2": "R2_floor", "2w": "R2w_floor", "3": "R3_floor", "4": "G_in"}[c]
        rw = np.array(o["readouts"][raw]); fl = np.array(o["readouts"][flo])
        for l in (L // 2, L - 1):
            lines.append(f"| {NAME[m]} | {l} | {f3(T[l])} | {rng(NA[l])} | {rng(NB[l])} | {T[l] / NB[l].mean():.2f} | "
                         f"{f3(rw[l, 0])} / {f3(rw[l, 1 + D:].mean())} | {f3(fl[l, 0])} |")
        v = o["verdicts"][c]
        lines.append(f"| {NAME[m]} | 层剖面 Spearman | T vs N_B {v['rho_profile_NB']:.2f} | T vs N_A {v['rho_profile_NA']:.2f} | | "
                     f"中位 T/mean(N_B) 全层 {np.median(T / NB.mean(1)):.2f} | | |")
    lines.append("")
lines.append("结论 4 表中\"原值\"列为 G(预测下一) T / N_B，\"地板\"列为 G(输入) T（bit）。")
lines.append("")

# ---------------------------------------------------------------- crossover
lines += ["## 3. 结论 4：交叉层（ΔG > 0 的首层 / 持续交叉层；无 = None）", "",
          "| 模型 | 语料 | 读数 | T 首 / 持续 | N_A 8 draws 持续 | N_B 8 draws 持续 | 判定 |", "|---|---|---|---|---|---|---|"]
for m in MODELS:
    for corp in ("flores", "ud"):
        for c in ("4", "4n"):
            v = R[m][corp]["verdicts"][c]
            pa = [x[1] for x in v["cross_NA"]]; pb = [x[1] for x in v["cross_NB"]]
            lines.append(f"| {NAME[m]} | {corp} | {'预测下一' if c == '4' else '真实下一'} | {v['cross_T'][0]} / {v['cross_T'][1]} | "
                         f"{pa} | {pb} | {v['cross_rel']} |")
            summary[m][f"cross_{c}_{corp}"] = {"T": v["cross_T"], "NA": pa, "NB": pb, "rel": v["cross_rel"]}
lines.append("")
# G values at representative layers
lines += ["G（bit）原值：", "", "| 模型 | 层 | G_in T / N_A / N_B | G_pred T / N_A / N_B | G_nxt T / N_A / N_B |", "|---|---|---|---|---|"]
for m in MODELS:
    D = R[m]["meta"]["draws"]; o = R[m]["flores"]["readouts"]
    L = len(o["G_in"])
    for l in (0, L // 2, L - 1):
        cell = []
        for g in ("G_in", "G_pred", "G_nxt"):
            a = np.array(o[g])[l]
            cell.append(f"{a[0]:.2f} / {a[1:1 + D].mean():.2f} / {a[1 + D:].mean():.2f}")
        lines.append(f"| {NAME[m]} | {l} | " + " | ".join(cell) + " |")
lines.append("")

# ---------------------------------------------------------------- positive controls
lines += ["## 4. 阳性对照", "", "| 模型 | 两遍一致 | hook fp32 / T-vs-model | N_B 校准负载 TV 均值（最大） | 测量负载 TV N_B vs T（flores 均值） | "
          "T 最大负载 / 均匀（flores 中位） | 置换对照 |·|≤.01 格比例（R1/R2/R2w/R3） | 置换 G 最大（in / pred） | 第 0 层 R1 T / 地板 |",
          "|---|---|---|---|---|---|---|---|---|"]
for m in MODELS:
    r = R[m]; D = r["meta"]["draws"]
    of, ou = r["flores"]["readouts"], r["ud"]["readouts"]
    tvf = np.array(of["loadTV_B"])[:, 1 + D:].mean()
    ml = np.median(np.array(of["maxload"])[:, 0])
    fr = []
    for k, o in (("R1_ctrl", of), ("R2_ctrl", ou), ("R2w_ctrl", ou), ("R3_ctrl", of)):
        a = np.abs(np.array(o[k]))
        fr.append(f"{(a <= .01).mean():.3f}")
    gmax = max(np.nanmax(of["G_shin"]), np.nanmax(ou["G_shin"])), max(np.nanmax(of["G_shpr"]), np.nanmax(ou["G_shpr"]))
    R1 = np.array(of["R1"]); R1f = np.array(of["R1_floor"])
    lines.append(f"| {NAME[m]} | {r['det_exact_min']:.4f} | {r['meta']['hook_agreement']:.4f} / {r['meta']['t_vs_model']:.4f} | "
                 f"{r['loadtv_B_cal_mean']:.4f}（{r['loadtv_B_cal_max']:.4f}） | {tvf:.3f} | {ml:.2f} | {' / '.join(fr)} | "
                 f"{gmax[0]:.3f} / {gmax[1]:.3f} | {R1[0, 0]:.3f} / {R1f[0, 0]:.3f} |")
    summary[m]["controls"] = {"det": r["det_exact_min"], "hook": r["meta"]["hook_agreement"], "tv_cal": r["loadtv_B_cal_mean"],
                              "tv_meas_flores": float(tvf), "maxload_T_flores": float(ml), "shuffle_frac": fr,
                              "G_shuffle_max": gmax, "ntok": r["meta"]["ntok"], "wall_s": r["meta"]["wall_s"]}
lines.append("")
lines += ["语料规模：" + "；".join(f"{NAME[m]} flores {R[m]['meta']['ntok']['flores']} / ud {R[m]['meta']['ntok']['ud']} token，"
                                 f"UD 词末 token {R[m]['ud']['readouts']['n_pos_tokens']}（保留 UPOS {R[m]['ud']['readouts'].get('pos_kept')} 类），"
                                 f"R1 合格 token {R[m]['flores']['readouts']['n_R1_tokens']} / id {R[m]['flores']['readouts']['n_R1_ids']}"
                                 for m in MODELS), ""]

# ---------------------------------------------------------------- secondary readouts (raw)
lines += ["## 5. 补充读数（只报；T / N_A 均值 / N_B 均值，l* 与末层）", "", "| 模型 | 读数 | l* | 末层 |", "|---|---|---|---|"]
for m in MODELS:
    D = R[m]["meta"]["draws"]
    for corp, keys in (("flores", ["VS1", "VSK", "R3any", "R3any_floor", "R3ov", "R3ov_floor", "VS1_in", "VS1_pred", "VS1_nxt"]),
                       ("ud", ["R2ent"])):
        o = R[m][corp]["readouts"]
        for k in keys:
            a = np.array(o[k]); L = a.shape[0]
            cell = [f"{a[l, 0]:.3f} / {a[l, 1:1 + D].mean():.3f} / {a[l, 1 + D:].mean():.3f}" for l in (L // 2, L - 1)]
            lines.append(f"| {NAME[m]} | {k}（{corp}） | {cell[0]} | {cell[1]} |")
lines.append("")
(OUT / "tables.md").write_text("\n".join(lines))
json.dump(summary, open(OUT / "summary.json", "w"), indent=1)

# ---------------------------------------------------------------- figures
CA, CB, CT = "#d08c2b", "#3a78b5", "#111111"
for c, corp, desc, short in CLAIMS:
    fig, axes = plt.subplots(1, len(MODELS), figsize=(4.2 * len(MODELS), 3.2), squeeze=False)
    for ax, m in zip(axes[0], MODELS):
        D = R[m]["meta"]["draws"]
        T, NA, NB = fam(J(R[m][corp], c), D)
        x = np.arange(len(T))
        for N, col, lab in ((NA, CA, "N_A Haar (8)"), (NB, CB, "N_B load-matched (8)")):
            ax.fill_between(x, N.min(1), N.max(1), color=col, alpha=.3, lw=0)
            ax.plot(x, N.mean(1), color=col, lw=1.2, label=lab)
        ax.plot(x, T, color=CT, lw=1.8, label="T trained")
        ax.axhline(0, color="grey", lw=.6)
        v = R[m][corp]["verdicts"][c]["verdict"]
        ax.set_title(f"{NAME[m]} — {v}", fontsize=9)
        ax.set_xlabel("layer")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0][0].set_ylabel(desc, fontsize=8)
    axes[0][0].legend(fontsize=7, frameon=False)
    fig.suptitle(f"Claim {c}: {short} ({corp})", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / f"fig_claim{c}.png", dpi=150)
    plt.close(fig)
print("wrote tables.md, summary.json, figures")
