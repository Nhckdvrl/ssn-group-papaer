#!/usr/bin/env python3
"""E186 readouts that only the enriched store allows (card: division/experiments/E186-atlas-capture-breadth.md,
"新存储才有的读数"). CPU only; reads ~/mechpop_cache/e186/<key>/ (read-only).

  --part ctx    continuous context dependence: per input id (>= 30 occurrences, English view = FLORES eng + UD), the SD
                over occurrences of the top-1 softmax gate p1 = exp(v0 - lse) and of the top-1 margin v0 - v1; per layer
                the id-average for every router; Spearman over ids of SD(p1) T vs N_B-mean.
  --part resa   residual (a) by prediction-entropy tercile (English view, positions with a true next token):
                I_hat(e; pred | inp), I_hat(e; inp), I_hat(e; pred) per tercile (E185 estimator, all 17 routers).
  --part vs8    OLMoE eq. (8) vocabulary specialization (k = 1) for input / predicted-next / true-next id on FLORES eng
                (E184 claim-4 corpus; ids with >= 5 occurrences), all 17 routers.
  --part geom   sentence-mean geometry on the 20 non-English FLORES sides: variance share of language side and of
                parallel-sentence id (SS_between / SS_total), G2-type centroid dispersion (between / within) for both,
                in the raw space and in T's readout subspace (row-centred W_T, rank <= E-1).
  --part sat    training-time saturation (OLMoE-0924 checkpoints vs main): per layer mean |S_t ∩ S_main| / K and top-1
                agreement for T and for the fixed random routers N_F (same matrices at both checkpoints); cross-draw
                N_F baseline; N_F load entropy.  usage: --part sat --key olmoe0924_s5k (reference = olmoe0924_main)
Writes results/e186/extra_<part>_<key>.json"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import Plan, mi_marg, mi_cond, jdump  # noqa: E402

SRC = os.environ.get("E186_SRC", os.path.expanduser("~/mechpop_cache/e186"))
RES = os.path.join(os.path.dirname(__file__), "..", "results", "e186")
ap = argparse.ArgumentParser()
ap.add_argument("--part", required=True, choices=["ctx", "resa", "vs8", "geom", "sat"])
ap.add_argument("--key", required=True)
ap.add_argument("--ref", default="olmoe0924_main")
a = ap.parse_args()
os.makedirs(RES, exist_ok=True)
t0 = time.time()
base = f"{SRC}/{a.key}"
meta = json.load(open(f"{base}/meta.json"))
tm = dict(np.load(f"{base}/tokmeta.npz"))
L, E, K, D = meta["L"], meta["E"], meta["K"], meta["draws"]
iT, iA, iB = 0, list(range(1, 1 + D)), list(range(1 + D, 1 + 2 * D))
# English-view readouts compare T with the English-calibrated N_Ben (补登记 11-09 22:20); iB stays the multilingual family
iBen = list(range(1 + 2 * D, 1 + 3 * D)) if "N_Ben" in meta["router_index"] else iB
eng = meta["sides"].index("eng_Latn")
side, corpus = tm["side"].astype(np.int64), tm["corpus"].astype(np.int64)
engview = np.where((corpus == 1) | (side == eng))[0]
out = {"key": a.key, "part": a.part, "L": L, "E": E, "K": K}


def log(*x):
    print(f"[{time.time() - t0:7.1f}s]", *x, flush=True)


if a.part == "ctx":
    topv = np.load(f"{base}/topv.npy", mmap_mode="r")
    lse = np.load(f"{base}/lse.npy", mmap_mode="r")
    inp = tm["inp"][engview].astype(np.int64)
    cnt = np.bincount(inp)
    ids = np.where(cnt >= 30)[0]
    keep = cnt[inp] >= 30
    tok = engview[keep]
    _, code = np.unique(inp[keep], return_inverse=True)
    n = np.bincount(code).astype(np.float64)
    R = topv.shape[2]
    res = {k: np.zeros((L, R)) for k in ("p1_mean", "p1_sd", "margin_mean", "margin_sd")}
    rho = np.zeros(L)
    from scipy.stats import spearmanr
    for l in range(L):
        v = np.asarray(topv[l][tok]).astype(np.float32)          # [n, R, K]
        z = np.asarray(lse[l][tok]).astype(np.float32)           # [n, R]
        p1 = np.exp(v[..., 0] - z)
        mg = v[..., 0] - v[..., 1]
        sds = {}
        for nm, x in (("p1", p1), ("margin", mg)):
            s1 = np.stack([np.bincount(code, weights=x[:, r]) for r in range(R)], 1) / n[:, None]
            s2 = np.stack([np.bincount(code, weights=x[:, r] ** 2) for r in range(R)], 1) / n[:, None]
            sd = np.sqrt(np.maximum(s2 - s1 ** 2, 0))                # [nid, R]
            res[f"{nm}_mean"][l] = s1.mean(0)
            res[f"{nm}_sd"][l] = sd.mean(0)
            sds[nm] = sd
        rho[l] = spearmanr(sds["p1"][:, iT], sds["p1"][:, iBen].mean(1))[0]
    out.update({k: v.tolist() for k, v in res.items()})
    out.update(spearman_p1sd_T_vs_NB=rho.tolist(), n_ids=int(len(ids)), n_tok=int(tok.size), iB_english=iBen, iA=iA)

elif a.part == "resa":
    topk = np.load(f"{base}/topk.npy", mmap_mode="r")
    v = engview[tm["nxt"][engview] >= 0]
    inp, pred = tm["inp"].astype(np.int64), tm["pred"].astype(np.int64)
    pent = tm["pent"].astype(np.float32)
    q = np.quantile(pent[v], [1 / 3, 2 / 3])
    terc = np.full(inp.size, -1)
    terc[v] = np.digitize(pent[v], q)
    p = Plan(v)
    for t in range(3):
        m = terc == t
        p.add_marg(f"inp@q{t}", inp, sub=m)
        p.add_marg(f"pred@q{t}", pred, sub=m)
        p.add_cond(f"pred|inp@q{t}", pred, inp, sub=m)
    res = {}
    for l in range(L):
        blk = np.asarray(topk[l][:, :, 0]).astype(np.int64)
        for r in range(blk.shape[1]):
            for nm, f in p.marg.items():
                res.setdefault(nm, np.zeros((L, blk.shape[1], 4)))[l, r] = mi_marg(blk[f["idx"], r], f, E)
            for nm, f in p.cond.items():
                res.setdefault(nm, np.zeros((L, blk.shape[1], 4)))[l, r] = mi_cond(blk[f["idx"], r], f, E)
        log("layer", l)
    out.update({k: v.tolist() for k, v in res.items()})
    out.update(iB_english=iBen, iA=iA, pent_terciles_bits=q.tolist(), n=int(v.size),
               acc_by_tercile=[float((pred == tm["nxt"])[v][terc[v] == t].mean()) for t in range(3)])

elif a.part == "vs8":
    topk = np.load(f"{base}/topk.npy", mmap_mode="r")
    fl = np.where((side == eng) & (tm["nxt"] >= 0))[0]

    def codes(x):
        return np.unique(x, return_inverse=True)[1]

    def vocab_spec(x, S, nx, E):
        k = S.shape[1]
        N = np.bincount(np.repeat(x, k) * E + S.ravel(), minlength=nx * E).reshape(nx, E).astype(np.float64)
        Nx = np.bincount(x, minlength=nx).astype(np.float64)
        Ne = N.sum(0)
        ok = Ne > 0
        spec = ((N / np.where(ok, Ne, 1)[None, :]) * (N / Nx[:, None])).sum(0)
        return float(spec[ok].mean())

    xs = {"inp": tm["inp"][fl], "pred": tm["pred"][fl], "nxt": tm["nxt"][fl]}
    el = {k: np.bincount(codes(x))[codes(x)] >= 5 for k, x in xs.items()}
    res = {k: np.zeros((L, topk.shape[2])) for k in xs}
    for l in range(L):
        blk = np.asarray(topk[l][fl, :, 0]).astype(np.int64)
        for r in range(blk.shape[1]):
            for k, x in xs.items():
                c = codes(x[el[k]])
                res[k][l, r] = vocab_spec(c, blk[el[k], r][:, None], int(c.max()) + 1, E)
    out.update({f"VS1_{k}": v.tolist() for k, v in res.items()})
    out["n"] = int(fl.size)
    out.update(iB_english=iBen, iA=iA)

elif a.part == "geom":
    hm = np.load(f"{base}/hmean.npy", mmap_mode="r")             # [L, NSEQ, d]
    W = np.load(f"{base}/wT.npy")
    seq_side = tm["side"][np.r_[True, tm["seq"][1:] != tm["seq"][:-1]]].astype(np.int64)
    seq_sid = tm["sid"][np.r_[True, tm["seq"][1:] != tm["seq"][:-1]]].astype(np.int64)
    seq_corp = tm["corpus"][np.r_[True, tm["seq"][1:] != tm["seq"][:-1]]].astype(np.int64)
    rows = np.where((seq_corp == 0) & (seq_side != eng))[0]
    lab = {"lang": seq_side[rows], "sid": seq_sid[rows]}
    rng = np.random.default_rng(186)
    res = {f"{sp}_{k}_{m}": np.zeros(L) for sp in ("raw", "ro") for k in lab for m in ("ss", "g2")}

    def stats(X, y):
        X = X - X.mean(0)
        tot = (X ** 2).sum()
        u, inv = np.unique(y, return_inverse=True)
        C = np.zeros((len(u), X.shape[1]))
        np.add.at(C, inv, X)
        nn = np.bincount(inv).astype(np.float64)
        C /= nn[:, None]
        ss = float((nn[:, None] * C ** 2).sum() / tot)
        within = float(np.linalg.norm(X - C[inv], axis=1).mean())
        if len(u) <= 50:
            i, j = np.triu_indices(len(u), 1)
        else:
            i, j = rng.integers(0, len(u), 20000), rng.integers(0, len(u), 20000)
            k = i != j
            i, j = i[k], j[k]
        between = float(np.linalg.norm(C[i] - C[j], axis=1).mean())
        return ss, between / within

    for l in range(L):
        X = np.asarray(hm[l][rows]).astype(np.float64)
        Wc = W[l] - W[l].mean(0, keepdims=True)
        U, S, Vt = np.linalg.svd(Wc, full_matrices=False)
        V = Vt[S > 1e-6 * S[0]].T
        for sp, Xs in (("raw", X), ("ro", X @ V)):
            for k, y in lab.items():
                res[f"{sp}_{k}_ss"][l], res[f"{sp}_{k}_g2"][l] = stats(Xs, y)
        log("layer", l)
    out.update({k: v.tolist() for k, v in res.items()})
    out["n_rows"] = int(rows.size)

elif a.part == "sat":
    ref = f"{SRC}/{a.ref}"
    tr = dict(np.load(f"{ref}/tokmeta.npz"))
    assert np.array_equal(tr["inp"], tm["inp"]), "token streams differ between checkpoints"
    A1, A2 = np.load(f"{base}/topk.npy", mmap_mode="r"), np.load(f"{ref}/topk.npy", mmap_mode="r")
    F1, F2 = np.load(f"{base}/topk_fix.npy", mmap_mode="r"), np.load(f"{ref}/topk_fix.npy", mmap_mode="r")
    res = {k: np.zeros(L) for k in ("T_ov", "T_top1", "NF0_ov", "NF1_ov", "NF0_top1", "NF_cross_ov",
                                     "NF0_loadH", "T_loadH")}

    def ov(S1, S2):
        return float((S1[:, :, None] == S2[:, None, :]).sum((1, 2)).mean() / S1.shape[1])

    def loadH(S):
        c = np.bincount(S.ravel(), minlength=E).astype(np.float64)
        c /= c.sum()
        return float(-(c[c > 0] * np.log2(c[c > 0])).sum())

    sub = np.random.default_rng(186).choice(tm["inp"].size, min(400000, tm["inp"].size), replace=False)
    sub.sort()
    for l in range(L):
        t1, t2 = np.asarray(A1[l][:, 0])[sub], np.asarray(A2[l][:, 0])[sub]
        f1, f2 = np.asarray(F1[l])[sub], np.asarray(F2[l])[sub]
        res["T_ov"][l] = ov(t1, t2)
        res["T_top1"][l] = float((t1[:, 0] == t2[:, 0]).mean())
        res["NF0_ov"][l] = ov(f1[:, 0], f2[:, 0])
        res["NF1_ov"][l] = ov(f1[:, 1], f2[:, 1])
        res["NF0_top1"][l] = float((f1[:, 0, 0] == f2[:, 0, 0]).mean())
        res["NF_cross_ov"][l] = ov(f1[:, 0], f2[:, 1])
        res["NF0_loadH"][l] = loadH(f1[:, 0])
        res["T_loadH"][l] = loadH(t1)
    out.update({k: v.tolist() for k, v in res.items()})
    out.update(ref=a.ref, n_sub=int(sub.size))

jdump(f"{RES}/extra_{a.part}_{a.key}.json", out)
log("saved", f"{RES}/extra_{a.part}_{a.key}.json")
