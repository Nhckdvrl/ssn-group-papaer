"""E187 report: tables.md, summary.json and figures from the e187_* result files (results/e187/)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
C = os.path.expanduser("~/mechpop_cache/e187")
J = lambda f: json.load(open(f"{RES}/{f}")) if os.path.exists(f"{RES}/{f}") else None
dec = J("decomp.json"); wi = J("wdrift_instruct.json"); wb = J("wdrift_base.json"); bvi = J("base_vs_instruct.json")
e182 = J("e182_base_vs_instruct.json"); e184c = J("e184_classes.json"); cor = J("e184_coroute.json"); tsc = J("toksub_classes.json")
BP = {"B1↔B2": (12, range(6, 18)), "B2↔B3": (12, range(18, 30)), "B1↔B3": (24, range(6, 18))}
REF = {"lag 1": 1, "lag 11": 11, "lag 13": 13}
out, S = [], {}
f3 = lambda x: "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"


def sel(rows, lag, ls=None, inblock=False):
    r = [x for x in rows if x["lag"] == lag and (ls is None or x["l"] in ls)]
    if inblock:
        r = [x for x in r if 6 <= x["l"] and x["m"] <= 41]
    return r


def mean(rows, k, i=None):
    v = [(x[k][i] if i is not None else x[k]) for x in rows if k in x]
    return float(np.mean(v)) if v else None


# ------------------------------------------------------------------ 1. decomposition
if dec:
    out += ["## 1. 交叉套用分解（toksub：20 语 × 1000 token，全部 48 层；主口径 = 增益归路由器）", "",
            "块对 = 三份拷贝之间；参照 = 第 6–41 层内 lag 1 / 11 / 13 的同一读数（匈牙利配对在无对应关系的层间是\"最佳对齐\"）。"
            "O = T_l(h_l) vs π T_m(h_m)；H = 同一路由器 T_l 作用于 h_l 与 g_l⊙x̂_m；R = T_l 与 T_m 作用于同一 x̂_m；R′ = 作用于同一 x̂_l。"
            "几何地板 = 同一个随机路由器作用于 x̂_l 与 x̂_m（8 draw 均值）。", "",
            "| 对 | O top-1 | H | R | R′ | O top-8 | H | R | R′ | 地板 N_A / N_B / N_G top-1 | 地板 top-8 N_A / N_B / N_G | 随机置换 top-1（p99） | token 打乱期望 top-1 |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    groups = [(n, sel(dec, lag, ls)) for n, (lag, ls) in BP.items()] + [(n, sel(dec, lag, inblock=True)) for n, lag in REF.items()]
    for n, rr in groups:
        g1 = " / ".join(f3(mean(rr, f"geo_{f}_top1", 0)) for f in ("N_A", "N_B", "N_G"))
        g8 = " / ".join(f3(mean(rr, f"geo_{f}_top8", 0)) for f in ("N_A", "N_B", "N_G"))
        out.append(f"| {n}（{len(rr)} 对） | " + " | ".join(f3(mean(rr, f"{k}_top1")) for k in ("O", "H", "R", "Rp")) + " | " +
                   " | ".join(f3(mean(rr, f"{k}_top8")) for k in ("O", "H", "R", "Rp")) +
                   f" | {g1} | {g8} | {f3(mean(rr, 'perm_floor_top1_mean'))}（{f3(mean(rr, 'perm_floor_top1_p99'))}） | {f3(mean(rr, 'chance_shuffle_top1'))} |")
        S[f"decomp_{n}"] = {k: mean(rr, k) for k in ("O_top1", "H_top1", "R_top1", "Rp_top1", "O_top8", "H_top8", "R_top8", "Rp_top8",
                                                    "H2_top1", "R2_top1", "Rp2_top1", "O_absraw_top1", "O_expert_top1",
                                                    "perm_floor_top1_mean", "chance_shuffle_top1")}
        for f in ("N_A", "N_B", "N_G"):
            S[f"decomp_{n}"][f"geo_{f}_top1"] = mean(rr, f"geo_{f}_top1", 0); S[f"decomp_{n}"][f"geo_{f}_top8"] = mean(rr, f"geo_{f}_top8", 0)
    out += ["", "副口径（增益归隐状态：原始 h 喂给另一层的 W）与专家配对稳健性（top-1）：", "",
            "| 对 | H2 | R2 | R′2 | O（|cos| 原始行配对） | O（专家权重配对） | R（专家权重配对） |", "|---|---|---|---|---|---|---|"]
    for n, rr in groups:
        out.append(f"| {n} | " + " | ".join(f3(mean(rr, k)) for k in ("H2_top1", "R2_top1", "Rp2_top1", "O_absraw_top1", "O_expert_top1", "R_expert_top1")) + " |")
    out += ["", "逐块内位置（top-1；CI = 句子聚类自助 95%；地板 = 三族 8 draw 中最大值）：", "",
            "| 块对 | l→m | O [CI] | H | R | R′ | 地板 max(N_A, N_B, N_G) | O top-8 | H top-8 | R top-8 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for n, (lag, ls) in BP.items():
        for x in sel(dec, lag, ls):
            gmax = max(x[f"geo_{f}_top1"][2] for f in ("N_A", "N_B", "N_G"))
            out.append(f"| {n} | {x['l']}→{x['m']} | {x['O_top1']:.3f} [{x['O_top1_ci'][0]:.3f}, {x['O_top1_ci'][1]:.3f}] | {x['H_top1']:.3f} | "
                       f"{x['R_top1']:.3f} | {x['Rp_top1']:.3f} | {gmax:.3f} | {x['O_top8']:.3f} | {x['H_top8']:.3f} | {x['R_top8']:.3f} |")
    pcs = [x["pc_gain_recovery_top8"] for x in dec if "pc_gain_recovery_top8" in x]
    out += ["", f"阳性对照：增益恢复 top-8 一致 {', '.join(f'{v:.4f}' for v in pcs)}（应 ≥ .99）。", ""]
    S["pc_gain_recovery_top8"] = pcs
    # figure
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for ax, (n, (lag, ls)) in zip(axs, BP.items()):
        rr = sel(dec, lag, ls); x = np.arange(len(rr))
        for k, c, lab in (("O", "k", "O observed"), ("H", "tab:blue", "H same router (hidden drift)"),
                          ("R", "tab:red", "R same input x̂_m (router drift)"), ("Rp", "tab:orange", "R′ same input x̂_l")):
            ax.plot(x, [r[f"{k}_top1"] for r in rr], "-o", ms=3, c=c, label=lab)
        for f, c in (("N_A", "0.5"), ("N_B", "0.7"), ("N_G", "0.85")):
            ax.fill_between(x, [r[f"geo_{f}_top1"][1] for r in rr], [r[f"geo_{f}_top1"][2] for r in rr], color=c, alpha=.6,
                            label=f"shared random router {f}" if n == "B1↔B2" else None)
        l1 = {r["l"]: r["O_top1"] for r in dec if r["lag"] == 1}
        ax.plot(x, [l1[r["l"]] for r in rr], ":", c="purple", label="O at lag 1 (l, l+1)" if n == "B1↔B2" else None)
        ax.set_title(f"{n}  (layers {rr[0]['l']}–{rr[-1]['l']} vs +{lag})", fontsize=9); ax.set_xlabel("position in block")
    axs[0].set_ylabel("top-1 agreement"); axs[0].legend(fontsize=6.5, loc="upper left")
    plt.tight_layout(); plt.savefig(f"{RES}/fig_decomp.png", dpi=150); plt.close()

# ------------------------------------------------------------------ 2. weights
for key, w in (("Instruct", wi), ("Base", wb)):
    if not w:
        continue
    rows = w["rows"]
    cols = [("router_cos_centred", "路由器行（中心化）"), ("router_cos_eff", "有效路由器 W·g"), ("exp_gate_cos_routermatch", "专家 gate"),
            ("exp_up_cos_routermatch", "专家 up"), ("exp_down_cos_routermatch", "专家 down"), ("exp_all_cos_expertmatch", "专家（权重配对）"),
            ("attn_q_cos", "q"), ("attn_k_cos", "k"), ("attn_v_cos", "v"), ("attn_o_cos", "o"), ("post_ln_cos", "post-ln 增益"),
            ("match_router_vs_expert", "两种配对一致比例")]
    out += [f"## 2. 权重漂移（{key}；专家为草图：gate/up 前 32 神经元行、down 前 85 输出行（缩减草图，见卡偏差记录）；余弦按配对平均）", "",
            "| 对 | " + " | ".join(c[1] for c in cols) + " | 专家未配对地板 p99 | 相对变化 路由器 / 专家 / q |", "|---|" + "---|" * (len(cols) + 2)]
    groups = [(n, sel(rows, lag, ls)) for n, (lag, ls) in BP.items()] + [(n, sel(rows, lag, inblock=True)) for n, lag in REF.items()]
    for n, rr in groups:
        out.append(f"| {n} | " + " | ".join(f3(mean(rr, c[0])) for c in cols) +
                   f" | {f3(mean(rr, 'exp_all_floor_p99'))} | {f3(mean(rr, 'router_rel'))} / {f3(mean(rr, 'exp_all_rel_routermatch'))} / {f3(mean(rr, 'attn_q_rel'))} |")
        S[f"w_{key}_{n}"] = {c[0]: mean(rr, c[0]) for c in cols}
    if os.path.exists(f"{C}/match_{key.lower()}.npz"):
        M = np.load(f"{C}/match_{key.lower()}.npz")
        idf = {n: float(np.mean([(M[f"{r['l']}_{r['m']}_router"] == np.arange(128)).mean() for r in sel(rows, lag, ls)])) for n, (lag, ls) in BP.items()}
        out += ["", "路由器配对是否就是恒等（同一专家编号）：" + "，".join(f"{n} {v:.3f}" for n, v in idf.items()), ""]
        S[f"identity_match_{key}"] = idf
    out += ["", "草图误差（gate 两个不相交神经元子集上的配对余弦）：" + "；".join(f"{k}: {v['rows0_32']:.3f} vs {v['rows640_672']:.3f}" for k, v in w["sketch_check"].items()), ""]
    # lineage: star decomposition per weight type
    out += [f"### 谱系（{key}）：三块成对余弦与三叶星形分解 a_i = √(cos_ij·cos_ik/cos_jk)（逐块内位置平均）", "",
            "| 读数 | cos(B1,B2) | cos(B2,B3) | cos(B1,B3) | a1 | a2 | a3 |", "|---|---|---|---|---|---|---|"]
    lin = {}
    for c, nm in cols[:11]:
        v12 = np.array([r[c] for r in sel(rows, 12, range(6, 18))]); v23 = np.array([r[c] for r in sel(rows, 12, range(18, 30))])
        v13 = np.array([r[c] for r in sel(rows, 24, range(6, 18))])
        with np.errstate(invalid="ignore"):
            a1 = np.sqrt(v12 * v13 / v23); a2 = np.sqrt(v12 * v23 / v13); a3 = np.sqrt(v13 * v23 / v12)
        lin[c] = dict(c12=float(v12.mean()), c23=float(v23.mean()), c13=float(v13.mean()), a1=float(np.nanmean(a1)), a2=float(np.nanmean(a2)),
                      a3=float(np.nanmean(a3)), frac_c13_lowest=float(np.mean((v13 < v12) & (v13 < v23))))
        out.append(f"| {nm} | {v12.mean():.3f} | {v23.mean():.3f} | {v13.mean():.3f} | {np.nanmean(a1):.3f} | {np.nanmean(a2):.3f} | {np.nanmean(a3):.3f} |")
    S[f"lineage_{key}"] = lin
    out.append("")
    if key == "Instruct":
        fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))
        for n, ls_ in (("B1↔B2", "-"), ("B2↔B3", "--"), ("B1↔B3", ":")):
            lag, rl = BP[n]; rr = sel(rows, lag, rl); x = np.arange(len(rr))
            for c, col in (("router_cos_centred", "k"), ("exp_gate_cos_routermatch", "tab:green"), ("exp_up_cos_routermatch", "tab:olive"),
                           ("exp_down_cos_routermatch", "tab:cyan")):
                axs[0].plot(x, [r[c] for r in rr], ls_, c=col, label=f"{c.split('_')[0]} {c.split('_')[1]} {n}" if True else None)
            for c, col in (("attn_q_cos", "tab:red"), ("attn_k_cos", "tab:orange"), ("attn_v_cos", "tab:blue"), ("attn_o_cos", "tab:purple")):
                axs[1].plot(x, [r[c] for r in rr], ls_, c=col, label=f"{c.split('_')[1]} {n}")
        r1 = sel(rows, 1, inblock=True)
        axs[0].axhline(np.mean([r["router_cos_centred"] for r in r1]), c="k", lw=.6, alpha=.5)
        axs[0].set_title("router rows / matched experts (cos)", fontsize=9); axs[1].set_title("attention projections (flattened cos)", fontsize=9)
        for a in axs:
            a.set_xlabel("position in block"); a.legend(fontsize=5, ncol=3)
        plt.tight_layout(); plt.savefig(f"{RES}/fig_wdrift.png", dpi=150); plt.close()

if bvi:
    out += ["### Base vs Instruct 同层（后训练改了多少；专家恒等对应）", "",
            "| 层段 | 路由器行 cos | 专家草图 cos | q cos | o cos | 相对变化 路由器 / 专家 / q |", "|---|---|---|---|---|---|"]
    for nm, ls in (("0–5", range(0, 6)), ("6–17", range(6, 18)), ("18–29", range(18, 30)), ("30–41", range(30, 42)), ("42–47", range(42, 48))):
        rr = [r for r in bvi if r["l"] in ls]
        out.append(f"| {nm} | {mean(rr, 'router_cos'):.4f} | {mean(rr, 'exp_all_cos'):.4f} | {mean(rr, 'attn_q_cos'):.4f} | {mean(rr, 'attn_o_cos'):.4f} | "
                   f"{mean(rr, 'router_rel'):.4f} / {mean(rr, 'exp_all_rel'):.4f} / {mean(rr, 'attn_q_rel'):.4f} |")
    out.append("")
lagt = J("base_lagtest.json")
if lagt:
    out += ["### Base 的权重 lag 检验（q/o/v 展平余弦，全部 lag 的平均；与残差笔记的 Instruct 读数同法）", "",
            "| 模型 | lag 12 q / o / v | lag 24 q / o / v | 其他 lag 的 max |cos| |", "|---|---|---|---|"]
    for k, v in lagt.items():
        out.append(f"| {k} | {v['12'][0]:.3f} / {v['12'][1]:.3f} / {v['12'][2]:.3f} | {v['24'][0]:.3f} / {v['24'][1]:.3f} / {v['24'][2]:.3f} | {v['other_max']:.4f} |")
    out.append(""); S["lagtest"] = lagt

if e182:
    out += ["## 5. Base vs Instruct 的拷贝层路由一致率（E182 同一语料 158 万 token，各自路由器行配对）", "",
            "| 对 | Instruct top-1 | Base top-1 | Instruct top-8 | Base top-8 | 逐对差 (I − B) top-1 范围 |", "|---|---|---|---|---|---|"]
    groups = [(n, sel(e182["copy"], lag, ls)) for n, (lag, ls) in BP.items()] + [(n, sel(e182["copy"], lag, inblock=True)) for n, lag in REF.items()]
    for n, rr in groups:
        d = [r["instruct_top1"] - r["base_top1"] for r in rr]
        out.append(f"| {n} | {mean(rr, 'instruct_top1'):.3f} | {mean(rr, 'base_top1'):.3f} | {mean(rr, 'instruct_top8'):.3f} | {mean(rr, 'base_top8'):.3f} | {min(d):+.3f} … {max(d):+.3f} |")
        S[f"e182_{n}"] = {k: mean(rr, k) for k in ("instruct_top1", "base_top1", "instruct_top8", "base_top8")}
    sl = e182["same_layer"]
    out += ["", "同层 Instruct vs Base 路由一致（恒等专家，参照）：" + "，".join(
        f"{nm} top-1 {np.mean([r['top1'] for r in sl if r['l'] in ls]):.3f}" for nm, ls in
        (("0–5", range(6)), ("6–41", range(6, 42)), ("42–47", range(42, 48)))), ""]

# ------------------------------------------------------------------ 3/4. classes
if e184c:
    P = e184c["pairs"]
    out += ["## 4a. 按 token 类的拷贝层一致率 O（E184 英语存储 8.6 万 token，只有路由；B1↔B2 + B2↔B3 共 24 对平均；括号 = token 数）", ""]
    pp = [p for p in P if p["lag"] == 12]; p24 = [p for p in P if p["lag"] == 24]
    S["e184_O_top1_lag12"] = float(np.mean([p["top1"] for p in pp])); S["e184_O_top1_lag24"] = float(np.mean([p["top1"] for p in p24]))
    for fld, nm in (("Hx_top1", "E185 H(e|id) 三分位（第 l 层，283 个高频 id）"), ("freq_top1", "频率五分位（本存储计数）"),
                    ("pos_top1", "位置"), ("letter_top1", "字母 / 非字母"), ("upos_top1", "UPOS（词末 token）")):
        keys = list(pp[0][fld].keys())
        out.append(f"- **{nm}**：" + "；".join(f"{k} {np.mean([p[fld][k][0] for p in pp if k in p[fld]]):.3f}（{pp[0][fld][k][1]}）" for k in keys))
        S[f"e184_{fld}"] = {k: float(np.mean([p[fld][k][0] for p in pp if k in p[fld]])) for k in keys}
    out += [f"- H(e|id) 覆盖率 {np.mean([p['Hx_coverage'] for p in pp]):.3f}；逐 id Spearman(H(e|id), id 平均一致率) 均值 {np.mean([p['spearman_Hx_vs_id_agree'] for p in pp]):.3f}"
            f"（范围 {min(p['spearman_Hx_vs_id_agree'] for p in pp):.3f} … {max(p['spearman_Hx_vs_id_agree'] for p in pp):.3f}）",
            f"- [POST-HOC] 类型层面（≥ 30 次的 id 的众数专家）一致率：lag 12 {np.mean([p['typelevel_mode_agree'] for p in pp]):.3f}，lag 24 {np.mean([p['typelevel_mode_agree'] for p in p24]):.3f}"
            f"（{pp[0]['typelevel_n_ids']} 个 id）；两层都落在各自 id 众数专家上的 token 比例 {np.mean([p['frac_tokens_both_at_id_mode'] for p in pp]):.3f}", ""]
    S["e184_typelevel"] = float(np.mean([p["typelevel_mode_agree"] for p in pp])); S["e184_spearman_Hx"] = float(np.mean([p["spearman_Hx_vs_id_agree"] for p in pp]))
if tsc:
    P = [p for p in tsc["pairs"] if p["lag"] == 12]
    out += ["## 4b. 按 token 类的 O / H / R（toksub 20 语；lag 12 的 24 对平均；括号 = token 数）", "",
            "| 类 | O | H | R | R′ |", "|---|---|---|---|---|"]
    for cn in ("letter", "pos", "freq", "script", "lang"):
        for k, n in tsc["n_by_class"][cn].items():
            out.append(f"| {cn}={k}（{n}） | " + " | ".join(f"{np.mean([p[f'{q}_t1_{cn}'][k] for p in P]):.3f}" for q in ("O", "H", "R", "Rp")) + " |")
    S["toksub_classes"] = {cn: {k: {q: float(np.mean([p[f'{q}_t1_{cn}'][k] for p in P])) for q in ("O", "H", "R", "Rp")}
                                for k in tsc["n_by_class"][cn]} for cn in ("letter", "pos", "freq", "script")}
    out.append("")
if e184c and tsc:
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.4), gridspec_kw={"width_ratios": [1, 1.4, 1.2]})
    pp = [p for p in e184c["pairs"] if p["lag"] == 12]
    for ax, fld, ttl in ((axs[0], "Hx_top1", "E184 English: by H(e|id) tertile"), (axs[1], "freq_top1", "E184 English: by frequency quintile")):
        ks = list(pp[0][fld].keys()); ax.bar(range(len(ks)), [np.mean([p[fld][k][0] for p in pp]) for k in ks], color="0.4")
        ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks, fontsize=7); ax.set_title(ttl, fontsize=9)
    axs[0].set_ylabel("O top-1 (copy pairs, lag 12)")
    P = [p for p in tsc["pairs"] if p["lag"] == 12]; ks = list(tsc["n_by_class"]["pos"].keys()) + list(tsc["n_by_class"]["letter"].keys())
    for j, (q, c) in enumerate((("O", "k"), ("H", "tab:blue"), ("R", "tab:red"))):
        v = [np.mean([p[f"{q}_t1_pos"][k] for p in P]) for k in tsc["n_by_class"]["pos"]] + [np.mean([p[f"{q}_t1_letter"][k] for p in P]) for k in tsc["n_by_class"]["letter"]]
        axs[2].bar(np.arange(len(ks)) + (j - 1) * .27, v, .27, color=c, label=q)
    axs[2].set_xticks(range(len(ks))); axs[2].set_xticklabels([f"pos {k}" for k in tsc["n_by_class"]["pos"]] + list(tsc["n_by_class"]["letter"]), fontsize=6.5, rotation=20)
    axs[2].legend(fontsize=7); axs[2].set_title("toksub (20 languages): O / H / R by class", fontsize=9)
    plt.tight_layout(); plt.savefig(f"{RES}/fig_classes.png", dpi=150); plt.close()
if cor:
    out += ["## 6. 无标签共路由相关（E184 英语存储，同 token 出现对；不依赖专家配对；与 E167/E173 的 T_ctx / T_D 同式）", "",
            "| 对 | T_ctx | T_D | 地板（类型内置换，均值 / max|·|） |", "|---|---|---|---|"]
    groups = [(n, sel(cor, lag, ls)) for n, (lag, ls) in BP.items()] + [(n, sel(cor, lag, inblock=True)) for n, lag in REF.items()]
    for n, rr in groups:
        fl = [x["T_ctx_floor"] for x in rr if "T_ctx_floor" in x]
        out.append(f"| {n} | {mean(rr, 'T_ctx'):.3f} | {mean(rr, 'T_D'):.3f} | " + (f"{np.mean([f[0] for f in fl]):.3f} / {max(f[1] for f in fl):.3f}" if fl else "—") + " |")
        S[f"coroute_{n}"] = {"T_ctx": mean(rr, "T_ctx"), "T_D": mean(rr, "T_D")}
    out.append("")
open(f"{RES}/tables.md", "w").write("# E187 结果表（`scripts/e187_report.py` 生成）\n\n" + "\n".join(out) + "\n")
json.dump(S, open(f"{RES}/summary.json", "w"), indent=1, ensure_ascii=False)
print("\n".join(out[:40]))
