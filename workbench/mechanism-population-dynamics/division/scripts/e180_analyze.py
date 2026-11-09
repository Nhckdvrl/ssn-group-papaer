#!/usr/bin/env python3
"""E180 analysis (card: division/experiments/E180-script-vs-language-routing.md).

Per layer, routing-distribution JSD (base 2; expert-usage P(e) from top-k counts over equalised tokens) between
pairs P0-P4 (+ secondary hin/urd, zho), for T, N_A (8), N_B (8); paired sentence bootstrap (1000); H-language /
H-script layer sets; pre-registered decision table; token-type-matched readout (letterless token types,
within-type label-shuffle null); last-8-layer stratification by predicted-next-token script; one figure per model.

Usage: e180_analyze.py OUT_DIR key=CAPTURE_DIR [key=CAPTURE_DIR ...]   (key in qwen3, gptoss, olmoe)
       e180_analyze.py OUT_DIR --fig-only   (redraw figures from OUT_DIR/summary.json)
"""
import json, os, sys, unicodedata
import numpy as np

OUT = sys.argv[1]
CAPS = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
os.makedirs(OUT, exist_ok=True)
NAME = {"qwen3": "Qwen3-30B-A3B", "gptoss": "GPT-OSS-20B", "olmoe": "OLMoE-1B-7B-0125-Instruct"}
HF = {"qwen3": "Qwen/Qwen3-30B-A3B", "gptoss": "openai/gpt-oss-20b", "olmoe": "allenai/OLMoE-1B-7B-0125-Instruct"}
SEG = {48: dict(edge=list(range(0, 4)) + list(range(44, 48)), mid=list(range(7, 35))),
       24: dict(edge=[0, 1, 22, 23], mid=list(range(4, 18))),
       16: dict(edge=[0, 1, 14, 15], mid=list(range(2, 12)))}
NB = 1000
PAIRS = {
    "P1": [("srp_Cyrl", "srp_Latn")],
    "P2n": [("srp_Cyrl", "mkd_Cyrl"), ("srp_Cyrl", "bul_Cyrl")],
    "P2hrv": [("srp_Latn", "hrv_Latn")],
    "P2bos": [("srp_Latn", "bos_Latn")],
    "P3": [("srp_Cyrl", "rus_Cyrl"), ("srp_Cyrl", "ukr_Cyrl"), ("srp_Latn", "ces_Latn"), ("srp_Latn", "pol_Latn"),
           ("srp_Latn", "slv_Latn")],
    "P4": [("srp_Cyrl", x) for x in ("slv_Latn", "ces_Latn", "pol_Latn")] +
          [("srp_Latn", x) for x in ("mkd_Cyrl", "bul_Cyrl", "rus_Cyrl", "ukr_Cyrl")],
    "P4hrv": [("srp_Cyrl", "hrv_Latn")],
    "P1i": [("hin_Deva", "urd_Arab")],
    "P2i": [("hin_Deva", "npi_Deva"), ("hin_Deva", "mar_Deva"), ("urd_Arab", "snd_Arab"), ("urd_Arab", "pes_Arab")],
    "P1z": [("zho_Hans", "zho_Hant")],
    "P2z": [("zho_Hant", "yue_Hant")],
}
SPLITS = {"P0": "srp_Cyrl", "P0L": "srp_Latn"}
CONTRASTS = {"main": ("P1", "P2n"), "hrv": ("P1", "P2hrv"), "hin_urd": ("P1i", "P2i"), "zho": ("P1z", "P2z")}


def jsd2(P, Q):
    M = 0.5 * (P + Q)
    f = lambda a, b: np.where(a > 0, a * np.log2(np.where(a > 0, a, 1) / np.where(b > 0, b, 1)), 0).sum(-1)
    return 0.5 * f(P, M) + 0.5 * f(Q, M)


def norm(C):
    return C / np.maximum(C.sum(-1, keepdims=True), 1e-30)


def runs(layers):
    out, cur = [], []
    for l in sorted(layers):
        if cur and l == cur[-1] + 1:
            cur.append(l)
        else:
            if cur:
                out.append(cur)
            cur = [l]
    if cur:
        out.append(cur)
    return out


def fmt_runs(layers):
    r = runs(layers)
    return "∅" if not r else ", ".join(f"{a[0]}" if len(a) == 1 else f"{a[0]}–{a[-1]}" for a in r)


def script_class(s):
    if not s or "�" in s:
        return "other"
    cats = [unicodedata.category(c) for c in s]
    names = [unicodedata.name(c, "") for c in s]
    has_l = any(c[0] in "LM" for c in cats)
    if not has_l:
        return "neutral"
    cyr = any(c[0] in "LM" and "CYRILLIC" in n for c, n in zip(cats, names))
    lat = any(c[0] in "LM" and "LATIN" in n for c, n in zip(cats, names))
    if cyr and not lat:
        return "cyr"
    if lat and not cyr:
        return "lat"
    return "other"


def decide(lang_set, script_set, L, fam_sets):
    """Pre-registered decision table on T's sets; fam_sets = {fam: H-language set}."""
    if not lang_set:
        return ("(i) H-script everywhere" if len(script_set) >= 0.9 * L
                else f"(iv) inconclusive: no H-language layer but H-script only {len(script_set)}/{L} layers"), {}
    r = runs(lang_set)
    band = r[0]
    if len(r) == 1 and len(band) >= 2 and band[0] >= 2 and band[-1] <= L - 3:
        per = {}
        for f, s in fam_sets.items():
            ov = len(set(band) & set(s)) / len(band)
            per[f] = ("(ii) band in T, not in " + f if ov < 0.5 else "(iii) band in T and in " + f) + f" (overlap {ov:.2f})"
        return "band " + fmt_runs(band), per
    return f"(iv) inconclusive: H-language set {fmt_runs(lang_set)} (non-contiguous / edge / length 1)", {}


def analyze(key, CAP):
    meta = json.load(open(os.path.join(CAP, "meta.json")))
    langs, NS, D, K, E = meta["langs"], meta["n_sent"], meta["draws"], meta["K"], meta["E"]
    PS = np.load(os.path.join(CAP, "persent.npy"), mmap_mode="r")
    L, NU, NR, _ = PS.shape
    FAM = {"T": [0], "N_A": list(range(1, 1 + D)), "N_B": list(range(1 + D, 1 + 2 * D))}
    rng = np.random.default_rng(180)
    Wb = np.stack([np.bincount(rng.integers(0, NS, NS), minlength=NS) for _ in range(NB)]).astype(np.float32)
    perm = np.random.default_rng(180).permutation(NS)
    hA = np.zeros(NS, bool); hA[perm[:NS // 2]] = True
    li = {lg: i for i, lg in enumerate(langs)}
    pairs = {k: v for k, v in PAIRS.items() if all(a in li and b in li for a, b in v)}
    splits = {k: v for k, v in SPLITS.items() if v in li}
    Dp = {k: np.zeros((L, NR)) for k in list(pairs) + list(splits)}
    Db = {k: np.zeros((NB, L, NR), np.float32) for k in list(pairs) + list(splits)}
    sumchk = 0.0
    for l in range(L):
        pt, bt = {}, {}
        for lg, i in li.items():
            C = np.asarray(PS[l, i * NS:(i + 1) * NS], dtype=np.float32).reshape(NS, NR * E)
            pt[lg] = C.sum(0).reshape(NR, E)
            bt[lg] = (Wb @ C).reshape(NB, NR, E)
            if lg in splits.values():
                pt[lg + "|A"] = C[hA].sum(0).reshape(NR, E)
                pt[lg + "|B"] = C[~hA].sum(0).reshape(NR, E)
                bt[lg + "|A"] = ((Wb * hA) @ C).reshape(NB, NR, E)
                bt[lg + "|B"] = ((Wb * ~hA) @ C).reshape(NB, NR, E)
        for k, plist in pairs.items():
            Dp[k][l] = np.mean([jsd2(norm(pt[a]), norm(pt[b])) for a, b in plist], 0)
            Db[k][:, l] = np.mean([jsd2(norm(bt[a]), norm(bt[b])) for a, b in plist], 0)
        for k, lg in splits.items():
            Dp[k][l] = jsd2(norm(pt[lg + "|A"]), norm(pt[lg + "|B"]))
            Db[k][:, l] = jsd2(norm(bt[lg + "|A"]), norm(bt[lg + "|B"]))
    # ---------------------------------------------------------------- contrasts and sets
    res = {"model": NAME[key], "L": L, "D": {k: v.tolist() for k, v in Dp.items()}, "contrasts": {}}
    for cname, (a, b) in CONTRASTS.items():
        if a not in pairs or b not in pairs:
            continue
        dpt, dbt = Dp[a] - Dp[b], Db[a] - Db[b]
        cr = {}
        for f, idx in FAM.items():
            p = dpt[:, idx].mean(1)
            bs = dbt[:, :, idx].mean(2)
            lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
            neg = (dpt[:, idx] < 0).sum(1)
            cr[f] = {"delta": p.tolist(), "lo": lo.tolist(), "hi": hi.tolist(), "n_neg_draws": neg.tolist(),
                     "draw_min": dpt[:, idx].min(1).tolist(), "draw_max": dpt[:, idx].max(1).tolist(),
                     "lang_set": [l for l in range(L) if hi[l] < 0], "script_set": [l for l in range(L) if lo[l] > 0],
                     "point_lang_set": [l for l in range(L) if p[l] < 0],
                     "edge_mean": float(p[SEG[L]["edge"]].mean()), "mid_mean": float(p[SEG[L]["mid"]].mean())}
        dec, per = decide(cr["T"]["lang_set"], cr["T"]["script_set"], L,
                          {f: cr[f]["lang_set"] for f in ("N_A", "N_B")})
        nulls_script_everywhere = {f: (not cr[f]["lang_set"]) and len(cr[f]["script_set"]) >= 0.9 * L
                                   for f in ("N_A", "N_B")}
        cr["decision"] = {"T": dec, "per_null": per, "nulls_H_script_everywhere": nulls_script_everywhere}
        res["contrasts"][cname] = cr
    # floor check: P0 / min over pairs P1..P4 (T)
    main_pairs = [k for k in ("P1", "P2n", "P2hrv", "P3", "P4") if k in pairs]
    mn = np.min([Dp[k][:, 0] for k in main_pairs], 0)
    res["floor_ratio_T"] = (Dp["P0"][:, 0] / mn).tolist() if "P0" in Dp else None
    res["Dci_T"] = {k: np.percentile(Db[k][:, :, 0], [2.5, 97.5], axis=0).tolist() for k in Dp}
    res["Dnull"] = {k: {f: [Dp[k][:, FAM[f]].mean(1).tolist(), Dp[k][:, FAM[f]].min(1).tolist(),
                            Dp[k][:, FAM[f]].max(1).tolist()] for f in ("N_A", "N_B")} for k in Dp}
    # ---------------------------------------------------------------- token-level readouts
    tm = np.load(os.path.join(CAP, "tokmeta.npz"))
    TK = np.load(os.path.join(CAP, "topk.npy"), mmap_mode="r")  # [L, NTOK, 3, K]
    tlang, tsid, tinp, tpred, tsel = tm["lang"], tm["sid"], tm["inp"], tm["pred"], tm["sel"]
    # sanity: per-sentence selected counts equal within groups; T counts from topk == persent
    eqchk = 0
    for g, gl in meta["groups"].items():
        gl = [x for x in gl if x in li]
        if not gl:
            continue
        cnts = np.stack([np.bincount(tsid[(tlang == li[x]) & tsel], minlength=NS) for x in gl])
        eqchk = max(eqchk, int((cnts.max(0) - cnts.min(0)).max()))
    res["equalisation_max_diff"] = eqchk
    l0 = L // 2
    s = li["srp_Cyrl"]
    m = (tlang == s) & tsel
    oh = np.bincount(np.asarray(TK[l0, m, 0]).reshape(-1), minlength=E)
    res["topk_vs_persent_absdiff"] = float(np.abs(oh - np.asarray(PS[l0, s * NS:(s + 1) * NS, 0]).sum(0)).max())
    res["persent_total_check"] = int(np.asarray(PS[l0, s * NS:(s + 1) * NS, 0]).sum() - K * m.sum())

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(HF[key])
    vocab_ids = np.unique(np.concatenate([tinp, tpred]))
    cls = {int(t): script_class(tok.decode([int(t)])) for t in vocab_ids}
    inp_cls = np.array([cls[int(t)] for t in tinp])
    pred_cls = np.array([cls[int(t)] for t in tpred])
    res["pred_class_share"] = {lg: {c: float(np.mean(pred_cls[tlang == li[lg]] == c)) for c in
                                    ("neutral", "cyr", "lat", "other")}
                               for lg in ("srp_Cyrl", "srp_Latn", "mkd_Cyrl", "bul_Cyrl", "hrv_Latn") if lg in li}

    def onehot(l, idx, r):
        O = np.zeros((len(idx), E), np.float32)
        S = np.asarray(TK[l, idx, r]).astype(np.int64)
        np.add.at(O, (np.repeat(np.arange(len(idx)), K), S.reshape(-1)), 1.0)
        return O

    # 辅读数 1: letterless token types, type-matched, within-type label shuffle
    tt_pairs = {"P1": ("srp_Cyrl", "srp_Latn"), "Cyrl-mkd": ("srp_Cyrl", "mkd_Cyrl"),
                "Cyrl-bul": ("srp_Cyrl", "bul_Cyrl"), "P2hrv": ("srp_Latn", "hrv_Latn")}
    NP = 100
    tt = {}
    rr = np.random.default_rng(180)
    for pn, (a, b) in tt_pairs.items():
        ma = np.where((tlang == li[a]) & (inp_cls == "neutral"))[0]
        mb = np.where((tlang == li[b]) & (inp_cls == "neutral"))[0]
        ta, tb = tinp[ma], tinp[mb]
        idxA, idxB, grp = [], [], []
        for t in np.intersect1d(ta, tb):
            ia, ib = ma[ta == t], mb[tb == t]
            n = min(len(ia), len(ib))
            idxA.append(rr.choice(ia, n, replace=False)); idxB.append(rr.choice(ib, n, replace=False))
        idxA, idxB = np.concatenate(idxA), np.concatenate(idxB)
        allidx = np.concatenate([idxA, idxB])
        types = tinp[allidx]
        lab0 = np.r_[np.ones(len(idxA)), np.zeros(len(idxB))]
        labs = np.zeros((NP, len(allidx)), np.float32)
        order = np.argsort(types, kind="stable")
        bounds = np.flatnonzero(np.diff(types[order])) + 1
        for p in range(NP):
            lp = lab0.copy()
            for g in np.split(order, bounds):
                lp[g] = rr.permutation(lab0[g])
            labs[p] = lp
        out = np.zeros((L, 3, 3))  # observed, perm mean, perm p95
        for l in range(L):
            for r in range(3):
                O = onehot(l, allidx, r)
                obs = jsd2(norm(lab0 @ O), norm((1 - lab0) @ O))
                pj = jsd2(norm(labs @ O), norm((1 - labs) @ O))
                out[l, r] = obs, pj.mean(), np.percentile(pj, 95)
        tt[pn] = {"n_occ_per_side": int(len(idxA)), "n_types": int(len(np.unique(types))), "vals": out.tolist()}
    ex = {pn: np.array(v["vals"])[:, :, 0] - np.array(v["vals"])[:, :, 1] for pn, v in tt.items()}
    ex["P2n"] = 0.5 * (ex["Cyrl-mkd"] + ex["Cyrl-bul"])
    res["tokentype"] = {"pairs": tt, "excess_P1_minus_P2n": (ex["P1"] - ex["P2n"]).tolist(),
                        "excess_P1_minus_P2hrv": (ex["P1"] - ex["P2hrv"]).tolist()}

    # 辅读数 2: last 8 layers, stratified by predicted-next-token script
    sides = ["srp_Cyrl", "srp_Latn", "mkd_Cyrl", "bul_Cyrl"]
    strat = {}
    for c in ("neutral", "cyr", "lat"):
        pools = {sd: np.where((tlang == li[sd]) & (pred_cls == c))[0] for sd in sides}
        n = min(len(v) for v in pools.values())
        if n < 50:
            strat[c] = {"n": int(n)}
            continue
        pick = {sd: np.sort(rr.choice(v, n, replace=False)) for sd, v in pools.items()}
        rows = []
        for l in range(L - 8, L):
            row = []
            for r in range(3):
                P = {sd: norm(onehot(l, pick[sd], r).sum(0)) for sd in sides}
                d1 = jsd2(P["srp_Cyrl"], P["srp_Latn"])
                d2 = 0.5 * (jsd2(P["srp_Cyrl"], P["mkd_Cyrl"]) + jsd2(P["srp_Cyrl"], P["bul_Cyrl"]))
                row.append([float(d1), float(d2)])
            rows.append(row)
        strat[c] = {"n": int(n), "layers": list(range(L - 8, L)), "vals": rows}
    res["strat"] = strat
    return res


def f3(x):
    return f"{x:.3f}"


def fig(key, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    L = res["L"]
    x = np.arange(L)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    cols = {"P1": "#c0392b", "P2n": "#2471a3", "P2hrv": "#7d3c98", "P3": "#239b56", "P0": "#7f8c8d"}
    lab = {"P1": "P1 srp Cyrl↔Latn (same lang, diff script)", "P2n": "P2 srp_Cyrl↔mkd/bul (same script)",
           "P2hrv": "P2-hrv srp_Latn↔hrv", "P3": "P3 farther same-script", "P0": "P0 split-half floor"}
    for k, c in cols.items():
        y = np.array(res["D"][k])[:, 0]
        ax[0].plot(x, y, color=c, lw=1.6, label=lab[k])
        if k in ("P1", "P2n"):
            lo, hi = np.array(res["Dci_T"][k])
            ax[0].fill_between(x, lo, hi, color=c, alpha=.25, lw=0)
            _, mn, mx = (np.array(v) for v in res["Dnull"][k]["N_B"])
            ax[0].fill_between(x, mn, mx, color=c, alpha=.10, lw=0, hatch="///")
            ax[0].plot(x, np.array(res["Dnull"][k]["N_B"][0]), color=c, lw=.8, ls="--")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("layer"); ax[0].set_ylabel("routing JSD (bits, log)")
    ax[0].set_title(f"{NAME[key]}: trained router T (dashed / hatched: N_B mean / range)", fontsize=9)
    ax[0].legend(fontsize=7)
    c = res["contrasts"]["main"]
    for f, col in (("T", "k"), ("N_A", "#e67e22"), ("N_B", "#16a085")):
        y, lo, hi = (np.array(c[f][q]) for q in ("delta", "lo", "hi"))
        ax[1].plot(x, y, color=col, lw=1.6, label=f + (" (8-draw mean)" if f != "T" else ""))
        ax[1].fill_between(x, lo, hi, color=col, alpha=.2, lw=0)
    for l in c["T"]["lang_set"]:
        ax[1].axvspan(l - .5, l + .5, color="#c0392b", alpha=.12, lw=0)
    ax[1].axhline(0, color="grey", lw=.8)
    ax[1].set_xlabel("layer"); ax[1].set_ylabel("Δ = D(P1) − D(P2-nearest)")
    ax[1].set_title("Δ < 0: same language closer than same script (shaded: T's H-language layers)", fontsize=9)
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"fig_{key}.png"), dpi=160)
    plt.close(fig)


if len(sys.argv) > 2 and sys.argv[2] == "--fig-only":  # redraw figures from summary.json
    for key, res in json.load(open(os.path.join(OUT, "summary.json"))).items():
        fig(key, res)
    sys.exit(0)

md = ["# E180 结果表（自动生成：scripts/e180_analyze.py）\n",
      "D = 逐层路由 JSD（底 2，专家使用分布，逐句等 token 抽样）。Δ = D(P1) − D(P2-nearest)；[ ] = 句子配对 bootstrap 95%（1000 次）；"
      "零模型 = 8 draws 均值，区间是同一 bootstrap 下 8-draw 均值的 95%，x/8 = Δ<0 的 draw 数。H-语言层 = 区间上界 < 0；H-文字层 = 区间下界 > 0。\n"]
allres = {}
for key, cap in CAPS.items():
    res = analyze(key, cap)
    allres[key] = res
    meta = json.load(open(os.path.join(cap, "meta.json")))
    fig(key, res)
    L = res["L"]
    md.append(f"\n## {NAME[key]}（{L} 层，E={meta['E']}，k={meta['K']}）\n")
    md.append(f"- 每侧 token 数（全部）：{meta['ntok']}；逐句均衡后每侧被抽 token：{meta['nsel']}")
    md.append(f"- 阳性对照：两次前向 top-k 完全一致率 min {meta['det_exact_min']:.4f}；hook fp32 重算 vs 模型 {meta['hook_agreement']:.4f}；"
              f"T logits vs 模型 {meta['t_vs_model']:.4f}；N_B 负载 TV 均值 {meta['loadtv_B_mean']:.4f}（最大 {meta['loadtv_B_max']:.4f}）；"
              f"组内逐句被抽 token 数最大差 {res['equalisation_max_diff']}；topk vs persent 计数差 {res['topk_vs_persent_absdiff']:.0f}；"
              f"persent 总数核对 {res['persent_total_check']}；P0 / min(P1..P4) 逐层最大 {max(res['floor_ratio_T']):.3f}（中位 {np.median(res['floor_ratio_T']):.3f}）")
    for cname, title in (("main", "主统计量 Δ = D(P1) − D(P2-nearest)"), ("hrv", "Δ_hrv = D(P1) − D(P2-hrv)（单独报，不进决策）"),
                         ("hin_urd", "次要：hin↔urd − mean(hin↔npi/mar, urd↔snd/pes)"), ("zho", "次要：zho_Hans↔zho_Hant − zho_Hant↔yue_Hant")):
        if cname not in res["contrasts"]:
            continue
        c = res["contrasts"][cname]
        md.append(f"\n**{title}**\n")
        md.append("| 路由器 | H-语言层（区间上界<0） | H-文字层（下界>0） | 点估计 Δ<0 的层 | edge 均值 Δ | middle 均值 Δ |")
        md.append("|---|---|---|---|---|---|")
        for f in ("T", "N_A", "N_B"):
            cf = c[f]
            md.append(f"| {f} | {fmt_runs(cf['lang_set'])} | {fmt_runs(cf['script_set'])}（{len(cf['script_set'])}/{L}） | "
                      f"{fmt_runs(cf['point_lang_set'])} | {cf['edge_mean']:+.4f} | {cf['mid_mean']:+.4f} |")
        dd = c["decision"]
        md.append(f"\n决策表（T）：**{dd['T']}**" + ("；" + "；".join(dd["per_null"].values()) if dd["per_null"] else "") +
                  f"；零模型是否也 H-文字处处：N_A {dd['nulls_H_script_everywhere']['N_A']}、N_B {dd['nulls_H_script_everywhere']['N_B']}")
    md.append("\n**逐层表（主配对）**\n")
    md.append("| 层 | D(P0) | D(P1) T [95%] | D(P2n) T [95%] | D(P2hrv) | D(P3) | D(P4) | D(P4hrv) | Δ T [95%] | Δ N_A [95%] x/8 | Δ N_B [95%] x/8 | Δ_hrv T [95%] |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    c, ch = res["contrasts"]["main"], res["contrasts"]["hrv"]
    for l in range(L):
        Dl = {k: res["D"][k][l][0] for k in res["D"]}
        ci = {k: res["Dci_T"][k] for k in ("P1", "P2n")}
        cell = lambda cf: f"{cf['delta'][l]:+.4f} [{cf['lo'][l]:+.4f}, {cf['hi'][l]:+.4f}]"
        md.append(f"| {l} | {Dl['P0']:.4f} | {Dl['P1']:.4f} [{ci['P1'][0][l]:.4f}, {ci['P1'][1][l]:.4f}] | "
                  f"{Dl['P2n']:.4f} [{ci['P2n'][0][l]:.4f}, {ci['P2n'][1][l]:.4f}] | {Dl['P2hrv']:.4f} | {Dl['P3']:.4f} | "
                  f"{Dl['P4']:.4f} | {Dl['P4hrv']:.4f} | {cell(c['T'])} | {cell(c['N_A'])} {c['N_A']['n_neg_draws'][l]}/8 | "
                  f"{cell(c['N_B'])} {c['N_B']['n_neg_draws'][l]}/8 | {cell(ch['T'])} |")
    md.append("\n**零模型的配对距离（8-draw 均值）**：D(P1) / D(P2n) / D(P0)\n")
    md.append("| 层 | N_A | N_B |")
    md.append("|---|---|---|")
    for l in range(L):
        g = lambda f: " / ".join(f"{res['Dnull'][k][f][0][l]:.4f}" for k in ("P1", "P2n", "P0"))
        md.append(f"| {l} | {g('N_A')} | {g('N_B')} |")
    md.append("\n**次要配对逐层 Δ（T [95%]；N_A、N_B 8-draw 均值）**\n")
    md.append("| 层 | hin/urd T | N_A | N_B | zho T | N_A | N_B |")
    md.append("|---|---|---|---|---|---|---|")
    ci_, cz = res["contrasts"]["hin_urd"], res["contrasts"]["zho"]
    for l in range(L):
        md.append(f"| {l} | {ci_['T']['delta'][l]:+.4f} [{ci_['T']['lo'][l]:+.4f}, {ci_['T']['hi'][l]:+.4f}] | "
                  f"{ci_['N_A']['delta'][l]:+.4f} | {ci_['N_B']['delta'][l]:+.4f} | "
                  f"{cz['T']['delta'][l]:+.4f} [{cz['T']['lo'][l]:+.4f}, {cz['T']['hi'][l]:+.4f}] | "
                  f"{cz['N_A']['delta'][l]:+.4f} | {cz['N_B']['delta'][l]:+.4f} |")
    tt = res["tokentype"]
    md.append("\n**辅读数 1：无字母 token 类型的类型匹配 JSD（超出量 = 观测 − 类型内打乱均值）**\n")
    md.append("每侧出现数 / 类型数：" + "；".join(f"{k} {v['n_occ_per_side']} / {v['n_types']}" for k, v in tt["pairs"].items()))
    md.append("\n| 层 | T：超出 P1 / P2n / P2hrv（P1>p95?） | T：P1−P2n | N_A0：P1−P2n | N_B0：P1−P2n |")
    md.append("|---|---|---|---|---|")
    V = {k: np.array(v["vals"]) for k, v in tt["pairs"].items()}
    E1 = np.array(tt["excess_P1_minus_P2n"])
    for l in range(L):
        exs = lambda k: V[k][l, 0, 0] - V[k][l, 0, 1]
        p2n = 0.5 * (exs("Cyrl-mkd") + exs("Cyrl-bul"))
        md.append(f"| {l} | {exs('P1'):.4f} / {p2n:.4f} / {exs('P2hrv'):.4f}（{'是' if V['P1'][l, 0, 0] > V['P1'][l, 0, 2] else '否'}） | "
                  f"{E1[l, 0]:+.4f} | {E1[l, 1]:+.4f} | {E1[l, 2]:+.4f} |")
    for r, nm in enumerate(("T", "N_A0", "N_B0")):
        md.append(f"- {nm}：超出量 P1 < P2n 的层：{fmt_runs([l for l in range(L) if E1[l, r] < 0])}")
    md.append("\n**辅读数 2：末 8 层按预测下一个 token 的文字分层（T / N_A0 / N_B0 的 D(P1), D(P2n)）**\n")
    md.append("预测 token 文字份额：" + "；".join(f"{lg} " + ", ".join(f"{c} {v:.2f}" for c, v in d.items())
                                         for lg, d in res["pred_class_share"].items()))
    md.append("\n| 层级（每侧 n） | 层 | T D(P1) / D(P2n) → Δ | N_A0 Δ | N_B0 Δ |")
    md.append("|---|---|---|---|---|")
    for cnm, st in res["strat"].items():
        if "vals" not in st:
            md.append(f"| {cnm}（{st['n']}，太少不算） | | | | |")
            continue
        for j, l in enumerate(st["layers"]):
            v = st["vals"][j]
            md.append(f"| {cnm}（{st['n']}） | {l} | {v[0][0]:.4f} / {v[0][1]:.4f} → {v[0][0] - v[0][1]:+.4f} | "
                      f"{v[1][0] - v[1][1]:+.4f} | {v[2][0] - v[2][1]:+.4f} |")

open(os.path.join(OUT, "tables.md"), "w").write("\n".join(md) + "\n")
json.dump(allres, open(os.path.join(OUT, "summary.json"), "w"))
print("\n".join(md[:2]))
for key, res in allres.items():
    for cname, c in res["contrasts"].items():
        print(key, cname, "T lang", fmt_runs(c["T"]["lang_set"]), "| N_A", fmt_runs(c["N_A"]["lang_set"]), "| N_B",
              fmt_runs(c["N_B"]["lang_set"]), "|", c["decision"]["T"], c["decision"]["per_null"])
