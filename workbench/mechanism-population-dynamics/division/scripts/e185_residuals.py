"""E185 residuals.  Card: division/experiments/E185-routing-variance-atlas.md

  --part a     : D184 per-input-id contributions to I(e; pred | inp) (T vs N_B draws), layers L//2 and L-1.
  --part b182  : D182 JSD decomposition (observed vs lexical counterfactual) for S/U pairs, T only, sel_LET/sel_NON.
  --part b180  : D180 same for the Slavic group (srp_Cyrl/srp_Latn/mkd/bul/hrv), T / N_A0 / N_B0, own balancing.
  --part nullagg : D182 aggregated 17-router counts -> I_slot(e; side / lang / script) per group and class.
writes results/e185/res_<part>_<model>.json"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
import scipy.sparse as sp

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import CACHE, BANDS, tokclass_table, jdump, H_keys  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--part", required=True, choices=["a", "b182", "b180", "nullagg"])
ap.add_argument("--model", required=True)
ap.add_argument("--boot", type=int, default=200)
args = ap.parse_args()
RES = os.environ.get("E185_RES", os.path.join(os.path.dirname(__file__), "..", "results", "e185"))
rng = np.random.default_rng(185)


def jsd(p, q):
    p = p / p.sum(-1, keepdims=True)
    q = q / q.sum(-1, keepdims=True)
    m = (p + q) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(p > 0, p * np.log2(p / m), 0).sum(-1)
        b = np.where(q > 0, q * np.log2(q / m), 0).sum(-1)
    return (a + b) / 2


# ============================================================== part a
if args.part == "a":
    base = f"{CACHE}/e184/{args.model}"
    meta = json.load(open(f"{base}/meta.json"))
    tm = dict(np.load(f"{base}/tokmeta.npz"))
    L, E = meta["L"], meta["E"]
    topk = np.load(f"{base}/topk.npy", mmap_mode="r")
    keep = np.where(tm["nxt"] >= 0)[0]
    inp, pred, nxt = tm["inp"][keep], tm["pred"][keep], tm["nxt"][keep]
    seq = tm["seq"][keep].astype(np.int64) + 100000 * tm["corpus"][keep]
    from e185_lib import dense, pool_rare, shuffle_within
    S = dense(inp)
    X = pool_rare(dense(pred))
    N = S.size
    shs = [shuffle_within(X, S, rng) for _ in range(3)]
    tok, strs, _ = tokclass_table(args.model)
    nS = S.max() + 1
    cS = np.bincount(S, minlength=nS)

    def per_stratum_I(e, Xc):
        """plug-in I(e;X | S=s) * p(s) for every stratum s (bits)."""
        def Hs(keys_s, keys_full):
            # sum over cells within each stratum of -c log c, grouped by stratum
            u, c = np.unique(keys_full, return_counts=True)
            st = keys_s[np.searchsorted(keys_full, u, sorter=None)] if False else None
            return u, c
        out = np.zeros(nS)
        # H(e|S=s), H(e|S=s,X) via cell counts
        def neg_clogc_by_stratum(key):
            u, inv, c = np.unique(key, return_inverse=True, return_counts=True)
            first = np.zeros(len(u), np.int64)
            first[inv] = np.arange(key.size)
            s_of_cell = S[first]
            return np.bincount(s_of_cell, weights=c * np.log2(c), minlength=nS)
        a = neg_clogc_by_stratum(S * E + e)                                # sum c log c over (s,e)
        b = neg_clogc_by_stratum((S.astype(np.int64) * (X.max() + 1) + Xc) * E + e)   # over (s,x,e)
        c2 = neg_clogc_by_stratum(S.astype(np.int64) * (X.max() + 1) + Xc)            # over (s,x)
        # N p(s) I(e;X|s) = sum_{sxe} c log c - sum_{sx} c log c - sum_{se} c log c + c_s log c_s
        with np.errstate(divide="ignore", invalid="ignore"):
            cs_log = np.where(cS > 0, cS * np.log2(np.maximum(cS, 1)), 0)
        return (b - c2 - a + cs_log) / N

    res = {"model": args.model, "layers": {}}
    lay = [L // 2, L - 1]
    for l in lay:
        blk = np.asarray(topk[l][keep, :, 0]).astype(np.int64)        # [N, 17]
        contrib = np.zeros((17, nS))
        for r in range(17):
            e = blk[:, r]
            I = per_stratum_I(e, X)
            fl = np.mean([per_stratum_I(e, x) for x in shs], 0)
            contrib[r] = I - fl
        T, NB, NA = contrib[0], contrib[9:].mean(0), contrib[1:9].mean(0)
        d = T - NB
        ids_of = np.zeros(nS, np.int64)
        ids_of[S] = inp
        rows = []
        for j in list(np.argsort(d)[:12]) + list(np.argsort(d)[::-1][:12]):
            x = int(ids_of[j])
            occ = np.where(S == j)[0]
            # how many distinct predicted ids follow this input, share of most common
            pc = Counter(pred[occ].tolist())
            rows.append({"id": x, "str": strs[x], "n": int(cS[j]), "T": float(T[j]), "N_B": float(NB[j]),
                         "N_B_min": float(contrib[9:, j].min()), "N_B_max": float(contrib[9:, j].max()),
                         "n_pred_types": len(pc), "top_preds": [(strs[k], v) for k, v in pc.most_common(4)],
                         "pred_correct": float((pred[occ] == nxt[occ]).mean())})
        res["layers"][str(l)] = {"sum_T": float(T.sum()), "sum_NB": float(NB.sum()), "sum_NA": float(NA.sum()),
                                 "sum_NB_draws": contrib[9:].sum(1).tolist(),
                                 "share_of_diff_from_top20_neg": float(np.sort(d)[:20].sum() / d[d < 0].sum()),
                                 "sum_neg_diff": float(d[d < 0].sum()), "sum_pos_diff": float(d[d > 0].sum()),
                                 "most_negative_then_positive": rows}
        # frequency relation: correlation of per-id diff (normalised by p(s)) with log count
        from scipy.stats import spearmanr
        m = cS >= 10
        res["layers"][str(l)]["spearman_diff_per_token_vs_logfreq"] = float(
            spearmanr(d[m] / (cS[m] / N), np.log(cS[m]))[0])
        print("layer", l, res["layers"][str(l)]["sum_T"], res["layers"][str(l)]["sum_NB"], flush=True)
    jdump(os.path.join(RES, f"res_a_{args.model}.json"), res)


# ============================================================== part b (JSD decomposition)
def decompose(top, side, sid, inp, sel, sides, pairs, nboot, NS):
    """top: [N, R, K] experts of selected-or-not tokens; returns per router, per pair: D_obs, D_lex (point + boot)."""
    E = int(top.max()) + 1 if False else None
    out = {}
    m = sel & np.isin(side, sides)
    idx = np.where(m)[0]
    sd, sn, tk = side[idx], sid[idx], inp[idx]
    _, tkd = np.unique(tk, return_inverse=True)
    ntok = tkd.max() + 1
    smap = {s: i for i, s in enumerate(sides)}
    sloc = np.array([smap[s] for s in sd])
    unit = sloc * NS + sn                        # (side, sentence)
    nU = len(sides) * NS
    # token-composition matrix: units x token types
    Mt = sp.csr_matrix((np.ones(idx.size), (unit, tkd)), shape=(nU, ntok))
    # weighted overlap of token distributions per pair (point estimate)
    tokdist = np.asarray(sp.csr_matrix((np.ones(idx.size), (sloc, tkd)), shape=(len(sides), ntok)).todense())
    tokdist /= tokdist.sum(1, keepdims=True)
    boots = [rng.integers(0, NS, NS) for _ in range(nboot)]
    for r in range(top.shape[1]):
        ee = top[idx, r, :].astype(np.int64)        # [n, K]
        Ex = 256
        Ex = int(ee.max()) + 1
        n, K = ee.shape
        obs_u = np.zeros((nU, Ex))
        np.add.at(obs_u, (np.repeat(unit, K), ee.reshape(-1)), 1)
        q = np.zeros((ntok, Ex))
        np.add.at(q, (np.repeat(tkd, K), ee.reshape(-1)), 1)
        q /= q.sum(1, keepdims=True)
        lex_u = (Mt @ q) * K
        res = {}
        for which, U in (("obs", obs_u), ("lex", lex_u)):
            U3 = U.reshape(len(sides), NS, Ex)
            pt = U3.sum(1)
            bt = np.stack([np.stack([np.bincount(b, minlength=NS) @ U3[s] for s in range(len(sides))])
                           for b in boots])                         # [B, sides, E]
            res[which] = (pt, bt)
        out[r] = {}
        for pname, plist in pairs.items():
            vals = {}
            for which in ("obs", "lex"):
                pt, bt = res[which]
                vals[which] = (np.mean([jsd(pt[smap[a]], pt[smap[b]]) for a, b in plist]),
                               np.mean([jsd(bt[:, smap[a]], bt[:, smap[b]]) for a, b in plist], 0))
            ov = np.mean([np.minimum(tokdist[smap[a]], tokdist[smap[b]]).sum() for a, b in plist])
            out[r][pname] = dict(obs=vals["obs"], lex=vals["lex"], overlap=float(ov))
    return out


def summarize(dec, contrasts, L, nR):
    """dec[l][r][pair] -> per router: per layer Delta_obs, Delta_lex, Delta_ctx with boot CI."""
    out = {}
    for r in range(nR):
        rr = {}
        for (p1, p2) in contrasts:
            key = f"{p1}-{p2}"
            rows = {k: [] for k in ("D1_obs", "D2_obs", "D1_lex", "D2_lex", "d_obs", "d_obs_lo", "d_obs_hi",
                                    "d_lex", "d_lex_lo", "d_lex_hi", "d_ctx", "d_ctx_lo", "d_ctx_hi", "ov1", "ov2")}
            for l in range(L):
                a, b = dec[l][r][p1], dec[l][r][p2]
                do = a["obs"][0] - b["obs"][0]
                dl = a["lex"][0] - b["lex"][0]
                bo = a["obs"][1] - b["obs"][1]
                bl = a["lex"][1] - b["lex"][1]
                bc = bo - bl
                rows["D1_obs"].append(a["obs"][0]); rows["D2_obs"].append(b["obs"][0])
                rows["D1_lex"].append(a["lex"][0]); rows["D2_lex"].append(b["lex"][0])
                rows["d_obs"].append(do); rows["d_lex"].append(dl); rows["d_ctx"].append(do - dl)
                for k, v in (("d_obs", bo), ("d_lex", bl), ("d_ctx", bc)):
                    rows[k + "_lo"].append(float(np.quantile(v, .025)))
                    rows[k + "_hi"].append(float(np.quantile(v, .975)))
                rows["ov1"].append(a["overlap"]); rows["ov2"].append(b["overlap"])
            rr[key] = rows
        out[r] = rr
    return out


if args.part in ("b182", "b180"):
    src = "e182" if args.part == "b182" else "e180"
    base = f"{CACHE}/{src}/{args.model}"
    meta = json.load(open(f"{base}/meta.json"))
    tm = dict(np.load(f"{base}/tokmeta.npz"))
    L = meta["L"]
    langs = meta["langs"]
    side = tm["lang"].astype(np.int64)
    sid = tm["sid"].astype(np.int64)
    inp = tm["inp"].astype(np.int64)
    NS = meta["n_sent"]
    LI = {lg: i for i, lg in enumerate(langs)}
    if args.part == "b182":
        topk = np.load(f"{base}/topk_T.npy", mmap_mode="r")
        groups = {"S": ["srp_Cyrl", "srp_Latn", "mkd_Cyrl", "bul_Cyrl", "hrv_Latn"],
                  "U": ["uzn_Latn", "uzn_Cyrl", "kaz_Cyrl", "kir_Cyrl", "tur_Latn", "azj_Latn"]}
        sels = {c: tm[f"sel_{c}"] for c in ("LET", "NON", "ALL")}
        rnames = ["T"]
    else:
        topk = np.load(f"{base}/topk.npy", mmap_mode="r")
        groups = {"S": ["srp_Cyrl", "srp_Latn", "mkd_Cyrl", "bul_Cyrl", "hrv_Latn"]}
        rnames = meta["topk_routers"]
        # own per-sentence per-class balancing over the Slavic group (E182 rule, seed 185)
        _, _, clsv = tokclass_table(args.model)
        cls = clsv[inp]
        slav = [LI[x] for x in meta["groups"]["slavic"]]
        sels = {}
        for cname, cv in (("LET", 1), ("NON", 2)):
            s = np.zeros(inp.size, bool)
            m = (cls == cv) & np.isin(side, slav)
            idx = np.where(m)[0]
            key = side[idx] * NS + sid[idx]
            order = np.argsort(key, kind="stable")
            ks = key[order]
            u, st, ct = np.unique(ks, return_index=True, return_counts=True)
            cnt = np.zeros((len(langs), NS), np.int64)
            cnt[u // NS, u % NS] = ct
            nmin = cnt[slav].min(0)
            for uu, s0, c0 in zip(u, st, ct):
                k = nmin[uu % NS]
                if k:
                    pick = order[s0 + rng.choice(c0, k, replace=False)]
                    s[idx[pick]] = True
            sels[cname] = s
        sels["ALL"] = tm["sel"]
    pairs = {"S": {"P1": [("srp_Cyrl", "srp_Latn")], "P2n": [("srp_Cyrl", "mkd_Cyrl"), ("srp_Cyrl", "bul_Cyrl")],
                   "hrv0": [("srp_Latn", "hrv_Latn")]},
             "U": {"P1U": [("uzn_Latn", "uzn_Cyrl")],
                   "P2U": [("uzn_Latn", "tur_Latn"), ("uzn_Latn", "azj_Latn"), ("uzn_Cyrl", "kaz_Cyrl"),
                           ("uzn_Cyrl", "kir_Cyrl")],
                   "kazkir": [("uzn_Cyrl", "kaz_Cyrl"), ("uzn_Cyrl", "kir_Cyrl")],
                   "turazj": [("uzn_Latn", "tur_Latn"), ("uzn_Latn", "azj_Latn")]}}
    contrasts = {"S": [("P1", "P2n"), ("hrv0", "P2n")], "U": [("P1U", "P2U"), ("P1U", "kazkir"), ("P1U", "turazj")]}
    full = {"model": args.model, "part": args.part, "routers": rnames, "groups": {}}
    for g, gs in groups.items():
        sides = [LI[x] for x in gs]
        pp = {k: [(LI[a], LI[b]) for a, b in v] for k, v in pairs[g].items()}
        # translate pair lists to side indices used inside decompose (it maps by side id)
        pp2 = {k: [(a, b) for a, b in v] for k, v in pp.items()}
        full["groups"][g] = {}
        for cname, sel in sels.items():
            dec = {}
            for l in range(L):
                blk = np.asarray(topk[l])
                if blk.ndim == 2:
                    blk = blk[:, None, :]
                dec[l] = decompose(blk, side, sid, inp, sel, sides, pp2, args.boot, NS)
            full["groups"][g][cname] = summarize(dec, contrasts[g], L, blk.shape[1])
            print(g, cname, "done", flush=True)
    jdump(os.path.join(RES, f"res_{args.part}_{args.model}.json"), full)


# ============================================================== part nullagg
if args.part == "nullagg":
    base = f"{CACHE}/e182/{args.model}"
    meta = json.load(open(f"{base}/meta.json"))
    L, E = meta["L"], meta["E"]
    langs = meta["langs"]
    NS = meta["n_sent"]
    lang_of = [lg.split("_")[0] for lg in langs]
    scr_of = [lg.split("_")[1] for lg in langs]
    out = {"model": args.model, "groups": {}}

    def mi_counts(C):
        """C: [labels, E] counts -> plug-in I (bits) between label and slot expert."""
        n = C.sum()
        pxy = C / n
        px = pxy.sum(1, keepdims=True)
        py = pxy.sum(0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            return float(np.nansum(np.where(pxy > 0, pxy * np.log2(pxy / (px * py)), 0)))

    for cname in ("ALL", "LET", "NON"):
        ps = np.load(f"{base}/ps_{cname}.npy", mmap_mode="r")      # [L, NU, 17, E]
        for g, gs in meta["groups"].items():
            si = [langs.index(x) for x in gs]
            labs = {"side": np.arange(len(si)),
                    "lang": np.unique([lang_of[i] for i in si], return_inverse=True)[1],
                    "script": np.unique([scr_of[i] for i in si], return_inverse=True)[1]}
            perms = [np.stack([rng.permutation(len(si)) for _ in range(NS)]) for _ in range(3)]  # [NS, sides]
            res = {k: np.zeros((L, 17, 2)) for k in labs}
            for l in range(L):
                blk = np.asarray(ps[l]).astype(np.float64)               # [NU, 17, E]
                U = np.stack([blk[i * NS:(i + 1) * NS] for i in si])       # [sides, NS, 17, E]
                for r in range(17):
                    Ur = U[:, :, r, :]                                     # [sides, NS, E]
                    for k, lab in labs.items():
                        nl = lab.max() + 1
                        C = np.zeros((nl, E))
                        np.add.at(C, lab, Ur.sum(1))
                        I = mi_counts(C)
                        fl = []
                        for P in perms:
                            # within each sentence, side j's counts are reassigned to label of side P[s, j]
                            Cp = np.zeros((nl, E))
                            for j in range(len(si)):
                                lj = lab[P[:, j]]                         # [NS]
                                np.add.at(Cp, lj, Ur[j])
                            fl.append(mi_counts(Cp))
                        res[k][l, r] = (I - np.mean(fl), I)
                print(cname, g, "layer", l, flush=True) if l == L - 1 else None
            out["groups"].setdefault(g, {})[cname] = {k: v.tolist() for k, v in res.items()}
    jdump(os.path.join(RES, f"res_nullagg_{args.model}.json"), out)
