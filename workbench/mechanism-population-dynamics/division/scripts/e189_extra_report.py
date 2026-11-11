"""E189 addendum report: appends §7–§9 to report/tables.md, adds keys to summary.json, writes fig_margins.png,
fig_layer_timing.png, fig_subspace_share.png.  Reads node-local e189/extra.json (run after e189_report.py)."""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = "/tmp/xiang_e186/e189"; OUTD = sys.argv[1] if len(sys.argv) > 1 else f"{IN}/report"
X = json.load(open(f"{IN}/extra.json"))
M, S, A = X["margins"], X["share"], X["arrival_layer"]
NAMES = ["20B", "83B", "335B", "587B", "838B", "1.09T", "1.34T", "5.1T", "发布版"]
LBL = ["20B", "83B", "335B", "587B", "838B", "1.09T", "1.34T", "5.1T", "rel"]
TOKX = [20e9, 83e9, 335e9, 587e9, 838e9, 1.09e12, 1.34e12, 5.1e12, 7.5e12]
L, NK = 16, 9
MID = range(2, 12)
GROUPS = {"第 0 层": [0], "浅 1–5": range(1, 6), "中 6–10": range(6, 11), "深 11–15": range(11, 16)}
md = ["", "# 追加（11-11，POST-HOC；卡末\"追加（11-11）\"节）", ""]


def gmean(key, t, layers, j=1):
    return float(np.mean([M[f"{l}_{t}"][key][j] if isinstance(M[f"{l}_{t}"][key], list) else M[f"{l}_{t}"][key] for l in layers]))


md += ["## §7 路由器 logit 边距 / softmax 饱和（T_t 作用在自己的输入上；逐 token 中位数，再按层组平均；括号为第 0 层）", "",
       "| t | top1−top2 | top8−top9 | top-1 概率 | top-8 概率和 | 熵（bit） | logit 尺度（token 内 sd） | 行范数 W / W·diag(g) | 增益均值 |", "|---|---|---|---|---|---|---|---|---|"]
for t in range(NK):
    c = lambda k: f"{gmean(k, t, MID):.3f}（{gmean(k, t, [0]):.3f}）"
    md.append(f"| {NAMES[t]} | {c('gap12')} | {c('gap89')} | {c('p1')} | {c('p8sum')} | {c('entropy_bits')} | {c('logit_sd')} | "
              f"{gmean('rownorm_W', t, MID):.3f} / {gmean('rownorm_Weff', t, MID):.3f}（{gmean('rownorm_W', t, [0]):.3f} / {gmean('rownorm_Weff', t, [0]):.3f}） | {gmean('gain_mean', t, MID):.3f} |")
md += ["", "按层组（top8−top9 中位数 · top-8 概率和中位数 · 熵中位数）：", "", "| 层组 | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for g, ls in GROUPS.items():
    md.append(f"| {g} | " + " | ".join(f"{gmean('gap89', t, ls):.2f} · {gmean('p8sum', t, ls):.2f} · {gmean('entropy_bits', t, ls):.2f}" for t in range(NK)) + " |")
md += ["", "四分位（mid 段均值；top8−top9 与 top-8 概率和的 [q25, q75]）：", "", "| t | top8−top9 | top-8 概率和 |", "|---|---|---|"]
for t in range(NK):
    md.append(f"| {NAMES[t]} | [{gmean('gap89', t, MID, 0):.3f}, {gmean('gap89', t, MID, 2):.3f}] | [{gmean('p8sum', t, MID, 0):.3f}, {gmean('p8sum', t, MID, 2):.3f}] |")
md += ["", "逐层 top-8 概率和中位数：", "", "| 层 | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for l in range(L):
    md.append(f"| {l} | " + " | ".join(f"{M[f'{l}_{t}']['p8sum'][1]:.2f}" for t in range(NK)) + " |")
md += ["", "逐层 top8−top9 logit 差中位数：", "", "| 层 | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for l in range(L):
    md.append(f"| {l} | " + " | ".join(f"{M[f'{l}_{t}']['gap89'][1]:.3f}" for t in range(NK)) + " |")

fmt = lambda x: "未达" if x is None else (f"{x / 1e12:.2f}T" if x >= 1e12 else f"{x / 1e9:.0f}B")
md += ["", "## §8 逐层到达时间（归一化 n 越过 .5 / .8 的 token 数；R · H · O）", "", "| 层 | top-8 n=.5 | top-8 n=.8 | top-1 n=.5 | top-1 n=.8 |", "|---|---|---|---|---|"]
for l in range(L):
    md.append(f"| {l} | " + " | ".join(" · ".join(fmt(A[f"{l}_{c}_{nm}_{thr}"]) for c in ("R", "H", "O")) for nm in ("top8", "top1") for thr in (.5, .8)) + " |")

md += ["", "## §9 几何是否向读出子空间集中（x̂_t 的能量份额；mid 段均值；括号为 token 中心化后）", "",
       "| t | P_F（终点读出） | P_t（当期读出） | 随机 63 维 均值 [min,max] | 中心化 PC63 自身份额 | 主角 cos：P_t–PC63 / P_F–PC63 / 随机–PC63 |", "|---|---|---|---|---|---|"]
sm = lambda k, t, ls=MID, j=None: float(np.mean([S[f"{l}_{t}"][k] if j is None else S[f"{l}_{t}"][k][j] for l in ls]))
for t in range(NK):
    md.append(f"| {NAMES[t]} | {sm('PF', t):.3f}（{sm('PF_c', t):.3f}） | {sm('Pt', t):.3f}（{sm('Pt_c', t):.3f}） | "
              f"{sm('rand', t, j=0):.3f} [{sm('rand', t, j=1):.3f}, {sm('rand', t, j=2):.3f}]（{sm('rand_c', t, j=0):.3f}） | {sm('pc_share_c', t):.3f} | "
              f"{sm('pa_Pt_PC', t):.3f} / {sm('pa_PF_PC', t):.3f} / {sm('pa_rand_PC', t):.3f} |")
md += ["", "按层组的 P_F 份额（中心化）· P_t 份额（中心化）：", "", "| 层组 | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for g, ls in GROUPS.items():
    md.append(f"| {g} | " + " | ".join(f"{sm('PF_c', t, ls):.3f} · {sm('Pt_c', t, ls):.3f}" for t in range(NK)) + " |")
open(f"{OUTD}/tables.md", "a").write("\n".join(md) + "\n")
SJ = json.load(open(f"{OUTD}/summary.json"))
SJ["addendum_margins_mid"] = {k: [gmean(k, t, MID) for t in range(NK)] for k in ("gap12", "gap89", "p1", "p8sum", "entropy_bits", "logit_sd", "rownorm_W", "rownorm_Weff")}
SJ["addendum_margins_l0"] = {k: [gmean(k, t, [0]) for t in range(NK)] for k in ("gap12", "gap89", "p1", "p8sum", "entropy_bits", "logit_sd", "rownorm_Weff")}
SJ["addendum_arrival_layer"] = A
SJ["addendum_share_mid"] = {k: [sm(k, t) for t in range(NK)] for k in ("PF", "Pt", "PF_c", "Pt_c", "pc_share_c", "pa_Pt_PC", "pa_PF_PC", "pa_rand_PC")}
SJ["addendum_share_mid"]["rand"] = [sm("rand", t, j=0) for t in range(NK)]; SJ["addendum_share_mid"]["rand_c"] = [sm("rand_c", t, j=0) for t in range(NK)]
json.dump(SJ, open(f"{OUTD}/summary.json", "w"), ensure_ascii=False, indent=0)

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
GC = {"第 0 层": "#eb6834", "浅 1–5": "#1baf7a", "中 6–10": "#2a78d6", "深 11–15": "#6250d6"}
GE = {"第 0 层": "layer 0", "浅 1–5": "layers 1–5", "中 6–10": "layers 6–10", "深 11–15": "layers 11–15"}
x = np.array(TOKX)
fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
for j, (k, yl) in enumerate((("gap89", "median top8−top9 logit gap"), ("p8sum", "median top-8 prob. mass"), ("entropy_bits", "median routing entropy (bits)"), ("rownorm_Weff", "mean row norm of W·diag(g)"))):
    for g, ls in GROUPS.items():
        ax[j].plot(x, [gmean(k, t, ls) for t in range(NK)], "-o", color=GC[g], lw=2, ms=4, label=GE[g])
    ax[j].axvspan(335e9, 838e9, color="#eee", lw=0)
    ax[j].set_xscale("log"); ax[j].set_xticks(x); ax[j].set_xticklabels(LBL, rotation=45, fontsize=7); ax[j].set_ylabel(yl)
ax[0].legend(fontsize=7, frameon=False); ax[0].set_title("shaded: 335B–838B (R reaches n=.5 / layer-0 rewrite)", fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_margins.png", dpi=150)

fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for j, nm in enumerate(("top8", "top1")):
    for c, colr in (("R", "#eb6834"), ("H", "#2a78d6"), ("O", "#0b0b0b")):
        for thr, ls in ((.5, "-o"), (.8, "--s")):
            v = [A[f"{l}_{c}_{nm}_{thr}"] or np.nan for l in range(L)]
            ax[j].plot(range(L), v, ls, color=colr, lw=1.8 if c != "O" else 1, ms=4, label=f"{c} n={thr}")
    ax[j].set_yscale("log"); ax[j].set_xlabel("layer"); ax[j].set_title(f"arrival time ({nm}; missing = not reached by 5.1T)")
    ax[j].set_yticks(TOKX[:8]); ax[j].set_yticklabels(LBL[:8])
ax[0].set_ylabel("training tokens"); ax[0].legend(fontsize=7, frameon=False, ncol=2)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_layer_timing.png", dpi=150)

fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for k, colr, lab in (("PF_c", "#eb6834", "P_F (release readout)"), ("Pt_c", "#2a78d6", "P_t (own readout)"), ("rand_c", "#888", "random 63-dim"), ("pc_share_c", "#0b0b0b", "top-63 PCs (ceiling)")):
    ax[0].plot(x, [sm(k, t) if k != "rand_c" else sm(k, t, j=0) for t in range(NK)], "-o", color=colr, lw=2, ms=4, label=lab)
ax[0].set_yscale("log"); ax[0].set_title("energy share of centred hidden x_t (layers 2–11)"); ax[0].legend(fontsize=7, frameon=False)
for k, colr, lab in (("pa_Pt_PC", "#2a78d6", "P_t vs PCs"), ("pa_PF_PC", "#eb6834", "P_F vs PCs"), ("pa_rand_PC", "#888", "random vs PCs")):
    ax[1].plot(x, [sm(k, t) for t in range(NK)], "-o", color=colr, lw=2, ms=4, label=lab)
ax[1].set_title("mean principal-angle cosine with top-63 PCs of x_t"); ax[1].legend(fontsize=7, frameon=False)
for a in ax:
    a.set_xscale("log"); a.set_xticks(x); a.set_xticklabels(LBL, rotation=45, fontsize=7)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_subspace_share.png", dpi=150)
print("ok")
