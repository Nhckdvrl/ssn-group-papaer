"""E189 report: tables.md (all tables, no verdict table), summary.json, fig_decomp_training.png, fig_l0_grid.png.
Card: division/experiments/E189-training-axis-routing-decomposition.md.  Reads node-local e189/{decomp,prep,classes}.json."""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = "/tmp/xiang_e186/e189"
OUTD = sys.argv[1] if len(sys.argv) > 1 else f"{IN}/report"
import os
os.makedirs(OUTD, exist_ok=True)
R = json.load(open(f"{IN}/decomp.json"))
PR = json.load(open(f"{IN}/prep.json"))["report"]
CL = json.load(open(f"{IN}/classes.json"))
LY = {int(k): v for k, v in R["layers"].items()}
L = sorted(LY)
MID = [l for l in range(2, 12) if l in LY]
NAMES = ["20B", "83B", "335B", "587B", "838B", "1.09T", "1.34T", "5.1T", "发布版"]
TOKX = [20e9, 83e9, 335e9, 587e9, 838e9, 1.09e12, 1.34e12, 5.1e12, 7.5e12]   # release plotted right of 5.1T (display only)
NK = 9
COMPS = ["O", "H", "R", "Hp", "Rp"]
CN = {"O": "O", "H": "H", "R": "R", "Hp": "H′", "Rp": "R′"}
md = []
f3 = lambda x: f"{x:.3f}"


def mid(get):
    return float(np.mean([get(LY[l]) for l in MID]))


def comp_mid(key, t, c, i):
    return mid(lambda r: r[key][t][c][i])


# ---------------------------------------------------------------- arrival times
def arrival(vals, chance, thr):
    n = [(v - c) / (1 - c) for v, c in zip(vals, chance)]
    lx = np.log10(TOKX[:8])
    for i in range(1, 8):
        if n[i - 1] < thr <= n[i]:
            f = (thr - n[i - 1]) / (n[i] - n[i - 1])
            return 10 ** (lx[i - 1] + f * (lx[i] - lx[i - 1]))
    return TOKX[0] if n[0] >= thr else None


def fmt_tok(x):
    if x is None:
        return "未达（≤5.1T）"
    return f"{x / 1e12:.2f}T" if x >= 1e12 else f"{x / 1e9:.0f}B"


S = {"positive_controls": {}, "mid": {}, "arrival": {}, "adjacent": {}, "subspace": {}, "l0": {}}
# ---------------------------------------------------------------- §0 controls
pc = S["positive_controls"]
pc["meta_identical"] = PR["pc_meta_identical"]; pc["rebuild_inp_equal"] = PR["pc_rebuild_inp_equal"]
pc["self_pair"] = [min(LY[l]["pc_self"][i] for l in L) for i in (0, 1)]
pc["gain_recovery_top8_min"] = min(LY[l]["pc_gain_recovery_top8"] for l in L)
pc["hung_perm_recovery_min"] = min(LY[l]["pc_hung_perm_recovery"] for l in L)
pc["min_abs_gain"] = R["min_abs_gain"]
pc["store"] = {k: {"top1_min": min(v[str(l)][0] if str(l) in v else v[l][0] for l in L),
                   "top8_min": min(v[str(l)][1] if str(l) in v else v[l][1] for l in L), "n": R["store_pc_rows"][k]}
               for k, v in R["store_pc"].items()}
idr = np.array([[LY[l]["identity_rate_eff"][t] for t in range(NK)] for l in L])
idr_raw = np.array([[LY[l]["identity_rate_raw"][t] for t in range(NK)] for l in L])
pc["identity_rate_eff_layer_mean"] = idr.mean(0).tolist()
md += ["# E189 结果表：OLMoE-0924 训练轴上的路由分歧交叉套用分解", "",
       "卡：`division/experiments/E189-training-axis-routing-decomposition.md`。终点 F = 发布版；主口径 = 增益算进路由器；"
       "mid 段 = 第 2–11 层均值；括号外 top-1 一致，括号内或单列 top-8 重合；22,000 token（20 语 FLORES dev × 1000 + UD EWT 2000）。"
       "**本文件只列测量，不写判决表；读法在卡的结果节。**", "",
       "## §0 阳性对照与执行", "",
       f"- 九个检查点 toksub_meta 逐行一致：{pc['meta_identical']}；重建序列 inp 与 toksub 相等比例 {pc['rebuild_inp_equal']:.3f}。",
       f"- 自身对（t = F）top-1 / top-8 = {pc['self_pair'][0]:.3f} / {pc['self_pair'][1]:.3f}；增益恢复 top-8 最小 {pc['gain_recovery_top8_min']:.4f}；"
       f"匈牙利置换恢复率最小 {pc['hung_perm_recovery_min']:.3f}；min |g| = {pc['min_abs_gain']:.2e}。",
       "- 与 E186 存储（bf16 前向）同 token 的 T 重合（16 层最小值，top-1 / top-8，n）："
       + "；".join(f"{k.replace('olmoe0924_', '')} {v['top1_min']:.3f} / {v['top8_min']:.3f}（{v['n']}）" for k, v in pc["store"].items()) + "。",
       f"- UD 2000 行中有 UPOS 三类标签的 {PR['ud_rows_with_upos_group']}；H(e∣id) 三分位覆盖 {PR['Hid_token_coverage']:.3f} 的 token（305 个 id，E186 英语视图得出）。",
       "", "**专家编号恒等率**（每层路由器行中心化有符号余弦的匈牙利配对落在同编号的比例；有效路由器 W·diag(g)；括号为原始 W）", "",
       "| 层 | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for i, l in enumerate(L):
    md.append(f"| {l} | " + " | ".join(f"{idr[i, t]:.2f}（{idr_raw[i, t]:.2f}）" for t in range(NK)) + " |")
md.append("| 均值 | " + " | ".join(f"{idr[:, t].mean():.2f}" for t in range(NK)) + " |")

# ---------------------------------------------------------------- §1 decomposition
md += ["", "## §1 分解（终点 = 发布版；mid 段；top-1（top-8）；95% 句聚类自助 CI 为 top-8）", "",
       "| t | O | H | R | H′ | R′ | O 的打乱期望 | 地板 N_A / N_B / N_G（top-8，8 draw 均值 [min,max] 合并） | 匈牙利配对 O / R（top-8） |",
       "|---|---|---|---|---|---|---|---|---|"]
mci = np.array(R["mid_ci"]) if "mid_ci" in R else None
for t in range(NK):
    row = []
    for ci_, c in enumerate(COMPS):
        a1, a8 = comp_mid("toF", t, c, 0), comp_mid("toF", t, c, 1)
        S["mid"].setdefault(c, {"top1": [], "top8": [], "top8_ci": []})
        S["mid"][c]["top1"].append(a1); S["mid"][c]["top8"].append(a8)
        cc = mci[t, ci_, 1].tolist() if mci is not None else None
        S["mid"][c]["top8_ci"].append(cc)
        row.append(f"{a1:.3f}（{a8:.3f}" + (f" [{cc[0]:.3f}, {cc[1]:.3f}]" if cc else "") + "）")
    ch = (comp_mid("toF", t, "O_chance", 0), comp_mid("toF", t, "O_chance", 1))
    geo = []
    for fam in ("N_A", "N_B", "N_G"):
        arr = np.array([np.array(LY[l]["geo"][fam]["toF"])[:, t, 1] for l in MID])   # [mid, draws]
        geo.append(f"{arr.mean():.3f} [{arr.mean(0).min():.3f}, {arr.mean(0).max():.3f}]")
        S["mid"].setdefault("geo_" + fam, {"top1": [], "top8": []})
        S["mid"]["geo_" + fam]["top8"].append(float(arr.mean()))
        S["mid"]["geo_" + fam]["top1"].append(float(np.mean([np.array(LY[l]["geo"][fam]["toF"])[:, t, 0] for l in MID])))
    hO = mid(lambda r: r["toF"][t]["O_hung"][1]); hR = mid(lambda r: r["toF"][t]["R_hung"][1])
    md.append(f"| {NAMES[t]} | " + " | ".join(row) + f" | {ch[0]:.3f}（{ch[1]:.3f}） | " + " / ".join(geo) + f" | {hO:.3f} / {hR:.3f} |")
md += ["", "副口径（增益算进隐状态：原始 h_s 喂给 W_t）mid 段 top-1（top-8）：", "", "| t | O | H | R | H′ | R′ |", "|---|---|---|---|---|---|"]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{comp_mid('toF_raw', t, c, 0):.3f}（{comp_mid('toF_raw', t, c, 1):.3f}）" for c in COMPS) + " |")
md += ["", "以 5.1T（退火前）为终点的稳健性（mid 段 top-1（top-8））：", "", "| t | O | H | R | H′ | R′ |", "|---|---|---|---|---|---|"]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{comp_mid('to51', t, c, 0):.3f}（{comp_mid('to51', t, c, 1):.3f}）" for c in COMPS) + " |")
md += ["", "英语子集（FLORES eng + UD，3000 token）mid 段 top-8，与 §22 5a（英语视图 T / N_F）对账；N_A 为第 0 个 draw：", "",
       "| t | O | H | R | 地板 N_A draw0 |", "|---|---|---|---|---|"]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{mid(lambda r: r['toF_eng'][t][c][1]):.3f}" for c in ("O", "H", "R"))
              + f" | {mid(lambda r: r['geo']['N_A']['toF_eng_draw0'][t][1]):.3f} |")
S["eng_O_top8"] = [mid(lambda r: r["toF_eng"][t]["O"][1]) for t in range(NK)]

# per-layer
for i, nm in ((1, "top-8"), (0, "top-1")):
    md += ["", f"**逐层 O / H / R（{nm}）**：每格 O · H · R", "", "| 层 | " + " | ".join(NAMES[:8]) + " |", "|---|" + "---|" * 8]
    for l in L:
        md.append(f"| {l} | " + " | ".join(" · ".join(f"{LY[l]['toF'][t][c][i]:.2f}" for c in ("O", "H", "R")) for t in range(8)) + " |")
md += ["", "**逐层 H′ / R′（top-8）**：每格 H′ · R′", "", "| 层 | " + " | ".join(NAMES[:8]) + " |", "|---|" + "---|" * 8]
for l in L:
    md.append(f"| {l} | " + " | ".join(" · ".join(f"{LY[l]['toF'][t][c][1]:.2f}" for c in ("Hp", "Rp")) for t in range(8)) + " |")
md += ["", "**逐层几何地板 N_A（top-8，8 draw 均值）**", "", "| 层 | " + " | ".join(NAMES[:8]) + " |", "|---|" + "---|" * 8]
for l in L:
    md.append(f"| {l} | " + " | ".join(f"{np.array(LY[l]['geo']['N_A']['toF'])[:, t, 1].mean():.2f}" for t in range(8)) + " |")

# arrival
md += ["", "**到达时间**（mid 段均值；n = (x − c)/(1 − c)，c = 该分量的打乱期望（mid 段均值）；对数 token 轴线性插值；只是概括）", "",
       "| 分量 | top-8 n=.5 | top-8 n=.8 | top-1 n=.5 | top-1 n=.8 |", "|---|---|---|---|---|"]
for c in COMPS:
    row = []
    for i in (1, 0):
        vals = [comp_mid("toF", t, c, i) for t in range(8)]
        chs = [comp_mid("toF", t, c + "_chance", i) for t in range(8)]
        for thr in (.5, .8):
            a = arrival(vals, chs, thr)
            S["arrival"][f"{c}_top{8 if i else 1}_{thr}"] = a
            row.append(fmt_tok(a))
    md.append(f"| {CN[c]} | " + " | ".join(row) + " |")
for fam in ("N_A", "N_B", "N_G"):
    row = []
    for i in (1, 0):
        vals = S["mid"]["geo_" + fam]["top8" if i else "top1"][:8]
        chs = [comp_mid("toF", t, "H_chance", i) for t in range(8)]
        for thr in (.5, .8):
            a = arrival(vals, chs, thr); S["arrival"][f"geo_{fam}_top{8 if i else 1}_{thr}"] = a
            row.append(fmt_tok(a))
    md.append(f"| 地板 {fam} | " + " | ".join(row) + " |")

# grid
md += ["", "## §1b 全网格 G(t, s) = agree(T_t(x̂_s), T_F(x̂_F))（mid 段 top-8；行 = 路由器检查点 t，列 = 隐状态检查点 s）", "",
       "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
GR = np.array([[mid(lambda r: r["grid"][t][s][1]) for s in range(NK)] for t in range(NK)])
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{GR[t, s]:.3f}" for s in range(NK)) + " |")
S["grid_mid_top8"] = GR.tolist()

# ---------------------------------------------------------------- §2 adjacent
md += ["", "## §2 相邻检查点增量（t_i → t_{i+1}，以 t_{i+1} 为终点；mid 段 1 − 一致率，top-8（top-1））", "",
       "| 段 | 1−O | 1−H | 1−R | 1−H′ | 1−R′ | 地板 1−N_A / N_B / N_G（top-8） |", "|---|---|---|---|---|---|---|"]
for i in range(NK - 1):
    vals = {c: (1 - mid(lambda r: r["adj"][i][c][1]), 1 - mid(lambda r: r["adj"][i][c][0])) for c in COMPS}
    S["adjacent"][f"{NAMES[i]}→{NAMES[i + 1]}"] = vals
    geo = " / ".join(f"{1 - np.mean([np.array(LY[l]['geo'][fam]['adj'])[:, i, 1].mean() for l in MID]):.3f}" for fam in ("N_A", "N_B", "N_G"))
    md.append(f"| {NAMES[i]}→{NAMES[i + 1]} | " + " | ".join(f"{vals[c][0]:.3f}（{vals[c][1]:.3f}）" for c in COMPS) + f" | {geo} |")
md += ["", "逐层相邻增量 1 − R / 1 − H（top-8）：", "", "| 层 | " + " | ".join(f"{NAMES[i]}→{NAMES[i + 1]}" for i in range(NK - 1)) + " |", "|---|" + "---|" * (NK - 1)]
for l in L:
    md.append(f"| {l} | " + " | ".join(f"{1 - LY[l]['adj'][i]['R'][1]:.2f} / {1 - LY[l]['adj'][i]['H'][1]:.2f}" for i in range(NK - 1)) + " |")

# ---------------------------------------------------------------- §3 subspace
md += ["", "## §3 子空间说：隐状态 x̂_t 相对 x̂_F 的漂移，读出子空间 P_F（W_F·diag(g_F) 中心化行空间）内 / 外（mid 段）", "",
       "相对漂移 = ‖a−b‖/‖b‖ 的 token 均值；cos = 逐 token 余弦均值；CKA 为线性 CKA（全空间与子空间外用固定 4000 token 子样本）；"
       "id 均值 / 残差 = 出现 ≥ 5 次的 id（覆盖 " + f"{R['idmean_coverage']:.3f}）上的分解。", "",
       "| t | 漂移 内 / 外 / 全 | cos 内 / 外 / 全 | CKA 内 / 外 / 全 | id 均值漂移 全 / 内 | 残差漂移 全 / 内 | CKA id 均值 全 / 内 | CKA 残差 全 / 内 | P_t 与 P_F 主角 cos 均值 | 子空间内能量（t） |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for t in range(NK):
    g = lambda k, j=None: mid(lambda r: r["subspace"][t][k] if j is None else r["subspace"][t][k][j])
    d = {k: g(k) for k in ("cka_in", "cka_out", "cka_full", "cka_idmean_full", "cka_idmean_in", "cka_resid_full", "cka_resid_in", "pa_cos_mean", "energy_in_t")}
    for k in ("in", "out", "full", "idmean_full", "idmean_in", "resid_full", "resid_in"):
        d[k + "_drift"] = g(k, 0); d[k + "_cos"] = g(k, 1)
    S["subspace"][NAMES[t]] = d
    md.append(f"| {NAMES[t]} | {d['in_drift']:.3f} / {d['out_drift']:.3f} / {d['full_drift']:.3f} | {d['in_cos']:.3f} / {d['out_cos']:.3f} / {d['full_cos']:.3f} | "
              f"{d['cka_in']:.3f} / {d['cka_out']:.3f} / {d['cka_full']:.3f} | {d['idmean_full_drift']:.3f} / {d['idmean_in_drift']:.3f} | "
              f"{d['resid_full_drift']:.3f} / {d['resid_in_drift']:.3f} | {d['cka_idmean_full']:.3f} / {d['cka_idmean_in']:.3f} | "
              f"{d['cka_resid_full']:.3f} / {d['cka_resid_in']:.3f} | {d['pa_cos_mean']:.3f} | {d['energy_in_t']:.3f} |")
md += ["", "id 均值分量在发布版隐状态中的能量占比（mid 段）：全空间 "
       f"{mid(lambda r: r['subspace'][8]['energy_idmean_full']):.3f}，子空间内 {mid(lambda r: r['subspace'][8]['energy_idmean_in']):.3f}。", "",
       "逐层子空间内 / 外相对漂移（20B · 335B · 1.34T）：", "", "| 层 | 内 | 外 | CKA 内 | CKA 外 |", "|---|---|---|---|---|"]
for l in L:
    sb = LY[l]["subspace"]
    md.append(f"| {l} | " + " · ".join(f"{sb[t]['in'][0]:.2f}" for t in (0, 2, 6)) + " | " + " · ".join(f"{sb[t]['out'][0]:.2f}" for t in (0, 2, 6))
              + " | " + " · ".join(f"{sb[t]['cka_in']:.2f}" for t in (0, 2, 6)) + " | " + " · ".join(f"{sb[t]['cka_out']:.2f}" for t in (0, 2, 6)) + " |")

# ---------------------------------------------------------------- §4 layer 0 grid
l0 = LY[0]
RA = np.array(l0["l0_grid"]["ratio"]); SP = np.array(l0["l0_grid"]["share_prev"]); SI = np.array(l0["l0_grid"]["share_inp"])
GE = np.array(l0["l0_grid_eng_ratio"]); NB = np.array(l0["l0_NB_diag"])
S["l0"] = {"ratio": RA.tolist(), "share_prev": SP.tolist(), "share_inp": SI.tolist(), "ratio_eng": GE.tolist(), "NB_diag": NB.tolist()}
md += ["", "## §4 第 0 层前一 token 路由：9 × 9 网格（行 = 路由器 T_t，列 = 隐状态 x̂_s；读数 Î(top-1; 前一 id) / Î(top-1; 输入 id)，e185_lib.mi_marg，22k token）", "",
       "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{RA[t, s]:.2f}" for s in range(NK)) + " |")
md += ["", "前一 id 份额 Î/H(top-1)（同一网格）：", "", "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{SP[t, s]:.3f}" for s in range(NK)) + " |")
md += ["", "输入 id 份额：", "", "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{SI[t, s]:.3f}" for s in range(NK)) + " |")
md += ["", "英语子集（eng + UD，3000 token）同一比值网格（小样本，估计器偏差大，只看形状）：", "", "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
for t in range(NK):
    md.append(f"| {NAMES[t]} | " + " | ".join(f"{GE[t, s]:.2f}" for s in range(NK)) + " |")
md += ["", "对角线对账：T_t(x̂_t) 比值 vs N_B 型随机路由器（以 W_t 为模板、负载拟合在 x̂_t 上、1 draw）vs §22 5b（E186 英语视图 T / N_B）：", "",
       "| t | T（本卡 22k） | N_B（本卡，1 draw） | E186 T | E186 N_B |", "|---|---|---|---|---|"]
E186 = [(.17, .14), (.17, .14), (.34, .30), (.76, .55), (1.05, .76), (1.34, .94), (1.58, 1.09), (2.35, 1.58), (2.30, 1.56)]
for t in range(NK):
    md.append(f"| {NAMES[t]} | {RA[t, t]:.2f} | {NB[t][2]:.2f} | {E186[t][0]:.2f} | {E186[t][1]:.2f} |")

# ---------------------------------------------------------------- §5 classes, §6 examples
md += ["", "## §5 token 类（mid 段 top-8；O · H · R；t = 20B / 335B / 1.34T / 5.1T；20B 与 1.34T 的 O 附 95% CI）", "",
       f"覆盖：H(e∣id) 三分位 {CL['coverage']['Hid']:.3f}，UPOS 三类 {CL['coverage']['upos_UD']:.3f}（全部 22k 中的比例）。"]
for cname, rows in CL["classes"].items():
    md += ["", f"**{cname}**", "", "| 类 | n | 20B | 335B | 1.34T | 5.1T | O@20B CI | O@1.34T CI |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cells = [" · ".join(f"{r[f'{c}_top8@{tn}']:.2f}" for c in ("O", "H", "R")) for tn in ("20B", "335B", "1.34T", "5.1T")]
        md.append(f"| {r['class']} | {r['n']} | " + " | ".join(cells) + f" | [{r['O_top8@20B_ci'][0]:.2f}, {r['O_top8@20B_ci'][1]:.2f}] | [{r['O_top8@1.34T_ci'][0]:.2f}, {r['O_top8@1.34T_ci'][1]:.2f}] |")
ex = CL["examples"]
md += ["", f"## §6 原始样例（≥ 30 次的 id：{ex['n_ids_ge30']} 个，覆盖 {ex['token_coverage']:.3f} 的 token；mid 段 top-8）"]
esc = lambda s: s.replace("|", "\\|").replace("\n", " ")
for tn in ("20B", "1.34T"):
    for kk, title in (("lowest_O", "O 最低 20"), ("highest_O", "O 最高 20"), ("R_gt_H", "R − H 最大 10"), ("H_gt_R", "H − R 最大 10")):
        md += ["", f"**{tn}：{title}**", "", "| token | n | O | H | R | 语言（前 4） | O 最低处上下文 | O 最高处上下文 |", "|---|---|---|---|---|---|---|---|"]
        for d in ex[tn][kk]:
            md.append(f"| `{esc(repr(d['str']))}` | {d['n']} | {d['O']:.2f} | {d['H']:.2f} | {d['R']:.2f} | {','.join(d['langs'])} | {esc(d['ctx_lowO'])} | {esc(d['ctx_highO'])} |")
S["classes"] = CL["classes"]; S["examples_meta"] = {"n_ids_ge30": ex["n_ids_ge30"], "coverage": ex["token_coverage"]}
open(f"{OUTD}/tables.md", "w").write("\n".join(md) + "\n")
json.dump(S, open(f"{OUTD}/summary.json", "w"), ensure_ascii=False, indent=0)

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
for fp in ["Noto Sans CJK JP", "Noto Sans CJK SC", "IPAexGothic", "TakaoGothic"]:
    from matplotlib import font_manager
    if any(fp in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fp; break
COL = {"O": "#0b0b0b", "H": "#2a78d6", "R": "#eb6834", "Hp": "#1baf7a", "Rp": "#e87ba4"}
LAB = {"O": "O observed", "H": "H: final router, hidden drift", "R": "R: final input, router drift",
       "Hp": "H′: router t, hidden drift", "Rp": "R′: input t, router drift"}
fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
x = np.array(TOKX)
for c in COMPS:
    v = np.array(S["mid"][c]["top8"])
    ax[0].plot(x, v, "-o", color=COL[c], lw=2, ms=4, label=LAB[c])
    if S["mid"][c]["top8_ci"][0]:
        cc = np.array(S["mid"][c]["top8_ci"]); ax[0].fill_between(x, cc[:, 0], cc[:, 1], color=COL[c], alpha=.15, lw=0)
for fam, ls in (("N_A", ":"), ("N_B", "--"), ("N_G", "-.")):
    ax[0].plot(x, S["mid"]["geo_" + fam]["top8"], ls, color="#888", lw=1.2, label=f"floor {fam} (shared random router)")
ax[0].set_xscale("log"); ax[0].set_xticks(x); ax[0].set_xticklabels(["20B", "83B", "335B", "587B", "838B", "1.09T", "1.34T", "5.1T", "rel"], rotation=45)
ax[0].set_ylabel("top-8 overlap with release (layers 2–11)"); ax[0].set_title("(a) decomposition vs release"); ax[0].legend(fontsize=6.5, frameon=False)
segs = list(S["adjacent"].keys()); xs = np.arange(len(segs)); w = .16
for j, c in enumerate(COMPS):
    ax[1].bar(xs + (j - 2) * w, [S["adjacent"][s][c][0] for s in segs], w * .9, color=COL[c], label=CN[c])
ax[1].set_xticks(xs); ax[1].set_xticklabels(["20B→83B", "→335B", "→587B", "→838B", "→1.09T", "→1.34T", "→5.1T", "→rel"], rotation=45)
ax[1].set_ylabel("1 − top-8 overlap (adjacent checkpoints)"); ax[1].set_title("(b) per-segment change"); ax[1].legend(fontsize=7, frameon=False)
sb = S["subspace"]
for k, colr, lab in (("in", "#eb6834", "inside readout subspace"), ("out", "#2a78d6", "outside"), ("full", "#0b0b0b", "full space")):
    ax[2].plot(x[:8], [sb[n][f"{k}_cos"] for n in NAMES[:8]], "-o", color=colr, lw=2, ms=4, label=f"cos {lab}")
    ax[2].plot(x[:8], [sb[n][f"cka_{k}"] for n in NAMES[:8]], "--", color=colr, lw=1.2, label=f"CKA {lab}")
ax[2].set_xscale("log"); ax[2].set_xticks(x[:8]); ax[2].set_xticklabels(NAMES[:8], rotation=45)
ax[2].set_title("(c) hidden-state similarity to release"); ax[2].legend(fontsize=6.5, frameon=False)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_decomp_training.png", dpi=150)

fig, ax = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
im = ax[0].imshow(RA, cmap="Blues", origin="upper")
for t in range(NK):
    for s in range(NK):
        ax[0].text(s, t, f"{RA[t, s]:.2f}", ha="center", va="center", fontsize=6.5, color="white" if RA[t, s] > 1.3 else "#0b0b0b")
lbl = ["20B", "83B", "335B", "587B", "838B", "1.09T", "1.34T", "5.1T", "rel"]
ax[0].set_xticks(range(NK)); ax[0].set_xticklabels(lbl, rotation=45); ax[0].set_yticks(range(NK)); ax[0].set_yticklabels(lbl)
ax[0].set_xlabel("hidden states from checkpoint s"); ax[0].set_ylabel("router T_t from checkpoint t")
ax[0].set_title("(a) layer 0: Î(prev id) / Î(input id)"); plt.colorbar(im, ax=ax[0], fraction=.046)
for s, colr in ((2, "#1baf7a"), (5, "#2a78d6"), (8, "#0b0b0b")):
    ax[1].plot(x, RA[:, s], "-o", color=colr, lw=2, ms=4, label=f"fixed hidden s={lbl[s]}, vary router t")
for t, colr in ((5, "#eb6834"), (8, "#e87ba4")):
    ax[1].plot(x, RA[t, :], "--s", color=colr, lw=1.5, ms=4, label=f"fixed router t={lbl[t]}, vary hidden s")
ax[1].plot(x, NB[:, 2], ":", color="#888", lw=1.5, label="diagonal, N_B random router")
ax[1].axhline(1, color="#ccc", lw=.8); ax[1].set_xscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels(lbl, rotation=45)
ax[1].set_title("(b) slices"); ax[1].legend(fontsize=6.5, frameon=False)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_l0_grid.png", dpi=150)
print("report written", OUTD)
