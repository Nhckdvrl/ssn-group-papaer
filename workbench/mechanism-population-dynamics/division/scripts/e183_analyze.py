#!/usr/bin/env python3
"""E183 analysis (card: division/experiments/E183-routing-alignment-vs-transfer.md). 0 GPU.

Routing side from the E179 caches (~/mechpop_cache/e179/<model>/): div.npy (Bandarkar per-sentence divergence,
all routers / draws), tallies.npz counts (per-language top-k counts), persent.npy (per-sentence counts, T / N_A0 /
N_B0 / N_G0). Transfer side from results/e183/belebele_<model>.json.
Writes results/e183/summary.json, tables.md, fig_scatter.png.
"""
import json, os
import numpy as np
from scipy.stats import rankdata, spearmanr, pearsonr

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "e183")
CACHE = "/home/xiang/mechpop_cache/e179"
MODELS = {"qwen3": "Qwen3-30B-A3B", "gptoss": "GPT-OSS-20B", "olmoe": "OLMoE-0125-Instruct"}
MIDDLE = {"qwen3": range(7, 35), "gptoss": range(3, 19), "olmoe": range(2, 12)}  # card: Bandarkar / E179
SEG179 = {"qwen3": (list(range(0, 4)) + list(range(44, 48)), range(7, 35)),
          "gptoss": ([0, 1, 22, 23], range(4, 18)), "olmoe": ([0, 1, 14, 15], range(2, 12))}
BAND12 = ["arb_Arab", "asm_Beng", "bam_Latn", "ben_Beng", "fra_Latn", "hin_Deva", "lit_Latn", "ory_Orya",
          "pes_Arab", "srp_Cyrl", "tha_Thai", "zho_Hans"]
PRUNE_LANGS = ["deu_Latn", "jpn_Jpan", "arb_Arab", "ben_Beng"]  # 2605.28042 calibration langs (arz -> arb)
NB, NBOOT, NPERM, D = 10000, 10000, 10000, 8
IA, IB = list(range(1, 1 + D)), list(range(1 + D, 1 + 2 * D))
CHAT = {}  # filled if a pre-registered chat fallback file exists and the raw control failed
THRESH = {"qwen3": 0.85, "gptoss": 0.80, "olmoe": 0.60}


def jsd(p, q, base=np.e):
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(p > 0, p * np.log(p / m), 0).sum(-1)
        b = np.where(q > 0, q * np.log(q / m), 0).sum(-1)
    return 0.5 * (a + b) / np.log(base)


def rho_rows(X, y):
    """Spearman of each row of X (n_rep, n) against matching rows of y (n_rep, n)."""
    rx, ry = rankdata(X, axis=1), rankdata(y, axis=1)
    rx -= rx.mean(1, keepdims=True); ry -= ry.mean(1, keepdims=True)
    den = np.sqrt((rx ** 2).sum(1) * (ry ** 2).sum(1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (rx * ry).sum(1) / den


def corr_block(x, x_nb, x_na, y, seed, kind="spearman"):
    """x: T divergence per language; x_nb / x_na: 8-draw-mean divergences; y: accuracy."""
    f = (lambda a, b: spearmanr(a, b)[0]) if kind == "spearman" else (lambda a, b: pearsonr(a, b)[0])
    out = {"rho_T": f(x, y), "rho_NB": f(x_nb, y), "rho_NA": f(x_na, y)}
    out["delta_NB"] = out["rho_NB"] - out["rho_T"]
    out["delta_NA"] = out["rho_NA"] - out["rho_T"]
    if kind != "spearman":
        return out
    n = len(y)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, (NBOOT, n))
    Y = y[idx]
    rT, rB, rA = rho_rows(x[idx], Y), rho_rows(x_nb[idx], Y), rho_rows(x_na[idx], Y)
    ok = np.isfinite(rT) & np.isfinite(rB) & np.isfinite(rA)
    q = lambda v: [float(np.percentile(v[ok], 2.5)), float(np.percentile(v[ok], 97.5))]
    out.update(ci_T=q(rT), ci_NB=q(rB), ci_NA=q(rA), ci_delta_NB=q(rB - rT), ci_delta_NA=q(rA - rT),
               n_boot_ok=int(ok.sum()))
    P = np.array([rng.permutation(y) for _ in range(NPERM)])
    for k, v in (("T", x), ("NB", x_nb), ("NA", x_na)):
        rp = rho_rows(np.broadcast_to(v, P.shape).copy(), P)
        out[f"perm_p_{k}"] = float((1 + (np.abs(rp) >= abs(out[f"rho_{k}"]) - 1e-12).sum()) / (1 + NPERM))
    return out


# ------------------------------------------------------------------ 2605.28042 allocation (Appendix B)
def allocate(d, L, E, K, k):
    C = L * (E - k)
    c = np.full(L, float(K))
    B = float(C - L * K)
    full = np.zeros(L, bool)
    while B > 1e-9 and (~full).any():
        U = ~full
        w = d[U] / d[U].sum() if d[U].sum() > 0 else np.full(U.sum(), 1.0 / U.sum())
        prov = c[U] + w * B
        over = prov > E
        B = float((prov[over] - E).sum())  # overflow returns to the budget
        c[U] = np.minimum(prov, E)
        full = c >= E - 1e-12
    fl = np.floor(c + 1e-9).astype(int)
    rem = int(round(C - fl.sum()))
    order = np.argsort(-(c - fl), kind="stable")
    for i in order:
        if rem <= 0:
            break
        if fl[i] < E:
            fl[i] += 1; rem -= 1
    assert fl.sum() == C and fl.min() >= K and fl.max() <= E, (fl, C)
    return fl


def keep_sets(mass, cap):
    return [set(np.argsort(-mass[l], kind="stable")[:cap[l]].tolist()) for l in range(len(cap))]


def overlap(SA, SB):
    return sum(len(a & b) for a, b in zip(SA, SB)) / sum(len(a) for a in SA)


def persent_div(ps, langs, col, li, NS):
    """mean over sentences of unnormalised JSD (nats) between per-sentence count distributions of lang li and eng."""
    L = ps.shape[0]
    out = np.zeros(L)
    for l in range(L):
        a = ps[l, li * NS:(li + 1) * NS, col].astype(np.float64)
        e = ps[l, 0:NS, col].astype(np.float64)
        a /= a.sum(1, keepdims=True); e /= e.sum(1, keepdims=True)
        out[l] = jsd(a, e).mean()
    return out


# ------------------------------------------------------------------ script covariate (card 补登记 11-09 19:35)
def quarter_bands(L):
    q = L // 4
    return {"edge": list(range(0, q)) + list(range(L - q, L)), "middle_half": list(range(q, L - q))}


def partial_rho_rows(X, Y, Z):
    """partial Spearman of rows of X vs Y controlling for binary Z (rows); NaN if Z constant."""
    rx, ry = rankdata(X, axis=1), rankdata(Y, axis=1)
    out = np.full(X.shape[0], np.nan)
    for i in range(X.shape[0]):
        z = Z[i].astype(float)
        if z.min() == z.max():
            continue
        A = np.stack([np.ones_like(z), z], 1)
        ex = rx[i] - A @ np.linalg.lstsq(A, rx[i], rcond=None)[0]
        ey = ry[i] - A @ np.linalg.lstsq(A, ry[i], rcond=None)[0]
        den = np.sqrt((ex ** 2).sum() * (ey ** 2).sum())
        out[i] = (ex * ey).sum() / den if den > 0 else np.nan
    return out


def script_block(xT, xB, xA, y, lat, seed):
    """(a) all, (b) within Latin / non-Latin, (c) partial on Latin indicator; T vs N_B (and N_A)."""
    rng = np.random.default_rng(seed)
    n = len(y)
    res = {}
    sp = lambda a, b: float(spearmanr(a, b)[0])
    def boot_delta(fn, idx_pool):
        m = len(idx_pool)
        I = np.asarray(idx_pool)[rng.integers(0, m, (NBOOT, m))]
        rT, rB = fn(xT[I], y[I], lat[I]), fn(xB[I], y[I], lat[I])
        ok = np.isfinite(rT) & np.isfinite(rB)
        d = rB[ok] - rT[ok]
        return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], int((~ok).sum())
    sfn = lambda X, Y, Z: rho_rows(X, Y)
    pfn = partial_rho_rows
    allidx = list(range(n))
    r = {"rho_T": sp(xT, y), "rho_NB": sp(xB, y), "rho_NA": sp(xA, y)}
    r["delta_NB"] = r["rho_NB"] - r["rho_T"]
    r["ci_delta_NB"], r["boot_dropped"] = boot_delta(sfn, allidx)
    res["all"] = r
    for name, sel in (("latin", np.where(lat == 1)[0]), ("nonlatin", np.where(lat == 0)[0])):
        r = {"n": int(len(sel)), "rho_T": sp(xT[sel], y[sel]), "rho_NB": sp(xB[sel], y[sel]), "rho_NA": sp(xA[sel], y[sel])}
        r["delta_NB"] = r["rho_NB"] - r["rho_T"]
        if len(sel) >= 8:
            r["ci_delta_NB"], r["boot_dropped"] = boot_delta(sfn, list(sel))
        res[name] = r
    one = lambda v: float(partial_rho_rows(v[None], y[None], lat[None])[0])
    r = {"rho_T": one(xT), "rho_NB": one(xB), "rho_NA": one(xA)}
    r["delta_NB"] = r["rho_NB"] - r["rho_T"]
    r["ci_delta_NB"], r["boot_dropped"] = boot_delta(pfn, allidx)
    # within-script permutation p for partial rho of T
    P = np.tile(y, (NPERM, 1))
    for g in (0, 1):
        idx = np.where(lat == g)[0]
        P[:, idx] = np.array([rng.permutation(y[idx]) for _ in range(NPERM)])
    rp = partial_rho_rows(np.tile(xT, (NPERM, 1)), P, np.tile(lat, (NPERM, 1)))
    r["perm_p_T_within_script"] = float((1 + (np.abs(rp) >= abs(r["rho_T"]) - 1e-12).sum()) / (1 + NPERM))
    rpB = partial_rho_rows(np.tile(xB, (NPERM, 1)), P, np.tile(lat, (NPERM, 1)))
    r["perm_p_NB_within_script"] = float((1 + (np.abs(rpB) >= abs(r["rho_NB"]) - 1e-12).sum()) / (1 + NPERM))
    res["partial"] = r
    return res


def analyze(key):
    cap = os.path.join(CACHE, key)
    meta = json.load(open(os.path.join(cap, "meta.json")))
    langs, L, E, K, NS = meta["langs"], meta["L"], meta["E"], meta["K"], meta["n_sent"]
    NL = len(langs)
    bj = json.load(open(os.path.join(RES, f"belebele_{key}.json")))
    use = bj
    chat_path = os.path.join(RES, f"belebele_{key}_chat.json")
    parts = [os.path.join(RES, "_logs", f"belebele_{key}_chat_{x}.json") for x in ("a", "b")]
    if all(os.path.exists(x) for x in parts):  # chat fallback was split over two GPUs; English is in both halves
        pj = [json.load(open(x)) for x in parts]
        merged = dict(pj[0]); merged["acc"] = {**pj[0]["acc"], **pj[1]["acc"]}
        merged["pred_letter_counts"] = {**pj[0]["pred_letter_counts"], **pj[1]["pred_letter_counts"]}
        merged["eng_acc_both_halves"] = [pj[0]["acc"]["eng_Latn"], pj[1]["acc"]["eng_Latn"]]
        merged["wall_s_parts"] = [pj[0]["wall_s"], pj[1]["wall_s"]]
        json.dump(merged, open(chat_path, "w"), indent=1)
    fallback = bj["acc"]["eng_Latn"] < THRESH[key]
    if fallback and os.path.exists(chat_path):
        use = json.load(open(chat_path))
    acc_all = np.array([use["acc"][lg] for lg in langs])
    res = {"key": key, "name": MODELS[key], "L": L, "E": E, "K": K, "acc": dict(zip(langs, acc_all.tolist())),
           "acc_raw_prompt": bj["acc"], "fallback_triggered": bool(fallback), "fallback_used": use is not bj,
           "middle": [min(MIDDLE[key]), max(MIDDLE[key])]}
    # ---------------- routing divergences [router 0..16, lang, layer]
    div = np.load(os.path.join(cap, "div.npy"), mmap_mode="r")
    R = 1 + 2 * D
    DB = np.stack([np.asarray(div[:, :, :, r]).mean(1) for r in range(R)])  # [R, NL, L]
    cnt = np.load(os.path.join(cap, "tallies.npz"))["counts"][:, :R].astype(np.float64)  # [L, R, NL, E]
    P = cnt / cnt.sum(-1, keepdims=True)
    DJ = np.stack([np.stack([jsd(P[:, r, li], P[:, r, 0], base=2) for li in range(NL)]) for r in range(R)])
    # self-check vs E179 summary (U of R4 for T)
    s179 = json.load(open(os.path.join(HERE, "..", "results", "e179", "summary.json")))[key]
    edge, mid = SEG179[key]
    R4T = DB[0, 1:].mean(0)
    res["selfcheck_U_R4_T"] = [float(R4T[edge].mean() / R4T[list(mid)].mean()), s179["U_R4"]["T"]["mean"]]
    # ---------------- correlations
    non = [i for i, lg in enumerate(langs) if lg != "eng_Latn"]
    sub12 = [langs.index(lg) for lg in BAND12]
    bands = {"middle": list(MIDDLE[key]), "all": list(range(L))}
    cells = {}
    seed = 183
    for dname, Dm in (("DB", DB), ("DJ", DJ)):
        for bname, bl in bands.items():
            agg = Dm[:, :, bl].mean(-1)  # [R, NL]
            for sname, li in (("19", non), ("12", sub12)):
                x, xb, xa = agg[0, li], agg[IB][:, li].mean(0), agg[IA][:, li].mean(0)
                y = acc_all[li]
                for kind in ("spearman", "pearson"):
                    c = corr_block(x, xb, xa, y, seed, kind)
                    seed += 1
                    if kind == "spearman":
                        c["rho_NB_draws"] = [float(spearmanr(agg[r, li], y)[0]) for r in IB]
                        c["rho_NA_draws"] = [float(spearmanr(agg[r, li], y)[0]) for r in IA]
                    cells[f"{dname}|{bname}|{sname}|{kind}"] = {k: (float(v) if np.isscalar(v) else v)
                                                                for k, v in c.items()}
    res["cells"] = cells
    res["primary"] = cells["DB|middle|19|spearman"]
    # gap check: Spearman(D, gap) == -Spearman(D, acc)
    gap = acc_all[0] - acc_all[non]
    res["primary_gap_rho_T"] = float(spearmanr(DB[0, non][:, list(MIDDLE[key])].mean(-1), gap)[0])
    # ---------------- Bandarkar exact: per middle layer Pearson r, 12 analysis languages
    bk = {}
    for sname, li in (("12", sub12), ("19", non)):
        rT = [pearsonr(DB[0, li, l], acc_all[li])[0] for l in MIDDLE[key]]
        rB = [pearsonr(DB[IB][:, li, l].mean(0), acc_all[li])[0] for l in MIDDLE[key]]
        bk[sname] = {"T_min": float(np.min(rT)), "T_max": float(np.max(rT)), "T_median": float(np.median(rT)),
                     "NB_min": float(np.min(rB)), "NB_max": float(np.max(rB)), "NB_median": float(np.median(rB)),
                     "T_per_layer": [float(v) for v in rT], "NB_per_layer": [float(v) for v in rB]}
    res["bandarkar_exact"] = bk
    # ---------------- 2605.28042 pruning allocation
    ps = np.load(os.path.join(cap, "persent.npy"), mmap_mode="r")  # [L, NU, 4, E]: T, N_A0, N_B0, N_G0
    pr = {}
    for frac_name, k in (("50", E // 2), ("56.25", 9 * E // 16)):
        rows = {}
        for li in non:
            lg = langs[li]
            dT = persent_div(ps, langs, 0, li, NS)
            dB0 = persent_div(ps, langs, 2, li, NS)
            massT = cnt[:, 0, li]
            massB0 = cnt[:, 1 + D, li]
            cT, cB0 = allocate(dT, L, E, K, k), allocate(dB0, L, E, K, k)
            cDBT = allocate(DB[0, li], L, E, K, k)
            cDBB = allocate(DB[IB][:, li].mean(0), L, E, K, k)
            ST = keep_sets(massT, cT)
            rows[lg] = {"alloc_overlap_persent": overlap(ST, keep_sets(massT, cB0)),
                        "alloc_overlap_DB": overlap(keep_sets(massT, cDBT), keep_sets(massT, cDBB)),
                        "own_rank_overlap_NB0": overlap(ST, keep_sets(massB0, cB0)),
                        "cap_spearman": float(spearmanr(cT, cB0)[0]),
                        "cap_moved": int(np.abs(cT - cB0).sum() // 2),
                        "uniform_vs_T_overlap": overlap(ST, keep_sets(massT, np.full(L, E - k))),
                        "cap_T": cT.tolist(), "cap_NB0": cB0.tolist()}
        agg_ = lambda key2, ls: float(np.mean([rows[x][key2] for x in ls]))
        pr[frac_name] = {"per_lang": rows,
                         **{f"{m}_{tag}": agg_(m, ls) for m in ("alloc_overlap_persent", "alloc_overlap_DB",
                                                                "own_rank_overlap_NB0", "uniform_vs_T_overlap",
                                                                "cap_spearman")
                            for tag, ls in (("paper4", PRUNE_LANGS), ("all19", [langs[i] for i in non]))},
                         "alloc_overlap_persent_min19": float(min(rows[langs[i]]["alloc_overlap_persent"] for i in non))}
    # ---------------- script covariate (补登记 19:35)
    lat_all = np.array([1 if lg.endswith("_Latn") else 0 for lg in langs])
    qb = quarter_bands(L)
    sb_bands = {"edge": qb["edge"], "middle_half": qb["middle_half"], "bandarkar_middle": list(MIDDLE[key])}
    scr = {"bands": {k: [min(v), max(v)] if k != "edge" else v for k, v in sb_bands.items()}}
    for bname, bl in sb_bands.items():
        agg = DB[:, :, bl].mean(-1)
        xT, xB, xA = agg[0, non], agg[IB][:, non].mean(0), agg[IA][:, non].mean(0)
        scr[bname] = script_block(xT, xB, xA, acc_all[non], lat_all[non], 1900 + len(bl))
        # variant: include English (divergence 0 by construction)
        e = [0] + non
        aggE = agg.copy(); aggE[:, 0] = 0.0
        scr[bname]["all20"] = {"rho_T": float(spearmanr(aggE[0, e], acc_all[e])[0]),
                               "rho_NB": float(spearmanr(aggE[IB][:, e].mean(0), acc_all[e])[0])}
    res["script"] = scr
    res["pruning"] = pr
    res["controls"] = {"eng_acc": float(acc_all[0]), "eng_threshold": THRESH[key],
                       "eng_pass": bool(acc_all[0] >= THRESH[key]),
                       "n_langs_above_.30": int((acc_all[non] > 0.30).sum())}
    plot = {"langs": [langs[i] for i in non], "x_T": DB[0, non][:, list(MIDDLE[key])].mean(-1).tolist(),
            "x_NB": DB[IB][:, non][:, :, list(MIDDLE[key])].mean(-1).mean(0).tolist(),
            "acc": acc_all[non].tolist()}
    return res, plot


def decide(prim):
    rule_readout = all(p["delta_NB"] < 0.1 and p["ci_delta_NB"][0] <= 0 <= p["ci_delta_NB"][1] for p in prim.values())
    n_info = sum(p["delta_NB"] >= 0.2 and p["ci_delta_NB"][0] > 0 for p in prim.values())
    if rule_readout:
        return "H-readout"
    if n_info >= 2:
        return "H-info"
    return "mixed"


def decide_script(m):
    """card 补登记 19:35 rule; m = one model's result dict."""
    adv = m["primary"]["delta_NB"] >= 0.1
    out = {"primary_advantage": bool(adv)}
    for b in ("edge", "middle_half", "bandarkar_middle"):
        p, nl = m["script"][b]["partial"], m["script"][b]["nonlatin"]
        surv = p["delta_NB"] >= 0.1 and p["ci_delta_NB"][0] > 0
        gone = (p["delta_NB"] < 0.1 or p["ci_delta_NB"][0] <= 0) and \
               (nl["delta_NB"] < 0.1 or nl.get("ci_delta_NB", [-1, 1])[0] <= 0)
        out[b] = {"partial_survives": bool(surv), "gone_partial_and_nonlatin": bool(gone),
                  "masked_by_script": bool((not adv) and p["delta_NB"] >= 0.2 and p["ci_delta_NB"][0] > 0),
                  "T_partial_sig": p["perm_p_T_within_script"] < 0.05}
    if adv:
        carriers = [b for b in ("edge", "middle_half") if out[b]["partial_survives"]]
        out["verdict"] = ("advantage survives script control in " + "+".join(carriers)) if carriers else \
            ("advantage disappears -> script sharing" if out["middle_half"]["gone_partial_and_nonlatin"]
             and out["edge"]["gone_partial_and_nonlatin"] else "advantage partly reduced (see cells)")
    else:
        out["verdict"] = "no primary advantage to test" + (
            "; script masks a T advantage in " + "+".join(b for b in ("edge", "middle_half") if out[b]["masked_by_script"])
            if any(out[b]["masked_by_script"] for b in ("edge", "middle_half")) else "")
    return out


def main():
    out, plots = {}, {}
    for key in MODELS:
        if not os.path.exists(os.path.join(RES, f"belebele_{key}.json")):
            print("missing", key); continue
        out[key], plots[key] = analyze(key)
        print(key, "primary", {k: out[key]["primary"][k] for k in ("rho_T", "rho_NB", "rho_NA", "delta_NB")})
    prim = {k: v["primary"] for k, v in out.items()}
    dec = decide(prim) if len(prim) == 3 else "incomplete"
    out["_decision"] = dec
    out["_per_model_branch"] = {k: ("readout-like" if p["delta_NB"] < 0.1 and p["ci_delta_NB"][0] <= 0 <= p["ci_delta_NB"][1]
                                    else "info-like" if p["delta_NB"] >= 0.2 and p["ci_delta_NB"][0] > 0
                                    else "NB-stronger" if p["delta_NB"] <= -0.2 and p["ci_delta_NB"][1] < 0
                                    else "neither") for k, p in prim.items()}
    out["_T_significant"] = {k: p["perm_p_T"] < 0.05 for k, p in prim.items()}
    out["_script_decision"] = {k: decide_script(out[k]) for k in prim}
    json.dump(out, open(os.path.join(RES, "summary.json"), "w"), indent=1)
    write_tables(out)
    figure(plots, out)
    print("decision:", dec, out["_per_model_branch"], out["_T_significant"])


def ci(c):
    return f"[{c[0]:+.2f}, {c[1]:+.2f}]"


def write_tables(out):
    ks = [k for k in MODELS if k in out]
    md = ["# E183 tables（自动生成：`scripts/e183_analyze.py`）\n",
          "ρ = Spearman，跨 19 种非英语；D_B = Bandarkar 熵归一 JSD（句均），middle 带；N_A / N_B = 8-draw 均值散度；"
          "Δ = ρ_NB − ρ_T（正 = 训练路由器预测更强）；CI = 语言配对 bootstrap 10,000 次 95%；p = 置换 10,000 次双侧。\n",
          "## Belebele 准确率（零样本，lm-eval 模板，字母对数似然）\n",
          "| 语言 | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|" + "---|" * len(ks)]
    langs = list(out[ks[0]]["acc"].keys())
    for lg in langs:
        md.append(f"| {lg} | " + " | ".join(f"{out[k]['acc'][lg]:.3f}" for k in ks) + " |")
    md.append("| 阳性对照：英语 ≥ 下限 | " + " | ".join(
        f"{out[k]['controls']['eng_acc']:.3f} ≥ {out[k]['controls']['eng_threshold']:.2f}："
        f"{'过' if out[k]['controls']['eng_pass'] else '不过'}" for k in ks) + " |")
    md.append("| > .30 的非英语数 | " + " | ".join(str(out[k]['controls']['n_langs_above_.30']) for k in ks) + " |")
    md.append("| 退路（聊天模板）触发 / 采用 | " + " | ".join(
        f"{out[k]['fallback_triggered']} / {out[k]['fallback_used']}" for k in ks) + " |")
    md += ["\n## 主格：D_B、middle 带、19 语、Spearman\n",
           "| | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|" + "---|" * len(ks)]
    P = {k: out[k]["primary"] for k in ks}
    rows = [("middle 带（0 起）", lambda k: f"{out[k]['middle'][0]}–{out[k]['middle'][1]}"),
            ("ρ_T [CI]；置换 p", lambda k: f"{P[k]['rho_T']:+.2f} {ci(P[k]['ci_T'])}；p = {P[k]['perm_p_T']:.4f}"),
            ("ρ_NB [CI]；置换 p", lambda k: f"{P[k]['rho_NB']:+.2f} {ci(P[k]['ci_NB'])}；p = {P[k]['perm_p_NB']:.4f}"),
            ("ρ_NB 逐 draw 最小–最大", lambda k: f"{min(P[k]['rho_NB_draws']):+.2f} – {max(P[k]['rho_NB_draws']):+.2f}"),
            ("ρ_NA [CI]；置换 p", lambda k: f"{P[k]['rho_NA']:+.2f} {ci(P[k]['ci_NA'])}；p = {P[k]['perm_p_NA']:.4f}"),
            ("ρ_NA 逐 draw 最小–最大", lambda k: f"{min(P[k]['rho_NA_draws']):+.2f} – {max(P[k]['rho_NA_draws']):+.2f}"),
            ("**Δ_NB = ρ_NB − ρ_T [CI]**", lambda k: f"**{P[k]['delta_NB']:+.2f} {ci(P[k]['ci_delta_NB'])}**"),
            ("Δ_NA = ρ_NA − ρ_T [CI]", lambda k: f"{P[k]['delta_NA']:+.2f} {ci(P[k]['ci_delta_NA'])}"),
            ("对 gap 的 ρ_T（≡ −ρ_T）", lambda k: f"{out[k]['primary_gap_rho_T']:+.2f}"),
            ("逐模型分支", lambda k: out["_per_model_branch"].get(k, "")),
            ("T 显著（p < .05）", lambda k: str(out["_T_significant"].get(k, "")))]
    for name, f in rows:
        md.append(f"| {name} | " + " | ".join(f(k) for k in ks) + " |")
    md.append(f"\n**预登记判决：{out['_decision']}**\n")
    md += ["## Bandarkar 原统计量：middle 带逐层 Pearson r(Div_T, acc)\n",
           "原文：OLMoE r ∈ [−.95, −.80]；GPT-OSS 最弱 [−.40, −.60]；Qwen3 与 Phi-3.5 居中。\n",
           "| 语言集 | 路由器 | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|---|" + "---|" * len(ks)]
    for s in ("12", "19"):
        for r in ("T", "NB"):
            md.append(f"| {s} 语 | {r} | " + " | ".join(
                f"[{out[k]['bandarkar_exact'][s][r + '_min']:+.2f}, {out[k]['bandarkar_exact'][s][r + '_max']:+.2f}]，"
                f"中位 {out[k]['bandarkar_exact'][s][r + '_median']:+.2f}" for k in ks) + " |")
    md += ["\n## 补充格（ρ_T / ρ_NB / ρ_NA；Δ_NB [CI]；Pearson 行无 CI）\n",
           "| 散度 | 层 | 语言 | 相关 | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|---|---|---|" + "---|" * len(ks)]
    for cell in out[ks[0]]["cells"]:
        dn, bn, sn, kind = cell.split("|")
        def c(k):
            v = out[k]["cells"][cell]
            s = f"{v['rho_T']:+.2f} / {v['rho_NB']:+.2f} / {v['rho_NA']:+.2f}；Δ {v['delta_NB']:+.2f}"
            return s + (f" {ci(v['ci_delta_NB'])}" if "ci_delta_NB" in v else "")
        md.append(f"| {dn} | {bn} | {sn} | {kind} | " + " | ".join(c(k) for k in ks) + " |")
    md += ["\n## 次要：2605.28042 剪枝分配（T 的 routing mass 排序；容量由 T vs N_B 的散度分配）\n",
           "allocation-only 重合 = |S_T ∩ S_NB| / |S_T|；paper4 = deu / jpn / arb（代 arz）/ ben 平均；"
           "own-rank = N_B0 自己的计数排序 + N_B0 容量（有构造性偏差：N_B 偏置拟合到 T 的负载）；"
           "uniform = 均匀分配与 T 动态分配的重合（参照：动态分配本身改动多少）。\n",
           "| 剪枝率 | 读数 | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|---|" + "---|" * len(ks)]
    for fr in ("50", "56.25"):
        for m, lab in (("alloc_overlap_persent_paper4", "allocation-only（逐句计数 d，N_B0），paper4"),
                       ("alloc_overlap_persent_all19", "allocation-only（逐句计数 d，N_B0），19 语平均"),
                       ("alloc_overlap_persent_min19", "allocation-only（逐句计数 d，N_B0），19 语最小"),
                       ("alloc_overlap_DB_all19", "allocation-only（D_B，N_B 8-draw），19 语平均"),
                       ("cap_spearman_all19", "容量向量 Spearman(c_T, c_NB0)，19 语平均"),
                       ("own_rank_overlap_NB0_all19", "own-rank 重合（补充），19 语平均"),
                       ("uniform_vs_T_overlap_all19", "均匀 vs T 动态（参照），19 语平均")):
            md.append(f"| {fr}% | {lab} | " + " | ".join(f"{out[k]['pruning'][fr][m]:.3f}" for k in ks) + " |")
    md += ["\n## 补登记（19:35）：文字协变量（D_B；ρ_T / ρ_NB；Δ = ρ_NB − ρ_T [CI]）\n",
           "拉丁 = bam fra lit deu spa swh（6）；非拉丁 13；edge = 前后各 1/4 层，middle½ = 中间一半，B-mid = Bandarkar middle 带。"
           "偏相关 = 控制拉丁指标的偏 Spearman；p_组内 = 文字组内置换 acc 的偏相关 p。\n",
           "| 层带 | 读数 | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|---|" + "---|" * len(ks)]
    def sc(v, withci=True):
        t = f"{v['rho_T']:+.2f} / {v['rho_NB']:+.2f}；Δ {v['delta_NB']:+.2f}"
        return t + (f" {ci(v['ci_delta_NB'])}" if withci and "ci_delta_NB" in v else "")
    for b, bl in (("edge", "edge"), ("middle_half", "middle½"), ("bandarkar_middle", "B-mid")):
        md.append(f"| {bl} | (a) 19 语 | " + " | ".join(sc(out[k]['script'][b]['all']) for k in ks) + " |")
        md.append(f"| {bl} | (a′) 含英语 20 语（无 CI） | " + " | ".join(
            f"{out[k]['script'][b]['all20']['rho_T']:+.2f} / {out[k]['script'][b]['all20']['rho_NB']:+.2f}" for k in ks) + " |")
        md.append(f"| {bl} | (b) 拉丁内 n=6（只描述） | " + " | ".join(sc(out[k]['script'][b]['latin'], False) for k in ks) + " |")
        md.append(f"| {bl} | (b) 非拉丁内 n=13 | " + " | ".join(sc(out[k]['script'][b]['nonlatin']) for k in ks) + " |")
        md.append(f"| {bl} | (c) 偏相关 | " + " | ".join(sc(out[k]['script'][b]['partial']) for k in ks) + " |")
        md.append(f"| {bl} | (c) p_组内：T / N_B | " + " | ".join(
            f"{out[k]['script'][b]['partial']['perm_p_T_within_script']:.4f} / {out[k]['script'][b]['partial']['perm_p_NB_within_script']:.4f}"
            for k in ks) + " |")
    md.append("| — | **补登记判读** | " + " | ".join(out["_script_decision"][k]["verdict"] for k in ks) + " |")
    md += ["\n## 管线自检\n", "| | " + " | ".join(MODELS[k] for k in ks) + " |", "|---|" + "---|" * len(ks),
           "| U(R4) of T：本脚本 / E179 summary | " + " | ".join(
               f"{out[k]['selfcheck_U_R4_T'][0]:.4f} / {out[k]['selfcheck_U_R4_T'][1]:.4f}" for k in ks) + " |"]
    open(os.path.join(RES, "tables.md"), "w").write("\n".join(md) + "\n")


def figure(plots, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ks = list(plots)
    fig, axes = plt.subplots(1, len(ks), figsize=(4.2 * len(ks), 4.0), sharey=True)
    axes = np.atleast_1d(axes)
    cT, cB = "#2a78d6", "#eb6834"
    for ax, k in zip(axes, ks):
        p = plots[k]
        z = lambda v: (np.array(v) - np.mean(v)) / np.std(v)
        xT, xB, y = z(p["x_T"]), z(p["x_NB"]), np.array(p["acc"])
        for i in range(len(y)):
            ax.plot([xT[i], xB[i]], [y[i], y[i]], color="#bbbbbb", lw=0.8, zorder=1)
        ax.scatter(xT, y, s=34, color=cT, edgecolor="white", lw=1, zorder=3, label="trained router T")
        ax.scatter(xB, y, s=34, marker="s", color=cB, edgecolor="white", lw=1, zorder=2,
                   label="load-matched null N_B (8-draw mean)")
        for i, lg in enumerate(p["langs"]):
            ax.annotate(lg[:3], (xT[i], y[i]), xytext=(3, 2), textcoords="offset points", fontsize=6.5, color="#444444")
        pr = out[k]["primary"]
        ax.set_title(f"{MODELS[k]}\nρ_T = {pr['rho_T']:+.2f}, ρ_NB = {pr['rho_NB']:+.2f}, Δ = {pr['delta_NB']:+.2f}",
                     fontsize=9)
        ax.set_xlabel("divergence from English, middle layers (z-score)", fontsize=8)
        ax.axhline(0.25, color="#999999", lw=0.8, ls=":")
        ax.grid(alpha=0.25, lw=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("Belebele accuracy (zero-shot)", fontsize=8)
    axes[-1].legend(fontsize=7, loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "fig_scatter.png"), dpi=160)


if __name__ == "__main__":
    main()
