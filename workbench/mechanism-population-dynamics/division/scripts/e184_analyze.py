#!/usr/bin/env python3
"""E184 analysis (card: division/experiments/E184-token-level-claims-under-null.md). CPU only.

Usage: e184_analyze.py MODEL [MODEL ...]   (reads ~/mechpop_cache/e184/<model>/; writes results/e184/<model>.json)
Readouts per layer x router x corpus (router 0 = T, 1..8 = N_A, 9..16 = N_B):
  R1  token-id purity (top-1, ids with N_x >= 5), floor = id permutation (5); + OLMoE vocab spec (k=1, k=K)
  R2  Antoine Spec_POS on UD word-final tokens (UPOS with n_p >= 50), floor = UPOS permutation (5);
      R2w floor = UPOS permutation within input-token id (5); + ST-MoE top-1 class entropy / ln E
  R3  adjacent first-choice repetition rep1, floor = random pairing (5); + repAny, mean overlap
  R4  cross-fitted predictive information G(x) of the top-1 expert, x in {inp, pred, nxt}, A = 8, 2 folds by
      sequence id parity; judged: dG = G(pred) - G(inp) (dG' with nxt); ratio reported only where G(inp) > .05; shuffled-x control; + OLMoE vocab spec k=1
Shuffle control: shuffle draw 0 treated as data vs mean of draws 1..4.
Split halves (FLORES / UD): sequences with even / odd id; R4 folds inside a half use (seq // 2) parity.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
CACHE = Path.home() / "mechpop_cache/e184"
OUT = WB / "results/e184"
A, SEED, NSH, MIN_X, MIN_P = 8.0, 184, 5, 5, 50
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:6.1f}s]", *a, flush=True)


def codes(v):
    return np.unique(v, return_inverse=True)[1].astype(np.int64)


def table(x, e, nx, E, w=None):
    return np.bincount(x * E + e, weights=w, minlength=nx * E).reshape(nx, E)


# ------------------------------------------------------------------ readouts on one subset
def purity(x, e, nx, E):
    N = table(x, e, nx, E)
    return float(N.max(1).sum() / N.sum())


def vocab_spec(x, S, nx, E):
    """OLMoE eq. (8) with E175 expert aggregation; S (n, k) expert ids (k=1 or K)."""
    k = S.shape[1]
    N = table(np.repeat(x, k), S.ravel(), nx, E)  # N^(k)_{x,e}
    Nx = np.bincount(x, minlength=nx).astype(np.float64)
    Ne = N.sum(0)
    ok = Ne > 0
    spec = ((N / np.where(ok, Ne, 1)[None, :]) * (N / Nx[:, None])).sum(0)
    return float(spec[ok].mean())


def spec_pos(p, S, npos, E, K, keep):
    C = table(np.repeat(p, K), S.ravel(), npos, E)
    n = np.bincount(p, minlength=npos).astype(np.float64)
    sp = np.sort(C, 1)[:, ::-1][:, :K].sum(1) / np.maximum(C.sum(1), 1)
    return float((sp[keep] * n[keep]).sum() / n[keep].sum())


def class_entropy(p, e, npos, E, keep):
    C = table(p, e, npos, E)
    n = C.sum(1)
    q = C / np.maximum(n, 1)[:, None]
    H = -(q * np.log(np.where(q > 0, q, 1))).sum(1) / np.log(E)
    return float((H[keep] * n[keep]).sum() / n[keep].sum())


def crossfit_G(x, e, fold, E):
    """E175 estimator: 2-fold cross-fitted predictive information (bits)."""
    nx = int(x.max()) + 1
    g = []
    for f in (0, 1):
        tr, te = fold != f, fold == f
        pm = (np.bincount(e[tr], minlength=E) + 1.0) / (tr.sum() + E)
        N = table(x[tr], e[tr], nx, E)
        P = (N + A * pm[None, :]) / (N.sum(1, keepdims=True) + A)
        g.append(float(-np.log2(pm[e[te]]).mean() + np.log2(P[x[te], e[te]]).mean()))
    return float(np.mean(g))


def within_group_perm(groups, labels, rng):
    p1 = np.lexsort((np.arange(len(groups)), groups))
    p2 = np.lexsort((rng.random(len(groups)), groups))
    out = np.empty_like(labels)
    out[p1] = labels[p2]
    return out


def analyse_subset(TK, meta, sel, E, K, fold_mode, want_secondary=True):
    """TK: (L, NTOK, R, K) uint8 memmap; sel: bool mask over tokens (one corpus or half). Returns dict of arrays."""
    L, _, R, _ = TK.shape
    rng = np.random.default_rng(SEED)
    gi = np.flatnonzero(sel)
    inp, pred, nxt, seq, upos = (meta[k][gi] for k in ("inp", "pred", "nxt", "seq", "upos"))
    # --- R1 eligibility and permutations
    xi = codes(inp)
    cnt = np.bincount(xi)
    el = cnt[xi] >= MIN_X
    x1 = codes(inp[el]); nx1 = int(x1.max()) + 1
    perms1 = [rng.permutation(el.sum()) for _ in range(NSH)]
    # --- R3 adjacent pairs (within sequence)
    a = np.flatnonzero(nxt >= 0)
    assert np.all(seq[a] == seq[a + 1])
    rpairs = [rng.permutation(len(gi))[:len(a)] for _ in range(NSH)]  # random partners
    # --- R4 positions
    xin, xpr, xnx = codes(inp[a]), codes(pred[a]), codes(nxt[a])
    fold = (seq[a] % 2) if fold_mode == "parity" else ((seq[a] // 2) % 2)
    shin, shpr = xin[rng.permutation(len(a))], xpr[rng.permutation(len(a))]
    el_p, el_n = [np.bincount(c)[c] >= MIN_X for c in (xpr, xnx)]
    el_i = np.bincount(xin)[xin] >= MIN_X
    # --- R2 POS
    pw = np.flatnonzero(upos >= 0)
    have_pos = len(pw) > 0
    if have_pos:
        p = upos[pw].astype(np.int64)
        npos = 17
        keep = np.bincount(p, minlength=npos) >= MIN_P
        pperm = [p[rng.permutation(len(p))] for _ in range(NSH)]
        pwin = [within_group_perm(inp[pw], p, rng) for _ in range(NSH)]
    out = {k: np.full((L, R), np.nan) for k in
           ["R1", "R1_floor", "R1_ctrl", "VS1", "VSK", "R3", "R3_floor", "R3_ctrl", "R3any", "R3any_floor",
            "R3ov", "R3ov_floor", "G_in", "G_pred", "G_nxt", "G_shin", "G_shpr", "VS1_in", "VS1_pred", "VS1_nxt",
            "R2", "R2_floor", "R2_ctrl", "R2w_floor", "R2w_ctrl", "R2ent", "loadTV_B", "maxload"]}
    for l in range(L):
        Sl = np.asarray(TK[l, gi])  # (n, R, K)
        for r in range(R):
            S = Sl[:, r, :].astype(np.int64)
            e = S[:, 0]
            # R1
            ee = e[el]
            out["R1"][l, r] = purity(x1, ee, nx1, E)
            fl = [purity(x1[pm], ee, nx1, E) for pm in perms1]
            out["R1_floor"][l, r] = np.mean(fl)
            out["R1_ctrl"][l, r] = fl[0] - np.mean(fl[1:])
            # load diagnostics (K-slot loads)
            ld = np.bincount(S.ravel(), minlength=E) / S.size
            out["maxload"][l, r] = ld.max() * E
            if r == 0:
                ldT = ld
            out["loadTV_B"][l, r] = 0.5 * np.abs(ld - ldT).sum()
            # R3
            e1, e2 = e[a], e[a + 1]
            out["R3"][l, r] = float((e1 == e2).mean())
            fr = [float((e1 == e[rp]).mean()) for rp in rpairs]
            out["R3_floor"][l, r] = np.mean(fr)
            out["R3_ctrl"][l, r] = fr[0] - np.mean(fr[1:])
            # R4
            out["G_in"][l, r] = crossfit_G(xin, e1, fold, E)
            out["G_pred"][l, r] = crossfit_G(xpr, e1, fold, E)
            out["G_nxt"][l, r] = crossfit_G(xnx, e1, fold, E)
            out["G_shin"][l, r] = crossfit_G(shin, e1, fold, E)
            out["G_shpr"][l, r] = crossfit_G(shpr, e1, fold, E)
            if have_pos:
                Sp = S[pw]
                out["R2"][l, r] = spec_pos(p, Sp, npos, E, K, keep)
                fp = [spec_pos(pp, Sp, npos, E, K, keep) for pp in pperm]
                out["R2_floor"][l, r] = np.mean(fp)
                out["R2_ctrl"][l, r] = fp[0] - np.mean(fp[1:])
                fw = [spec_pos(pp, Sp, npos, E, K, keep) for pp in pwin]
                out["R2w_floor"][l, r] = np.mean(fw)
                out["R2w_ctrl"][l, r] = fw[0] - np.mean(fw[1:])
            if not want_secondary:
                continue
            out["VS1"][l, r] = vocab_spec(x1, ee[:, None], nx1, E)
            out["VSK"][l, r] = vocab_spec(x1, S[el], nx1, E)
            S1, S2 = S[a], S[a + 1]
            ov = (S1[:, :, None] == S2[:, None, :]).sum((1, 2))
            out["R3any"][l, r] = float((ov > 0).mean())
            out["R3ov"][l, r] = float(ov.mean() / K)
            ovf = [(S1[:, :, None] == S[rp][:, None, :]).sum((1, 2)) for rp in rpairs[:2]]
            out["R3any_floor"][l, r] = np.mean([(o > 0).mean() for o in ovf])
            out["R3ov_floor"][l, r] = np.mean([o.mean() / K for o in ovf])
            for nm, c, m in (("VS1_in", xin, el_i), ("VS1_pred", xpr, el_p), ("VS1_nxt", xnx, el_n)):
                cc = codes(c[m])
                out[nm][l, r] = vocab_spec(cc, e1[m][:, None], int(cc.max()) + 1, E)
            if have_pos:
                out["R2ent"][l, r] = class_entropy(p, e[pw], npos, E, keep)
        if l % 8 == 0:
            log(f"  layer {l}/{L}")
    out["n_tok"] = len(gi); out["n_pairs"] = len(a); out["n_R1_tokens"] = int(el.sum()); out["n_R1_ids"] = nx1
    out["n_pos_tokens"] = int(len(pw))
    if have_pos:
        out["pos_kept"] = int(keep.sum())
    return out


# ------------------------------------------------------------------ verdicts
def classify(T, NA, NB):
    """per-layer class: above / below / within / split."""
    aA, aB = NA.max(1), NB.max(1)
    iA, iB = NA.min(1), NB.min(1)
    cls = []
    for t, xa, xb, na, nb in zip(T, aA, aB, iA, iB):
        if t > xa and t > xb:
            cls.append("above")
        elif t < na and t < nb:
            cls.append("below")
        elif (na <= t <= xa) or (nb <= t <= xb):
            cls.append("within")
        else:
            cls.append("split")
    return cls


def verdict(T, NA, NB, diff=False):
    cls = classify(T, NA, NB)
    L = len(T)
    need = int(np.ceil(2 * L / 3))
    c = {k: cls.count(k) for k in ("above", "below", "within", "split")}
    if c["above"] >= need:
        v = "survives"
        ab = [i for i, k in enumerate(cls) if k == "above"]
        mx = np.maximum(NA.max(1), NB.max(1))
        if diff:  # claim 4 (bits): median excess over the null max; marginal if < .05 bit
            ratio = float(np.median(T[ab] - mx[ab]))
            marginal = ratio < 0.05
        else:
            ratio = float(np.median(T[ab] / mx[ab])) if np.all(mx[ab] > 0) else float("nan")
            marginal = ratio < 1.25
        if marginal:
            v = "survives (marginal)"
    elif c["within"] >= need:
        v, ratio = "geometry", float("nan")
    elif c["below"] >= need:
        v, ratio = "below-null", float("nan")
    else:
        v, ratio = "null-family-dependent", float("nan")
    if not v.startswith("survives"):
        ratio = float("nan")
    return {"verdict": v, "counts": c, "need": need, "ratio_above_median": ratio, "classes": cls}


def crossover(dg):
    """first layer with G(next) - G(in) > 0 and persistent crossover layer (> 0 at it and all deeper); None if absent."""
    L = len(dg)
    first = next((l for l in range(L) if dg[l] > 0), None)
    pers = None
    for l in range(L - 1, -1, -1):
        if dg[l] > 0:
            pers = l
        else:
            break
    return first, pers


def judged(o, claim, D):
    """judgement quantity per (layer, router)."""
    if claim == "1":
        return o["R1"] - o["R1_floor"]
    if claim == "2":
        return o["R2"] - o["R2_floor"]
    if claim == "2w":
        return o["R2"] - o["R2w_floor"]
    if claim == "3":
        return o["R3"] - o["R3_floor"]
    if claim == "4":  # amended after the smoke test (card, 11-09): difference, not ratio
        return o["G_pred"] - o["G_in"]
    if claim == "4n":
        return o["G_nxt"] - o["G_in"]
    raise ValueError(claim)


def judge_all(o, D, claims):
    res = {}
    for c in claims:
        J = judged(o, c, D)
        T, NA, NB = J[:, 0], J[:, 1:1 + D], J[:, 1 + D:1 + 2 * D]
        v = verdict(T, NA, NB, diff=c in ("4", "4n"))
        from scipy.stats import spearmanr
        v["rho_profile_NB"] = float(spearmanr(T, NB.mean(1)).correlation)
        v["rho_profile_NA"] = float(spearmanr(T, NA.mean(1)).correlation)
        if c in ("4", "4n"):
            cT = crossover(T)
            cn = [crossover(J[:, r]) for r in range(1, 1 + 2 * D)]
            L = len(T)
            pers_null = [x[1] if x[1] is not None else L for x in cn]
            pT = cT[1]
            if pT is None:
                rel = "T no crossover"
            elif pT < min(pers_null):
                rel = "earlier"
            elif pT <= max(pers_null):
                rel = "same"
            else:
                rel = "later"
            v.update(cross_T=cT, cross_NA=[x for x in cn[:D]], cross_NB=[x for x in cn[D:]], cross_rel=rel)
        res[c] = v
    return res


def tolist(o):
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in o.items()}


def main():
    for key in sys.argv[1:]:
        src = CACHE / key
        meta_j = json.load(open(src / "meta.json"))
        E, K, L, D = meta_j["E"], meta_j["K"], meta_j["L"], meta_j["draws"]
        meta = dict(np.load(src / "tokmeta.npz"))
        TK = np.load(src / "topk.npy", mmap_mode="r")
        diag = dict(np.load(src / "diag.npz"))
        corp, seq = meta["corpus"], meta["seq"]
        res = {"meta": meta_j, "det_exact_min": float(diag["det_exact"].min()),
               "loadtv_B_cal_mean": float(diag["loadtv_B"].mean()), "loadtv_B_cal_max": float(diag["loadtv_B"].max())}
        for cname, ci, claims in (("flores", 0, ["1", "3", "4", "4n"]), ("ud", 1, ["1", "2", "2w", "3", "4", "4n"])):
            log(f"{key} {cname} full")
            o = analyse_subset(TK, meta, corp == ci, E, K, "parity")
            res[cname] = {"readouts": tolist(o), "verdicts": judge_all(o, D, claims)}
            for h in (0, 1):
                log(f"{key} {cname} half {h}")
                oh = analyse_subset(TK, meta, (corp == ci) & (seq % 2 == h), E, K, "half", want_secondary=False)
                res[cname][f"half{h}"] = {"verdicts": judge_all(oh, D, claims),
                                          "readouts": {k: tolist(oh)[k] for k in ("R1", "R1_floor", "R2", "R2_floor",
                                                                                   "R2w_floor", "R3", "R3_floor",
                                                                                   "G_in", "G_pred", "G_nxt")}}
        OUT.mkdir(parents=True, exist_ok=True)
        json.dump(res, open(OUT / f"{key}.json", "w"))
        log(f"wrote {OUT / f'{key}.json'}")


if __name__ == "__main__":
    main()
