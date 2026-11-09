#!/usr/bin/env python3
"""E181-step1 analysis: LAPE (Tang et al. 2402.16438, identify.py) layer profiles, trained vs NA-n / NB-n nulls.
Card: division/experiments/E181-DRAFT-unit-level-language-null.md section 0 (decision table frozen there).
Inputs: ~/mechpop_cache/e181/{qwen3,llama2}/ ; outputs: division/results/e181/{tables.md, summary.json, fig_*.png}.
"""
import json, os
import numpy as np
import torch
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C = "/home/xiang/mechpop_cache/e181"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e181")
D = 8
TANG7 = ["eng_Latn", "zho_Hans", "fra_Latn", "spa_Latn", "vie_Latn", "ind_Latn", "jpn_Jpan"]
torch.set_num_threads(16)


def tang(P, top_rate=0.01, abs_thr=None):
    """P [L, N, K] activation probabilities. Returns dict with per-layer counts and thresholds (Tang identify.py)."""
    L, N, K = P.shape
    flat = P.reshape(-1)
    if abs_thr is None:
        top_prob = float(flat.kthvalue(int(round(flat.numel() * 0.95))).values)
    else:
        top_prob = abs_thr[0]
    s = P.sum(-1, keepdim=True)
    nrm = P / s
    nrm[torch.isnan(nrm)] = 0
    logp = torch.where(nrm > 0, nrm.log(), torch.zeros_like(nrm))
    ent = -(nrm * logp).sum(-1)
    elig = (P > top_prob).sum(-1) > 0
    ent_m = ent.clone()
    ent_m[~elig] = float("inf")
    k = int(round(L * N * top_rate))
    if abs_thr is None:
        vals, idx = ent_m.reshape(-1).topk(k, largest=False)
        sel = torch.zeros(L * N, dtype=torch.bool)
        sel[idx] = True
        sel = sel.view(L, N)
        ent_thr = float(vals[-1])
    else:
        ent_thr = abs_thr[1]
        sel = ent_m <= ent_thr
    assign = ((P > top_prob) & sel[..., None]).sum(1)  # [L, K] neurons assigned to each language per layer
    alive = s.squeeze(-1) > 0
    S = torch.where(alive, 1 - ent / np.log(K), torch.zeros_like(ent)).sum(1) / alive.sum(1).clamp(min=1)
    return {"count": sel.sum(1).numpy().astype(float), "top_prob": top_prob, "ent_thr": ent_thr,
            "assign": assign.numpy(), "S": S.numpy(), "n_elig": int(elig.sum())}


def probs(counts, ntok):
    """counts [L, K, N] -> P [L, N, K] float32."""
    return (torch.from_numpy(counts.astype(np.float32)) / torch.as_tensor(ntok, dtype=torch.float32)[None, :, None]
            ).permute(0, 2, 1).contiguous()


def run_set(get_counts, ntok, ntok_sh, top_rate, has_sh=True):
    """get_counts(r) -> [L, K, N]. Returns per-router Tang results with per-draw thresholds and with T's thresholds."""
    res = {"T": tang(probs(get_counts(0), ntok), top_rate)}
    absthr = (res["T"]["top_prob"], res["T"]["ent_thr"])
    for fam, off in (("NA", 1), ("NB", 1 + D)):
        res[fam] = [tang(probs(get_counts(off + j), ntok), top_rate) for j in range(D)]
        res[fam + "_abs"] = [tang(probs(get_counts(off + j), ntok), top_rate, absthr) for j in range(D)]
    if has_sh:
        res["SH"] = tang(probs(get_counts(1 + 2 * D), ntok_sh), top_rate)
    return res


def share(c, edge):
    return float(c[edge].sum() / max(c.sum(), 1e-9))


def decide(res, edge, key_suffix=""):
    cT = res["T"]["count"]
    sT = share(cT, edge)
    out = {"share_T": sT, "fam": {}}
    for fam in ("NA", "NB"):
        R = res[fam + key_suffix]
        cs = np.stack([r["count"] for r in R])
        sh = np.array([share(c, edge) for c in cs])
        rho = float(spearmanr(cT, cs.mean(0)).correlation)
        out["fam"][fam] = {"rho": rho, "share_mean": float(sh.mean()), "share_min": float(sh.min()),
                           "share_max": float(sh.max()), "ratio": float(sh.mean() / sT) if sT > 0 else float("nan"),
                           "inherit": bool(rho >= .8 and .85 <= sh.mean() / sT <= 1.15),
                           "exceeds": bool(sT >= 1.25 * sh.max()), "rho_lt_05": bool(rho < .5)}
    f = out["fam"]
    if f["NA"]["inherit"] and f["NB"]["inherit"]:
        out["branch"] = "inherited"
    elif (f["NA"]["exceeds"] and f["NB"]["exceeds"]) or (f["NA"]["rho_lt_05"] and f["NB"]["rho_lt_05"]):
        out["branch"] = "departs"
    else:
        out["branch"] = "null-family-dependent"
    return out


def U(c, edge, mid):
    return float(c[edge].mean() / max(c[mid].mean(), 1e-9))


def fmt_profile_table(res, L, edge, title):
    lines = [f"### {title}", "", "| 层 | T | NA-n 均值 [min–max] | NB-n 均值 [min–max] | 打乱地板 | S_N T / NA / NB |", "|---|---|---|---|---|---|"]
    cA = np.stack([r["count"] for r in res["NA"]])
    cB = np.stack([r["count"] for r in res["NB"]])
    SA = np.stack([r["S"] for r in res["NA"]]).mean(0)
    SB = np.stack([r["S"] for r in res["NB"]]).mean(0)
    for l in range(L):
        mark = " *" if l in edge else ""
        sh = res["SH"]["count"][l] if "SH" in res else float("nan")
        lines.append(f"| {l}{mark} | {res['T']['count'][l]:.0f} | {cA[:, l].mean():.0f} [{cA[:, l].min():.0f}–{cA[:, l].max():.0f}] | "
                     f"{cB[:, l].mean():.0f} [{cB[:, l].min():.0f}–{cB[:, l].max():.0f}] | {sh:.0f} | "
                     f"{res['T']['S'][l]:.3f} / {SA[l]:.3f} / {SB[l]:.3f} |")
    lines.append("")
    lines.append("`*` = 首尾层（决策用）。")
    return lines


def fmt_decision(dec, label):
    f = dec["fam"]
    return (f"| {label} | {dec['share_T']:.3f} | {f['NA']['share_mean']:.3f} [{f['NA']['share_min']:.3f}–{f['NA']['share_max']:.3f}] | "
            f"{f['NA']['ratio']:.2f} | {f['NA']['rho']:.2f} | {f['NB']['share_mean']:.3f} [{f['NB']['share_min']:.3f}–{f['NB']['share_max']:.3f}] | "
            f"{f['NB']['ratio']:.2f} | {f['NB']['rho']:.2f} | **{dec['branch']}** |")


DEC_HEAD = ["| 版本 | 首尾份额 T | NA-n 份额 均值 [min–max] | NA/T | ρ(T, NA) | NB-n 份额 均值 [min–max] | NB/T | ρ(T, NB) | 分支 |",
            "|---|---|---|---|---|---|---|---|---|"]


def figure(res, L, edge, title, path, tang7=None):
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    x = np.arange(L)
    for fam, col in (("NA", "#8c8c8c"), ("NB", "#d95f02")):
        cs = np.stack([r["count"] for r in res[fam]])
        ax.fill_between(x, cs.min(0), cs.max(0), color=col, alpha=.25, lw=0)
        ax.plot(x, cs.mean(0), color=col, lw=1.2, label=f"{fam}-n (8 draws: mean, min–max)")
    ax.plot(x, res["T"]["count"], color="#1b4f9c", lw=2, marker="o", ms=3, label="trained")
    if "SH" in res:
        ax.plot(x, res["SH"]["count"], color="k", lw=.8, ls=":", label="trained, language labels shuffled")
    if tang7 is not None:
        ax.plot(x, tang7, color="#1b4f9c", lw=1, ls="--", label="trained, Tang-7 languages")
    for e in edge:
        ax.axvspan(e - .5, e + .5, color="#1b4f9c", alpha=.05, lw=0)
    ax.set_xlabel("layer")
    ax.set_ylabel("language-specific neurons\n(LAPE bottom 1%, symlog)")
    ax.set_title(title, fontsize=10)
    ax.set_xlim(-.5, L - .5)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=7, frameon=False, loc="upper center")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


summary, md = {}, ["# E181-step1 结果表（语言专属神经元层剖面 vs 同隐状态随机神经元零模型）", "",
                   "卡：`division/experiments/E181-DRAFT-unit-level-language-null.md` §0（决策表跑前冻结）。读数 = Tang LAPE（identify.py：95 分位资格 + 全模型熵最低 1%），每个零模型 draw 各自重算阈值；NA-n = 读入端 Haar 旋转；NB-n = 同旋转 + 每神经元阈值匹配训练神经元激活率；8 draws（NA/NB 配对共用 R）。", ""]

# ======================================================================= M2 Llama-2-7B (first: sanity gate)
mL = json.load(open(f"{C}/llama2/meta.json"))
full = np.load(f"{C}/llama2/full.npy", mmap_mode="r")
subc = np.load(f"{C}/llama2/sub.npy", mmap_mode="r")
dL = np.load(f"{C}/llama2/diag.npz")
L2 = mL["L"]
langs = mL["langs"]
i20 = [langs.index(x) for x in mL["langs20"]]
i7 = [langs.index(x) for x in TANG7]
nt = np.array([mL["ntok"][x] for x in langs], float)
edgeL = [0, 1, 28, 29, 30, 31]
midL = list(range(2, 28))
first2, last4 = [0, 1], [28, 29, 30, 31]
# Tang-7 sanity (full stream, T only + nulls secondary)
r7 = run_set(lambda r: np.asarray(full[r][:, i7]), nt[i7], None, .01, has_sh=False)
c7 = r7["T"]["count"]
s7 = share(c7, edgeL)
f2 = c7[first2].mean() / max(c7[midL].mean(), 1e-9)
l4 = c7[last4].mean() / max(c7[midL].mean(), 1e-9)
sanity = bool(s7 >= .5 and f2 >= 2 and l4 >= 2)
summary["llama2_tang7"] = {"share": s7, "first2_over_mid": f2, "last4_over_mid": l4, "pass": sanity,
                           "profile": c7.tolist(), "dec_secondary": decide(r7, edgeL)}
md += ["# M2 Llama-2-7B（32 层 × 11,008；FLORES-200 dev 997 句；BOS 不计）", "",
       "## 前提检查：Tang-7（eng zho fra spa vie ind jpn），全量流，1%", "",
       f"- 首尾份额（层 0,1,28–31） = **{s7:.3f}**（门槛 ≥ .5；层数占比 .19）；前 2 层每层均值 ÷ 中段（2–27）= **{f2:.1f}×**，后 4 层 = **{l4:.1f}×**（门槛各 ≥ 2）→ **{'通过' if sanity else '不通过'}**。",
       f"- T 逐层个数：{', '.join(f'{int(v)}' for v in c7)}", "",
       ("**按预登记：前提检查通过，下列分支即判决。**" if sanity else
        "**按预登记：前提检查不通过 → 停。下面两个模型表中的“分支”列只是把冻结的决策规则机械套用后的记录，不构成判决；本步不给判决分支。**"), ""]

ntsh = dL["ntok_sh"]
rF = run_set(lambda r: np.asarray(full[r][:, i20]), nt[i20], ntsh, .01)
rF5 = run_set(lambda r: np.asarray(full[r][:, i20]), nt[i20], ntsh, .05)
rS = run_set(lambda r: np.asarray(subc[r]), np.full(20, 1000.), np.full(20, 1000.), .01, has_sh=False)
decF, decF5, decS = decide(rF, edgeL), decide(rF5, edgeL), decide(rS, edgeL)
decFabs = decide(rF, edgeL, "_abs")
# rate-matching control on the measurement set (language-balanced rate over 20 langs)
pT = (np.asarray(full[0][:, i20]) / nt[i20][None, :, None]).mean(1)  # [L, N]
rel = []
for j in range(D):
    pB = (np.asarray(full[1 + D + j][:, i20]) / nt[i20][None, :, None]).mean(1)
    v = pT >= 1.0 / nt[i20].min()
    rel.append(float(np.median(np.abs(pB[v] - pT[v]) / pT[v])))
ctlL = {"nb_relerr_median_heldout_per_draw": rel, "nb_relerr_pass": bool(max(rel) <= .05),
        "cal_relerr_insample_max": float(dL["cal_relerr_med"].max()),
        "ent_thr_T": rF["T"]["ent_thr"], "ent_thr_shuffle": rF["SH"]["ent_thr"],
        "shuffle_pass": bool(rF["T"]["ent_thr"] < rF["SH"]["ent_thr"]),
        "two_pass": bool(mL["two_pass_identical_all"]), "hook_sign_agreement_min": mL["hook_sign_agreement_min"],
        "hook_pass": bool(mL["hook_sign_agreement_min"] >= .999),
        "rate_T_mean": float(pT.mean()), "U_T": U(rF["T"]["count"], edgeL, midL)}
summary["llama2"] = {"full_1pct": decF, "full_5pct": decF5, "sub_1pct": decS, "full_1pct_Tabs": decFabs,
                     "controls": ctlL, "profile_T": rF["T"]["count"].tolist(),
                     "profile_NA_mean": np.stack([r["count"] for r in rF["NA"]]).mean(0).tolist(),
                     "profile_NB_mean": np.stack([r["count"] for r in rF["NB"]]).mean(0).tolist(),
                     "profile_SH": rF["SH"]["count"].tolist(),
                     "S_T": rF["T"]["S"].tolist(), "top_prob_T": rF["T"]["top_prob"],
                     "assign_T_by_lang": dict(zip(mL["langs20"], rF["T"]["assign"].sum(0).tolist()))}
md += ["## 决策（20 语）", "", *DEC_HEAD,
       fmt_decision(decF, "**主：全量流，1%**"), fmt_decision(decF5, "全量流，5%（次）"),
       fmt_decision(decS, "子样本每语 1,000 token，1%（对账）"), fmt_decision(decFabs, "全量流，1%，沿用 T 绝对阈值（次）"),
       fmt_decision(summary["llama2_tang7"]["dec_secondary"], "Tang-7，全量流，1%（次）"), "",
       f"- U_T（首尾每层均值 ÷ 中段）= {ctlL['U_T']:.2f}。",
       "",
       "## 阳性对照", "",
       f"- NB-n 激活率匹配（校准集拟合 → 测量集，语言等权率，中位相对误差，8 draws）：{', '.join(f'{x:.3f}' for x in rel)} → {'过' if ctlL['nb_relerr_pass'] else '不过'}（门槛 ≤ .05）；校准集内 ≤ {ctlL['cal_relerr_insample_max']:.4f}。",
       f"- 打乱地板：1% LAPE 阈值 T = {ctlL['ent_thr_T']:.3f}，打乱 = {ctlL['ent_thr_shuffle']:.3f}（log 20 = {np.log(20):.3f}）→ {'过' if ctlL['shuffle_pass'] else '不过'}。",
       f"- 两遍一致：{ctlL['two_pass']}；hook 符号一致率最小 {ctlL['hook_sign_agreement_min']:.6f} → {'过' if ctlL['hook_pass'] else '不过'}。", "",
       *fmt_profile_table(rF, L2, edgeL, "逐层个数（全量流，1%，20 语）"), ""]
figure(rF, L2, edgeL, "Llama-2-7B MLP neurons, FLORES-200 dev, 20 languages", os.path.join(OUT, "fig_llama2.png"), tang7=c7)

# ======================================================================= M1 Qwen3-30B-A3B experts
mQ = json.load(open(f"{C}/qwen3/meta.json"))
unc = np.load(f"{C}/qwen3/uncond.npy", mmap_mode="r")
rou = np.load(f"{C}/qwen3/routed.npy", mmap_mode="r")
dQ = np.load(f"{C}/qwen3/diag.npz")
LQ = mQ["L"]
edgeQ = [0, 1, 2] + list(range(42, 48))
midQ = list(range(3, 42))
edgeQ179 = [0, 1, 2, 3, 44, 45, 46, 47]
n1k = np.full(20, 1000.)
rQ = run_set(lambda r: np.asarray(unc[r]), n1k, n1k, .01)
rQ5 = run_set(lambda r: np.asarray(unc[r]), n1k, n1k, .05)
rQr = run_set(lambda r: np.asarray(rou[r]), n1k, None, .01, has_sh=False)
qi5 = [mQ["langs"].index(x) for x in ["eng_Latn", "zho_Hans", "fra_Latn", "spa_Latn", "jpn_Jpan"]]
rQt5 = tang(probs(np.asarray(unc[0][:, qi5]), n1k[qi5]), .01)
decQ, decQ5, decQr, decQabs = decide(rQ, edgeQ), decide(rQ5, edgeQ), decide(rQr, edgeQ), decide(rQ, edgeQ, "_abs")
decQ179 = decide(rQ, edgeQ179)
sub_sensitive = decF["branch"] != decS["branch"]
ctlQ = {"nb_relerr_median_heldout": float(np.median(dQ["relerr_med"])),
        "nb_relerr_median_max_layer_draw": float(dQ["relerr_med"].max()),
        "nb_relerr_pass": bool(np.median(dQ["relerr_med"]) <= .05),
        "ent_thr_T": rQ["T"]["ent_thr"], "ent_thr_shuffle": rQ["SH"]["ent_thr"],
        "shuffle_pass": bool(rQ["T"]["ent_thr"] < rQ["SH"]["ent_thr"]),
        "two_pass": bool(dQ["two_pass_identical"].all()), "U_T": U(rQ["T"]["count"], edgeQ, midQ),
        "rate_T_by_layer": dQ["rate_T"].tolist(), "rate_NA_by_layer": dQ["na_rate"].mean(1).tolist()}
summary["qwen3"] = {"uncond_1pct": decQ, "uncond_5pct": decQ5, "routed_1pct": decQr, "uncond_1pct_Tabs": decQabs,
                    "uncond_1pct_e179_edges": decQ179, "subsample_sensitive_flag": sub_sensitive, "controls": ctlQ,
                    "profile_T": rQ["T"]["count"].tolist(),
                    "profile_NA_mean": np.stack([r["count"] for r in rQ["NA"]]).mean(0).tolist(),
                    "profile_NB_mean": np.stack([r["count"] for r in rQ["NB"]]).mean(0).tolist(),
                    "profile_SH": rQ["SH"]["count"].tolist(), "profile_T_tang5": rQt5["count"].tolist(),
                    "S_T": rQ["T"]["S"].tolist(),
                    "assign_T_by_lang": dict(zip(mQ["langs"], rQ["T"]["assign"].sum(0).tolist()))}
md += ["# M1 Qwen3-30B-A3B 专家 FFN 神经元（48 层 × 98,304；E179 缓存每语 1,000 token）", "",
       "## 决策（20 语）", "", *DEC_HEAD,
       fmt_decision(decQ, "**主：非条件，1%**"), fmt_decision(decQ5, "非条件，5%（次）"),
       fmt_decision(decQr, "路由条件，1%（次）"), fmt_decision(decQabs, "非条件，1%，沿用 T 绝对阈值（次）"),
       fmt_decision(decQ179, "非条件，1%，E179 层段 0–3 ∪ 44–47（次）"), "",
       f"- 首尾层 = 0–2 ∪ 42–47（9/48 = .19）；U_T（首尾每层均值 ÷ 中段 3–41）= {ctlQ['U_T']:.2f}。",
       f"- Llama 全量 vs 子样本判决{'不同 → 本判决标\"对子样本量敏感\"' if sub_sensitive else '相同 → 不标子样本敏感'}。",
       f"- Tang-5 子集（eng zho fra spa jpn）T 逐层个数：{', '.join(str(int(v)) for v in rQt5['count'])}", "",
       "## 阳性对照", "",
       f"- NB-n 留出折激活率匹配：中位相对误差（层 × draw 的中位）= {ctlQ['nb_relerr_median_heldout']:.4f}，最大层 / draw {ctlQ['nb_relerr_median_max_layer_draw']:.4f} → {'过' if ctlQ['nb_relerr_pass'] else '不过'}。",
       f"- 打乱地板：1% LAPE 阈值 T = {ctlQ['ent_thr_T']:.3f}，打乱 = {ctlQ['ent_thr_shuffle']:.3f} → {'过' if ctlQ['shuffle_pass'] else '不过'}。",
       f"- 两遍一致（每层 T 激活逐元素）：{ctlQ['two_pass']}。", "",
       *fmt_profile_table(rQ, LQ, edgeQ, "逐层个数（非条件，1%，20 语）"), ""]
figure(rQ, LQ, edgeQ, "Qwen3-30B-A3B expert-FFN neurons, FLORES-200 dev subsample, 20 languages",
       os.path.join(OUT, "fig_qwen3.png"))

summary["sanity_gate_pass"] = sanity
open(os.path.join(OUT, "tables.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({"sanity": summary["llama2_tang7"] | {"profile": None},
                  "llama2": {k: (v["branch"], v["share_T"], {f: (v["fam"][f]["share_mean"], v["fam"][f]["share_max"], v["fam"][f]["rho"]) for f in v["fam"]})
                             for k, v in summary["llama2"].items() if isinstance(v, dict) and "branch" in v},
                  "qwen3": {k: (v["branch"], v["share_T"], {f: (v["fam"][f]["share_mean"], v["fam"][f]["share_max"], v["fam"][f]["rho"]) for f in v["fam"]})
                            for k, v in summary["qwen3"].items() if isinstance(v, dict) and "branch" in v},
                  "ctlL": ctlL, "ctlQ": {k: v for k, v in ctlQ.items() if not k.startswith("rate")}}, indent=1, default=str))
