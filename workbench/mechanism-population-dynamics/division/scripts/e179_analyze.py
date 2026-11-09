#!/usr/bin/env python3
"""E179 analysis (card: experiments/E179-language-geometry-replication.md). Readouts R1/R2/R4/R5 as E178 for
T vs N_A / N_B / N_G / N_T / N_Tk, label-permutation floor, sentence bootstrap; pre-registered decision table
(i)-(iv) incl. the 11-09 15:56 amendment (G3 subspace split); one figure per model.

Usage: e179_analyze.py OUT_DIR key=CAPTURE_DIR [key=CAPTURE_DIR ...]   (key in qwen3, gptoss, olmoe)
"""
import json, os, sys
import numpy as np
from scipy.stats import spearmanr

OUT = sys.argv[1]
CAPS = dict(a.split("=", 1) for a in sys.argv[2:])
os.makedirs(OUT, exist_ok=True)
NAME = {"qwen3": "Qwen3-30B-A3B", "gptoss": "GPT-OSS-20B", "olmoe": "OLMoE-1B-7B-0125-Instruct"}
SEG = {48: dict(edge=list(range(0, 4)) + list(range(44, 48)), mid=list(range(7, 35)),
                chen={"early 0-4": range(0, 5), "middle 22-26": range(22, 27), "late 43-47": range(43, 48)}),
       24: dict(edge=[0, 1, 22, 23], mid=list(range(4, 18)),
                chen={"early 0-2": range(0, 3), "middle 11-13": range(11, 14), "late 21-23": range(21, 24)}),
       16: dict(edge=[0, 1, 14, 15], mid=list(range(2, 12)),
                chen={"early 0-1": range(0, 2), "middle 7-8": range(7, 9), "late 14-15": range(14, 16)})}
CHEN = ["arb_Arab", "ben_Beng", "deu_Latn", "eng_Latn", "spa_Latn", "fra_Latn", "jpn_Jpan", "kor_Hang",
        "swh_Latn", "zho_Hans"]
NULLS = ("N_A", "N_B", "N_G", "N_T", "N_Tk")
E178_SUMMARY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e178", "summary.json")


def jsd2(P, Q):
    M = 0.5 * (P + Q)
    f = lambda a, b: np.where(a > 0, a * np.log2(np.where(a > 0, a, 1) / np.where(b > 0, b, 1)), 0).sum(-1)
    return 0.5 * f(P, M) + 0.5 * f(Q, M)


def pair_mean_jsd(C, idx=None):
    if idx is not None:
        C = C[..., idx, :]
    P = C / np.maximum(C.sum(-1, keepdims=True), 1e-30)
    iu, ju = np.triu_indices(P.shape[-2], 1)
    return jsd2(P[..., iu, :], P[..., ju, :]).mean(-1)


def excl(C, thr):
    tot = C.sum(-2)
    share = C.max(-2) / np.maximum(tot, 1e-30)
    return ((share >= thr) & (tot > 0)).mean(-1)


def chen_excl(C, nt, idx):
    p = C[..., idx, :] / nt[..., idx, None]
    W = p / np.maximum(p.sum(-2, keepdims=True), 1e-30)
    return (W > 0.4).sum((-2, -1)).astype(float)


def sp(a, b):
    return float(spearmanr(a, b).correlation)


def analyze(key, CAP):
    rng = np.random.default_rng(179)
    z = np.load(os.path.join(CAP, "tallies.npz"))
    meta = json.load(open(os.path.join(CAP, "meta.json")))
    counts = z["counts"].astype(np.float64)
    ntok = z["ntok"].astype(np.float64)
    langs = list(z["langs"])
    L, NR, NL, E = counts.shape
    K, D, NS = meta["K"], meta["draws"], meta["n_sent"]
    FAM = {"T": [0]}
    for i, f in enumerate(NULLS):
        FAM[f] = list(range(1 + i * D, 1 + (i + 1) * D))
    seg = SEG[L]
    chen_idx = [langs.index(x) for x in CHEN if x in langs]
    R1 = pair_mean_jsd(counts)
    R2_50, R2_80 = excl(counts, .5), excl(counts, .8)
    R5 = chen_excl(counts, np.broadcast_to(ntok, counts.shape[:-1]), chen_idx)
    div = np.load(os.path.join(CAP, "div.npy"))
    R4 = div[1:].mean((0, 1))
    loads = counts.sum(2) / ntok.sum()
    maxload = loads.max(-1) / (K / E)
    nt_identity = max(float(np.abs(counts[:, FAM["N_T"]] - counts[:, FAM["N_B"]]).max()),
                      float(np.abs(counts[:, FAM["N_Tk"]] - counts[:, FAM["N_B"]]).max()))

    # permutation floor + bootstrap
    ps = np.load(os.path.join(CAP, "persent.npy"), mmap_mode="r")
    NU = ps.shape[1]
    lab = np.repeat(np.arange(NL), NS)
    perm = {}
    for j, name in enumerate(["T", "N_A0", "N_B0", "N_G0"]):
        X = np.ascontiguousarray(np.transpose(ps[:, :, j, :], (1, 0, 2))).reshape(NU, L * E).astype(np.float32)
        ntu = X[:, :E].sum(1) / K
        r1, r2a, r5 = [], [], []
        for _ in range(200 if j == 0 else 50):
            pl = rng.permutation(lab)
            G = np.zeros((NL, NU), np.float32)
            G[pl, np.arange(NU)] = 1
            C = (G @ X).reshape(NL, L, E).transpose(1, 0, 2).astype(np.float64)
            nt = np.broadcast_to(G @ ntu, (L, NL))
            r1.append(pair_mean_jsd(C)); r2a.append(excl(C, .5)); r5.append(chen_excl(C, nt, chen_idx))
        perm[name] = {"R1": np.array(r1), "R2_50": np.array(r2a), "R5": np.array(r5)}
        if j == 0:
            Ct = np.stack([X[lab == i].sum(0) for i in range(NL)]).reshape(NL, L, E).transpose(1, 0, 2)
            tally_match = float(np.abs(Ct - counts[:, 0]).max())
            Xl = X.reshape(NL, NS, L * E)
            b1, b4 = [], []
            for _ in range(200):
                w = np.bincount(rng.integers(0, NS, NS), minlength=NS).astype(np.float32)
                C = np.einsum("s,lsf->lf", w, Xl).reshape(NL, L, E).transpose(1, 0, 2).astype(np.float64)
                b1.append(pair_mean_jsd(C))
                b4.append((div[1:, :, :, 0] * w[None, :, None]).sum(1).mean(0) / w.sum())
            boot = {"R1": np.percentile(b1, [2.5, 97.5], 0), "R4": np.percentile(b4, [2.5, 97.5], 0)}
        del X

    fm = lambda R, f: R[:, FAM[f]].mean(1)
    U = lambda R: R[seg["edge"]].mean(0) / R[seg["mid"]].mean(0)  # per router
    res = {"key": key, "name": NAME[key], "L": L, "E": E, "K": K, "d": meta["d"]}
    # (i) replication on R1
    U1, U4 = U(R1), U(R4)
    res["U_R1"] = {f: {"mean": float(U1[FAM[f]].mean()), "min": float(U1[FAM[f]].min()), "max": float(U1[FAM[f]].max())} for f in FAM}
    res["U_R4"] = {f: {"mean": float(U4[FAM[f]].mean()), "min": float(U4[FAM[f]].min()), "max": float(U4[FAM[f]].max())} for f in FAM}
    res["U_ratio_T_over_null_R1"] = {f: res["U_R1"]["T"]["mean"] / res["U_R1"][f]["mean"] for f in NULLS}
    res["spearman_R1"] = {f: sp(R1[:, 0], fm(R1, f)) for f in NULLS}
    res["spearman_R1_draws"] = {f: [min(sp(R1[:, 0], R1[:, j]) for j in FAM[f]), max(sp(R1[:, 0], R1[:, j]) for j in FAM[f])] for f in NULLS}
    res["spearman_R4"] = {f: sp(R4[:, 0], fm(R4, f)) for f in NULLS}
    res["dec_i"] = bool(all(.85 <= res["U_ratio_T_over_null_R1"][f] <= 1.15 for f in ("N_A", "N_B")) and res["spearman_R1"]["N_B"] >= .8)
    # (ii) constant factor
    rat = R1[:, 0] / fm(R1, "N_B")
    res["ratio_R1_T_NB"] = rat.tolist()
    res["edge_ratio"], res["mid_ratio"] = float(rat[seg["edge"]].mean()), float(rat[seg["mid"]].mean())
    res["edge_over_mid"] = res["edge_ratio"] / res["mid_ratio"]
    res["edge_over_mid_ratio_of_means"] = float((R1[seg["edge"], 0].mean() / fm(R1, "N_B")[seg["edge"]].mean()) /
                                                (R1[seg["mid"], 0].mean() / fm(R1, "N_B")[seg["mid"]].mean()))
    res["dec_ii"] = bool(abs(res["edge_over_mid"] - 1) <= .2)
    res["ratio_R1_T_NA_median"] = float(np.median(R1[:, 0] / fm(R1, "N_A")))
    res["ratio_R1_T_NB_median"] = float(np.median(rat))
    # (iii) sharpness on R4
    for f in ("N_T", "N_Tk", "N_B"):
        rr = R4[:, 0] / fm(R4, f)
        res[f"R4_T_over_{f}"] = {"median": float(np.median(rr)), "edge": float(rr[seg["edge"]].mean()),
                                 "mid": float(rr[seg["mid"]].mean()), "min": float(rr.min()), "max": float(rr.max())}

    def sharp(m):
        return ("sharpness (0.8-1.25)" if .8 <= m <= 1.25 else "not sharpness (>=1.5)" if m >= 1.5 else
                "partial/undetermined (1.25-1.5)" if m > 1.25 else "N_T above T (<0.8)")
    res["dec_iii"] = sharp(res["R4_T_over_N_T"]["median"])
    res["dec_iii_Tk"] = sharp(res["R4_T_over_N_Tk"]["median"])
    # descriptive / controls
    res["T_maxload"] = {"median": float(np.median(maxload[:, 0])), "max": float(maxload[:, 0].max()),
                        "argmax_layer": int(maxload[:, 0].argmax())}
    res["null_maxload_median"] = {f: float(np.median(maxload[:, FAM[f]])) for f in ("N_A", "N_B", "N_G")}
    res["controls"] = {"det_exact_min": meta["det_exact_min"], "hook_fp32_vs_model": meta["hook_agreement"],
                       "T_logits_vs_model": meta["t_vs_model"], "loadtv_B_mean": float(z["loadtv_B"].mean()),
                       "loadtv_B_max": float(z["loadtv_B"].max()), "loadtv_pass": bool(z["loadtv_B"].mean() <= .01),
                       "N_T_count_identity_maxdiff": nt_identity, "N_T_entropy_residual_max": float(z["resT"].max()),
                       "N_Tk_entropy_residual_max": float(z["resTk"].max()), "tally_match": tally_match,
                       "sT_median": float(np.median(z["sT"])), "sT_range": [float(z["sT"].min()), float(z["sT"].max())],
                       "sTk_median": float(np.median(z["sTk"])),
                       "entT_full_mean": float(z["entT_full"].mean()), "entB_full_mean": float(z["entB_full"].mean()),
                       "entT_topk_mean": float(z["entT_topk"].mean()), "entB_topk_mean": float(z["entB_topk"].mean())}
    if key == "qwen3" and os.path.exists(E178_SUMMARY):
        old = json.load(open(E178_SUMMARY))["R1"]
        res["controls"]["e178_repro_maxdiff"] = {f: float(np.abs(np.array(old[f]) - R1[:, FAM[f]]).max()) for f in ("T", "N_A", "N_B")}
    # (iv) geometry
    gpath = os.path.join(CAP, "geometry.json")
    geo = None
    if os.path.exists(gpath):
        gj = json.load(open(gpath))
        geo = {lv: {k: np.array([gj[lv][str(l)][k] for l in range(L)]) for k in gj[lv]["0"] if k != "G1_acc_permuted"}
               for lv in gj}
        res["G_permuted_ctrl"] = {str(l): gj["tok"][str(l)]["G1_acc_permuted"] for l in (0, L - 1)}
        nb, t = fm(R1, "N_B"), R1[:, 0]
        res["G"] = {}
        for lv in geo:
            for k, v in geo[lv].items():
                if k.endswith("_nll") or k == "rank":
                    continue
                sat = bool(v.max() - v.min() < .01)
                res["G"][f"{lv}:{k}"] = {"profile": v.tolist(), "range": [float(v.min()), float(v.max())], "saturated": sat,
                                         "rho_NB": sp(v, nb), "rho_T": sp(v, t),
                                         "edge_mean": float(v[seg["edge"]].mean()), "mid_mean": float(v[seg["mid"]].mean())}
        g = res["G"]
        ok = lambda k: (not g[k]["saturated"]) and g[k]["rho_NB"] >= .8
        G1, G2 = "tok:G1_acc", "sent:G2"
        G3 = ["tok:G3_k50_prin_acc", "sent:G3_k50_prin_disp"]
        res["dec_iv_original"] = ("supported" if ok(G1) and ok(G2) else "partial" if ok(G1) or ok(G2) else "not supported")
        if ok(G1):
            res["dec_iv"] = "(iv-a) full-dim geometry shows the U"
        elif ok(G2) or any(ok(k) for k in G3):
            res["dec_iv"] = "(iv-b) routing reads the anisotropic principal-direction geometry"
        else:
            res["dec_iv"] = "(iv-c) not supported"
        res["expectation"] = {"G2>=.8": g[G2]["rho_NB"] >= .8, "G3prin>=.8": {k: g[k]["rho_NB"] >= .8 for k in G3},
                              "G1full<.5": g[G1]["rho_NB"] < .5}
    return res, dict(R1=R1, R4=R4, R2_50=R2_50, R2_80=R2_80, R5=R5, FAM=FAM, perm=perm, boot=boot, geo=geo,
                     seg=seg, ntok=ntok, langs=langs, maxload=maxload)


f3 = lambda x: f"{x:.3f}"


def famcell(R, FAM, f, l, fmt=f3):
    v = R[l, FAM[f]]
    return fmt(v.mean()) if f == "T" else f"{fmt(v.mean())} [{fmt(v.min())}–{fmt(v.max())}]"


ALL, md = {}, []
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
COL = {"T": "#1f1f1e", "N_A": "#2a78d6", "N_B": "#eb6834", "N_T": "#9b59b6", "N_G": "#1baf7a"}

for key, CAP in CAPS.items():
    res, A = analyze(key, CAP)
    ALL[key] = res
    R1, R4, FAM, seg, perm, boot, geo = A["R1"], A["R4"], A["FAM"], A["seg"], A["perm"], A["boot"], A["geo"]
    L = res["L"]
    md.append(f"# {res['name']}（L={L}，E={res['E']}，top-{res['K']}，d={res['d']}）\n")
    md.append(f"层段：edge {seg['edge']}；middle {seg['mid'][0]}–{seg['mid'][-1]}。\n")
    md.append("## R1（20 语两两 JSD，底 2）逐层\n\nT 括号 = 句子 bootstrap 95%；零模型 = 8 draws 均值 [最小–最大]；N_T 的 R1 与 N_B 恒等（构造性），不列。\n")
    md.append("| 层 | T [95%] | N_A | N_B | N_G | N_perm 均值 (95 分位) | T/N_A | T/N_B |\n|---|---|---|---|---|---|---|---|")
    for l in range(L):
        pr = perm["T"]["R1"][:, l]
        md.append(f"| {l} | {R1[l, 0]:.3f} [{boot['R1'][0, l]:.3f}, {boot['R1'][1, l]:.3f}] | {famcell(R1, FAM, 'N_A', l)} | "
                  f"{famcell(R1, FAM, 'N_B', l)} | {famcell(R1, FAM, 'N_G', l)} | {pr.mean():.4f} ({np.percentile(pr, 95):.4f}) | "
                  f"{R1[l, 0] / R1[l, FAM['N_A']].mean():.2f} | {R1[l, 0] / R1[l, FAM['N_B']].mean():.2f} |")
    md.append("\n## R4（Bandarkar：与配对英文句的熵归一 JSD，19 语平均）逐层\n")
    md.append("| 层 | T [95%] | N_A | N_B | N_T（全 softmax 熵匹配） | N_Tk（top-k 熵匹配） | N_G | T/N_B | T/N_T | T/N_Tk |\n|---|---|---|---|---|---|---|---|---|---|")
    for l in range(L):
        md.append(f"| {l} | {R4[l, 0]:.3f} [{boot['R4'][0, l]:.3f}, {boot['R4'][1, l]:.3f}] | " +
                  " | ".join(famcell(R4, FAM, f, l) for f in ("N_A", "N_B", "N_T", "N_Tk", "N_G")) + " | " +
                  " | ".join(f"{R4[l, 0] / R4[l, FAM[f]].mean():.2f}" for f in ("N_B", "N_T", "N_Tk")) + " |")
    md.append("\n## U 对比（mean edge / mean middle）\n\n| 读数 | T | N_A | N_B | N_T | N_Tk | N_G |\n|---|---|---|---|---|---|---|")
    for rn in ("U_R1", "U_R4"):
        u = res[rn]
        md.append(f"| {rn[2:]} | {u['T']['mean']:.2f} | " + " | ".join(
            f"{u[f]['mean']:.2f} [{u[f]['min']:.2f}–{u[f]['max']:.2f}]" for f in NULLS[:1] + ("N_B", "N_T", "N_Tk", "N_G")) + " |")
    md.append("\n## R2 / R5 按层段\n\n| 层段 | 读数 | T | N_A | N_B | N_G | N_perm 均值 (95 分位) |\n|---|---|---|---|---|---|---|")
    segs = {"edge": seg["edge"], "middle": seg["mid"], **{k: list(v) for k, v in seg["chen"].items()}, "全部": list(range(L))}
    for sname, rows in segs.items():
        for rname, R, pk in [("R2@50", A["R2_50"], "R2_50"), ("R2@80", A["R2_80"], None), ("R5 独占数", A["R5"], "R5")]:
            g = R[rows].mean(0)
            fmt = (lambda x: f"{x:.1f}") if rname.startswith("R5") else f3
            cells = [fmt(g[0])] + [f"{fmt(g[FAM[f]].mean())} [{fmt(g[FAM[f]].min())}–{fmt(g[FAM[f]].max())}]" for f in ("N_A", "N_B", "N_G")]
            pc = "—"
            if pk:
                pg = perm["T"][pk][:, rows].mean(1)
                pc = f"{fmt(pg.mean())} ({fmt(np.percentile(pg, 95))})"
            md.append(f"| {sname} | {rname} | " + " | ".join(cells) + f" | {pc} |")
    if geo is not None:
        md.append("\n## G 直接几何测量（路由器输入隐状态）逐层\n\nG1 = 20 类探针 5 折准确率（机会 .05）；G2 = 质心离散度；G3 = PCA 主空间（前 k₅₀ 个主成分）/ 残差空间的探针准确率与离散度。\n")
        cols = [("sent", "G1_acc"), ("tok", "G1_acc"), ("sent", "G2"), ("tok", "G2"), ("sent", "k50"), ("tok", "k50"),
                ("tok", "G3_k50_prin_acc"), ("tok", "G3_k50_res_acc"), ("sent", "G3_k50_prin_disp"), ("sent", "G3_k50_res_disp"),
                ("tok", "G3_k16_prin_acc"), ("sent", "G3_k16_prin_disp")]
        md.append("| 层 | N_B R1 | " + " | ".join(f"{lv}:{k}" for lv, k in cols) + " |\n|" + "---|" * (len(cols) + 2))
        nb = R1[:, FAM["N_B"]].mean(1)
        for l in range(L):
            md.append(f"| {l} | {nb[l]:.3f} | " + " | ".join(
                (f"{int(geo[lv][k][l])}" if k == "k50" else f"{geo[lv][k][l]:.3f}") for lv, k in cols) + " |")
        md.append("\n**G 剖面与路由 R1 剖面的 Spearman**（饱和 = 跨层 max−min < .01）\n\n| G 读数 | 范围 | edge 均值 / middle 均值 | ρ(·, N_B R1) | ρ(·, T R1) | 饱和 |\n|---|---|---|---|---|---|")
        for k, v in res["G"].items():
            if k.endswith(":k50"):
                continue
            md.append(f"| {k} | {v['range'][0]:.3f}–{v['range'][1]:.3f} | {v['edge_mean']:.3f} / {v['mid_mean']:.3f} | "
                      f"{v['rho_NB']:.2f} | {v['rho_T']:.2f} | {'是' if v['saturated'] else ''} |")
        md.append(f"\n置换标签对照（token 级 G1，层 0 / 末层）：{res['G_permuted_ctrl']}")
    md.append("\n## 决策表\n")
    md.append(f"- (i) U_T/U_null（R1）：" + "、".join(f"{f} {res['U_ratio_T_over_null_R1'][f]:.2f}" for f in ("N_A", "N_B", "N_G")) +
              f"；Spearman(T, N_B) {res['spearman_R1']['N_B']:.3f}（逐 draw {res['spearman_R1_draws']['N_B'][0]:.2f}–{res['spearman_R1_draws']['N_B'][1]:.2f}），"
              f"Spearman(T, N_A) {res['spearman_R1']['N_A']:.3f} → 本模型条件 {'成立' if res['dec_i'] else '不成立'}")
    md.append(f"- (ii) T/N_B（R1）edge {res['edge_ratio']:.2f}× / middle {res['mid_ratio']:.2f}× → edge/middle {res['edge_over_mid']:.3f}"
              f"（均值之比版本 {res['edge_over_mid_ratio_of_means']:.3f}）→ {'深度无关常数倍复现' if res['dec_ii'] else '模型特有（差 > 20%）'}；T/N_B 全层中位 {res['ratio_R1_T_NB_median']:.2f}，T/N_A 中位 {res['ratio_R1_T_NA_median']:.2f}")
    md.append(f"- (iii) R4 上 T/N_T 全层中位 {res['R4_T_over_N_T']['median']:.2f}（edge {res['R4_T_over_N_T']['edge']:.2f}，middle {res['R4_T_over_N_T']['mid']:.2f}，范围 {res['R4_T_over_N_T']['min']:.2f}–{res['R4_T_over_N_T']['max']:.2f}）→ {res['dec_iii']}；"
              f"N_Tk：中位 {res['R4_T_over_N_Tk']['median']:.2f} → {res['dec_iii_Tk']}；对照 T/N_B 中位 {res['R4_T_over_N_B']['median']:.2f}")
    if geo is not None:
        md.append(f"- (iv) 原口径 {res['dec_iv_original']}；补登记措辞 {res['dec_iv']}；期望检验 {res['expectation']}")
    c = res["controls"]
    md.append(f"\n## 阳性对照与描述\n\n- 两次前向 top-k 完全一致率最小 {c['det_exact_min']:.4f}；hook fp32 重算 vs 模型选择 {c['hook_fp32_vs_model']:.5f}；T logits vs 模型选择 {c['T_logits_vs_model']:.5f}"
              f"\n- N_B 负载匹配 TV 均值 {c['loadtv_B_mean']:.4f}（≤ .01：{'通过' if c['loadtv_pass'] else '不通过'}）、最大 {c['loadtv_B_max']:.4f}"
              f"\n- N_T / N_Tk 计数与 N_B 最大差 {c['N_T_count_identity_maxdiff']:.0f}；熵匹配残差最大 N_T {c['N_T_entropy_residual_max']:.2e}、N_Tk {c['N_Tk_entropy_residual_max']:.2e}；"
              f"缩放 s 中位 N_T {c['sT_median']:.3f}（范围 {c['sT_range'][0]:.3f}–{c['sT_range'][1]:.3f}）、N_Tk {c['sTk_median']:.3f}"
              f"\n- 校准集平均熵（nats）：全 softmax T {c['entT_full_mean']:.3f} vs N_B {c['entB_full_mean']:.3f}；top-k 重归一 T {c['entT_topk_mean']:.3f} vs N_B {c['entB_topk_mean']:.3f}"
              f"\n- T 自身 max 负载 / 均匀：中位 {res['T_maxload']['median']:.2f}、最大 {res['T_maxload']['max']:.2f}（层 {res['T_maxload']['argmax_layer']}）；零模型中位 " +
              "、".join(f"{f} {v:.2f}" for f, v in res["null_maxload_median"].items()) +
              f"\n- 逐句计数 = 逐语言计数（最大差）{c['tally_match']:.0f}" +
              (f"\n- Qwen3 重采 vs E178 的 R1 最大绝对差：{c['e178_repro_maxdiff']}" if "e178_repro_maxdiff" in c else "") +
              "\n- 每语言 token 数：" + "、".join(f"{lg.split('_')[0]} {int(n)}" for lg, n in zip(A["langs"], A["ntok"])) + "\n")

    # figure
    ncol = 3 if geo is not None else 2
    fig, axs = plt.subplots(1, ncol, figsize=(4.6 * ncol, 3.6))
    x = np.arange(L)
    for ax, R, title, fams in [(axs[0], R1, "R1: mean pairwise JSD of P(expert | language)", ("N_A", "N_B", "N_T")),
                               (axs[1], R4, "R4 (Bandarkar): entropy-normalised JSD to paired English", ("N_A", "N_B", "N_T"))]:
        for f in fams:
            v = R[:, FAM[f]]
            ax.fill_between(x, v.min(1), v.max(1), color=COL[f], alpha=.15, lw=0)
            ax.plot(x, v.mean(1), color=COL[f], lw=1.5, ls="--" if f == "N_T" else "-",
                    label={"N_A": "N_A: W·R (Haar)", "N_B": "N_B: N1 load-matched", "N_T": "N_T: N_B, sharpness-matched"
                           + (" (= N_B on R1)" if R is R1 else "")}[f])
        ax.plot(x, R[:, 0], color=COL["T"], lw=2, label="trained router")
        ax.set_xlabel("MoE layer"); ax.set_title(title, fontsize=8.5, loc="left"); ax.set_ylim(bottom=0)
        ax.grid(axis="y", color="#e6e5e0", lw=.6)
    axs[0].legend(frameon=False, fontsize=7)
    if geo is not None:
        ax = axs[2]
        nrm = lambda v: (v - v.min()) / (v.max() - v.min() + 1e-12)
        ax.plot(x, nrm(R1[:, FAM["N_B"]].mean(1)), color=COL["N_B"], lw=2.2, label="N_B R1")
        ax.plot(x, nrm(R1[:, 0]), color=COL["T"], lw=1.2, alpha=.6, label="T R1")
        for (lv, k), c_, ls, lab in [(("tok", "G1_acc"), "#2a78d6", "-", "G1 full-dim probe (token)"),
                                     (("sent", "G2"), "#1baf7a", "-", "G2 centroid dispersion (sentence)"),
                                     (("tok", "G3_k50_prin_acc"), "#9b59b6", "--", "G3 principal-subspace probe (token, k50)"),
                                     (("sent", "G3_k50_prin_disp"), "#c0392b", "--", "G3 principal-subspace dispersion (sent, k50)")]:
            ax.plot(x, nrm(geo[lv][k]), color=c_, ls=ls, lw=1.3,
                    label=f"{lab}  ρ={res['G'][lv + ':' + k]['rho_NB']:.2f}")
        ax.set_title("Geometry of router inputs vs N_B R1 (each min–max normalised)", fontsize=8.5, loc="left")
        ax.set_xlabel("MoE layer"); ax.legend(frameon=False, fontsize=6.3)
    fig.suptitle(f"{res['name']}, FLORES-200 dev, 20 languages (bands = 8 draws min–max)", fontsize=9, x=.01, ha="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"fig_{key}.png"), dpi=170)
    plt.close(fig)

open(os.path.join(OUT, "tables.md"), "w").write("\n".join(md) + "\n")
json.dump(ALL, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=float)
for k, r in ALL.items():
    print(k, json.dumps({x: r.get(x) for x in ("dec_i", "dec_ii", "dec_iii", "dec_iii_Tk", "dec_iv", "dec_iv_original",
                                                "edge_over_mid", "U_ratio_T_over_null_R1", "spearman_R1", "T_maxload")}, default=float))
