"""E191 report (card: division/experiments/E191-flame-early-trajectory-decomposition.md): tables.md (all tables, no
verdict table), summary.json, fig_decomp_training.png, fig_l1_grid.png.  e189_report.py adapted: 10 checkpoints,
top-6, 8 MoE layers (Megatron 1-8; mid band 2-7), two endpoints (F = iter 5473 post-decay, F2 = iter 4860 pre-decay),
two views (eng = FLORES eng + UD, main; noneng = 19 FLORES languages, OOD).  Reads node-local e191/*.json."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = os.environ.get("E191_BASE", "/tmp/xiang_flame") + "/e191"
OUTD = sys.argv[1] if len(sys.argv) > 1 else f"{IN}/report"
os.makedirs(OUTD, exist_ok=True)
PR = json.load(open(f"{IN}/prep.json"))["report"]
ITERS = [540, 1080, 1620, 2160, 2700, 3240, 3780, 4320, 4860, 5473]
TOKX = [i * 1024 * 2048 for i in ITERS]
NAMES = [f"{t / 1e9:.2f}B" for t in TOKX]
NK, F, F2 = 10, 9, 8
COMPS = ["O", "H", "R", "Hp", "Rp"]
CN = {"O": "O", "H": "H", "R": "R", "Hp": "H′", "Rp": "R′"}
LID = lambda j: j + 1                      # store index -> Megatron layer id
VIEWS = {"eng": "主视图（FLORES eng 6000 + UD 6000 = 12,000 token）", "noneng": "副视图（19 种非英语 FLORES，各 500 = 9,500 token；分布外）"}
D = {v: json.load(open(f"{IN}/decomp_{v}.json")) for v in VIEWS if os.path.exists(f"{IN}/decomp_{v}.json")}
CL = {v: json.load(open(f"{IN}/classes_{v}.json")) for v in VIEWS if os.path.exists(f"{IN}/classes_{v}.json")}
VER = {i: json.load(open(f"/tmp/xiang_flame/verify/i{i}.json")) for i in (540, 4860, 5473) if os.path.exists(f"/tmp/xiang_flame/verify/i{i}.json")}
META = [json.load(open(p)) if os.path.exists(p := f"/tmp/xiang_flame/hidden/flame290m_i{i}/meta.json") else {"lm_loss": {"flores_eng": [float("nan")], "ud": [float("nan")]}} for i in ITERS]
md, S = [], {"positive_controls": {}, "views": {}}


def arrival(vals, chance, thr, upto):
    n = [(v - c) / (1 - c) for v, c in zip(vals, chance)]
    lx = np.log10(TOKX[:upto])
    if n[0] >= thr:
        return ("≤", TOKX[0])
    for i in range(1, upto):
        if n[i - 1] < thr <= n[i]:
            f = (thr - n[i - 1]) / (n[i] - n[i - 1]); return ("", 10 ** (lx[i - 1] + f * (lx[i] - lx[i - 1])))
    return None


fmt = lambda a: "未达" if a is None else f"{a[0]}{a[1] / 1e9:.2f}B"

# ---------------------------------------------------------------- §0 controls
pc = S["positive_controls"]
pc["lm_loss_eng"] = [[m["lm_loss"]["flores_eng"][0], m["lm_loss"]["ud"][0]] for m in META]
pc["meta_identical"] = PR["pc_meta_identical"]; pc["rebuild_inp_equal"] = PR["pc_rebuild_inp_equal"]
pc["tokenizer_md5_equal"] = PR["pc_tokenizer_md5_equal_pythia410m"]
pc["verify"] = VER
md += ["# E191 结果表：FLAME-MoE-290M 早期训练段（1.13–11.48B token）的路由分歧交叉套用分解", "",
       "卡：`division/experiments/E191-flame-early-trajectory-decomposition.md`。主口径 = 增益算进路由器；top-6；"
       "MoE 层 = Megatron 第 1–8 层（第 0 层稠密）；mid 段 = 第 2–7 层均值；括号外 top-1 一致，括号内 top-6 重合。"
       "终点 F = iter 5473（衰减后），F2 = iter 4860（衰减前，衰减从 iter 4926 起）。**本文件只列测量，不写判决表；读法在卡的结果节。**", "",
       "## §0 阳性对照", "",
       f"- 十个点 toksub_meta 逐行一致：{pc['meta_identical']}；重建 inp 相等 {pc['rebuild_inp_equal']:.3f}；分词器 md5 = pythia-410m：{pc['tokenizer_md5_equal']}；"
       f"UD 行有 UPOS 三类 {PR['ud_rows_with_upos_group']} / {PR['ud_rows']}。", "",
       "**(a1) 英语 LM loss（逐 token 平均 NLL，nats；FLORES eng dev 997 句 / UD EWT 段落）**", "",
       "| t | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK,
       "| FLORES eng | " + " | ".join(f"{x[0]:.3f}" for x in pc["lm_loss_eng"]) + " |",
       "| UD | " + " | ".join(f"{x[1]:.3f}" for x in pc["lm_loss_eng"]) + " |"]
if VER:
    md += ["", "**(a2)(a3) 映射消融与 Pythia 参照（英语合并 loss，nats）**", "", "| 检查点 | 正确映射 | qkv 按 [Q;K;V] 整块 | gate/up 对调 | 去共享专家 | Pythia-160m | Pythia-410m |", "|---|---|---|---|---|---|---|"]
    for i, v in VER.items():
        g = lambda k: f"{v[k]['all_eng']:.3f}" if k in v else "—"
        md.append(f"| iter {i} | {g('correct')} | {g('qkv_blocks')} | {g('swap_gateup')} | {g('no_shared')} | {g('ref_pythia-160m')} | {g('ref_pythia-410m')} |")

for view, R in D.items():
    LY = {int(k): v for k, v in R["layers"].items()}; L = sorted(LY); MID = [l for l in range(1, 7) if l in LY]
    mid = lambda get: float(np.mean([get(LY[l]) for l in MID]))
    cm = lambda key, t, c, i: mid(lambda r: r[key][t][c][i])
    SV = S["views"][view] = {"mid": {}, "arrival": {}, "adjacent": {}}
    md += ["", "---", "", f"# 视图：{VIEWS[view]}（N = {R['N']}）", ""]
    # controls
    selfp = [min(LY[l]["pc_self"][i] for l in L) for i in (0, 1)]
    md += [f"- 自身对 top-1 / top-6 = {selfp[0]:.3f} / {selfp[1]:.3f}；增益恢复 top-6 最小 {min(LY[l]['pc_gain_recovery_top8'] for l in L):.4f}；"
           f"匈牙利置换恢复最小 {min(LY[l]['pc_hung_perm_recovery'] for l in L):.3f}；min |g| = {R['min_abs_gain']:.3f}；id 均值覆盖 {R['idmean_coverage']:.3f}。",
           "", "**(b) fp32 重算 vs bf16 前向自身 gate 的 top-6**（每点取 8 层最小值；top-1 / top-6）：" +
           "；".join(f"{NAMES[k]} {min(LY[l]['pc_fp32_vs_bf16'][k][0] for l in L):.3f} / {min(LY[l]['pc_fp32_vs_bf16'][k][1] for l in L):.3f}" for k in range(NK)), ""]
    idr = np.array([[LY[l]["identity_rate_eff"][t] for t in range(NK)] for l in L])
    md += ["**(d) 专家编号恒等率**（有效路由器对 F 的匈牙利配对落在同编号的比例）", "", "| 层 | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
    for i, l in enumerate(L):
        md.append(f"| {LID(l)} | " + " | ".join(f"{idr[i, t]:.2f}" for t in range(NK)) + " |")
    SV["identity_rate"] = idr.tolist()
    # §1 decomposition, both endpoints
    for key, endn, upto in (("toF", "F = iter 5473（衰减后）", 9), ("to51", "F2 = iter 4860（衰减前）", 8)):
        md += ["", f"## §1 分解（终点 {endn}；mid 段；top-1（top-6 [95% 句聚类 CI]））", "",
               "| t | O | H | R | H′ | R′ | O 打乱期望 | 地板 N_A / N_B / N_G（top-6，8 draw 均值 [min,max]） |", "|---|---|---|---|---|---|---|---|"]
        mci = np.array(R["mid_ci"]) if key == "toF" else None
        SV["mid"][key] = {}
        for t in range(NK):
            row = []
            for ci_, c in enumerate(COMPS):
                a1, a8 = cm(key, t, c, 0), cm(key, t, c, 1)
                SV["mid"][key].setdefault(c, {"top1": [], "top6": []}); SV["mid"][key][c]["top1"].append(a1); SV["mid"][key][c]["top6"].append(a8)
                row.append(f"{a1:.3f}（{a8:.3f}" + (f" [{mci[t, ci_, 1, 0]:.3f}, {mci[t, ci_, 1, 1]:.3f}]" if mci is not None else "") + "）")
            ch = (cm(key, t, "O_chance", 0), cm(key, t, "O_chance", 1))
            geo = []
            for fam in ("N_A", "N_B", "N_G"):
                gk = "toF" if key == "toF" else "to51"
                arr = np.array([np.array(LY[l]["geo"][fam][gk])[:, t, 1] for l in MID])
                geo.append(f"{arr.mean():.3f} [{arr.mean(0).min():.3f}, {arr.mean(0).max():.3f}]")
                SV["mid"][key].setdefault("geo_" + fam, []).append(float(arr.mean()))
            md.append(f"| {NAMES[t]} | " + " | ".join(row) + f" | {ch[0]:.3f}（{ch[1]:.3f}） | " + " / ".join(geo) + " |")
        # arrival
        md += ["", f"到达时间（终点 {endn}；mid 段；n = (x − c)/(1 − c)，c = 打乱期望；对数 token 轴插值；只是概括）", "",
               "| 分量 | top-6 n=.5 | top-6 n=.8 | top-1 n=.5 | top-1 n=.8 |", "|---|---|---|---|---|"]
        for c in COMPS:
            row = []
            for i in (1, 0):
                vals = [cm(key, t, c, i) for t in range(upto)]; chs = [cm(key, t, c + "_chance", i) for t in range(upto)]
                for thr in (.5, .8):
                    a = arrival(vals, chs, thr, upto); SV["arrival"][f"{key}_{c}_top{6 if i else 1}_{thr}"] = a; row.append(fmt(a))
            md.append(f"| {CN[c]} | " + " | ".join(row) + " |")
    md += ["", "副口径（增益算进隐状态）mid 段 top-1（top-6），终点 F：", "", "| t | O | H | R | H′ | R′ |", "|---|---|---|---|---|---|"]
    for t in range(NK):
        md.append(f"| {NAMES[t]} | " + " | ".join(f"{cm('toF_raw', t, c, 0):.3f}（{cm('toF_raw', t, c, 1):.3f}）" for c in COMPS) + " |")
    for i, nm in ((1, "top-6"), (0, "top-1")):
        md += ["", f"**逐层 O · H · R（{nm}，终点 F）**", "", "| 层 | " + " | ".join(NAMES[:9]) + " |", "|---|" + "---|" * 9]
        for l in L:
            md.append(f"| {LID(l)} | " + " | ".join(" · ".join(f"{LY[l]['toF'][t][c][i]:.2f}" for c in ("O", "H", "R")) for t in range(9)) + " |")
    md += ["", "**逐层 H′ · R′（top-6，终点 F）**", "", "| 层 | " + " | ".join(NAMES[:9]) + " |", "|---|" + "---|" * 9]
    for l in L:
        md.append(f"| {LID(l)} | " + " | ".join(" · ".join(f"{LY[l]['toF'][t][c][1]:.2f}" for c in ("Hp", "Rp")) for t in range(9)) + " |")
    md += ["", "**逐层 O · H · R（top-6，终点 F2 = iter 4860）**", "", "| 层 | " + " | ".join(NAMES[:8]) + " |", "|---|" + "---|" * 8]
    for l in L:
        md.append(f"| {LID(l)} | " + " | ".join(" · ".join(f"{LY[l]['to51'][t][c][1]:.2f}" for c in ("O", "H", "R")) for t in range(8)) + " |")
    # per-layer arrival R vs H (F2, top-6, n=.5)
    md += ["", "**逐层到达（终点 F2，top-6，n = .5 / .8）**：R · H", "", "| 层 | R .5 | H .5 | R .8 | H .8 |", "|---|---|---|---|---|"]
    for l in L:
        r_ = []
        for thr in (.5, .8):
            for c in ("R", "H"):
                r_.append(fmt(arrival([LY[l]["to51"][t][c][1] for t in range(8)], [LY[l]["to51"][t][c + "_chance"][1] for t in range(8)], thr, 8)))
        md.append(f"| {LID(l)} | {r_[0]} | {r_[1]} | {r_[2]} | {r_[3]} |")
    # grid
    GR = np.array([[mid(lambda r: r["grid"][t][s][1]) for s in range(NK)] for t in range(NK)])
    SV["grid_mid_top6"] = GR.tolist()
    md += ["", "## §1b 全网格 G(t, s) = agree(T_t(x̂_s), T_F(x̂_F))（mid 段 top-6；行 = 路由器 t，列 = 隐状态 s）", "", "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
    for t in range(NK):
        md.append(f"| {NAMES[t]} | " + " | ".join(f"{GR[t, s]:.3f}" for s in range(NK)) + " |")
    # §2 adjacent
    md += ["", "## §2 相邻增量（t_i → t_{i+1}，以 t_{i+1} 为终点；mid 段 1 − 一致率，top-6（top-1））", "",
           "| 段 | 1−O | 1−H | 1−R | 1−H′ | 1−R′ | 地板 1−N_A / N_B / N_G（top-6） |", "|---|---|---|---|---|---|---|"]
    for i in range(NK - 1):
        vals = {c: (1 - mid(lambda r: r["adj"][i][c][1]), 1 - mid(lambda r: r["adj"][i][c][0])) for c in COMPS}
        SV["adjacent"][f"{NAMES[i]}→{NAMES[i + 1]}"] = vals
        geo = " / ".join(f"{1 - np.mean([np.array(LY[l]['geo'][fam]['adj'])[:, i, 1].mean() for l in MID]):.3f}" for fam in ("N_A", "N_B", "N_G"))
        md.append(f"| {NAMES[i]}→{NAMES[i + 1]} | " + " | ".join(f"{vals[c][0]:.3f}（{vals[c][1]:.3f}）" for c in COMPS) + f" | {geo} |")
    md += ["", "逐层相邻增量 1 − R / 1 − H（top-6）：", "", "| 层 | " + " | ".join(f"→{NAMES[i + 1]}" for i in range(NK - 1)) + " |", "|---|" + "---|" * (NK - 1)]
    for l in L:
        md.append(f"| {LID(l)} | " + " | ".join(f"{1 - LY[l]['adj'][i]['R'][1]:.2f} / {1 - LY[l]['adj'][i]['H'][1]:.2f}" for i in range(NK - 1)) + " |")
    # §3 subspace
    md += ["", "## §3 子空间：x̂_t 相对 x̂_F 的漂移，P_F（W_F·diag(g_F) 中心化行空间）内 / 外（mid 段）", "",
           "| t | 漂移 内 / 外 / 全 | cos 内 / 外 / 全 | CKA 内 / 外 / 全 | cos id 均值 全 / 内 | cos 残差 全 / 内 | CKA id 均值 全 / 内 | CKA 残差 全 / 内 | P_t·P_F 主角 cos | 能量份额 P_F / P_t / 随机 63 维（中心化） |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    SV["subspace"] = {}
    for t in range(NK):
        g = lambda k, j=None: mid(lambda r: r["subspace"][t][k] if j is None else r["subspace"][t][k][j])
        en = (mid(lambda r: r["energy"][t]["P_F"]), mid(lambda r: r["energy"][t]["P_t"]), mid(lambda r: float(np.mean(r["energy"][t]["rand"]))))
        d = {"drift": [g("in", 0), g("out", 0), g("full", 0)], "cos": [g("in", 1), g("out", 1), g("full", 1)],
             "cka": [g("cka_in"), g("cka_out"), g("cka_full")], "cos_idmean": [g("idmean_full", 1), g("idmean_in", 1)],
             "cos_resid": [g("resid_full", 1), g("resid_in", 1)], "cka_idmean": [g("cka_idmean_full"), g("cka_idmean_in")],
             "cka_resid": [g("cka_resid_full"), g("cka_resid_in")], "pa_cos": g("pa_cos_mean"), "energy": list(en)}
        SV["subspace"][NAMES[t]] = d
        j3 = lambda v: " / ".join(f"{x:.3f}" for x in v)
        md.append(f"| {NAMES[t]} | {j3(d['drift'])} | {j3(d['cos'])} | {j3(d['cka'])} | {j3(d['cos_idmean'])} | {j3(d['cos_resid'])} | {j3(d['cka_idmean'])} | {j3(d['cka_resid'])} | {d['pa_cos']:.3f} | {j3(d['energy'])} |")
    md += ["", f"id 均值分量在终点隐状态中的能量占比（mid 段）：全空间 {mid(lambda r: r['subspace'][F]['energy_idmean_full']):.3f}，子空间内 {mid(lambda r: r['subspace'][F]['energy_idmean_in']):.3f}。"]
    # §4 grids
    l1 = LY[0]
    RA = np.array(l1["l0_grid"]["ratio"]); SP = np.array(l1["l0_grid"]["share_prev"]); SI = np.array(l1["l0_grid"]["share_inp"]); NB = np.array(l1["l0_NB_diag"])
    SV["l1"] = {"ratio": RA.tolist(), "share_prev": SP.tolist(), "share_inp": SI.tolist(), "NB_diag": NB.tolist()}
    md += ["", "## §4 第 1 层（第一个 MoE 层）10 × 10 网格：Î(top-1; 前一 id) / Î(top-1; 输入 id)（行 = 路由器 T_t，列 = 隐状态 x̂_s）", "", "| t \\ s | " + " | ".join(NAMES) + " |", "|---|" + "---|" * NK]
    for t in range(NK):
        md.append(f"| {NAMES[t]} | " + " | ".join(f"{RA[t, s]:.2f}" for s in range(NK)) + " |")
    md += ["", "前一 id 份额 / 输入 id 份额（对角线）与 N_B 型随机路由器对角线比值：", "", "| t | 前一 id 份额 | 输入 id 份额 | 比值 T | 比值 N_B |", "|---|---|---|---|---|"]
    for t in range(NK):
        md.append(f"| {NAMES[t]} | {SP[t, t]:.3f} | {SI[t, t]:.3f} | {RA[t, t]:.2f} | {NB[t][2]:.2f} |")
    md += ["", "**各 MoE 层的同一比值网格**：对角线 / 固定隐状态 = F 换路由器 t / 固定路由器 = F 换隐状态 s", "", "| 层 | 切片 | " + " | ".join(NAMES) + " |", "|---|---|" + "---|" * NK]
    SV["grid_ratio_layers"] = {}
    for l in L:
        G_ = np.array(LY[l]["grid_ratio"]); SV["grid_ratio_layers"][LID(l)] = G_.tolist()
        for nm, v in (("对角线", np.diag(G_)), ("s=F 换 t", G_[:, F]), ("t=F 换 s", G_[F, :])):
            md.append(f"| {LID(l)} | {nm} | " + " | ".join(f"{x:.2f}" for x in v) + " |")
    # §5 classes / §6 examples
    if view in CL:
        C = CL[view]
        md += ["", "## §5 token 类（mid 段 top-6；O · H · R；t = 1.13B / 3.40B / 5.66B / 10.19B；1.13B 与 5.66B 的 O 附 95% CI）", "", f"覆盖：{C['coverage']}"]
        for cname, rows in C["classes"].items():
            md += ["", f"**{cname}**", "", "| 类 | n | 1.13B | 3.40B | 5.66B | 10.19B | O@1.13B CI | O@5.66B CI |", "|---|---|---|---|---|---|---|---|"]
            for r in rows:
                cells = [" · ".join(f"{r[f'{c}_top8@{tn}']:.2f}" for c in ("O", "H", "R")) for tn in ("1.13B", "3.40B", "5.66B", "10.19B")]
                md.append(f"| {r['class']} | {r['n']} | " + " | ".join(cells) + f" | [{r['O_top8@1.13B_ci'][0]:.2f}, {r['O_top8@1.13B_ci'][1]:.2f}] | [{r['O_top8@5.66B_ci'][0]:.2f}, {r['O_top8@5.66B_ci'][1]:.2f}] |")
        ex = C["examples"]; esc = lambda s: s.replace("|", "\\|").replace("\n", " ")
        md += ["", f"## §6 原始样例（≥ 30 次的 id：{ex['n_ids_ge30']} 个，覆盖 {ex['token_coverage']:.3f}；mid 段 top-6）"]
        for tn in ("1.13B", "5.66B"):
            for kk, title in (("lowest_O", "O 最低 20"), ("highest_O", "O 最高 20"), ("R_gt_H", "R − H 最大 10"), ("H_gt_R", "H − R 最大 10")):
                md += ["", f"**{tn}：{title}**", "", "| token | n | O | H | R | O 最低处上下文 | O 最高处上下文 |", "|---|---|---|---|---|---|---|"]
                for d in ex[tn][kk]:
                    md.append(f"| `{esc(repr(d['str']))}` | {d['n']} | {d['O']:.2f} | {d['H']:.2f} | {d['R']:.2f} | {esc(d['ctx_lowO'])} | {esc(d['ctx_highO'])} |")
        SV["classes"] = C["classes"]
open(f"{OUTD}/tables.md", "w").write("\n".join(md) + "\n")
json.dump(S, open(f"{OUTD}/summary.json", "w"), ensure_ascii=False, indent=0)

# ---------------------------------------------------------------- figures (main view)
SV = S["views"]["eng"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
COL = {"O": "#0b0b0b", "H": "#2a78d6", "R": "#eb6834", "Hp": "#1baf7a", "Rp": "#e87ba4"}
LAB = {"O": "O observed", "H": "H: endpoint router, hidden drift", "R": "R: endpoint input, router drift",
       "Hp": "H′: router t, hidden drift", "Rp": "R′: input t, router drift"}
x = np.array(TOKX) / 1e9
fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
for c in COMPS:
    ax[0].plot(x[:8], SV["mid"]["to51"][c]["top6"][:8], "-o", color=COL[c], lw=2, ms=4, label=LAB[c])
for fam, ls in (("N_A", ":"), ("N_B", "--"), ("N_G", "-.")):
    ax[0].plot(x[:8], SV["mid"]["to51"]["geo_" + fam][:8], ls, color="#888", lw=1.2, label=f"floor {fam}")
ax[0].set_xlabel("training tokens (B)"); ax[0].set_ylabel("top-6 overlap with iter 4860 (layers 2–7)")
ax[0].set_title("(a) decomposition vs pre-decay endpoint"); ax[0].legend(fontsize=6.5, frameon=False)
segs = list(SV["adjacent"].keys()); xs = np.arange(len(segs)); w = .16
for j, c in enumerate(COMPS):
    ax[1].bar(xs + (j - 2) * w, [SV["adjacent"][s][c][0] for s in segs], w * .9, color=COL[c], label=CN[c])
ax[1].set_xticks(xs); ax[1].set_xticklabels([s.split("→")[1] for s in segs], rotation=45)
ax[1].set_ylabel("1 − top-6 overlap (adjacent)"); ax[1].set_title("(b) per-segment change (→ checkpoint)"); ax[1].legend(fontsize=7, frameon=False)
sb = SV["subspace"]
for k, colr, lab in ((0, "#eb6834", "inside readout subspace"), (1, "#2a78d6", "outside"), (2, "#0b0b0b", "full")):
    ax[2].plot(x[:9], [sb[n]["cos"][k] for n in NAMES[:9]], "-o", color=colr, lw=2, ms=4, label=f"cos {lab}")
    ax[2].plot(x[:9], [sb[n]["cka"][k] for n in NAMES[:9]], "--", color=colr, lw=1.2, label=f"CKA {lab}")
ax[2].set_xlabel("training tokens (B)"); ax[2].set_title("(c) hidden-state similarity to iter 5473"); ax[2].legend(fontsize=6.5, frameon=False)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_decomp_training.png", dpi=150)

RA = np.array(SV["l1"]["ratio"]); NB = np.array(SV["l1"]["NB_diag"])
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
im = ax[0].imshow(RA, cmap="Blues", origin="upper")
for t in range(NK):
    for s in range(NK):
        ax[0].text(s, t, f"{RA[t, s]:.2f}", ha="center", va="center", fontsize=6, color="white" if RA[t, s] > .7 * RA.max() else "#0b0b0b")
lbl = [n.replace("B", "") for n in NAMES]
ax[0].set_xticks(range(NK)); ax[0].set_xticklabels(lbl, rotation=45); ax[0].set_yticks(range(NK)); ax[0].set_yticklabels(lbl)
ax[0].set_xlabel("hidden states from checkpoint s (B tokens)"); ax[0].set_ylabel("router T_t from checkpoint t")
ax[0].set_title("(a) MoE layer 1: Î(prev id) / Î(input id)"); plt.colorbar(im, ax=ax[0], fraction=.046)
for s, colr in ((0, "#1baf7a"), (4, "#2a78d6"), (9, "#0b0b0b")):
    ax[1].plot(x, RA[:, s], "-o", color=colr, lw=2, ms=4, label=f"fixed hidden s={lbl[s]}B, vary router t")
for t, colr in ((0, "#eb6834"), (9, "#e87ba4")):
    ax[1].plot(x, RA[t, :], "--s", color=colr, lw=1.5, ms=4, label=f"fixed router t={lbl[t]}B, vary hidden s")
ax[1].plot(x, NB[:, 2], ":", color="#888", lw=1.5, label="diagonal, N_B random router")
ax[1].set_xlabel("training tokens (B)"); ax[1].set_title("(b) slices"); ax[1].legend(fontsize=6.5, frameon=False)
fig.tight_layout(); fig.savefig(f"{OUTD}/fig_l1_grid.png", dpi=150)
print("report written", OUTD)
