#!/usr/bin/env python3
"""E178 analysis: readouts R1-R5 for the trained router T vs random routers N_A / N_B / N_G vs label-permutation
floor, the pre-registered decision table, positive controls, one figure (card: experiments/E178-...md).

Usage: e178_analyze.py CAPTURE_DIR OUT_DIR
"""
import json, os, sys
import numpy as np
from scipy.stats import spearmanr

CAP, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
z = np.load(os.path.join(CAP, "tallies.npz"))
meta = json.load(open(os.path.join(CAP, "meta.json")))
counts = z["counts"].astype(np.float64)  # L, NR, NL, E
ntok = z["ntok"].astype(np.float64)
langs = list(z["langs"])
L, NR, NL, E = counts.shape
K, D = meta["K"], meta["draws"]
NS = meta["n_sent"]
FAM = {"T": [0], "N_A": list(range(1, 1 + D)), "N_B": list(range(1 + D, 1 + 2 * D)),
       "N_G": list(range(1 + 2 * D, 1 + 3 * D))}
CHEN = ["arb_Arab", "ben_Beng", "deu_Latn", "eng_Latn", "spa_Latn", "fra_Latn", "jpn_Jpan", "kor_Hang",
        "swh_Latn", "zho_Hans"]
chen_idx = [langs.index(x) for x in CHEN if x in langs]
FIRST2, LAST2 = [0, 1], [L - 2, L - 1]
UEDGE = list(range(0, 4)) + list(range(L - 4, L))
UMID = list(range(7, 35))
CHEN_GROUPS = {"early 0-4": range(0, 5), "middle 22-26": range(22, 27), "late 43-47": range(43, 48)}
rng = np.random.default_rng(178)


def jsd2(P, Q):
    M = 0.5 * (P + Q)
    f = lambda a, b: np.where(a > 0, a * np.log2(np.where(a > 0, a, 1) / np.where(b > 0, b, 1)), 0).sum(-1)
    return 0.5 * f(P, M) + 0.5 * f(Q, M)


def pair_mean_jsd(C, idx=None):
    """C: (..., NL, E) counts -> mean pairwise JSD (base 2) over languages."""
    if idx is not None:
        C = C[..., idx, :]
    P = C / np.maximum(C.sum(-1, keepdims=True), 1e-30)
    n = P.shape[-2]
    iu, ju = np.triu_indices(n, 1)
    return jsd2(P[..., iu, :], P[..., ju, :]).mean(-1)


def excl(C, thr):
    """R2: fraction of experts whose max single-language share of routed tokens >= thr. C: (..., NL, E)."""
    tot = C.sum(-2)
    share = C.max(-2) / np.maximum(tot, 1e-30)
    return ((share >= thr) & (tot > 0)).mean(-1)


def chen_excl(C, nt, idx):
    """R5: sum over Chen's languages of #experts with normalised association W > 0.4. C: (..., NL, E); nt: (..., NL)."""
    p = C[..., idx, :] / nt[..., idx, None]
    W = p / np.maximum(p.sum(-2, keepdims=True), 1e-30)
    return (W > 0.4).sum((-2, -1)).astype(float)


R1 = pair_mean_jsd(counts)                   # L, NR
R1c = pair_mean_jsd(counts, chen_idx)        # Chen 1-JSD similarity = 1 - R1c
R2_50, R2_80 = excl(counts, .5), excl(counts, .8)
R5 = chen_excl(counts, np.broadcast_to(ntok, counts.shape[:-1]), chen_idx)
div = np.load(os.path.join(CAP, "div.npy"))  # NL, NS, L, NR
R4 = div[1:].mean((0, 1))                    # L, NR
loads = counts.sum(2) / ntok.sum()           # L, NR, E: fraction of tokens selecting each expert
maxload = loads.max(-1) / (K / E)            # L, NR

# ------------------------------------------------------------------ permutation floor + bootstrap (per-sentence counts)
ps = np.load(os.path.join(CAP, "persent.npy"), mmap_mode="r")  # L, NU, 4, E
NU = ps.shape[1]
lab = np.repeat(np.arange(NL), NS)
perm = {}
NPERM = {0: 200, 1: 50, 2: 50, 3: 50}
for j, name in enumerate(["T", "N_A0", "N_B0", "N_G0"]):
    X = np.ascontiguousarray(np.transpose(ps[:, :, j, :], (1, 0, 2))).reshape(NU, L * E).astype(np.float32)
    ntu = X[:, :E].sum(1) / K  # tokens per unit (layer 0)
    r1, r2a, r2b, r5 = [], [], [], []
    for _ in range(NPERM[j]):
        pl = rng.permutation(lab)
        G = np.zeros((NL, NU), np.float32)
        G[pl, np.arange(NU)] = 1
        C = (G @ X).reshape(NL, L, E).transpose(1, 0, 2).astype(np.float64)  # L, NL, E
        nt = np.broadcast_to(G @ ntu, (L, NL))
        r1.append(pair_mean_jsd(C)); r2a.append(excl(C, .5)); r2b.append(excl(C, .8)); r5.append(chen_excl(C, nt, chen_idx))
    perm[name] = {k: np.array(v) for k, v in zip(["R1", "R2_50", "R2_80", "R5"], [r1, r2a, r2b, r5])}
    if j == 0:
        # sanity: per-sentence tallies reproduce the per-language tallies of the trained router
        Ct = np.stack([X[lab == i].sum(0) for i in range(NL)]).reshape(NL, L, E).transpose(1, 0, 2)
        tally_match = float(np.abs(Ct - counts[:, 0]).max())
        # sentence bootstrap (same sentence ids resampled in every language)
        Xl = X.reshape(NL, NS, L * E)
        b1, b4 = [], []
        for _ in range(200):
            w = np.bincount(rng.integers(0, NS, NS), minlength=NS).astype(np.float32)
            C = np.einsum("s,lsf->lf", w, Xl).reshape(NL, L, E).transpose(1, 0, 2).astype(np.float64)
            b1.append(pair_mean_jsd(C))
            b4.append((div[1:, :, :, 0] * w[None, :, None]).sum(1).mean(0) / w.sum())
        boot = {"R1": np.percentile(b1, [2.5, 97.5], 0), "R4": np.percentile(b4, [2.5, 97.5], 0)}
    del X


def fam_stats(R):
    out = {}
    for f, idx in FAM.items():
        v = R[:, idx]
        out[f] = {"mean": v.mean(1), "min": v.min(1), "max": v.max(1)}
    return out


def decide(R, name):
    """Apply the pre-registered decision table to a per-layer readout R (L, NR)."""
    fs = fam_stats(R)
    T = fs["T"]["mean"]
    res = {"readout": name}
    for f in ("N_A", "N_B", "N_G"):
        m, lo, hi = fs[f]["mean"], fs[f]["min"], fs[f]["max"]
        rho = float(spearmanr(T, m).correlation)
        rho_draws = [float(spearmanr(T, R[:, j]).correlation) for j in FAM[f]]
        ratio = T / np.where(m != 0, m, np.nan)
        edge = {int(l): float(ratio[l]) for l in FIRST2 + LAST2}
        cond_i = bool(rho >= .8 and all(.7 <= r <= 1.4 for r in edge.values()))
        above = [int(l) for l in range(L) if T[l] >= 2 * m[l] and T[l] > hi[l]]
        below = [int(l) for l in range(L) if T[l] < lo[l]]
        res[f] = {"spearman": rho, "spearman_draws_minmax": [min(rho_draws), max(rho_draws)],
                  "edge_ratio": edge, "i": cond_i, "ii_layers": above, "below_layers": below,
                  "ratio_median": float(np.nanmedian(ratio))}
    A, B = res["N_A"], res["N_B"]
    both_ii = sorted(set(A["ii_layers"]) & set(B["ii_layers"]))
    both_below = sorted(set(A["below_layers"]) & set(B["below_layers"]))
    flip = (A["i"] != B["i"]) or (bool(A["ii_layers"]) != bool(B["ii_layers"]))
    branches = []
    if A["i"] and B["i"]:
        branches.append("(i)")
    if both_ii:
        branches.append("(ii)")
    if flip:
        branches.append("(iii)")
    if both_below:
        branches.append("(iv)")
    res.update(branches=branches or ["none"], ii_both_layers=both_ii, below_both_layers=both_below, flip=flip)
    return res


dec = {n: decide(R, n) for n, R in [("R1", R1), ("R4", R4), ("R5", R5), ("R2_50", R2_50)]}


def u4(R):
    return R[UEDGE].mean(0) / R[UMID].mean(0)


# ------------------------------------------------------------------ tables
f3 = lambda x: f"{x:.3f}"


def cell(R, f, l, fmt=f3):
    v = R[l, FAM[f]]
    return fmt(v.mean()) if f == "T" else f"{fmt(v.mean())} [{fmt(v.min())}–{fmt(v.max())}]"


md = []
md.append(f"## R1 语言专属度（20 语两两 JSD 平均，底 2），逐层\n\nT 括号 = 句子 bootstrap 95%；零模型括号 = 8 draws 最小–最大；N_perm = T 的标签置换 200 次均值（95 分位）。\n")
md.append("| 层 | T [95%] | N_A | N_B | N_G | N_perm | T/N_A | T/N_B |\n|---|---|---|---|---|---|---|---|")
for l in range(L):
    pr = perm["T"]["R1"][:, l]
    md.append(f"| {l} | {R1[l, 0]:.3f} [{boot['R1'][0, l]:.3f}, {boot['R1'][1, l]:.3f}] | {cell(R1, 'N_A', l)} | "
              f"{cell(R1, 'N_B', l)} | {cell(R1, 'N_G', l)} | {pr.mean():.4f} ({np.percentile(pr, 95):.4f}) | "
              f"{R1[l, 0] / R1[l, FAM['N_A']].mean():.2f} | {R1[l, 0] / R1[l, FAM['N_B']].mean():.2f} |")
md.append(f"\n## R4 Bandarkar 原读数（与配对英文句的熵归一 JSD，19 语平均），逐层\n")
md.append("| 层 | T [95%] | N_A | N_B | N_G | T/N_A | T/N_B |\n|---|---|---|---|---|---|---|")
for l in range(L):
    md.append(f"| {l} | {R4[l, 0]:.3f} [{boot['R4'][0, l]:.3f}, {boot['R4'][1, l]:.3f}] | {cell(R4, 'N_A', l)} | "
              f"{cell(R4, 'N_B', l)} | {cell(R4, 'N_G', l)} | {R4[l, 0] / R4[l, FAM['N_A']].mean():.2f} | "
              f"{R4[l, 0] / R4[l, FAM['N_B']].mean():.2f} |")
U = u4(R4)
md.append(f"\nU4 = mean(层 0–3 ∪ 44–47) / mean(层 7–34)：T {U[0]:.2f}；N_A {U[FAM['N_A']].mean():.2f} "
          f"[{U[FAM['N_A']].min():.2f}–{U[FAM['N_A']].max():.2f}]；N_B {U[FAM['N_B']].mean():.2f} "
          f"[{U[FAM['N_B']].min():.2f}–{U[FAM['N_B']].max():.2f}]；N_G {U[FAM['N_G']].mean():.2f} "
          f"[{U[FAM['N_G']].min():.2f}–{U[FAM['N_G']].max():.2f}]")
U1 = u4(R1)
md.append(f"\n（同一 U4 用在 R1 上：T {U1[0]:.2f}；N_A {U1[FAM['N_A']].mean():.2f}；N_B {U1[FAM['N_B']].mean():.2f}；N_G {U1[FAM['N_G']].mean():.2f}）")


def grp(R, rows):
    return R[list(rows)].mean(0)


md.append("\n## R2 独占度（专家被选 token 中单一语言份额 ≥ 阈值的专家比例）与 R5 Chen 原读数（10 语，W > 0.4 的独占专家数），按层段\n")
md.append("| 层段 | 读数 | T | N_A | N_B | N_G | N_perm 均值 (95 分位) |\n|---|---|---|---|---|---|---|")
segs = {"0–1": FIRST2, "0–4": range(0, 5), "7–34": UMID, "22–26": range(22, 27), "43–47": range(43, 48),
        "46–47": LAST2, "全部 48 层": range(L)}
for sname, rows in segs.items():
    for rname, R, pk in [("R2@50", R2_50, "R2_50"), ("R2@80", R2_80, "R2_80"), ("R5 独占数", R5, "R5")]:
        g = grp(R, rows)
        fmt = (lambda x: f"{x:.1f}") if rname.startswith("R5") else f3
        cells = [fmt(g[0])] + [f"{fmt(g[FAM[f]].mean())} [{fmt(g[FAM[f]].min())}–{fmt(g[FAM[f]].max())}]"
                               for f in ("N_A", "N_B", "N_G")]
        pg = perm["T"][pk][:, list(rows)].mean(1)
        md.append(f"| {sname} | {rname} | " + " | ".join(cells) + f" | {fmt(pg.mean())} ({fmt(np.percentile(pg, 95))}) |")
md.append("\nChen 的 1 − JSD 相似度（10 语两两平均，底 2）按其三组：" + "；".join(
    f"{g} T {1 - grp(R1c, r)[0]:.3f} / N_A {1 - grp(R1c, r)[FAM['N_A']].mean():.3f} / N_B {1 - grp(R1c, r)[FAM['N_B']].mean():.3f}"
    for g, r in CHEN_GROUPS.items()))

md.append("\n## 层剖面一致性（R3）与决策表判定\n")
md.append("| 读数 | 零模型 | Spearman（对 8-draw 均值）[逐 draw 最小–最大] | T/零 比：层 0 / 1 / 46 / 47 | (i) 成立 | (ii) 层（T ≥ 2×均值且 > draw 最大） | T 低于 draw 最小的层 |\n|---|---|---|---|---|---|---|")
for n, r in dec.items():
    for f in ("N_A", "N_B", "N_G"):
        x = r[f]
        md.append(f"| {n} | {f} | {x['spearman']:.3f} [{x['spearman_draws_minmax'][0]:.3f}–{x['spearman_draws_minmax'][1]:.3f}] | "
                  + " / ".join(f"{v:.2f}" for v in x["edge_ratio"].values())
                  + f" | {'是' if x['i'] else '否'} | {x['ii_layers'] or '无'} | {x['below_layers'] or '无'} |")
md.append("\n判定（只用 N_A、N_B，按预登记）：" + "；".join(
    f"{n} → {'+'.join(r['branches'])}（两族共同 (ii) 层 {r['ii_both_layers'] or '无'}；两族共同低于层 {r['below_both_layers'] or '无'}）"
    for n, r in dec.items()))

md.append("\n## 阳性对照与 sanity\n")
viol = {f: int((maxload[:, FAM[f]] > 2).sum()) for f in ("N_A", "N_B", "N_G")}
md.append(f"- 零模型负载（测量集，max 专家负载 / 均匀）：" + "；".join(
    f"{f} 最大 {maxload[:, FAM[f]].max():.2f}、中位 {np.median(maxload[:, FAM[f]]):.2f}、超 2× 的（层, draw）{viol[f]}/{L * D}"
    for f in ("N_A", "N_B", "N_G")) + f"；T 最大 {maxload[:, 0].max():.2f}（层 {int(maxload[:, 0].argmax())}）、中位 {np.median(maxload[:, 0]):.2f}")
md.append(f"- 训练路由器自一致（同一英文 batch 前向两次）：top-8 集合逐 token 完全一致率最小 {meta['det_exact_min']:.4f}，重叠率最小 {meta['det_overlap_min']:.4f}")
md.append(f"- hook 正确性（fp32 重算 h Wᵀ 的 top-8 与模型 gate 输出 top-8 的重叠率）：{meta['hook_agreement']:.5f}")
md.append(f"- N_B 校准集负载匹配总变差：均值 {z['loadtv_B'].mean():.4f}、最大 {z['loadtv_B'].max():.4f}；N_G 对均匀：均值 {z['loadtv_G'].mean():.4f}、最大 {z['loadtv_G'].max():.4f}")
md.append(f"- 逐句计数与逐语言计数一致（最大绝对差）：{tally_match:.0f}")
md.append(f"- 零模型第 0 个 draw 的置换地板 R1（全层平均）：" + "；".join(
    f"{k} {perm[k]['R1'].mean():.4f}" for k in perm) + f"；对应 draw 本身 R1 全层平均：N_A0 {R1[:, 1].mean():.4f}、N_B0 {R1[:, 1 + D].mean():.4f}、N_G0 {R1[:, 1 + 2 * D].mean():.4f}")
md.append(f"- 每语言 token 数：" + "、".join(f"{lg.split('_')[0]} {int(n)}" for lg, n in zip(langs, ntok)))
open(os.path.join(OUT, "tables.md"), "w").write("\n".join(md) + "\n")

summ = {"R1": {f: R1[:, idx].tolist() for f, idx in FAM.items()}, "R4": {f: R4[:, idx].tolist() for f, idx in FAM.items()},
        "R2_50": {f: R2_50[:, idx].tolist() for f, idx in FAM.items()}, "R2_80": {f: R2_80[:, idx].tolist() for f, idx in FAM.items()},
        "R5": {f: R5[:, idx].tolist() for f, idx in FAM.items()},
        "perm_T": {k: {"mean": v.mean(0).tolist(), "p95": np.percentile(v, 95, 0).tolist()} for k, v in perm["T"].items()},
        "boot_T": {k: v.tolist() for k, v in boot.items()}, "U4_R4": U.tolist(), "U4_R1": U1.tolist(),
        "decision": dec, "maxload": maxload.tolist(), "maxload_viol": viol, "tally_match": tally_match,
        "meta": meta}
json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=float)

# ------------------------------------------------------------------ figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
COL = {"T": "#1f1f1e", "N_A": "#2a78d6", "N_B": "#eb6834", "N_G": "#1baf7a"}
LAB = {"T": "trained router", "N_A": "N_A: W·R (Haar, full space)", "N_B": "N_B: repo N1 (subspace rot. + load-matched bias)",
       "N_G": "N_G: Gaussian gate (Frob.-matched, uniform load)"}
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
x = np.arange(L)
for ax, (R, title) in zip(axs, [(R1, "R1: mean pairwise JSD of P(expert | language), 20 languages"),
                                (R4, "R4 (Bandarkar): entropy-normalised JSD to paired English, 19 languages")]):
    for f in ("N_A", "N_B", "N_G"):
        v = R[:, FAM[f]]
        ax.fill_between(x, v.min(1), v.max(1), color=COL[f], alpha=.18, lw=0)
        ax.plot(x, v.mean(1), color=COL[f], lw=1.6, label=LAB[f], ls="-" if f != "N_G" else "--")
    ax.plot(x, R[:, 0], color=COL["T"], lw=2, label=LAB["T"])
    if R is R1:
        ax.plot(x, perm["T"]["R1"].mean(0), color="#8a8984", lw=1.2, ls=":", label="N_perm (label permutation of T)")
    ax.set_xlabel("MoE layer")
    ax.set_title(title, fontsize=8.5, loc="left")
    ax.grid(axis="y", color="#e6e5e0", lw=.6)
    ax.set_ylim(bottom=0)
axs[0].legend(frameon=False, fontsize=7, loc="upper center")
fig.suptitle("Qwen3-30B-A3B, FLORES-200 dev: trained vs random routers on the same hidden states (bands = 8 draws min–max)",
             fontsize=9, x=.01, ha="left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_r1_r4_by_layer.png"), dpi=170)
print("\n".join(md[-12:]))
print(json.dumps({n: r["branches"] for n, r in dec.items()}))
