#!/usr/bin/env python3
"""E182 analysis (card: division/experiments/E182-script-cost-lexical-carrier.md).

Per layer and token class (ALL / LET / NON / NONtm), routing-distribution JSD (base 2) between pairs of the S / U / H
groups, for T, N_A (8), N_B (8); paired sentence bootstrap (1000, seed 182). Readouts R1 Δ_letter, R2 Δ_nonletter
(+ R2-tm), R3 script-switch cost on a language-distance ladder, R4 excess over N_B / N_A per class; pre-registered
decision table; aux A1 (E180 dev arrays, T only) and A2 (ALL class). One figure per model.

Usage: e182_analyze.py OUT_DIR key=CAPTURE_DIR [...] [a1:key=E180_CAPTURE_DIR ...]
       keys: qwen3, qwen3base, gptoss, olmoe, gptoss_cal100
       e182_analyze.py OUT_DIR --fig-only
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e182_common as C  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
ARGS = [a for a in sys.argv[2:] if "=" in a]
CAPS = dict(a.split("=", 1) for a in ARGS if not a.startswith("a1:"))
A1CAPS = dict(a[3:].split("=", 1) for a in ARGS if a.startswith("a1:"))
NAME = {"qwen3": "Qwen3-30B-A3B (Instruct)", "qwen3base": "Qwen3-30B-A3B-Base", "gptoss": "GPT-OSS-20B",
        "olmoe": "OLMoE-1B-7B-0125-Instruct", "gptoss_cal100": "GPT-OSS-20B (N_B cal = dev 100)"}
HF = {"qwen3": "Qwen/Qwen3-30B-A3B", "qwen3base": "Qwen/Qwen3-30B-A3B-Base", "gptoss": "openai/gpt-oss-20b",
      "olmoe": "allenai/OLMoE-1B-7B-0125-Instruct", "gptoss_cal100": "openai/gpt-oss-20b"}
SEG = {48: dict(edge=list(range(0, 4)) + list(range(44, 48)), mid=list(range(7, 35))),
       24: dict(edge=[0, 1, 22, 23], mid=list(range(4, 18))),
       16: dict(edge=[0, 1, 14, 15], mid=list(range(2, 12)))}
NB = 1000
PAIRS = {
    "P1": [("srp_Cyrl", "srp_Latn")],
    "P2n": [("srp_Cyrl", "mkd_Cyrl"), ("srp_Cyrl", "bul_Cyrl")],
    "hrv": [("srp_Latn", "hrv_Latn")],
    "rusukr": [("srp_Cyrl", "rus_Cyrl"), ("srp_Cyrl", "ukr_Cyrl")],
    "slv": [("srp_Latn", "slv_Latn")],
    "cespol": [("srp_Latn", "ces_Latn"), ("srp_Latn", "pol_Latn")],
    "P1U": [("uzn_Latn", "uzn_Cyrl")],
    "P2U": [("uzn_Latn", "tur_Latn"), ("uzn_Latn", "azj_Latn"), ("uzn_Cyrl", "kaz_Cyrl"), ("uzn_Cyrl", "kir_Cyrl")],
    "kazkir": [("uzn_Cyrl", "kaz_Cyrl"), ("uzn_Cyrl", "kir_Cyrl")],
    "turazj": [("uzn_Latn", "tur_Latn"), ("uzn_Latn", "azj_Latn")],
    "P1H": [("hin_Deva", "urd_Arab")],
    "P2H": [("hin_Deva", "npi_Deva"), ("hin_Deva", "mar_Deva"), ("urd_Arab", "snd_Arab"), ("urd_Arab", "pes_Arab")],
}
SPLITS = {"P0S": "srp_Cyrl", "P0U": "uzn_Latn", "P0H": "hin_Deva"}
CONTR = {"S": ("P1", "P2n", "P0S"), "U": ("P1U", "P2U", "P0U"), "H": ("P1H", "P2H", "P0H")}
LADDER_S = [("hrv(0)", "hrv"), ("mkd/bul", "P2n"), ("rus/ukr", "rusukr")]
LADDER_SL = [("hrv", "hrv"), ("slv", "slv"), ("ces/pol", "cespol")]
LADDER_U = [("kaz/kir", "kazkir"), ("tur/azj", "turazj")]


def jsd2(P, Q):
    M = 0.5 * (P + Q)
    f = lambda a, b: np.where(a > 0, a * np.log2(np.where(a > 0, a, 1) / np.where(b > 0, b, 1)), 0).sum(-1)
    return 0.5 * f(P, M) + 0.5 * f(Q, M)


def norm(X):
    return X / np.maximum(X.sum(-1, keepdims=True), 1e-30)


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


def boot_weights(NS):
    rng = np.random.default_rng(182)
    Wb = np.stack([np.bincount(rng.integers(0, NS, NS), minlength=NS) for _ in range(NB)]).astype(np.float32)
    hA = np.zeros(NS, bool)
    hA[np.random.default_rng(182).permutation(NS)[:NS // 2]] = True
    return Wb, hA


def distances(PSc, langs, NS, Wb, hA, pairs, splits, L, NR, E):
    """PSc: [L, NU, NR, E] counts for one class -> point Dp[k] [L, NR], bootstrap Db[k] [NB, L, NR]."""
    li = {lg: i for i, lg in enumerate(langs)}
    Dp = {k: np.zeros((L, NR)) for k in list(pairs) + list(splits)}
    Db = {k: np.zeros((NB, L, NR), np.float32) for k in list(pairs) + list(splits)}
    for l in range(L):
        pt, bt = {}, {}
        for lg, i in li.items():
            Cm = np.asarray(PSc[l, i * NS:(i + 1) * NS], dtype=np.float32).reshape(NS, NR * E)
            pt[lg] = Cm.sum(0).reshape(NR, E)
            bt[lg] = (Wb @ Cm).reshape(NB, NR, E)
            if lg in splits.values():
                pt[lg + "|A"] = Cm[hA].sum(0).reshape(NR, E)
                pt[lg + "|B"] = Cm[~hA].sum(0).reshape(NR, E)
                bt[lg + "|A"] = ((Wb * hA) @ Cm).reshape(NB, NR, E)
                bt[lg + "|B"] = ((Wb * ~hA) @ Cm).reshape(NB, NR, E)
        cache = {}

        def J(a, b, boot):
            key = (a, b, boot)
            if key not in cache:
                src = bt if boot else pt
                cache[key] = jsd2(norm(src[a]), norm(src[b]))
            return cache[key]

        for k, plist in pairs.items():
            Dp[k][l] = np.mean([J(a, b, False) for a, b in plist], 0)
            Db[k][:, l] = np.mean([J(a, b, True) for a, b in plist], 0)
        for k, lg in splits.items():
            Dp[k][l] = J(lg + "|A", lg + "|B", False)
            Db[k][:, l] = J(lg + "|A", lg + "|B", True)
    return Dp, Db


def contrast(Dp, Db, a, b, FAM, L):
    dpt, dbt = Dp[a] - Dp[b], Db[a] - Db[b]
    cr = {}
    for f, idx in FAM.items():
        p = dpt[:, idx].mean(1)
        bs = dbt[:, :, idx].mean(2)
        lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
        cr[f] = {"delta": p.tolist(), "lo": lo.tolist(), "hi": hi.tolist(),
                 "n_neg_draws": (dpt[:, idx] < 0).sum(1).tolist(),
                 "draw_min": dpt[:, idx].min(1).tolist(), "draw_max": dpt[:, idx].max(1).tolist(),
                 "pos_set": [l for l in range(L) if lo[l] > 0], "neg_set": [l for l in range(L) if hi[l] < 0],
                 "edge_mean": float(p[SEG[L]["edge"]].mean()), "mid_mean": float(p[SEG[L]["mid"]].mean())}
    for f in ("N_B", "N_A"):  # R4 excess = Δ_T − mean_j Δ_f,j
        p = dpt[:, 0] - dpt[:, FAM[f]].mean(1)
        bs = dbt[:, :, 0] - dbt[:, :, FAM[f]].mean(2)
        lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
        cr["excess_" + f] = {"val": p.tolist(), "lo": lo.tolist(), "hi": hi.tolist(),
                             "pos_set": [l for l in range(L) if lo[l] > 0], "neg_set": [l for l in range(L) if hi[l] < 0],
                             "edge_mean": float(p[SEG[L]["edge"]].mean()), "mid_mean": float(p[SEG[L]["mid"]].mean())}
    return cr


def decide(cl, cn, L):
    """Pre-registered per-model rule. cl / cn: contrast dicts for LET and NON (or NONtm)."""
    T_l, T_n = cl["T"], cn["T"]
    c1n = len(T_l["pos_set"])
    c1 = c1n >= 0.9 * L
    ok = [l for l in range(2, L - 2) if T_n["lo"][l] <= 0]
    rr = runs(ok)
    band = max(rr, key=len) if rr else []  # max() returns the first longest -> earliest on ties
    need = math.ceil(L / 3)
    c2 = len(band) >= need
    exl, exn = np.array(cl["excess_N_B"]["val"]), np.array(cn["excess_N_B"]["val"])
    c3a_n = len(cl["excess_N_B"]["pos_set"])
    c3a = c3a_n >= 0.5 * L
    bset = band if band else SEG[L]["mid"]
    ml, mn = float(exl[bset].mean()), float(exn[bset].mean())
    c3b = ml > 0 and abs(mn) <= 0.25 * ml
    c3 = c3a and c3b
    ii = len(T_n["pos_set"]) >= 0.9 * L
    if c1 and c2 and c3:
        br = "(i-m)"
    elif ii:
        br = "(ii-m)"
    else:
        br = "partial: fails " + ",".join(n for n, v in (("C1", c1), ("C2", c2), ("C3", c3)) if not v)
    return {"branch": br, "C1": c1, "C1_n": c1n, "C2": c2, "band": band, "band_need": need,
            "band_sig_neg": [l for l in band if T_n["hi"][l] < 0], "C3": c3, "C3a": c3a, "C3a_n": c3a_n, "C3b": c3b,
            "C3b_layers": "band" if band else "middle segment (no band)", "C3b_mean_exLET": ml, "C3b_mean_exNON": mn,
            "ii": ii, "ii_n": len(T_n["pos_set"])}


def ladder(Dp, Db, rungs, p1, L, coord=True):
    """R3: nearest rung per layer (T), coordinate x (piecewise linear 0,1,2) with bootstrap CI."""
    d1 = Dp[p1][:, 0]
    R = np.stack([Dp[k][:, 0] for _, k in rungs], 1)  # [L, nr]
    nearest = [rungs[int(np.argmin(np.abs(R[l] - d1[l])))][0] for l in range(L)]
    out = {"nearest": nearest, "rungD": R.tolist(), "D1": d1.tolist(),
           "ratio_to_rung": (d1[:, None] / R).tolist()}
    if coord:
        def xcoord(d, r):  # d [..], r [..., 3]
            r0, r1, r2 = r[..., 0], r[..., 1], r[..., 2]
            ordered = (r0 < r1) & (r1 < r2)
            x = np.where(d <= r1, (d - r0) / (r1 - r0), 1 + (d - r1) / (r2 - r1))
            return np.where(ordered, x, np.nan), ordered
        x, ordd = xcoord(d1, R)
        Rb = np.stack([Db[k][:, :, 0] for _, k in rungs], -1)  # [NB, L, 3]
        xb, ob = xcoord(Db[p1][:, :, 0], Rb)
        lo = np.array([np.nanpercentile(xb[:, l], 2.5) if np.isfinite(xb[:, l]).any() else np.nan for l in range(L)])
        hi = np.array([np.nanpercentile(xb[:, l], 97.5) if np.isfinite(xb[:, l]).any() else np.nan for l in range(L)])
        out.update(x=np.where(np.isfinite(x), x, None).tolist(), x_lo=np.where(np.isfinite(lo), lo, None).tolist(),
                   x_hi=np.where(np.isfinite(hi), hi, None).tolist(), ordered=ordd.tolist(),
                   frac_ordered_boot=ob.mean(0).tolist())
    return out


def seg_summary(lad, L):
    res = {}
    segs = dict(SEG[L])
    segs["other"] = [l for l in range(L) if l not in segs["edge"] and l not in segs["mid"]]
    for s, ls in segs.items():
        if not ls:
            continue
        near = [lad["nearest"][l] for l in ls]
        modal = max(set(near), key=near.count)
        d = {"layers": fmt_runs(ls), "modal_nearest": modal, "counts": {k: near.count(k) for k in sorted(set(near))}}
        if "x" in lad:
            xs = [lad["x"][l] for l in ls if lad["x"][l] is not None]
            d["x_median"] = float(np.median(xs)) if xs else None
            d["n_unordered"] = sum(1 for l in ls if not lad["ordered"][l])
        res[s] = d
    return res


def analyze(key, CAP):
    meta = json.load(open(os.path.join(CAP, "meta.json")))
    langs, NS, D, K, E, L = meta["langs"], meta["n_sent"], meta["draws"], meta["K"], meta["E"], meta["L"]
    NR = 1 + 2 * D
    FAM = {"T": [0], "N_A": list(range(1, 1 + D)), "N_B": list(range(1 + D, 1 + 2 * D))}
    Wb, hA = boot_weights(NS)
    res = {"model": NAME[key], "L": L, "E": E, "K": K, "meta": {k: meta[k] for k in (
        "hook_agreement", "t_vs_model", "det_exact_min", "loadtv_B_mean", "loadtv_B_max", "nsel", "ntok",
        "n_cal", "wall_s", "max_sentence_n")}}
    D_all, C_all = {}, {}
    for c in C.CLASSES:
        PSc = np.load(os.path.join(CAP, f"ps_{c}.npy"), mmap_mode="r")
        Dp, Db = distances(PSc, langs, NS, Wb, hA, PAIRS, SPLITS, L, NR, E)
        D_all[c] = (Dp, Db)
        C_all[c] = {g: contrast(Dp, Db, a, b, FAM, L) for g, (a, b, _) in CONTR.items()}
        print(key, "class", c, "done", flush=True)
    res["contrasts"] = C_all
    res["D"] = {c: {k: v.tolist() for k, v in Dp.items()} for c, (Dp, _) in D_all.items()}
    res["Dci_T"] = {c: {k: np.percentile(Db[k][:, :, 0], [2.5, 97.5], axis=0).tolist() for k in Db}
                    for c, (_, Db) in D_all.items()}
    res["Dnull"] = {c: {k: {f: [Dp[k][:, FAM[f]].mean(1).tolist(), Dp[k][:, FAM[f]].min(1).tolist(),
                                Dp[k][:, FAM[f]].max(1).tolist()] for f in ("N_A", "N_B")} for k in Dp}
                    for c, (Dp, _) in D_all.items()}
    # decisions
    res["decision"] = {}
    for g in CONTR:
        dn = decide(C_all["LET"][g], C_all["NON"][g], L)
        dt = decide(C_all["LET"][g], C_all["NONtm"][g], L)
        dn["tm_variant"] = {k: dt[k] for k in ("branch", "C2", "band", "C3", "C3b", "C3b_mean_exNON", "ii", "ii_n")}
        dn["tm_flips"] = (dn["C2"] != dt["C2"]) or (dn["C3"] != dt["C3"])
        res["decision"][g] = dn
    # R3 ladders
    res["ladder"] = {}
    for c in ("ALL", "LET", "NON"):
        Dp, Db = D_all[c]
        lS = ladder(Dp, Db, LADDER_S, "P1", L)
        lSL = ladder(Dp, Db, LADDER_SL, "P1", L, coord=False)
        lU = ladder(Dp, Db, LADDER_U, "P1U", L, coord=False)
        ratio = {g: {f: (Dp[a][:, FAM[f]].mean(1) / Dp[b][:, FAM[f]].mean(1)).tolist() for f in FAM}
                 for g, (a, b, _) in CONTR.items()}
        res["ladder"][c] = {"S": lS, "S_latin": lSL, "U": lU, "ratio": ratio,
                            "S_seg": seg_summary(lS, L), "S_latin_seg": seg_summary(lSL, L), "U_seg": seg_summary(lU, L)}
    # floors per class (T)
    res["floor"] = {}
    for c in C.CLASSES:
        Dp = D_all[c][0]
        res["floor"][c] = {g: {"P1/P0_min": float((Dp[a][:, 0] / Dp[p0][:, 0]).min()),
                               "P1/P0_med": float(np.median(Dp[a][:, 0] / Dp[p0][:, 0])),
                               "P2/P0_min": float((Dp[b][:, 0] / Dp[p0][:, 0]).min()),
                               "P2/P0_med": float(np.median(Dp[b][:, 0] / Dp[p0][:, 0]))}
                           for g, (a, b, p0) in CONTR.items()}
    # sanity: equalisation per class, NONtm multisets, topk recount
    tm = np.load(os.path.join(CAP, "tokmeta.npz"))
    tlang, tsid, tinp = tm["lang"], tm["sid"], tm["inp"]
    li = {lg: i for i, lg in enumerate(langs)}
    eq = {}
    for c in C.CLASSES:
        sel = tm["sel_" + c]
        mx = 0
        for g, gl in meta["groups"].items():
            cn = np.stack([np.bincount(tsid[(tlang == li[x]) & sel], minlength=NS) for x in gl])
            mx = max(mx, int((cn.max(0) - cn.min(0)).max()))
        eq[c] = mx
    res["equalisation_max_diff"] = eq
    bad = 0
    sel = tm["sel_NONtm"]
    for g, gl in meta["groups"].items():
        per = []
        for x in gl:
            m = (tlang == li[x]) & sel
            o = np.lexsort((tinp[m], tsid[m]))
            per.append((tsid[m][o], tinp[m][o]))
        bad += sum(int(not (np.array_equal(p[0], per[0][0]) and np.array_equal(p[1], per[0][1]))) for p in per)
    res["nontm_multiset_mismatch_sides"] = bad
    TK = np.load(os.path.join(CAP, "topk_T.npy"), mmap_mode="r")
    l0 = L // 2
    dmax = 0
    for c in C.CLASSES:
        PSc = np.load(os.path.join(CAP, f"ps_{c}.npy"), mmap_mode="r")
        for x in ("srp_Cyrl", "uzn_Cyrl"):
            m = (tlang == li[x]) & tm["sel_" + c]
            oh = np.bincount(np.asarray(TK[l0][m]).reshape(-1).astype(np.int64), minlength=E)
            dmax = max(dmax, int(np.abs(oh - np.asarray(PSc[l0, li[x] * NS:(li[x] + 1) * NS, 0]).sum(0)).max()))
    res["topk_recount_absdiff"] = dmax
    cls = tm["cls"]
    res["class_share"] = {lg: {n: float(np.mean(cls[tlang == i] == v)) for n, v in meta["cls_code"].items()}
                          for lg, i in li.items()}
    return res


def a1(key, CAP):
    """Aux A1: E180 dev arrays, T only, same class definition and per-sentence per-class equalisation (S, 10 sides)."""
    from transformers import AutoTokenizer
    meta = json.load(open(os.path.join(CAP, "meta.json")))
    langs, NS, K, E = meta["langs"], meta["n_sent"], meta["K"], meta["E"]
    tm = np.load(os.path.join(CAP, "tokmeta.npz"))
    TK = np.load(os.path.join(CAP, "topk.npy"), mmap_mode="r")
    L = TK.shape[0]
    tlang, tsid, tinp = tm["lang"], tm["sid"], tm["inp"]
    tok = AutoTokenizer.from_pretrained(HF[key])
    code = {"let": 1, "non": 2}
    cmap = {int(t): code.get(C.token_class(tok.decode([int(t)])), 0) for t in np.unique(tinp)}
    tcls = np.array([cmap[int(t)] for t in tinp], np.int8)
    S = C.GROUPS["S"]
    li = {lg: langs.index(lg) for lg in S}
    rs = np.random.default_rng(182)
    sel = {c: np.zeros(len(tinp), bool) for c in (1, 2)}
    idx_by = {(lg, c): {} for lg in S for c in (1, 2)}
    for lg in S:
        m = tlang == li[lg]
        for c in (1, 2):
            ii = np.flatnonzero(m & (tcls == c))
            order = np.argsort(tsid[ii], kind="stable")
            ii = ii[order]
            bounds = np.searchsorted(tsid[ii], np.arange(NS + 1))
            idx_by[(lg, c)] = [ii[bounds[s]:bounds[s + 1]] for s in range(NS)]
    for s in range(NS):
        for c in (1, 2):
            n = min(len(idx_by[(lg, c)][s]) for lg in S)
            for lg in S:
                sel[c][rs.choice(idx_by[(lg, c)][s], n, replace=False)] = True
    Wb, _ = boot_weights(NS)
    out = {}
    pairs = {k: PAIRS[k] for k in ("P1", "P2n")}
    for c, cn in ((1, "LET"), (2, "NON")):
        dp = np.zeros(L)
        db = np.zeros((NB, L))
        for l in range(L):
            cnt = {}
            for lg in S:
                m = np.flatnonzero((tlang == li[lg]) & sel[c])
                M = np.zeros((NS, E), np.float32)
                np.add.at(M, (np.repeat(tsid[m], K), np.asarray(TK[l, m, 0]).reshape(-1).astype(np.int64)), 1.0)
                cnt[lg] = M
            pt = {lg: M.sum(0) for lg, M in cnt.items()}
            bt = {lg: Wb @ M for lg, M in cnt.items()}
            Dk = {k: np.mean([jsd2(norm(pt[a]), norm(pt[b])) for a, b in v]) for k, v in pairs.items()}
            Bk = {k: np.mean([jsd2(norm(bt[a]), norm(bt[b])) for a, b in v], 0) for k, v in pairs.items()}
            dp[l], db[:, l] = Dk["P1"] - Dk["P2n"], Bk["P1"] - Bk["P2n"]
        lo, hi = np.percentile(db, [2.5, 97.5], axis=0)
        out[cn] = {"delta": dp.tolist(), "lo": lo.tolist(), "hi": hi.tolist(),
                   "pos_set": [l for l in range(L) if lo[l] > 0], "neg_set": [l for l in range(L) if hi[l] < 0],
                   "n_per_side": int(sel[c][tlang == li["srp_Cyrl"]].sum()),
                   "edge_mean": float(dp[SEG[L]["edge"]].mean()), "mid_mean": float(dp[SEG[L]["mid"]].mean())}
    out["L"] = L
    return out


# ------------------------------------------------------------------------------------------------ figures
def fig(key, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    L = res["L"]
    x = np.arange(L)
    fig, ax = plt.subplots(2, 3, figsize=(16, 8))
    for row, (g, p1, title, rungs) in enumerate((("S", "P1", "Serbian srp_Cyrl↔srp_Latn", LADDER_S),
                                                  ("U", "P1U", "Uzbek uzn_Latn↔uzn_Cyrl", LADDER_U))):
        for col, c in enumerate(("LET", "NON")):
            a = ax[row, col]
            cr = res["contrasts"][c][g]
            y, lo, hi = (np.array(cr["T"][q]) for q in ("delta", "lo", "hi"))
            a.plot(x, y, color="k", lw=1.7, label="T")
            a.fill_between(x, lo, hi, color="k", alpha=.18, lw=0)
            nb = np.array(cr["N_B"]["delta"])
            a.plot(x, nb, color="#16a085", lw=1.2, ls="--", label="N_B (8-draw mean)")
            a.fill_between(x, cr["N_B"]["draw_min"], cr["N_B"]["draw_max"], color="#16a085", alpha=.18, lw=0,
                           label="N_B draw range")
            a.plot(x, cr["N_A"]["delta"], color="#e67e22", lw=1.0, ls=":", label="N_A (8-draw mean)")
            if c == "NON":
                a.plot(x, res["contrasts"]["NONtm"][g]["T"]["delta"], color="#8e44ad", lw=1.0, alpha=.8,
                       label="T, type-matched (NONtm)")
                band = res["decision"][g]["band"]
                if band:
                    a.axvspan(band[0] - .5, band[-1] + .5, color="#2471a3", alpha=.08, lw=0, label="C2 band")
            a.axhline(0, color="grey", lw=.8)
            a.set_xlabel("layer")
            a.set_ylabel("Δ = D(P1) − D(P2)")
            a.set_title(f"{title}: Δ on {'letter' if c == 'LET' else 'letterless'} tokens", fontsize=9)
            a.legend(fontsize=6.5)
        a = ax[row, 2]
        lad = res["ladder"]["ALL"][g if g == "S" else "U"]
        d1 = np.array(lad["D1"])
        lo, hi = np.array(res["Dci_T"]["ALL"][p1])
        a.plot(x, d1, color="#c0392b", lw=2, label="script switch (P1)")
        a.fill_between(x, lo, hi, color="#c0392b", alpha=.25, lw=0)
        R = np.array(lad["rungD"])
        cols = ["#7d3c98", "#2471a3", "#239b56"]
        for j, (nm, _) in enumerate(rungs):
            a.plot(x, R[:, j], color=cols[j], lw=1.3, label=f"same script → {nm}")
        a.set_yscale("log")
        a.set_xlabel("layer")
        a.set_ylabel("routing JSD (bits, log), all tokens, T")
        a.set_title("script-switch cost on a language-distance ladder", fontsize=9)
        a.legend(fontsize=6.5)
    fig.suptitle(f"E182 {res['model']} — decision S: {res['decision']['S']['branch']}; U: {res['decision']['U']['branch']}",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"fig_{key}.png"), dpi=150)
    plt.close(fig)


if len(sys.argv) > 2 and sys.argv[2] == "--fig-only":
    for key, r in json.load(open(os.path.join(OUT, "summary.json"))).items():
        if key != "_a1":
            fig(key, r)
    sys.exit(0)

# ------------------------------------------------------------------------------------------------ run + tables
# each model's result goes to OUT/_parts/<key>.json (so models can run in parallel); tables are rebuilt from all parts
PARTS = os.path.join(OUT, "_parts")
os.makedirs(PARTS, exist_ok=True)
for key, cap in CAPS.items():
    r = analyze(key, cap)
    json.dump(r, open(os.path.join(PARTS, f"{key}.json"), "w"))
    fig(key, r)
for k, cap in A1CAPS.items():
    json.dump(a1(k, cap), open(os.path.join(PARTS, f"_a1_{k}.json"), "w"))
allres, A1 = {}, {}
for fn in sorted(os.listdir(PARTS)):
    if fn.startswith("_a1_"):
        A1[fn[4:-5]] = json.load(open(os.path.join(PARTS, fn)))
    elif fn.endswith(".json"):
        allres[fn[:-5]] = json.load(open(os.path.join(PARTS, fn)))
allres["_a1"] = A1
json.dump(allres, open(os.path.join(OUT, "summary.json"), "w"))
del allres["_a1"]

f4 = lambda v: f"{v:+.4f}"
ci = lambda cf, l: f"{cf['delta'][l]:+.4f} [{cf['lo'][l]:+.4f}, {cf['hi'][l]:+.4f}]"
cie = lambda cf, l: f"{cf['val'][l]:+.4f} [{cf['lo'][l]:+.4f}, {cf['hi'][l]:+.4f}]"
md = ["# E182 结果表（自动生成：scripts/e182_analyze.py）\n",
      "D = 逐层路由 JSD（底 2，专家使用分布，逐句逐类别等 token 抽样）。Δ = D(P1) − D(P2)：S 组 P1 = srp_Cyrl↔srp_Latn、P2 = srp_Cyrl↔mkd/bul；"
      "U 组 P1 = uzn_Latn↔uzn_Cyrl、P2 = mean(uzn_Latn↔tur/azj, uzn_Cyrl↔kaz/kir)；H 组 P1 = hin↔urd、P2 = mean(hin↔npi/mar, urd↔snd/pes)。"
      "LET = 带字母 token，NON = 无字母 token，NONtm = 类型匹配的无字母 token，ALL = 全部。[ ] = 句子配对 bootstrap 95%（1000 次）；"
      "零模型 = 8 draws 均值。excess = Δ_T − mean Δ_N_B（同一 bootstrap 给区间）。测量 = FLORES-200 devtest 1012 句。\n"]
main_keys = [k for k in ("qwen3", "qwen3base", "gptoss", "olmoe") if k in allres]
cat = lambda b: "partial" if b.startswith("partial") else b
crit_diff = lambda dS, dU: ", ".join(f"{c}: S {'过' if dS[c] else '不过'} / U {'过' if dU[c] else '不过'}"
                                     for c in ("C1", "C2", "C3") if dS[c] != dU[c])
iv_cell = lambda dS, dU: ("是" if cat(dU["branch"]) != cat(dS["branch"]) else "否") + \
    (f"（逐条不一致：{crit_diff(dS, dU)}）" if crit_diff(dS, dU) else "")
md.append("## 决策汇总\n")
md.append("| 模型 | S 分支 | C1 Δ_LET>0 层 | C2 Δ_NON 不显著>0 的中段带 | C3a excess_LET>0 层 | C3b 带上 excess LET / NON | (ii) Δ_NON>0 层 | NONtm 是否翻转 C2/C3 | U 分支 | (iv)? | H 分支 |")
md.append("|---|---|---|---|---|---|---|---|---|---|---|")
for k in list(main_keys) + (["gptoss_cal100"] if "gptoss_cal100" in allres else []):
    r = allres[k]
    L = r["L"]
    dS, dU, dH = (r["decision"][g] for g in ("S", "U", "H"))
    md.append(f"| {NAME[k]} | **{dS['branch']}** | {dS['C1_n']}/{L} | {fmt_runs(dS['band'])}（{len(dS['band'])} 层，需 ≥ {dS['band_need']}） | "
              f"{dS['C3a_n']}/{L} | {dS['C3b_mean_exLET']:+.4f} / {dS['C3b_mean_exNON']:+.4f}（{dS['C3b_layers']}） | {dS['ii_n']}/{L} | "
              f"{'是' if dS['tm_flips'] else '否'}（tm: {dS['tm_variant']['branch']}） | **{dU['branch']}** | "
              f"{iv_cell(dS, dU)} | {dH['branch']} |")
brs = [allres[k]["decision"]["S"]["branch"] for k in main_keys]
md.append("\n(iv) 按分支类别比较（(i-m) / (ii-m) / 部分）；类别相同时另列 C1 / C2 / C3 逐条是否一致（实质分歧，不改分支）。")
glob = "(i)" if all(b == "(i-m)" for b in brs) else "(ii)" if all(b == "(ii-m)" for b in brs) else "(iii)"
md.append(f"\n全局分支（S，四个模型）：**{glob}**；(iv)（分支类别不同）模型：" +
          (", ".join(NAME[k] for k in main_keys if cat(allres[k]["decision"]["U"]["branch"]) != cat(allres[k]["decision"]["S"]["branch"])) or "无") +
          "；C1–C3 逐条不一致的模型：" + ("; ".join(f"{NAME[k]}（{crit_diff(allres[k]['decision']['S'], allres[k]['decision']['U'])}）"
                                       for k in main_keys if crit_diff(allres[k]["decision"]["S"], allres[k]["decision"]["U"])) or "无"))

md.append("\n## 层段均值（T 与 N_B 的 Δ；excess = T − N_B）\n")
md.append("| 模型 | 组 | 类别 | Δ_T edge / mid | Δ_N_B edge / mid | Δ_N_A edge / mid | excess_N_B edge / mid | Δ_T>0 层 | Δ_T<0 层 |")
md.append("|---|---|---|---|---|---|---|---|---|")
for k in main_keys:
    r = allres[k]
    for g in ("S", "U", "H"):
        for c in ("ALL", "LET", "NON", "NONtm"):
            cr = r["contrasts"][c][g]
            md.append(f"| {NAME[k]} | {g} | {c} | {cr['T']['edge_mean']:+.4f} / {cr['T']['mid_mean']:+.4f} | "
                      f"{cr['N_B']['edge_mean']:+.4f} / {cr['N_B']['mid_mean']:+.4f} | {cr['N_A']['edge_mean']:+.4f} / {cr['N_A']['mid_mean']:+.4f} | "
                      f"{cr['excess_N_B']['edge_mean']:+.4f} / {cr['excess_N_B']['mid_mean']:+.4f} | {fmt_runs(cr['T']['pos_set'])} | {fmt_runs(cr['T']['neg_set'])} |")

md.append("\n## R3 文字切换代价的语言距离标尺（T；按层段：众数最近级、坐标 x 中位；x：hrv(0)=0, mkd/bul=1, rus/ukr=2）\n")
md.append("| 模型 | 类别 | S edge | S middle | S other | S 拉丁副梯级 edge / mid | U edge | U middle | U other | r = D(P1)/D(P2) 中位 S / U / H（T；N_B） |")
md.append("|---|---|---|---|---|---|---|---|---|---|")
for k in main_keys:
    r = allres[k]
    for c in ("ALL", "LET", "NON"):
        lad = r["ladder"][c]
        def sg(s, seg):
            d = s.get(seg)
            if not d:
                return "—"
            x = d.get("x_median")
            return f"{d['modal_nearest']} {d['counts']}" + (f"，x̃={x:.2f}" if x is not None else "") + \
                (f"，无序 {d['n_unordered']}" if d.get("n_unordered") else "")
        rt = lad["ratio"]
        med = lambda g, f: float(np.median(rt[g][f]))
        md.append(f"| {NAME[k]} | {c} | {sg(lad['S_seg'], 'edge')} | {sg(lad['S_seg'], 'mid')} | {sg(lad['S_seg'], 'other')} | "
                  f"{lad['S_latin_seg']['edge']['modal_nearest']} / {lad['S_latin_seg']['mid']['modal_nearest']} | "
                  f"{sg(lad['U_seg'], 'edge')} | {sg(lad['U_seg'], 'mid')} | {sg(lad['U_seg'], 'other')} | "
                  f"{med('S', 'T'):.2f} / {med('U', 'T'):.2f} / {med('H', 'T'):.2f}（{med('S', 'N_B'):.2f} / {med('U', 'N_B'):.2f} / {med('H', 'N_B'):.2f}） |")

for k in list(main_keys) + (["gptoss_cal100"] if "gptoss_cal100" in allres else []):
    r = allres[k]
    L = r["L"]
    mt = r["meta"]
    md.append(f"\n## {NAME[k]}（{L} 层，E={r['E']}，k={r['K']}）\n")
    md.append(f"- 每侧被抽 token（类别 / 组）：{mt['nsel']}")
    md.append(f"- 阳性对照：两次前向 top-k 完全一致率 min {mt['det_exact_min']:.4f}；hook fp32 重算 vs 模型 {mt['hook_agreement']:.4f}；"
              f"T logits vs 模型 {mt['t_vs_model']:.4f}；N_B 负载 TV 均值 {mt['loadtv_B_mean']:.4f}（最大 {mt['loadtv_B_max']:.4f}；校准 dev 前 {mt['n_cal']} 句）；"
              f"逐句逐类别被抽数组内最大差 {r['equalisation_max_diff']}；NONtm 类型多重集不一致的语侧 {r['nontm_multiset_mismatch_sides']}；"
              f"T top-k 重新计数差 {r['topk_recount_absdiff']}")
    md.append("- 逐类别地板（T；D(P1)/D(P0)、D(P2)/D(P0) 最小 / 中位）：" + "；".join(
        f"{c} " + ", ".join(f"{g} {v['P1/P0_min']:.2f}/{v['P1/P0_med']:.2f}, {v['P2/P0_min']:.2f}/{v['P2/P0_med']:.2f}"
                            for g, v in r["floor"][c].items()) for c in ("LET", "NON", "NONtm")))
    cs = r["class_share"]
    md.append("- token 类别占比（let / non / frag / apos）：" + "；".join(
        f"{lg} {v['let']:.2f}/{v['non']:.2f}/{v['frag']:.2f}/{v['apos']:.2f}" for lg, v in cs.items()))
    for g, nm in (("S", "塞语"), ("U", "乌兹别克")):
        md.append(f"\n**{nm}组逐层（T [95%]；N_B = 8-draw 均值；excess = T − N_B）**\n")
        md.append("| 层 | Δ_LET T | N_B | excess_LET | Δ_NON T | N_B | excess_NON | Δ_NONtm T | R3 最近级 ALL / LET / NON | x (ALL) [95%] |")
        md.append("|---|---|---|---|---|---|---|---|---|---|")
        cl, cn, ct = (r["contrasts"][c][g] for c in ("LET", "NON", "NONtm"))
        for l in range(L):
            near = " / ".join(r["ladder"][c][g]["nearest"][l] for c in ("ALL", "LET", "NON"))
            if g == "S":
                la = r["ladder"]["ALL"]["S"]
                xs = "—" if la["x"][l] is None else (f"{la['x'][l]:.2f} [" + ("?" if la["x_lo"][l] is None else f"{la['x_lo'][l]:.2f}") +
                                                     ", " + ("?" if la["x_hi"][l] is None else f"{la['x_hi'][l]:.2f}") + "]")
            else:
                rr = r["ladder"]["ALL"]["U"]["ratio_to_rung"][l]
                xs = f"P1/kaz-kir {rr[0]:.2f}, P1/tur-azj {rr[1]:.2f}"
            md.append(f"| {l} | {ci(cl['T'], l)} | {cl['N_B']['delta'][l]:+.4f} | {cie(cl['excess_N_B'], l)} | {ci(cn['T'], l)} | "
                      f"{cn['N_B']['delta'][l]:+.4f} | {cie(cn['excess_N_B'], l)} | {ci(ct['T'], l)} | {near} | {xs} |")
    md.append("\n**H 组（hin↔urd，不同译文，只报）：** " + "；".join(
        f"{c}: T Δ>0 层 {fmt_runs(r['contrasts'][c]['H']['T']['pos_set'])}，Δ<0 层 {fmt_runs(r['contrasts'][c]['H']['T']['neg_set'])}"
        for c in ("ALL", "LET", "NON")))

if A1:
    md.append("\n## 辅读数 A1：E180 dev 数组上的 T（同一类别定义与逐句逐类别均衡，S 组 10 语侧）\n")
    md.append("| 模型 | Δ_LET T>0 层 | Δ_LET<0 层 | edge / mid | Δ_NON T>0 层 | Δ_NON<0 层 | edge / mid | 每侧 n LET / NON |")
    md.append("|---|---|---|---|---|---|---|---|")
    for k, a in A1.items():
        L = a["L"]
        md.append(f"| {NAME[k]} | {fmt_runs(a['LET']['pos_set'])}（{len(a['LET']['pos_set'])}/{L}） | {fmt_runs(a['LET']['neg_set'])} | "
                  f"{a['LET']['edge_mean']:+.4f} / {a['LET']['mid_mean']:+.4f} | {fmt_runs(a['NON']['pos_set'])} | {fmt_runs(a['NON']['neg_set'])} | "
                  f"{a['NON']['edge_mean']:+.4f} / {a['NON']['mid_mean']:+.4f} | {a['LET']['n_per_side']} / {a['NON']['n_per_side']} |")

open(os.path.join(OUT, "tables.md"), "w").write("\n".join(md) + "\n")
print("\n".join(md[:40]))
