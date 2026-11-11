#!/usr/bin/env python3
"""E190 analysis (CPU). Reads <run>/prep.pt, nll_*.npy, hookchk_*.json; writes tables_<key>.md, summary_<key>.json,
fig_*_<key>.png into --res. Usage: e190_analyze.py --run DIR --key KEY --tok TOKDIR --res OUTDIR"""
import argparse, glob, json, os
import numpy as np
import torch

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True); ap.add_argument("--key", required=True)
ap.add_argument("--tok", required=True); ap.add_argument("--res", required=True)
ap.add_argument("--nboot", type=int, default=1000)
a = ap.parse_args()
os.makedirs(a.res, exist_ok=True)
from transformers import AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(a.tok)
P = torch.load(os.path.join(a.run, "prep.pt"), weights_only=False)
ME, L, K, ARCH = P["ME"], P["L"], P["K"], P["arch"]
BANDS = {"olmoe": {"first": [0, 1], "mid": list(range(2, 12)), "last": list(range(12, 16))},
         "deepseek_v2": {"first": [0, 1], "mid": list(range(4, 19)), "last": list(range(19, 26))},
         "qwen3_moe": {"first": list(range(0, 4)), "mid": list(range(7, 35)), "last": list(range(35, 48))}}[ARCH]
SIDES = ["srp_Cyrl", "srp_Latn", "hrv_Latn", "bos_Latn", "slv_Latn", "ces_Latn", "pol_Latn", "mkd_Cyrl", "bul_Cyrl",
         "ukr_Cyrl", "rus_Cyrl", "hin_Deva", "urd_Arab", "npi_Deva", "mar_Deva", "snd_Arab", "pes_Arab", "zho_Hans",
         "zho_Hant", "yue_Hant", "eng_Latn"]
UPOS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
        "SCONJ", "SYM", "VERB", "X"]
nll0 = np.load(os.path.join(a.run, "nll_I0.npy"))
V = np.isfinite(nll0)                       # positions with a next-token target
seq = ME["seq"]; NSEQ = int(seq.max()) + 1
chk = {}
for f in glob.glob(os.path.join(a.run, "hookchk_*.json")):
    chk.update(json.load(open(f)))
D = {}
for f in glob.glob(os.path.join(a.run, "nll_*.npy")):
    n = os.path.basename(f)[4:-4]
    if n in ("I0", "orig", "I0_rerun"):
        continue
    D[n] = np.load(f) - nll0
rng = np.random.default_rng(190)
BOOT = rng.integers(0, NSEQ, (a.nboot, NSEQ))
BW = np.zeros((a.nboot, NSEQ), np.float32)
for b in range(a.nboot):
    BW[b] = np.bincount(BOOT[b], minlength=NSEQ)


def stats(dn, sel=None, boot=True):
    m = V if sel is None else (V & sel)
    x = dn[m]
    if x.size == 0:
        return None
    r = {"n": int(x.size), "mean": float(x.mean()), "median": float(np.median(x)), "p90": float(np.quantile(x, .9)),
         "p99": float(np.quantile(x, .99)), "frac_pos": float((x > 0).mean()), "frac_gt1": float((x > 1).mean()),
         "ppl_ratio": float(np.exp(x.mean()))}
    if boot:
        s = np.bincount(seq[m], weights=x, minlength=NSEQ); c = np.bincount(seq[m], minlength=NSEQ).astype(np.float64)
        bm = (BW @ s) / np.maximum(BW @ c, 1)
        r["ci"] = [float(np.quantile(bm, .025)), float(np.quantile(bm, .975))]
    return r


def i2(prefix, sel=None):
    """I2 over 5 seeds: mean of seed means, [min, max], SD; CI of seed 190."""
    ms = [stats(D[f"{prefix}_I2_s{s}"], sel, boot=False)["mean"] for s in range(190, 195) if f"{prefix}_I2_s{s}" in D]
    if not ms:
        return None
    r = stats(D[f"{prefix}_I2_s190"], sel)
    r.update(seed_mean=float(np.mean(ms)), seed_min=float(min(ms)), seed_max=float(max(ms)), seed_sd=float(np.std(ms, ddof=1)) if len(ms) > 1 else 0.0, nseeds=len(ms))
    return r


f3 = lambda x: f"{x:+.4f}" if x is not None else "—"
S = {"key": a.key, "arch": ARCH, "pc": P["pc"], "hookchk": chk}
T = []
T.append(f"# E190 结果表：{a.key}（{ARCH}，L = {L}，K = {K}）\n")
T.append("ΔNLL 单位 nat / token，以 I0（自写 forward、不覆盖）为零点；位置 t 的 ΔNLL = 预测 t+1 的 NLL 差。CI = 按序列聚类自助 1000 次 95%。I2 列给 5 个种子均值、[min, max] 与 SD；其余单种子（190）。\n")
# ---------------------------------------------------------------- §0 positive controls
pc = P["pc"]
T.append("## 0. 阳性对照与覆盖率\n")
T.append("| 项 | 值 |\n|---|---|")
for k, v in pc.items():
    T.append(f"| {k} | {v:.6g} |" if isinstance(v, float) else f"| {k} | {v} |")
bad = {k: v for k, v in chk.items() if v["replaced_rows"] and v["match"] != v["replaced_rows"]}
tot_m = sum(v["match"] for v in chk.values()); tot_r = sum(v["replaced_rows"] for v in chk.values())
T.append(f"| hook 核对：被覆盖行上分派集合 = 目标集合 | {tot_m}/{tot_r}（不符的条件 {len(bad)} 个） |")
for b in ["all"] + list(BANDS):
    if f"{b}_I0x" in D:
        x = D[f"{b}_I0x"][V]
        T.append(f"| I0x（{b}：用干净集合覆盖自身）mean / max abs ΔNLL | {x.mean():.2e} / {np.abs(x).max():.2e} |")
# H coverage
bands_mid = BANDS["mid"]
Hmid = np.full(len(P["idcnt"]), np.nan); Hmid[P["H_ids"]] = P["H_T"][bands_mid].mean(0)
HNB = np.full(len(P["idcnt"]), np.nan); HNB[P["H_ids"]] = P["H_NB"][bands_mid].mean(0)
Htok, HNBtok = Hmid[ME["inp"]], HNB[ME["inp"]]
cov = float(np.isfinite(Htok[V]).mean())
from scipy.stats import spearmanr  # noqa: E402
sp = float(spearmanr(P["H_T"][bands_mid].mean(0), P["H_NB"][bands_mid].mean(0)).correlation)
T.append(f"| H(e∣id) 覆盖（评估 token 中 id 在拟合集 ≥ 30 次） | {cov:.3f}（{len(P['H_ids'])} 个 id） |")
T.append(f"| Spearman_id(H_T, H_NB) mid（E186 英语视图 .85） | {sp:.3f} |")
S.update(H_coverage=cov, H_spearman_T_NB=sp)
qs = np.nanquantile(Htok[V], [1 / 3, 2 / 3])
terc = np.where(np.isnan(Htok), -1, np.digitize(Htok, qs))
T.append(f"| H 三分位切点（mid T，bit；评估 token 加权） | {qs[0]:.2f} / {qs[1]:.2f} |")
# E186 extremes recheck
idpos = {int(i): k for k, i in enumerate(P["H_ids"])}
chk_ids = []
for s in ["s", "ing", "es", "ed", "Great", "The", "This", "In", " the", " \""]:
    ii = tok.convert_tokens_to_ids(tok.tokenize(s)) if s.strip() else []
    if len(ii) == 1 and ii[0] in idpos:
        chk_ids.append(f"`{s}` {Hmid[ii[0]]:.2f}/{HNB[ii[0]]:.2f}")
T.append(f"| E186 极端 id 复核（H_T / H_NB mid，bit） | {'；'.join(chk_ids)} |\n")
# ---------------------------------------------------------------- §1 main
T.append("## 1. 层段 × 干预（全部评估 token）\n")
T.append("| 层段 | 干预 | mean ΔNLL [95% CI] | I2 种子 [min, max] / SD | median | p90 | p99 | P(Δ>0) | P(Δ>1) | PPL 比 |")
T.append("|---|---|---|---|---|---|---|---|---|---|")
S["bands"] = {}
for b in ["all"] + list(BANDS):
    S["bands"][b] = {}
    for c in ["I0x", "I1", "I2", "I3", "I4", "I5", "I6", "I1_w2", "I2_w2", "I3_w2", "I4_w2", "I5_w2"]:
        if c == "I2":
            r = i2(b)
        else:
            nm = f"{b}_{c}" if not c.endswith("_w2") or c.startswith("I1") else f"{b}_{c.split('_')[0]}_w2"
            r = stats(D[nm]) if nm in D else None
        if r is None:
            continue
        S["bands"][b][c] = r
        sd = f"[{r['seed_min']:+.4f}, {r['seed_max']:+.4f}] / {r['seed_sd']:.4f}" if c == "I2" else ""
        T.append(f"| {b} | {c} | {r['mean']:+.4f} [{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}] | {sd} | {r['median']:+.4f} | "
                 f"{r['p90']:+.4f} | {r['p99']:+.4f} | {r['frac_pos']:.3f} | {r['frac_gt1']:.4f} | {r['ppl_ratio']:.4f} |")
T.append("")
T.append("**派生量**（全部层 / 中段）：")
for b in ("all", "mid"):
    B = S["bands"].get(b, {})
    if "I2" in B and "I3" in B:
        i2m, i3m = B["I2"]["seed_mean"], B["I3"]["mean"]
        txt = f"- {b}：I2 {i2m:+.4f}，I3 {i3m:+.4f}，I2 − I3 = {i2m - i3m:+.4f}，I3 / I2 = {i3m / i2m:.3f}"
        if "I4" in B:
            txt += f"，I4 / I2 = {B['I4']['mean'] / i2m:.3f}"
        if "I1" in B:
            txt += f"，I1 / I2 = {B['I1']['mean'] / i2m:.3f}"
        if "I5" in B:
            txt += f"，I2 / I5 = {i2m / B['I5']['mean']:.4f}"
        if "I6" in B:
            txt += f"，I2 / I6 = {i2m / B['I6']['mean']:.4f}"
        T.append(txt)
T.append("")
# ---------------------------------------------------------------- §2 per layer
if "L0_I1" in D:
    T.append("## 2. 单层替换（逐层均值 ΔNLL）\n")
    T.append("| 层 | I1 | I2 种子均值 [min, max] | I3 | I4 | I5 | I6 | I2 − I3 | I3 / I2 |")
    T.append("|---|---|---|---|---|---|---|---|---|")
    S["layers"] = {}
    for l in range(L):
        g = lambda c: stats(D[f"L{l}_{c}"], boot=False)["mean"] if f"L{l}_{c}" in D else np.nan
        r2 = i2(f"L{l}")
        row = {"I1": g("I1"), "I2": r2["seed_mean"], "I2_min": r2["seed_min"], "I2_max": r2["seed_max"],
               "I3": g("I3"), "I4": g("I4"), "I5": g("I5"), "I6": g("I6")}
        S["layers"][l] = row
        T.append(f"| {l} | {row['I1']:+.4f} | {row['I2']:+.4f} [{row['I2_min']:+.4f}, {row['I2_max']:+.4f}] | {row['I3']:+.4f} | "
                 f"{row['I4']:+.4f} | {row['I5']:+.4f} | {row['I6']:+.4f} | {row['I2'] - row['I3']:+.4f} | {row['I3'] / row['I2']:.2f} |")
    T.append("")
# ---------------------------------------------------------------- token classes
strs = {}
def tstr(i):
    if i not in strs:
        strs[i] = tok.decode([int(i)])
    return strs[i]
uniq = np.unique(ME["inp"])
has_letter = {int(i): any(ch.isalpha() for ch in tstr(i)) for i in uniq}
lead_sp = {int(i): tstr(i).startswith(" ") for i in uniq}
HL = np.array([has_letter[int(i)] for i in ME["inp"]]); LS = np.array([lead_sp[int(i)] for i in ME["inp"]])
FN = {"ADP", "AUX", "CCONJ", "DET", "PART", "PRON", "SCONJ"}; CT = {"NOUN", "VERB", "ADJ", "ADV", "PROPN", "NUM", "INTJ"}
up = ME["upos"]
upn = np.array([UPOS[u] if u >= 0 else "" for u in up])
fq = P["idcnt"][ME["inp"]].astype(np.float64)
fqq = np.quantile(fq[V], [.2, .4, .6, .8])
fbin = np.digitize(fq, fqq)
pb = np.digitize(ME["pos"], [1, 4, 16, 64, 256])
PBN = ["0", "1–3", "4–15", "16–63", "64–255", "≥256"]
script = np.array([SIDES[s].split("_")[1] if s >= 0 else "en(wiki/UD)" for s in ME["side"]])
CORP = ["FLORES 非英", "FLORES eng", "wikitext test", "UD EWT test"]
classes = [("全部", np.ones_like(V))]
classes += [(f"位置段 {PBN[i]}", pb == i) for i in range(6)]
classes += [("UD 功能词（词末）", np.isin(upn, list(FN))), ("UD 内容词（词末）", np.isin(upn, list(CT))),
            ("UD 标点", np.isin(upn, ["PUNCT", "SYM"])), ("UD 词内片段（非词末）", (ME["corpus"] == 3) & (up < 0))]
classes += [(f"拟合集频率五分位 {i + 1}{'（最稀）' if i == 0 else '（最频）' if i == 4 else ''}", fbin == i) for i in range(5)]
classes += [("含字母", HL), ("不含字母", ~HL), ("字母·前导空格（词首）", HL & LS), ("字母·无前导空格（词中 / 词尾片段 / 句首）", HL & ~LS)]
classes += [(f"语料 {CORP[i]}", ME["corpus"] == i) for i in range(4)]
for sc in ["Latn", "Cyrl", "Deva", "Arab", "Hans", "Hant"]:
    classes.append((f"FLORES 非英 文字 {sc}", (ME["corpus"] == 0) & (script == sc)))
classes += [(f"H(e∣id) 三分位 {n}", terc == i) for i, n in enumerate(("低", "中", "高"))] + [("H(e∣id) 无值（拟合集 < 30 次）", terc == -1)]
hnq = np.nanquantile(HNBtok[V], [1 / 3, 2 / 3]); tnb = np.where(np.isnan(HNBtok), -1, np.digitize(HNBtok, hnq))
classes += [(f"H_NB(e∣id) 三分位 {n}", tnb == i) for i, n in enumerate(("低", "中", "高"))]
dlt = Htok - HNBtok; dq = np.nanquantile(dlt[V], [1 / 3, 2 / 3]); tdl = np.where(np.isnan(dlt), -1, np.digitize(dlt, dq))
classes += [(f"H_T − H_NB 三分位 {n}（低 = T 比几何更查表）", tdl == i) for i, n in enumerate(("低", "中", "高"))]
T.append("## 3. 按 token 类（在该类 token 上做预测时的 ΔNLL；归属注见卡）\n")
S["classes"] = {}
for b in ("all", "mid"):
    cs = [c for c in ("I1", "I2", "I3", "I4", "I5", "I6") if (c == "I2" and f"{b}_I2_s190" in D) or f"{b}_{c}" in D]
    T.append(f"### 层段 {b}\n")
    T.append("| 类 | n | " + " | ".join(cs) + " | I3 / I2 | I2 种子 SD |")
    T.append("|---|---|" + "---|" * len(cs) + "---|---|")
    S["classes"][b] = {}
    for nm, msk in classes:
        row = {}
        for c in cs:
            if c == "I2":
                r = i2(b, msk); row[c] = r["seed_mean"]; row["I2_sd"] = r["seed_sd"]; n = r["n"]
            else:
                r = stats(D[f"{b}_{c}"], msk, boot=False); row[c] = r["mean"] if r else np.nan
        S["classes"][b][nm] = dict(row, n=int((V & msk).sum()))
        T.append(f"| {nm} | {int((V & msk).sum())} | " + " | ".join(f"{row[c]:+.4f}" for c in cs) +
                 f" | {row.get('I3', np.nan) / row['I2']:.2f} | {row.get('I2_sd', np.nan):.4f} |")
    T.append("")
# H-tercile class-restricted I2
T.append("## 4. 只替换某一 H(e∣id) 三分位的 token（全部层，I2 种子 190）\n")
T.append("每行只替换该三分位里 I2 可替换的 token，其余 token 保持 T。「总 ΔNLL / 被替换 token」= 全评估集 ΔNLL 之和 ÷ 被替换 token 数（含对其他 token 的下游效应）。\n")
T.append("| 被替换的三分位 | 被替换 token 数 | 全集 mean ΔNLL [CI] | 总 ΔNLL / 被替换 token | 在被替换 token 本身上的 mean ΔNLL | 在其余 token 上的 mean ΔNLL |")
T.append("|---|---|---|---|---|---|")
S["restricted"] = {}
don = P["donors"]["I2_s190"]
for i, nm in enumerate(("Hlo", "Hmid", "Hhi")):
    k = f"all_I2_s190_{nm}"
    if k not in D:
        continue
    rep = (terc == i) & (don >= 0)
    r = stats(D[k]); x = D[k]
    tot = float(np.nansum(x[V])); nrep = int(rep.sum())
    on = float(x[V & rep].mean()); off_ = float(x[V & ~rep].mean())
    S["restricted"][nm] = dict(r, n_replaced=nrep, total_per_replaced=tot / nrep, on_replaced=on, on_others=off_)
    T.append(f"| {nm} | {nrep} | {r['mean']:+.4f} [{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}] | {tot / nrep:+.4f} | {on:+.4f} | {off_:+.4f} |")
T.append("")
# ---------------------------------------------------------------- POST-HOC: position-0 tokens left un-replaced
ph = [k for k in sorted(D) if k.endswith("_pos1")]
if ph:
    T.append("## 4b. POST-HOC（11-11，看过 §1–§3 后加）：位置 0 的 token 不替换（无 BOS 时序列首 token 是注意力汇点 / 句首路由）\n")
    T.append("| 条件 | mean ΔNLL [95% CI] | 位置 ≥ 1 上的 mean | H 三分位 低 / 中 / 高（预测位置） | 同条件含位置 0（§1 / §2） |")
    T.append("|---|---|---|---|---|")
    S["posthoc_pos1"] = {}
    for k in ph:
        r = stats(D[k]); r1 = stats(D[k], ME["pos"] >= 1, boot=False)
        ht = [stats(D[k], terc == i, boot=False)["mean"] for i in range(3)]
        base = k.replace("_pos1", "")
        b0 = stats(D[base], boot=False)["mean"] if base in D else np.nan
        S["posthoc_pos1"][k] = dict(r, mean_pos_ge1=r1["mean"], H_terciles=ht, with_pos0=b0)
        T.append(f"| {k} | {r['mean']:+.4f} [{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}] | {r1['mean']:+.4f} | " + " / ".join(f"{x:+.3f}" for x in ht) + f" | {b0:+.4f} |")
    T.append("")
# ---------------------------------------------------------------- §5 change magnitude (single-layer conditions)
if "L0_I1" in D:
    T.append("## 5. ΔNLL 与被替换层的路由变化量（单层条件，16 层合并）\n")
    T.append("变化比例 = 1 − |S_new ∩ S_T| / K（被替换层上）；I1 的 S_new 为查表集合（未见 id 保留 T），I2–I5 为供体的干净集合。\n")
    cs_ = P["clean_sel"]
    def ovl(A, B):
        oh = np.zeros((A.shape[0], int(max(A.max(), B.max())) + 1), bool)
        r = np.arange(A.shape[0])[:, None]
        oh[r, A] = True
        return oh[r, B].sum(1) / K
    bins = [0, 1e-9, .25, .5, .75, 1.0 + 1e-9]
    BN = ["0", "(0, .25)", "[.25, .5)", "[.5, .75)", "[.75, 1]"]
    res = {}
    for c in ("I1", "I2", "I3", "I5"):
        acc = {i: [] for i in range(5)}; t1acc = {0: [], 1: []}
        for l in range(L):
            nm = f"L{l}_{c}_s190" if c == "I2" else f"L{l}_{c}"
            if nm not in D:
                continue
            A = cs_[l].astype(np.int64)
            if c == "I1":
                Bs = P["look_sel"][l][ME["inp"]].astype(np.int64)
                okk = P["look_ok"][l][ME["inp"]]
                Bs = np.where(okk[:, None], Bs, A)
            else:
                dn = P["donors"][f"{c}_s190"]
                Bs = np.where((dn >= 0)[:, None], cs_[l][np.maximum(dn, 0)], cs_[l]).astype(np.int64)
            ch = 1 - ovl(A, Bs); t1 = (A[:, 0] != Bs[:, 0])
            if c == "I1":   # lookup sets are in frequency order, not gate order: top-1 change = clean top-1 not the lookup's most frequent
                pass
            bi = np.digitize(ch, bins) - 1
            x = D[nm]
            for i in range(5):
                mk = V & (bi == i)
                acc[i].append((x[mk].sum(), mk.sum()))
            for i in (0, 1):
                mk = V & (t1 == bool(i))
                t1acc[i].append((x[mk].sum(), mk.sum()))
        res[c] = {"bins": {BN[i]: (sum(s for s, _ in acc[i]) / max(sum(n for _, n in acc[i]), 1), int(sum(n for _, n in acc[i]))) for i in range(5)},
                  "top1": {("变" if i else "不变"): (sum(s for s, _ in t1acc[i]) / max(sum(n for _, n in t1acc[i]), 1), int(sum(n for _, n in t1acc[i]))) for i in (0, 1)}}
    S["change"] = res
    T.append("| 干预 | " + " | ".join(f"变化 {b}" for b in BN) + " | top-1 不变 | top-1 变 |")
    T.append("|---|" + "---|" * 7)
    for c, r in res.items():
        T.append(f"| {c} | " + " | ".join(f"{r['bins'][b][0]:+.4f} (n={r['bins'][b][1]})" for b in BN) + " | " +
                 " | ".join(f"{r['top1'][k][0]:+.4f} (n={r['top1'][k][1]})" for k in ("不变", "变")) + " |")
    T.append("\n（I1 的 top-1 比较用的是查表集合按频率排序的第一个，不是门值序，仅作参照。）\n")
# ---------------------------------------------------------------- §6 examples
T.append("## 6. 原始样例：全部层 I2（种子 190）ΔNLL 最大 / 最小各 20 个 token\n")
T.append("⟦x⟧ = 做预测的位置（其输入 token），→ 后为要预测的真实下一 token；H = H_T(e∣id) mid（bit）；变化 = 中段各层集合变化比例的均值。\n")
x = D.get("all_I2_s190")
if x is not None:
    dn = P["donors"]["I2_s190"]
    cs_ = P["clean_sel"]
    ex = {}
    for nm, order in (("最大", np.argsort(-np.where(V, x, -np.inf))[:20]), ("最小", np.argsort(np.where(V, x, np.inf))[:20])):
        T.append(f"**ΔNLL {nm}**\n")
        T.append("| ΔNLL | 上下文 | → 下一 | H | 变化 | 语料 |")
        T.append("|---|---|---|---|---|---|")
        ex[nm] = []
        for t in order:
            t = int(t)
            s0 = t - ME["pos"][t]
            ctx = tok.decode(ME["inp"][max(s0, t - 12):t].tolist()) + "⟦" + tstr(ME["inp"][t]) + "⟧"
            nx = tstr(ME["nxt"][t])
            if dn[t] >= 0:
                chs = np.mean([1 - len(set(cs_[l][t].tolist()) & set(cs_[l][dn[t]].tolist())) / K for l in BANDS["mid"]])
            else:
                chs = 0.0
            ctx_s = ctx.replace("|", "\\|").replace("\n", " ")
            T.append(f"| {x[t]:+.3f} | {ctx_s} | {nx.replace('|', '\\|')!r} | {Htok[t]:.2f} | {chs:.2f} | {CORP[ME['corpus'][t]]} |")
            ex[nm].append({"dnll": float(x[t]), "ctx": ctx, "next": nx, "H": float(Htok[t]), "change_mid": float(chs)})
        T.append("")
    S["examples"] = ex
# ---------------------------------------------------------------- §7 reference
T.append("## 7. 参照\n")
T.append("| 语料 | token 数 | I0 mean NLL | I0 PPL |\n|---|---|---|---|")
for i in range(4):
    mk = V & (ME["corpus"] == i)
    T.append(f"| {CORP[i]} | {int(mk.sum())} | {nll0[mk].mean():.3f} | {np.exp(nll0[mk].mean()):.2f} |")
cs_ = P["clean_sel"]
ov = []
for l in (range(L) if P["look_sel"].shape[1] > 1 else []):
    A = cs_[l].astype(np.int64); Bs = P["look_sel"][l][ME["inp"]].astype(np.int64)
    oh = np.zeros((A.shape[0], int(max(A.max(), Bs.max())) + 1), bool); r = np.arange(A.shape[0])[:, None]; oh[r, A] = True
    ov.append(float((oh[r, Bs].sum(1) / K)[P["look_ok"][l][ME["inp"]]].mean()))
S["T_vs_lookup_overlap"] = ov
T.append(f"\n评估集上 T 与 I1 查表集合的平均 top-{K} 重合（查表可用的 token）逐层：" + " ".join(f"{v:.2f}" for v in ov))
d2 = P["donors"]["I2_s190"]
ovd = []
for l in range(L):
    mk = d2 >= 0
    A = cs_[l][mk].astype(np.int64); Bs = cs_[l][d2[mk]].astype(np.int64)
    oh = np.zeros((A.shape[0], int(max(A.max(), Bs.max())) + 1), bool); r = np.arange(A.shape[0])[:, None]; oh[r, A] = True
    ovd.append(float((oh[r, Bs].sum(1) / K).mean()))
S["T_vs_I2donor_overlap"] = ovd
T.append(f"\nT 与 I2 供体（同 id 另一次出现）集合的平均 top-{K} 重合逐层：" + " ".join(f"{v:.2f}" for v in ovd) + "\n")
open(os.path.join(a.res, f"tables_{a.key}.md"), "w").write("\n".join(T))
json.dump(S, open(os.path.join(a.res, f"summary_{a.key}.json"), "w"), indent=1, default=float)
# ---------------------------------------------------------------- figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
if "layers" in S:
    fig, ax = plt.subplots(figsize=(7, 4))
    ls = np.arange(L)
    for c, col in (("I1", "#7f7f7f"), ("I3", "#2ca02c"), ("I4", "#9467bd"), ("I5", "#d62728"), ("I6", "#000000")):
        ax.plot(ls, [S["layers"][l][c] for l in ls], "o-", ms=3, label=c, color=col)
    ax.plot(ls, [S["layers"][l]["I2"] for l in ls], "o-", ms=3, label="I2 (5 seeds)", color="#1f77b4")
    ax.fill_between(ls, [S["layers"][l]["I2_min"] for l in ls], [S["layers"][l]["I2_max"] for l in ls], color="#1f77b4", alpha=.25)
    ax.set_yscale("symlog", linthresh=1e-3); ax.set_xlabel("replaced layer"); ax.set_ylabel("mean ΔNLL (nat/token)")
    ax.set_title(f"E190 {a.key}: single-layer routing replacement"); ax.legend(fontsize=7, ncol=3); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(a.res, f"fig_layers_{a.key}.png"), dpi=130); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
edges = np.concatenate([-np.logspace(1, -3, 60), np.logspace(-3, 1, 60)])
for c, col in (("all_I1", "#7f7f7f"), ("all_I2_s190", "#1f77b4"), ("all_I3", "#2ca02c"), ("all_I5", "#d62728"), ("all_I6", "#000000")):
    if c in D:
        h, _ = np.histogram(np.clip(D[c][V], -9.99, 9.99), bins=edges)
        ax.step(edges[:-1], h / V.sum(), where="post", label=c.replace("all_", ""), color=col)
ax.set_xscale("symlog", linthresh=1e-3); ax.set_yscale("log"); ax.set_xlabel("per-token ΔNLL (nat), all layers replaced")
ax.set_ylabel("fraction of tokens"); ax.legend(fontsize=7); ax.grid(alpha=.3); ax.set_title(f"E190 {a.key}: ΔNLL distribution")
fig.tight_layout(); fig.savefig(os.path.join(a.res, f"fig_dist_{a.key}.png"), dpi=130); plt.close(fig)
print("written", a.res)
