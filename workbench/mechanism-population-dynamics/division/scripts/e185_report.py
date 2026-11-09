"""E185 report: tables.md, tables_layers.md, summary.json, figures.  Card: division/experiments/E185-routing-variance-atlas.md"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import BANDS, NAMES, jdump  # noqa: E402

A = os.path.expanduser("~/mechpop_cache/atlas_e185")
RES = os.path.join(os.path.dirname(__file__), "..", "results", "e185")
M3 = ["qwen3", "gptoss", "olmoe"]
M4 = ["qwen3", "qwen3base", "gptoss", "olmoe"]


def load(data, m):
    p = f"{A}/{data}_{m}.npz"
    if not os.path.exists(p):
        return None, None
    return dict(np.load(p)), json.load(open(f"{A}/{data}_{m}.json"))


def segs(m, L):
    edge, mid = BANDS[m]
    e1 = [l for l in edge if l < L // 2]
    e2 = [l for l in edge if l >= L // 2]
    return {"edge-early": e1, "mid": mid, "edge-late": e2, "last": [L - 1]}


def share(a):
    """a: [L, R, 4] -> share = I_hat / H(e)."""
    return a[..., 0] / a[..., 3]


summary = {"gpu_hours": 0}
md, mdl = [], []
P = md.append

# ------------------------------------------------------------------ D184
P("# E185 结果表（自动生成：scripts/e185_report.py）\n")
P("份额 = Î(e; X) / H(e)：e = top-1 专家；Î = plug-in 互信息减去置换地板（3 次，同一组置换用于所有路由器 / 层）；"
  "条件量 Î(e; X | S) 的地板在每个 S 层内置换 X。T = 训练路由器；N_B = 负载匹配 N1 零模型、N_A = Haar 旋转零模型"
  "（D184：各 8 draws 的均值 [min, max]；D180：各 1 个 draw）。层段：edge-early / mid / edge-late 沿用 E179–E182；"
  "last = 末层。逐层全表见 `tables_layers.md`。\n")
FAC184 = ["inp", "prev", "nxt", "pred", "pos", "seq", "corpus", "upos"]
NEST184 = ["prev|inp", "nxt|inp", "pred|inp", "pos|inp", "seq|inp", "corpus|inp", "upos|inp", "inp|pred", "inp|prev",
           "nxt|pred", "pred|nxt", "pred|inp,prev", "pos|inp,prev"]
LABEL = {"inp": "输入 id", "prev": "前一 id", "nxt": "真实下一 id", "pred": "预测下一 id", "pos": "位置", "seq": "序列（句 / 段）",
         "corpus": "语料 FLORES/UD", "upos": "UPOS（UD 词末）", "side": "语侧", "lang": "语言", "script": "文字",
         "sid": "平行句 id（内容）", "inst": "句实例（语侧×句）", "cls": "token 类别"}


def lab(k):
    if "|" in k:
        x, s = k.split("|")
        return f"{'、'.join(LABEL.get(t, t) for t in x.split(','))} ∣ {'、'.join(LABEL.get(t, t) for t in s.split(','))}"
    return LABEL.get(k, k)


s184 = {}
P("## 1. D184 英语图谱（FLORES dev + UD EWT，T / 8 N_A / 8 N_B）\n")
for m in M3:
    r, info = load("d184", m)
    if r is None:
        P(f"**{NAMES[m]}：缺**\n")
        continue
    L = info["L"]
    sg = segs(m, L)
    s184[m] = {}
    P(f"### {NAMES[m]}（L = {L}，E = {info['E']}，K = {info['K']}；token {info['views']['full']}）\n")
    P("| 量 | 层段 | 份额 T | N_B 均值 [min, max] | N_A 均值 | T − N_B | T 在 N_B 范围外的层 (上/下) | 半分同号 |")
    P("|---|---|---|---|---|---|---|---|")
    for kind, facs in (("marg", FAC184), ("cond", NEST184)):
        for f in facs:
            key = f"full|{kind}|{f}"
            if key not in r:
                continue
            S = share(r[key])
            T, B, Aa = S[:, 0], S[:, 9:17], S[:, 1:9]
            above = (T > B.max(1)).sum()
            below = (T < B.min(1)).sum()
            hs = None
            if f"h0|{kind}|{f}" in r:
                d0 = share(r[f"h0|{kind}|{f}"])
                d1 = share(r[f"h1|{kind}|{f}"])
                g0 = d0[:, 0] - d0[:, 9:].mean(1)
                g1 = d1[:, 0] - d1[:, 9:].mean(1)
                hs = float((np.sign(g0) == np.sign(g1)).mean())
            s184[m][f"{kind}:{f}"] = {"T": T.tolist(), "NB": B.mean(1).tolist(), "NBmin": B.min(1).tolist(),
                                      "NBmax": B.max(1).tolist(), "NA": Aa.mean(1).tolist(),
                                      "above": int(above), "below": int(below), "half_sign_agree": hs,
                                      "bits_T": r[key][:, 0, 0].tolist(), "bits_NB": r[key][:, 9:, 0].mean(1).tolist()}
            first = True
            for sn, ls in sg.items():
                P(f"| {lab(f) if first else ''} | {sn} | {T[ls].mean():.3f} | {B[ls].mean(1).mean():.3f} "
                  f"[{B[ls].min(1).mean():.3f}, {B[ls].max(1).mean():.3f}] | {Aa[ls].mean():.3f} | "
                  f"{(T[ls] - B[ls].mean(1)).mean():+.3f} | {above if first else ''}{'/' + str(below) if first else ''} |"
                  f" {'' if hs is None or not first else f'{hs:.2f}'} |")
                first = False
    He = r["full|marg|inp"][:, :, 3]
    P(f"\nH(e)（bit，层段均值）T / N_B / N_A："
      + "；".join(f"{sn} {He[ls, 0].mean():.2f} / {He[ls, 9:].mean():.2f} / {He[ls, 1:9].mean():.2f}"
                  for sn, ls in sg.items()) + f"（log2 E = {np.log2(info['E']):.2f}）。")
    cov = info["cov"]
    P(f"条件层覆盖（落在出现 ≥ 2 次的层里的 token 比例）：输入 id {cov['full|prev|inp']:.3f}；"
      f"（输入, 前一）{cov['full|pred|inp,prev']:.3f}；UD 词末输入 id {cov['full|upos|inp']:.3f}。\n")
    # top-k slot version
    P("完整 top-k（槽位）版 vs top-1 版，mid 段份额 T − N_B：" + "；".join(
        f"{lab(f)} {(share(r[f'full|smarg|{f}'])[sg['mid'], 0] - share(r[f'full|smarg|{f}'])[sg['mid'], 9:].mean(1)).mean():+.3f}"
        f" / {(share(r[f'full|marg|{f}'])[sg['mid'], 0] - share(r[f'full|marg|{f}'])[sg['mid'], 9:].mean(1)).mean():+.3f}"
        for f in ["inp", "pred", "seq", "upos"]) + "；嵌套 " + "；".join(
        f"{lab(f)} {(share(r[f'full|scond|{f}'])[sg['mid'], 0] - share(r[f'full|scond|{f}'])[sg['mid'], 9:].mean(1)).mean():+.3f}"
        f" / {(share(r[f'full|cond|{f}'])[sg['mid'], 0] - share(r[f'full|cond|{f}'])[sg['mid'], 9:].mean(1)).mean():+.3f}"
        for f in ["pred|inp", "prev|inp", "seq|inp", "upos|inp"]) + "（槽位 / top-1）。\n")
    # floor noise
    fsd = np.nanmax(np.stack([r[k][..., 2] for k in r if k.startswith("full|")]))
    P(f"置换地板标准差最大值（全部格）：{fsd:.4f} bit。\n")
    s184[m]["floor_sd_max"] = float(fsd)
    # layer table
    mdl.append(f"## D184 {NAMES[m]}：逐层份额（T / N_B 均值 / N_A 均值）\n")
    cols = [f for f in FAC184] + [f for f in NEST184 if f"full|cond|{f}" in r]
    mdl.append("| 层 | " + " | ".join(lab(c) for c in cols) + " |")
    mdl.append("|---|" + "---|" * len(cols))
    for l in range(L):
        row = []
        for c in cols:
            S = share(r[f"full|{'cond' if '|' in c else 'marg'}|{c}"])
            row.append(f"{S[l, 0]:.3f} / {S[l, 9:].mean():.3f} / {S[l, 1:9].mean():.3f}")
        mdl.append(f"| {l} | " + " | ".join(row) + " |")
    mdl.append("")
summary["d184"] = s184

# ------------------------------------------------------------------ cross-fitted G_freq (补登记 2)
P("## 1b. 给定输入 id 之后：交叉拟合条件预测信息 G_freq(X ∣ 输入)（bit / token；补登记 2 的报告量）\n")
P("只在训练折出现 ≥ 20 次的输入 id 上评估（约一半 token）；序列前 / 后半两折；对数线性组合、w 交叉选取。"
  "阳性对照（`pc_crossfit.json`）：强效应恢复 .33–1.2、弱高基数效应（≈ .08 bit）恢复 0 → **G_freq 是下界，"
  "≈ 0 只表示低于约 .08 bit 的检测限**；回退对照（X = 输入 id 的粗分类）G_freq = 0。"
  "格 = T / N_B 均值 [min, max] / N_A 均值；末列 = T 高于 / 低于 N_B 全部 draw 的层数。\n")
scf = {}
for data, facs, title in (("d184", ["seq", "prev", "pred", "nxt", "pos", "corpus", "upos"], "D184 英语"),
                          ("d180", ["sid", "inst", "pred", "lang", "script"], "D180 20 语侧（N_B0 / N_A0 单 draw）")):
    P(f"### {title}\n")
    P("| 模型 | X | edge-early | mid | edge-late | last | 高 / 低层数 | G(输入) mid T / N_B |")
    P("|---|---|---|---|---|---|---|---|")
    for m in M3:
        p = f"{A}/cf_{data}_{m}.npz"
        if not os.path.exists(p):
            P(f"| {NAMES[m]} | 缺 | | | | | | |")
            continue
        r = dict(np.load(p))
        info = json.load(open(f"{A}/cf_{data}_{m}.json"))
        rn = info["routers"]
        L = info["L"]
        sg = segs(m, L)
        iT = rn.index("T")
        iB = list(range(9, 17)) if data == "d184" else [rn.index("N_B0")]
        iA = list(range(1, 9)) if data == "d184" else [rn.index("N_A0")]
        for f in facs:
            G = r[f][..., 3]
            T, B, Aa = G[:, iT], G[:, iB], G[:, iA]
            cells = []
            for sn, ls in sg.items():
                cells.append(f"{T[ls].mean():.3f} / {B[ls].mean():.3f} [{B[ls].min(1).mean():.3f}, {B[ls].max(1).mean():.3f}] / {Aa[ls].mean():.3f}")
            hi, lo = int((T > B.max(1)).sum()), int((T < B.min(1)).sum())
            gi = r[f][..., 0]
            P(f"| {NAMES[m]} | {lab(f)} | " + " | ".join(cells) + f" | {hi} / {lo} (of {L}) | {gi[sg['mid'], iT].mean():.2f} / {gi[sg['mid']][:, iB].mean():.2f} |")
            scf[f"{data}:{m}:{f}"] = {"T": T.tolist(), "NB": B.mean(1).tolist(), "NBmin": B.min(1).tolist(),
                                      "NBmax": B.max(1).tolist(), "NA": Aa.mean(1).tolist(), "hi": hi, "lo": lo,
                                      "frac_freq": float(np.nanmean(r[f][..., 4]))}
    P("")
summary["crossfit_Gfreq"] = scf
pcf = f"{RES}/pc_crossfit.json"
if os.path.exists(pcf):
    pc = json.load(open(pcf))
    P("阳性对照（合成专家，OLMoE D184 的真实 (输入, X) 联合）：" + "；".join(
        f"{k}: 真值 {v['true']:.3f}，G_freq {v.get('G_freq', float('nan')):.3f}" + (f"（plug-in Î 恢复 {v['plugin_hat_ratio']:.2f}）" if 'plugin_hat_ratio' in v else "")
        for k, v in pc.items()) + "。\n")

# residual (a) strata from the atlas
P("## 2. 残差 (a)：E184 \"下一 token 低于零模型\" 在图谱里的位置\n")
P("Î 单位 bit（不归一）。ΔÎ = Î(预测下一) − Î(输入)（E184 ΔG 的同向量）；条件量见列名。N_B 为 8-draw 均值 [min, max]。\n")
P("| 模型 | 层 | 子集 | Î(输入) T / N_B | Î(预测下一) T / N_B | ΔÎ T / N_B [min, max] | Î(预测下一∣输入) T / N_B [min, max] | Î(输入∣预测下一) T / N_B |")
P("|---|---|---|---|---|---|---|---|")
sa = {}
for m in M3:
    r, info = load("d184", m)
    if r is None:
        continue
    L = info["L"]
    sa[m] = {}
    for l in (L // 2, L - 1):
        for tag, sfx in (("全部", ""), ("预测正确", "@corr"), ("预测错误", "@wrong"), ("低频输入", "@f0"), ("中频", "@f1"),
                         ("高频输入", "@f2")):
            gi = r[f"full|marg|inp{sfx}"][l, :, 0]
            gp = r[f"full|marg|pred{sfx}"][l, :, 0]
            cpi = r[f"full|cond|pred|inp{sfx}"][l, :, 0]
            cip = r[f"full|cond|inp|pred{sfx}"][l, :, 0]
            d = gp - gi
            P(f"| {NAMES[m]} | {l} | {tag} | {gi[0]:.3f} / {gi[9:].mean():.3f} | {gp[0]:.3f} / {gp[9:].mean():.3f} | "
              f"{d[0]:+.3f} / {d[9:].mean():+.3f} [{d[9:].min():+.3f}, {d[9:].max():+.3f}] | {cpi[0]:.3f} / "
              f"{cpi[9:].mean():.3f} [{cpi[9:].min():.3f}, {cpi[9:].max():.3f}] | {cip[0]:.3f} / {cip[9:].mean():.3f} |")
            sa[m][f"{l}{sfx}"] = dict(inp=[gi[0], gi[9:].mean()], pred=[gp[0], gp[9:].mean()], dI=[d[0], d[9:].mean(), d[9:].min(), d[9:].max()],
                                      pred_given_inp=[cpi[0], cpi[9:].mean(), cpi[9:].min(), cpi[9:].max()],
                                      inp_given_pred=[cip[0], cip[9:].mean()])
    # layer counts
    gi = r["full|marg|inp"][:, :, 0]
    gp = r["full|marg|pred"][:, :, 0]
    cpi = r["full|cond|pred|inp"][:, :, 0]
    d = gp - gi
    nb_below = int(((d[:, 0] < d[:, 9:].min(1)) & (d[:, 0] < d[:, 1:9].min(1))).sum())
    c_above = int((cpi[:, 0] > cpi[:, 9:].max(1)).sum())
    c_below = int((cpi[:, 0] < cpi[:, 9:].min(1)).sum())
    sa[m]["layers_dI_below_both"] = nb_below
    sa[m]["layers_pred_given_inp_above_NB"] = c_above
    sa[m]["layers_pred_given_inp_below_NB"] = c_below
    P(f"| {NAMES[m]} | 全层 | 计数 | ΔÎ 低于两族全部 draw 的层 {nb_below}/{L}（E184 ΔG below 层：Qwen3 40/48、GPT-OSS 16/24、OLMoE 14/16） | "
      f"Î(预测下一∣输入) T 高于 N_B 全部 draw 的层 {c_above}/{L}，低于 {c_below}/{L} | | | |")
summary["residual_a_strata"] = sa
P("")
for m in M3:
    p = f"{RES}/res_a_{m}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    P(f"**{NAMES[m]} 逐输入 id 分解 Î(预测下一∣输入) = Σ_x p(x)·Î(e; 预测下一∣输入 = x)（逐 id 地板校正）：**\n")
    for l, v in d["layers"].items():
        P(f"- 层 {l}：Σ T {v['sum_T']:.3f}、N_B {v['sum_NB']:.3f}（draws {min(v['sum_NB_draws']):.3f}–{max(v['sum_NB_draws']):.3f}）、"
          f"N_A {v['sum_NA']:.3f} bit；T − N_B 的正贡献合计 {v['sum_pos_diff']:+.3f}、负贡献 {v['sum_neg_diff']:+.3f}；"
          f"逐 token 差与 log 频次 Spearman {v['spearman_diff_per_token_vs_logfreq']:.2f}。")
        rows = v["most_negative_then_positive"]
        neg = "、".join(f"`{x['str']!r}`（n {x['n']}，T {x['T']*1e3:.2f} vs N_B {x['N_B']*1e3:.2f} mbit）" for x in rows[:6])
        pos = "、".join(f"`{x['str']!r}`（n {x['n']}，T {x['T']*1e3:.2f} vs N_B {x['N_B']*1e3:.2f}；后接 "
                        + "/".join(repr(a) for a, _ in x["top_preds"][:3]) + "）" for x in rows[12:18])
        P(f"  - T < N_B 最多：{neg}")
        P(f"  - T > N_B 最多：{pos}")
    P("")

# ------------------------------------------------------------------ D180 / D182 multilingual maps
FACML = ["inp", "side", "lang", "script", "sid", "inst", "prev", "pred", "nxt", "pos", "cls"]
NESTML = ["side|inp", "lang|inp", "script|inp", "lang|inp,script", "script|inp,lang", "sid|inp", "inst|inp",
          "prev|inp", "pred|inp", "nxt|inp", "pos|inp"]
P("## 3. 多语图谱：D180（FLORES dev 20 语侧，T / N_A0 / N_B0 单 draw）\n")
s180 = {}
for m in M3:
    r, info = load("d180", m)
    if r is None:
        P(f"**{NAMES[m]}：缺**\n")
        continue
    L = info["L"]
    sg = segs(m, L)
    rn = info["routers"]
    iT, iA, iB = rn.index("T"), rn.index("N_A0"), rn.index("N_B0")
    s180[m] = {}
    P(f"### {NAMES[m]}（token {info['views']['full']}；LET {info['views']['LET']}、NON {info['views']['NON']}）\n")
    P("| 视图 | 量 | edge-early T / N_B0 / N_A0 | mid T / N_B0 / N_A0 | edge-late T / N_B0 / N_A0 | last T / N_B0 | T>N_B0 层 |")
    P("|---|---|---|---|---|---|---|")
    for vn in ("full", "LET", "NON"):
        for kind, facs in (("marg", FACML), ("cond", NESTML)):
            for f in facs:
                key = f"{vn}|{kind}|{f}"
                if key not in r:
                    continue
                S = share(r[key])
                cells = []
                for sn, ls in sg.items():
                    if sn == "last":
                        cells.append(f"{S[ls, iT].mean():.3f} / {S[ls, iB].mean():.3f}")
                    else:
                        cells.append(f"{S[ls, iT].mean():.3f} / {S[ls, iB].mean():.3f} / {S[ls, iA].mean():.3f}")
                P(f"| {vn} | {lab(f)} | " + " | ".join(cells) + f" | {(S[:, iT] > S[:, iB]).sum()}/{L} |")
                s180[m][f"{vn}:{kind}:{f}"] = {"T": S[:, iT].tolist(), "NB": S[:, iB].tolist(), "NA": S[:, iA].tolist(),
                                               "bits_T": r[key][:, iT, 0].tolist(), "bits_NB": r[key][:, iB, 0].tolist()}
    P("")
summary["d180"] = s180

P("## 4. 多语图谱：D182（FLORES devtest 22 语侧，只有 T；四模型含 Qwen3-Base）\n")
s182 = {}
P("| 模型 | 视图 | 量 | edge-early | mid | edge-late | last |")
P("|---|---|---|---|---|---|---|")
for m in M4:
    r, info = load("d182", m)
    if r is None:
        P(f"| {NAMES[m]} | 缺 | | | | | |")
        continue
    L = info["L"]
    sg = segs(m, L)
    s182[m] = {}
    for vn in ("full", "LET", "NON"):
        for kind, facs in (("marg", FACML), ("cond", NESTML)):
            for f in facs:
                key = f"{vn}|{kind}|{f}"
                if key not in r:
                    continue
                S = share(r[key])[:, 0]
                P(f"| {NAMES[m]} | {vn} | {lab(f)} | " + " | ".join(f"{S[ls].mean():.3f}" for ls in sg.values()) + " |")
                s182[m][f"{vn}:{kind}:{f}"] = S.tolist()
if "qwen3" in s182 and "qwen3base" in s182:
    a = np.array([s182["qwen3"][k] for k in s182["qwen3"] if k in s182["qwen3base"]])
    b = np.array([s182["qwen3base"][k] for k in s182["qwen3"] if k in s182["qwen3base"]])
    cc = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
    md_ = float(np.abs(a - b).max())
    P(f"\nQwen3 Instruct vs Base：全部（视图 × 量 × 层）格份额相关 {cc:.4f}，最大绝对差 {md_:.3f}。\n")
    summary["qwen3_inst_vs_base"] = {"corr": cc, "maxabs": md_}
summary["d182"] = s182

# aggregated nulls
P("## 5. 语言因子上的零模型（D182 聚合计数，T vs 8 N_A / 8 N_B）\n")
P("Î_slot(e; 标签)：按（语侧, 句）的 top-k 槽位计数（E182 均衡抽样 token）；地板 = 每句内置换语侧标签 3 次。单位 bit。"
  "格 = T / N_B 均值 [min, max] / N_A 均值。\n")
P("| 模型 | 组 | 类别 | 标签 | edge-early | mid | edge-late |")
P("|---|---|---|---|---|---|---|")
sn_ = {}
for m in M4:
    p = f"{RES}/res_nullagg_{m}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    sn_[m] = {}
    for g, gd in d["groups"].items():
        for c, cd in gd.items():
            for k, arr in cd.items():
                a = np.array(arr)[..., 0]           # [L, 17]
                L = a.shape[0]
                sg = segs(m, L)
                cells = []
                for snm in ("edge-early", "mid", "edge-late"):
                    ls = sg[snm]
                    B = a[ls][:, 9:].mean(0)
                    cells.append(f"{a[ls, 0].mean():.4f} / {B.mean():.4f} [{B.min():.4f}, {B.max():.4f}] / {a[ls][:, 1:9].mean():.4f}")
                P(f"| {NAMES[m]} | {g} | {c} | {LABEL.get(k, k)} | " + " | ".join(cells) + " |")
                sn_[m][f"{g}:{c}:{k}"] = {"T": a[:, 0].tolist(), "NB": a[:, 9:].mean(1).tolist(),
                                         "NBmin": a[:, 9:].min(1).tolist(), "NBmax": a[:, 9:].max(1).tolist(),
                                         "NA": a[:, 1:9].mean(1).tolist()}
summary["nullagg"] = sn_
P("")

# ------------------------------------------------------------------ token context dependence
P("## 6. token id 的上下文依赖度 H(e ∣ id)（等 n = 30，5 次子样本；bit；上限 log2 30 = 4.91）\n")
stok = {}
for data in ("d184", "d180"):
    for m in M3:
        p = f"{RES}/tok_{data}_{m}.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        stok[f"{data}:{m}"] = {k: d[k] for k in ("n_ids", "token_coverage", "overall", "categories", "spearman_H_logfreq",
                                                   "spearman_T_NB_over_ids", "layer_profile")}
        P(f"### {data.upper()} {NAMES[m]}：{d['n_ids']} 个 id（覆盖 {d['token_coverage']:.0%} 的 token），mid 段 {d['mid_band']}\n")
        o = d["overall"]
        P(f"全部：T {o['T']:.2f}、N_B {o['N_B']:.2f}、N_A {o['N_A']:.2f}（T − N_B {o['T_minus_NB']:+.2f}）；末层 T {o['T_last']:.2f} / N_B {o['NB_last']:.2f}。"
          f"Spearman(H, log 频次) T {d['spearman_H_logfreq']['T']:.2f} / N_B {d['spearman_H_logfreq']['N_B']:.2f}；"
          f"逐 id Spearman(H_T, H_NB) {d['spearman_T_NB_over_ids']:.2f}。\n")
        P("| 类型 | n | T | N_B | N_A | T − N_B | 末层 T / N_B |")
        P("|---|---|---|---|---|---|---|")
        for k, v in d["categories"].items():
            P(f"| {k} | {v['n']} | {v['T']:.2f} | {v['N_B']:.2f} | {v['N_A']:.2f} | {v['T_minus_NB']:+.2f} | {v['T_last']:.2f} / {v['NB_last']:.2f} |")
        if data == "d184":
            for key, title in (("most_context_dependent", "最依赖上下文"), ("least_context_dependent", "最不依赖上下文"),
                               ("T_more_lexical_than_NB", "T 比 N_B 更'查表'（H_T − H_NB 最负）"),
                               ("T_more_contextual_than_NB", "T 比 N_B 更依赖上下文（H_T − H_NB 最正）")):
                P(f"\n**{title}**（mid 段 H；样例取第 {d['lstar_examples']} 层 T 的 top-1 专家，⟦⟧ 为该 token）：\n")
                P("| token | n | H_T | H_NB | 纯度 T | UPOS | 样例（专家 #：份额：上下文） |")
                P("|---|---|---|---|---|---|---|")
                for x in d[key][:10]:
                    ex = " <br> ".join(f"#{e['expert']}（{e['share']:.0%}）{e['context'][-70:]}".replace("|", "∣") for e in x["examples"])
                    P(f"| `{x['str']!r}` | {x['n']} | {x['H_T_mid']:.2f} | {x['H_NB_mid']:.2f} | {x['purity_T_mid']:.2f} | {x['upos']} | {ex} |")
        P("")
summary["tokens"] = stok

# ------------------------------------------------------------------ residual (b)
P("## 7. 残差 (b)：塞语 / 乌兹别克反向的词表反事实分解\n")
P("D_obs = 两侧（E182 均衡选中 token）槽位分布的 JSD；D_lex = 每个 token 换成该 id 在组内所有语侧的合并路由分布后的 JSD"
  "（路由只由 token id 决定时的距离）；Δ = D(P1) − D(P2)；Δ_ctx = Δ_obs − Δ_lex。[ ] = 句子 bootstrap 200 次 95%。"
  "ov = 两侧 token 分布加权重合 Σ min(p_A, p_B)（P1 / P2）。层段均值。\n")
P("| 来源 | 模型 | 路由器 | 组 / 对比 | 类别 | 层段 | Δ_obs | Δ_lex | Δ_ctx | Δ_ctx 区间不含 0 的层（+/−） | ov P1 / P2 |")
P("|---|---|---|---|---|---|---|---|---|---|---|")
sb = {}
for part, models in (("b182", M4), ("b180", M3)):
    for m in models:
        p = f"{RES}/res_{part}_{m}.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        sb[f"{part}:{m}"] = d
        for g, gd in d["groups"].items():
            for c in ("LET", "NON", "ALL"):
                if c not in gd:
                    continue
                for ri, rr in gd[c].items():
                    rname = d["routers"][int(ri)]
                    for key, rows in rr.items():
                        L = len(rows["d_obs"])
                        sg = segs(m, L)
                        lo, hi = np.array(rows["d_ctx_lo"]), np.array(rows["d_ctx_hi"])
                        npos, nneg = int((lo > 0).sum()), int((hi < 0).sum())
                        for i, (snm, ls) in enumerate([(k, v) for k, v in sg.items() if k != "last"]):
                            f = lambda k: float(np.mean(np.array(rows[k])[ls]))
                            P(f"| {part} | {NAMES[m] if i == 0 else ''} | {rname if i == 0 else ''} | {g} {key} | {c} | {snm} | "
                              f"{f('d_obs'):+.4f} | {f('d_lex'):+.4f} | {f('d_ctx'):+.4f} | {f'{npos}/{nneg}' if i == 0 else ''} | "
                              f"{rows['ov1'][0]:.2f} / {rows['ov2'][0]:.2f} |")
P("")
jdump(f"{RES}/summary.json", summary)
open(f"{RES}/tables.md", "w").write("\n".join(md) + "\n")
open(f"{RES}/tables_layers.md", "w").write("# E185 逐层表（自动生成）\n\n" + "\n".join(mdl) + "\n")
print("written")
