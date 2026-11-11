"""E186 report: results/e186/tables.md, tables_layers.md, summary.json.  Card: division/experiments/E186-atlas-capture-breadth.md
Reads the E185-pipeline outputs on the E186 views (~/mechpop_cache/atlas_e186), the E185 outputs for the three E185
models (~/mechpop_cache/atlas_e185, comparison rows only), E186 store meta/diag, and results/e186/extra_*.json."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import BANDS, NAMES, E186_OLMOE, jdump  # noqa: E402

A6 = os.environ.get("E186_A6", os.path.expanduser("~/mechpop_cache/atlas_e186"))
A5 = os.environ.get("E186_A5", os.path.expanduser("~/mechpop_cache/atlas_e185"))
SRC = os.environ.get("E186_SRC", os.path.expanduser("~/mechpop_cache/e186"))
RES = os.environ.get("E186_RES", os.path.join(os.path.dirname(__file__), "..", "results", "e186"))
RES5 = os.environ.get("E186_RES5", os.path.join(os.path.dirname(__file__), "..", "results", "e185"))
NEW = ["phimoe", "mixtral", "dsv2lite"]
OLD = ["qwen3", "gptoss", "olmoe"]
OLM = E186_OLMOE
ALL6 = NEW + OLM
CMP = OLD + NEW + ["olmoe0924_main"]
LABEL = {"inp": "输入 id", "prev": "前一 id", "nxt": "真实下一 id", "pred": "预测下一 id", "pos": "位置", "seq": "序列（句 / 段）",
         "corpus": "语料 FLORES/UD", "upos": "UPOS（UD 词末）", "side": "语侧", "lang": "语言", "script": "文字",
         "sid": "平行句 id（内容）", "inst": "句实例（语侧×句）", "cls": "token 类别"}
FAC184 = ["inp", "prev", "nxt", "pred", "pos", "seq", "corpus", "upos"]
NEST184 = ["prev|inp", "nxt|inp", "pred|inp", "pos|inp", "seq|inp", "corpus|inp", "upos|inp", "inp|pred", "inp|prev"]
FACML = ["inp", "side", "lang", "script", "sid", "inst"]
NESTML = ["lang|inp", "script|inp", "sid|inp", "inst|inp", "lang|inp,script", "script|inp,lang"]


def lab(k):
    if "|" in k:
        x, s = k.split("|")
        return f"{'、'.join(LABEL.get(t, t) for t in x.split(','))} ∣ {'、'.join(LABEL.get(t, t) for t in s.split(','))}"
    return LABEL.get(k, k)


def adir(m):
    return A5 if m in OLD else A6


def load(prefix, m):
    p = f"{adir(m)}/{prefix}_{m}.npz"
    if not os.path.exists(p):
        return None, None
    return dict(np.load(p)), json.load(open(f"{adir(m)}/{prefix}_{m}.json"))


def ridx(rn):
    return rn.index("T"), [i for i, n in enumerate(rn) if n.startswith("N_A")], \
        [i for i, n in enumerate(rn) if n.startswith("N_B")]


def segs(m, L):
    edge, mid = BANDS[m]
    return {"edge-early": [l for l in edge if l < L // 2], "mid": mid, "edge-late": [l for l in edge if l >= L // 2],
            "last": [L - 1]}


def share(a):
    return a[..., 0] / a[..., 3]


def jl(p):
    return json.load(open(p)) if os.path.exists(p) else None


md, mdl = [], []
P = md.append
summary = {"models": ALL6}
P("# E186 结果表（自动生成：scripts/e186_report.py）\n")
P("口径同 E185：份额 = Î(e; X) / H(e)（e = top-1 专家；置换地板 3 次）；条件量地板在 S 层内置换；G_freq = 交叉拟合条件预测信息"
  "（只在 ≥ 20 次的输入 id 上评估，下界，检测限约 .08 bit）。T = 训练路由器；N_B = 负载匹配 N1（8 draws）；N_A = Haar（8 draws）。"
  "**E186 的多语视图也是 8 draws**（E185 的 D180 只有 N_B0 / N_A0 单 draw，比较行里 E185 模型的多语列标 ¹）。"
  "层段（跑前定）：Phi / Mixtral edge 0–1 ∪ 30–31、mid 5–23；DeepSeek-V2-Lite（MoE 层序号）edge 0–1 ∪ 24–25、mid 4–18；"
  "OLMoE-0924 同 OLMoE。家族间只比「同一因子的 T 相对本家族零模型」，不比绝对 bit。\n")

# ------------------------------------------------------------------ 0. capture controls
P("## 0. 采集与阳性对照\n")
P("| 模型 | 主机 / 卡 | 墙钟 (s) | token（FLORES 21 侧 + UD） | L / E / K | 两遍一致 min | hook fp32 min | T vs 模型 min | "
  "N_B TV 校准 均值 / max | N_B TV 测量（20 非英侧）均值 / max | N_Ben TV 校准 / 测量（英 + UD） | 三组 TV N_B（非英 / 英 / UD） | 三组 TV N_Ben | 英语下一 token 准确率 |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
ctrl = {}
for m in ALL6:
    mp = f"{SRC}/{m}/meta.json"
    if not os.path.exists(mp):
        P(f"| {NAMES[m]} | 缺 | | | | | | | | | | | | |")
        continue
    mt = json.load(open(mp))
    ctrl[m] = {k: mt[k] for k in ("wall_s", "ntok", "L", "E", "K", "det_exact_min", "hook_agreement_min",
                                  "t_vs_model_min", "loadtv_B_cal_mean", "loadtv_B_cal_max", "loadtv_B_meas_mean",
                                  "loadtv_B_meas_max", "loadtv_B_meas_grp_mean", "next_token_acc_eng", "host", "gpus",
                                  "loadtv_Ben_cal_mean", "loadtv_Ben_meas_mean", "loadtv_Ben_meas_grp_mean")}
    P(f"| {NAMES[m]} | {mt['host']} ×{len(mt['gpus'])} | {mt['wall_s']:.0f} | {mt['ntok']} | {mt['L']} / {mt['E']} / {mt['K']} | "
      f"{mt['det_exact_min']:.4f} | {mt['hook_agreement_min']:.4f} | {mt['t_vs_model_min']:.4f} | "
      f"{mt['loadtv_B_cal_mean']:.4f} / {mt['loadtv_B_cal_max']:.4f} | {mt['loadtv_B_meas_mean']:.4f} / {mt['loadtv_B_meas_max']:.4f} | "
      f"{mt['loadtv_Ben_cal_mean']:.4f} / {mt['loadtv_Ben_meas_mean']:.4f} | "
      + " / ".join(f"{x:.3f}" for x in mt["loadtv_B_meas_grp_mean"]) + " | "
      + " / ".join(f"{x:.3f}" for x in mt["loadtv_Ben_meas_grp_mean"]) + f" | {mt['next_token_acc_eng']:.3f} |")
summary["controls"] = ctrl
P("")

# ------------------------------------------------------------------ 1. D184-type maps
s184 = {}
P("## 1. 英语图谱（FLORES eng + UD EWT；T / 8 N_A / 8 N_B；同 E185 §1）\n")
for m in ALL6:
    r, info = load("d184", m)
    if r is None:
        P(f"**{NAMES[m]}：缺**\n")
        continue
    L = info["L"]
    sg = segs(m, L)
    iT, iA, iB = ridx(info["routers"])
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
            T, B, Aa = S[:, iT], S[:, iB], S[:, iA]
            above, below = int((T > B.max(1)).sum()), int((T < B.min(1)).sum())
            hs = None
            if f"h0|{kind}|{f}" in r:
                d0, d1 = share(r[f"h0|{kind}|{f}"]), share(r[f"h1|{kind}|{f}"])
                hs = float((np.sign(d0[:, iT] - d0[:, iB].mean(1)) == np.sign(d1[:, iT] - d1[:, iB].mean(1))).mean())
            s184[m][f"{kind}:{f}"] = {"T": T.tolist(), "NB": B.mean(1).tolist(), "NBmin": B.min(1).tolist(),
                                      "NBmax": B.max(1).tolist(), "NA": Aa.mean(1).tolist(), "above": above,
                                      "below": below, "half_sign_agree": hs, "bits_T": r[key][:, iT, 0].tolist(),
                                      "bits_NB": r[key][:, iB, 0].mean(1).tolist()}
            first = True
            for sn, ls in sg.items():
                if not ls:
                    continue
                P(f"| {lab(f) if first else ''} | {sn} | {T[ls].mean():.3f} | {B[ls].mean(1).mean():.3f} "
                  f"[{B[ls].min(1).mean():.3f}, {B[ls].max(1).mean():.3f}] | {Aa[ls].mean():.3f} | "
                  f"{(T[ls] - B[ls].mean(1)).mean():+.3f} | {(str(above) + '/' + str(below)) if first else ''} |"
                  f" {'' if hs is None or not first else f'{hs:.2f}'} |")
                first = False
    He = r["full|marg|inp"][:, :, 3]
    P(f"\nH(e)（bit）T / N_B / N_A：" + "；".join(f"{sn} {He[ls, iT].mean():.2f} / {He[ls][:, iB].mean():.2f} / "
                                                 f"{He[ls][:, iA].mean():.2f}" for sn, ls in sg.items() if ls)
      + f"（log2 E = {np.log2(info['E']):.2f}）。")
    fsd = np.nanmax(np.stack([r[k][..., 2] for k in r if k.startswith("full|")]))
    P(f"置换地板 SD 最大值 {fsd:.4f} bit。\n")
    s184[m]["floor_sd_max"] = float(fsd)
    mdl.append(f"## 英语 {NAMES[m]}：逐层份额（T / N_B 均值 / N_A 均值）\n")
    cols = FAC184 + [f for f in NEST184 if f"full|cond|{f}" in r]
    mdl.append("| 层 | " + " | ".join(lab(c) for c in cols) + " |")
    mdl.append("|---|" + "---|" * len(cols))
    for l in range(L):
        row = []
        for c in cols:
            S = share(r[f"full|{'cond' if '|' in c else 'marg'}|{c}"])
            row.append(f"{S[l, iT]:.3f} / {S[l, iB].mean():.3f} / {S[l, iA].mean():.3f}")
        mdl.append(f"| {l} | " + " | ".join(row) + " |")
    mdl.append("")
summary["d184"] = s184

# ------------------------------------------------------------------ 1b. G_freq
scf = {}
P("## 1b. 给定输入 id 之后：G_freq(X ∣ 输入)（bit / token）\n")
P("格 = T / N_B 均值 [min, max] / N_A 均值；末列 = T 高于 / 低于 N_B 全部 draw 的层数；G(输入) = 只用输入 id 的增益（尺度）。\n")
for data, facs, title in (("d184", ["seq", "prev", "pred", "nxt", "pos", "corpus", "upos"], "英语视图"),
                          ("d180", ["sid", "inst", "pred", "lang", "script"], "多语视图（20 侧，8 draws）")):
    P(f"### {title}\n")
    P("| 模型 | X | edge-early | mid | edge-late | last | 高 / 低层数 | G(输入) mid T / N_B |")
    P("|---|---|---|---|---|---|---|---|")
    for m in ALL6:
        r, info = load(f"cf_{data}", m)
        if r is None:
            P(f"| {NAMES[m]} | 缺 | | | | | | |")
            continue
        L = info["L"]
        sg = segs(m, L)
        iT, iA, iB = ridx(info["routers"])
        for f in facs:
            G = r[f][..., 3]
            T, B, Aa = G[:, iT], G[:, iB], G[:, iA]
            cells = [f"{T[ls].mean():.3f} / {B[ls].mean():.3f} [{B[ls].min(1).mean():.3f}, {B[ls].max(1).mean():.3f}] / "
                     f"{Aa[ls].mean():.3f}" for sn, ls in sg.items() if ls]
            hi, lo = int((T > B.max(1)).sum()), int((T < B.min(1)).sum())
            gi = r[f][..., 0]
            P(f"| {NAMES[m]} | {lab(f)} | " + " | ".join(cells) + f" | {hi} / {lo} (of {L}) | "
              f"{gi[sg['mid'], iT].mean():.2f} / {gi[sg['mid']][:, iB].mean():.2f} |")
            scf[f"{data}:{m}:{f}"] = {"T": T.tolist(), "NB": B.mean(1).tolist(), "NBmin": B.min(1).tolist(),
                                      "NBmax": B.max(1).tolist(), "NA": Aa.mean(1).tolist(), "hi": hi, "lo": lo}
    P("")
summary["crossfit_Gfreq"] = scf

# ------------------------------------------------------------------ 2. multilingual map (8 draws)
s180 = {}
P("## 2. 多语图谱（FLORES dev 20 语侧，T / 8 N_B / 8 N_A）\n")
for m in ALL6:
    r, info = load("d180", m)
    if r is None:
        P(f"**{NAMES[m]}：缺**\n")
        continue
    L = info["L"]
    sg = segs(m, L)
    iT, iA, iB = ridx(info["routers"])
    s180[m] = {}
    P(f"### {NAMES[m]}（token {info['views']['full']}；LET {info['views']['LET']}、NON {info['views']['NON']}）\n")
    P("| 视图 | 量 | edge-early T / N_B [min, max] | mid T / N_B [min, max] | edge-late T / N_B | last T / N_B | N_A mid | 高 / 低层数 |")
    P("|---|---|---|---|---|---|---|---|")
    for vn in ("full", "LET", "NON"):
        for kind, facs in (("marg", FACML), ("cond", NESTML)):
            for f in facs:
                key = f"{vn}|{kind}|{f}"
                if key not in r:
                    continue
                S = share(r[key])
                T, B = S[:, iT], S[:, iB]
                cells = []
                for sn, ls in sg.items():
                    if not ls:
                        cells.append("")
                    elif sn in ("edge-early", "mid"):
                        cells.append(f"{T[ls].mean():.3f} / {B[ls].mean():.3f} [{B[ls].min(1).mean():.3f}, {B[ls].max(1).mean():.3f}]")
                    else:
                        cells.append(f"{T[ls].mean():.3f} / {B[ls].mean():.3f}")
                hi, lo = int((T > B.max(1)).sum()), int((T < B.min(1)).sum())
                P(f"| {vn} | {lab(f)} | " + " | ".join(cells) + f" | {S[sg['mid']][:, iA].mean():.3f} | {hi} / {lo} |")
                s180[m][f"{vn}:{kind}:{f}"] = {"T": T.tolist(), "NB": B.mean(1).tolist(), "NBmin": B.min(1).tolist(),
                                               "NBmax": B.max(1).tolist(), "NA": S[:, iA].mean(1).tolist(),
                                               "hi": hi, "lo": lo}
    P("")
summary["d180"] = s180


# ------------------------------------------------------------------ 3. model comparison
def mid_ratio(r, rn, key, m, L):
    iT, iA, iB = ridx(rn)
    S = share(r[key])
    mid = BANDS[m][1]
    return float(S[mid, iT].mean() / S[mid][:, iB].mean())


def above_frac(r, rn, key, L, gkey=None):
    iT, iA, iB = ridx(rn)
    S = share(r[key]) if gkey is None else r[key][..., 3]
    return int((S[:, iT] > S[:, iB].max(1)).sum())


comp = {}
P("## 3. 家族对照（§21 的五条结构，逐模型；E185 三模型取自 atlas_e185）\n")
P("列：(a) 英语 mid 段边际份额 T / mean(N_B) 倍数：输入 · 前一 · 真实下一 · 预测下一 · UPOS（「词表锐化」= 这些倍数彼此接近、层间平坦）；"
  "(b) 多语 mid：语言边际倍数 → Î(语言∣输入, 文字) 倍数；(c) mid G_freq(平行句∣输入) T / N_B（bit）与 T 高于全部 N_B draw 的层数；"
  "(d) mid G_freq(语言∣输入) T（bit）；(e) G_freq(预测下一∣输入) T 高于全部 N_B draw 的层数；"
  "(f) mid Î(文字∣输入, 语言) 份额 T；(g) 第 0 层 Î(前一)/Î(输入) 份额比 T / N_B；(h) 逐 id H(e∣id) 的 T vs N_B Spearman（英语）。\n")
P("| 模型 | (a) 倍数 输入·前一·下一·预测·UPOS | (b) 语言倍数 边际 → 给定 token+文字 | (c) 平行句∣输入 T / N_B；高层数 | (d) 语言∣输入 T | (e) 预测下一∣输入 高层数 | (f) 文字∣输入,语言 | (g) 第 0 层 前一/输入 T / N_B | (h) Spearman |")
P("|---|---|---|---|---|---|---|---|---|")
for m in CMP:
    row = {}
    r, info = load("d184", m)
    if r is None:
        P(f"| {NAMES[m]} | 缺 | | | | | | | |")
        continue
    L, rn = info["L"], info["routers"]
    iT, iA, iB = ridx(rn)
    ra = [mid_ratio(r, rn, f"full|marg|{f}", m, L) for f in ["inp", "prev", "nxt", "pred", "upos"]]
    row["ratio_tokfactors_mid"] = ra
    S0p, S0i = share(r["full|marg|prev"])[0], share(r["full|marg|inp"])[0]
    row["l0_prev_over_inp_T"] = float(S0p[iT] / S0i[iT])
    row["l0_prev_over_inp_NB"] = float(S0p[iB].mean() / S0i[iB].mean())
    r8, i8 = load("d180", m)
    sup = "¹" if m in OLD else ""
    if r8 is not None:
        rn8 = i8["routers"]
        b0 = mid_ratio(r8, rn8, "full|marg|lang", m, L)
        b1 = mid_ratio(r8, rn8, "full|cond|lang|inp,script", m, L)
        iT8, _, iB8 = ridx(rn8)
        f_ = share(r8["full|cond|script|inp,lang"])[BANDS[m][1], iT8].mean()
        row.update(lang_ratio_marg=b0, lang_ratio_given_tok_script=b1, script_given_inp_lang_T=float(f_))
    else:
        b0 = b1 = f_ = np.nan
    c8, ci8 = load("cf_d180", m)
    if c8 is not None:
        iT8, _, iB8 = ridx(ci8["routers"])
        mid = BANDS[m][1]
        g = c8["sid"][..., 3]
        cT, cB = g[mid, iT8].mean(), g[mid][:, iB8].mean()
        chi = int((g[:, iT8] > g[:, iB8].max(1)).sum())
        dl = c8["lang"][..., 3][mid, iT8].mean()
        row.update(Gsid_mid_T=float(cT), Gsid_mid_NB=float(cB), Gsid_hi=chi, Glang_mid_T=float(dl))
    else:
        cT = cB = dl = np.nan
        chi = "–"
    c4, ci4 = load("cf_d184", m)
    if c4 is not None:
        iT4, _, iB4 = ridx(ci4["routers"])
        g = c4["pred"][..., 3]
        ehi = int((g[:, iT4] > g[:, iB4].max(1)).sum())
        row["Gpred_hi"] = ehi
    else:
        ehi = "–"
    tj = jl(f"{RES5 if m in OLD else RES}/tok_d184_{m}.json")
    sp = tj["spearman_T_NB_over_ids"] if tj else np.nan
    row["H_id_spearman"] = sp
    comp[m] = row
    P(f"| {NAMES[m]} | " + " · ".join(f"{x:.2f}" for x in ra) + f" | {b0:.2f} → {b1:.2f}{sup} | {cT:.3f} / {cB:.3f}{sup}；{chi}/{L} | "
      f"{dl:.3f}{sup} | {ehi}/{L} | {f_:.3f}{sup} | {row['l0_prev_over_inp_T']:.2f} / {row['l0_prev_over_inp_NB']:.2f} | {sp:.2f} |")
summary["comparison"] = comp
P("\n¹ E185 模型的多语零模型只有 N_B0 单 draw（「高层数」= T > N_B0 的层数）。\n")

# ------------------------------------------------------------------ 4. training time
P("## 4. 训练时间轴：OLMoE-1B-7B-0924（20B → 5.1T token → 退火发布版）\n")
P("列同 §3（多语列现在是 8 draws），另加：饱和 = mid 段逐 token top-k 与发布版的重合 |S_t ∩ S_main| / K（T；N_F = 同一固定随机矩阵作用于两个 checkpoint 的隐状态；"
  "N_F 交叉 = 两个不同固定矩阵之间的偶遇基线）；英语下一 token 准确率。\n")
P("| checkpoint | 准确率 | (a) 倍数 输入·前一·下一·预测·UPOS | (b) 语言倍数 边际 → 给定 token+文字 | (c) 平行句∣输入 T / N_B；高层数 | (d) 语言∣输入 T | (e) 预测∣输入 高层数 | (g) 第 0 层 前一/输入 T / N_B | 饱和 mid T / N_F / N_F 交叉 | 饱和 第 0 层 T / N_F |")
P("|---|---|---|---|---|---|---|---|---|---|")
tt = {}
for m in OLM:
    row = dict(comp.get(m, {}))
    r, info = load("d184", m)
    mt = jl(f"{SRC}/{m}/meta.json")
    if r is None or mt is None:
        P(f"| {NAMES[m]} | 缺 | | | | | | | | |")
        continue
    L, rn = info["L"], info["routers"]
    iT, iA, iB = ridx(rn)
    ra = [mid_ratio(r, rn, f"full|marg|{f}", m, L) for f in ["inp", "prev", "nxt", "pred", "upos"]]
    S0p, S0i = share(r["full|marg|prev"])[0], share(r["full|marg|inp"])[0]
    row.update(ratio_tokfactors_mid=ra, l0_prev_over_inp_T=float(S0p[iT] / S0i[iT]),
               l0_prev_over_inp_NB=float(S0p[iB].mean() / S0i[iB].mean()), acc=mt["next_token_acc_eng"])
    r8, i8 = load("d180", m)
    c8, ci8 = load("cf_d180", m)
    c4, ci4 = load("cf_d184", m)
    mid = BANDS[m][1]
    b0 = mid_ratio(r8, i8["routers"], "full|marg|lang", m, L) if r8 else np.nan
    b1 = mid_ratio(r8, i8["routers"], "full|cond|lang|inp,script", m, L) if r8 else np.nan
    if c8 is not None:
        iT8, _, iB8 = ridx(ci8["routers"])
        g = c8["sid"][..., 3]
        cT, cB, chi = g[mid, iT8].mean(), g[mid][:, iB8].mean(), int((g[:, iT8] > g[:, iB8].max(1)).sum())
        dl = c8["lang"][..., 3][mid, iT8].mean()
    else:
        cT = cB = dl = np.nan
        chi = "–"
    if c4 is not None:
        iT4, _, iB4 = ridx(ci4["routers"])
        g = c4["pred"][..., 3]
        ehi = int((g[:, iT4] > g[:, iB4].max(1)).sum())
    else:
        ehi = "–"
    sat = jl(f"{RES}/extra_sat_{m}.json")
    if sat and m != "olmoe0924_main":
        sT, sF = np.mean(np.array(sat["T_ov"])[mid]), np.mean([np.array(sat["NF0_ov"])[mid], np.array(sat["NF1_ov"])[mid]])
        sX = np.mean(np.array(sat["NF_cross_ov"])[mid])
        s0 = f"{sat['T_ov'][0]:.2f} / {(sat['NF0_ov'][0] + sat['NF1_ov'][0]) / 2:.2f}"
        row.update(sat_mid_T=sT, sat_mid_NF=sF, sat_mid_NFcross=sX, sat_T=sat["T_ov"],
                   sat_NF=((np.array(sat["NF0_ov"]) + np.array(sat["NF1_ov"])) / 2).tolist())
        ss = f"{sT:.2f} / {sF:.2f} / {sX:.2f}"
    else:
        ss, s0 = "1（参照）", "1（参照）"
    row.update(lang_ratio_marg=b0, lang_ratio_given_tok_script=b1, Gsid_mid_T=float(cT), Gsid_mid_NB=float(cB),
               Gsid_hi=chi, Glang_mid_T=float(dl), Gpred_hi=ehi)
    tt[m] = row
    P(f"| {NAMES[m]} | {mt['next_token_acc_eng']:.3f} | " + " · ".join(f"{x:.2f}" for x in ra) + f" | {b0:.2f} → {b1:.2f} | "
      f"{cT:.3f} / {cB:.3f}；{chi}/{L} | {dl:.3f} | {ehi}/{L} | {row['l0_prev_over_inp_T']:.2f} / {row['l0_prev_over_inp_NB']:.2f} | {ss} | {s0} |")
summary["training"] = tt
P("")

# ------------------------------------------------------------------ 5. residual (a)
P("## 5. 残差 (a)：下一 token 信息（E184 结论 4 / E185 观察 4）\n")
P("ΔÎ = Î(预测下一) − Î(输入)（bit，E184 ΔG 的同向读数）；「低于」= T 低于两族全部 draw 的层数；Î(预测下一∣输入) 的 T 高于 N_B 全部 draw 的层数；"
  "原式 (8) VS1（k = 1，FLORES eng，≥ 5 次）末层 输入 / 预测下一（T），以及 T 上「预测 > 输入」的层。\n")
P("| 模型 | ΔÎ 低于两族层数 | Î(预测∣输入) 高 / 低层数 | 末层 VS1 输入 / 预测（T） | VS1 预测 > 输入 的层（T） | 同（N_B 均值） | 熵三分位 Î(预测∣输入) mid T − N_B（低 / 中 / 高熵） | 三分位准确率 |")
P("|---|---|---|---|---|---|---|---|")
ra_ = {}
for m in NEW + OLM:
    r, info = load("d184", m)
    if r is None:
        continue
    L, rn = info["L"], info["routers"]
    iT, iA, iB = ridx(rn)
    dI = r["full|marg|pred"][..., 0] - r["full|marg|inp"][..., 0]
    below = int(((dI[:, iT] < dI[:, iB].min(1)) & (dI[:, iT] < dI[:, iA].min(1))).sum())
    c = r["full|cond|pred|inp"][..., 0]
    hi, lo = int((c[:, iT] > c[:, iB].max(1)).sum()), int((c[:, iT] < c[:, iB].min(1)).sum())
    vs = jl(f"{RES}/extra_vs8_{m}.json")
    if vs:
        vi, vp = np.array(vs["VS1_inp"]), np.array(vs["VS1_pred"])
        jB = vs["iB_english"]
        cr = [l for l in range(L) if vp[l, 0] > vi[l, 0]]
        crB = [l for l in range(L) if vp[l, jB].mean() > vi[l, jB].mean()]
        vtxt = f"{vi[L - 1, 0]:.3f} / {vp[L - 1, 0]:.3f} | {cr if cr else '无'} | {crB if crB else '无'}"
    else:
        vtxt = "缺 | | "
        cr = crB = None
    te = jl(f"{RES}/extra_resa_{m}.json")
    if te:
        mid = BANDS[m][1]
        tx = []
        for t in range(3):
            a_ = np.array(te[f"pred|inp@q{t}"])[..., 0]
            tx.append(f"{(a_[mid, 0] - a_[mid][:, te['iB_english']].mean(1)).mean():+.4f}")
        ttxt = " / ".join(tx) + " | " + " / ".join(f"{x:.2f}" for x in te["acc_by_tercile"])
    else:
        ttxt = "缺 | "
    ra_[m] = {"dI_below": below, "cond_hi": hi, "cond_lo": lo, "vs8_cross_T": cr, "vs8_cross_NB": crB}
    P(f"| {NAMES[m]} | {below}/{L} | {hi} / {lo} | {vtxt} | {ttxt} |")
summary["residual_a"] = ra_
P("")

# ------------------------------------------------------------------ 6. new readouts
P("## 6. 新存储才有的读数\n")
P("### 6a. 连续上下文依赖（英语视图，≥ 30 次的输入 id；top-1 softmax 门值 p1 = exp(v₀ − lse) 在同一 id 各次出现间的 SD，再对 id 平均）\n")
P("| 模型 | id 数 | mid SD(p1) T / N_B [min, max] | mid 均值 p1 T / N_B | mid SD(margin) T / N_B | Spearman_id(SD p1: T, N_B) mid |")
P("|---|---|---|---|---|---|")
cx = {}
for m in ALL6:
    c = jl(f"{RES}/extra_ctx_{m}.json")
    if c is None:
        continue
    mid = BANDS[m][1]
    sd, mu, mg = np.array(c["p1_sd"]), np.array(c["p1_mean"]), np.array(c["margin_sd"])
    iB = c["iB_english"]
    cx[m] = {"p1_sd_T": float(sd[mid, 0].mean()), "p1_sd_NB": float(sd[mid][:, iB].mean())}
    P(f"| {NAMES[m]} | {c['n_ids']} | {sd[mid, 0].mean():.3f} / {sd[mid][:, iB].mean():.3f} [{sd[mid][:, iB].min(1).mean():.3f}, {sd[mid][:, iB].max(1).mean():.3f}] | "
      f"{mu[mid, 0].mean():.3f} / {mu[mid][:, iB].mean():.3f} | {mg[mid, 0].mean():.2f} / {mg[mid][:, iB].mean():.2f} | "
      f"{np.nanmean(np.array(c['spearman_p1sd_T_vs_NB'])[mid]):.2f} |")
summary["ctx"] = cx
P("\n### 6b. 序列均值几何（20 个非英语侧；SS = 组间平方和 / 总平方和；G2 = 质心间距 / 组内距离；raw = 原始 h，ro = T 的读出子空间）\n")
P("| 模型 | 层段 | 语言 SS raw / ro | 平行句 SS raw / ro | 语言 G2 raw / ro | 平行句 G2 raw / ro |")
P("|---|---|---|---|---|---|")
gm = {}
for m in ALL6:
    g = jl(f"{RES}/extra_geom_{m}.json")
    if g is None:
        continue
    L = g["L"]
    gm[m] = {k: v for k, v in g.items() if isinstance(v, list)}
    for sn, ls in segs(m, L).items():
        if not ls:
            continue
        f = lambda k: np.mean(np.array(g[k])[ls])  # noqa: E731
        P(f"| {NAMES[m] if sn == 'edge-early' else ''} | {sn} | {f('raw_lang_ss'):.3f} / {f('ro_lang_ss'):.3f} | "
          f"{f('raw_sid_ss'):.3f} / {f('ro_sid_ss'):.3f} | {f('raw_lang_g2'):.2f} / {f('ro_lang_g2'):.2f} | "
          f"{f('raw_sid_g2'):.2f} / {f('ro_sid_g2'):.2f} |")
summary["geom"] = gm
P("")

# ------------------------------------------------------------------ 7. token context dependence
P("## 7. token id 的上下文依赖度 H(e∣id)（英语视图，等 n = 30；同 E185 §6）\n")
P("| 模型 | id 数 | mid H T / N_B / N_A | Spearman_id(H_T, H_NB) | 最依赖上下文（T mid H 最高 6 个） | 最不依赖（最低 6 个） |")
P("|---|---|---|---|---|---|")
for m in ALL6:
    tj = jl(f"{RES}/tok_d184_{m}.json")
    if tj is None:
        continue
    o = tj["overall"]
    P(f"| {NAMES[m]} | {tj['n_ids']} | {o['T']:.2f} / {o['N_B']:.2f} / {o['N_A']:.2f} | {tj['spearman_T_NB_over_ids']:.2f} | "
      + " ".join(f"`{x['str']!r}`" for x in tj["most_context_dependent"][:6]) + " | "
      + " ".join(f"`{x['str']!r}`" for x in tj["least_context_dependent"][:6]) + " |")
P("")

jdump(f"{RES}/summary.json", summary)
open(f"{RES}/tables.md", "w").write("\n".join(md) + "\n")
open(f"{RES}/tables_layers.md", "w").write("# E186 逐层表（自动生成）\n\n" + "\n".join(mdl) + "\n")
print("wrote", f"{RES}/tables.md")
