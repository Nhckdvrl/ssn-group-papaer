"""E185 supplementary estimator (card 补登记 11-09 20:00): cross-fitted conditional predictive information
G(X | inp) in bits/token.  Folds = first / second half of every sequence; p(e|inp), p(e|X) Dirichlet-smoothed (A=8)
on one fold; log p_w(e) ∝ log p(e|inp) + w [log p(e|X) - log p(e)], w chosen on odd-id sequences of the test fold and
evaluated on even ones (and vice versa); both fold directions averaged.  Also G(inp) = gain of p(e|inp) over p(e).

usage: e185_crossfit.py --data {d184,d180} --model M  |  e185_crossfit.py --pc   (synthetic recovery control)"""
import argparse
import json
import os
import sys
import time
from multiprocessing import get_context

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import CACHE, dense, jdump  # noqa: E402

A_SMOOTH = 8.0
WGRID = np.array([0, .25, .5, .75, 1, 1.5])
OUT = os.path.expanduser("~/mechpop_cache/atlas_e185")
RES = os.path.join(os.path.dirname(__file__), "..", "results", "e185")


def cond_table(code, e, mask, ncode, E, p0):
    C = np.bincount(code[mask] * E + e[mask], minlength=ncode * E).reshape(ncode, E).astype(np.float64)
    n = C.sum(1, keepdims=True)
    return np.log((C + A_SMOOTH * p0[None]) / (n + A_SMOOTH))


FREQ_ONLY = os.environ.get("E185_FREQ_ONLY") == "1"
FREQ_MIN = 20   # 补登记 2 (11-09 20:08): evaluation restricted to tokens whose input id has >= 20 training-fold occurrences


def G_one(e, S, X, fold, par, E, chunk=200_000):
    """e, S (dense inp), X (dense factor), fold (0/1), par (sequence parity 0/1) on one token subset.
    returns (G_inp, G_cond, w_mean, G_cond_freq, frac_freq): G_cond_freq is evaluated (and w chosen) only on test
    tokens whose input id occurs >= FREQ_MIN times in the training fold (p(e|inp) well estimated, so a coarse X
    cannot gain merely by acting as a back-off prior for rare ids)."""
    nS, nX = S.max() + 1, X.max() + 1
    gi, gc, ws, gf, ff = [], [], [], [], []
    for tr in (0, 1):
        m_tr, m_te = fold == tr, fold != tr
        p0 = (np.bincount(e[m_tr], minlength=E) + 1.0)
        p0 /= p0.sum()
        lp0 = np.log(p0)
        LS = cond_table(S, e, m_tr, nS, E, p0)
        LX = cond_table(X, e, m_tr, nX, E, p0)
        te = np.where(m_te)[0]
        if FREQ_ONLY:   # speed-up for the large D180 store: only the G_freq subset is scored (G_freq unchanged)
            te = te[np.bincount(S[m_tr], minlength=nS)[S[te]] >= FREQ_MIN]
            LS, LX, lp0 = LS.astype(np.float32), LX.astype(np.float32), lp0.astype(np.float32)
        ll = np.zeros((len(WGRID), te.size), np.float32 if FREQ_ONLY else np.float64)
        for c0 in range(0, te.size, chunk):
            t = te[c0:c0 + chunk]
            a = LS[S[t]]
            b = LX[X[t]] - lp0[None]
            et = e[t]
            for wi, w in enumerate(WGRID):
                z = a + w * b
                mx = z.max(1, keepdims=True)
                lse = mx[:, 0] + np.log(np.exp(z - mx).sum(1))
                ll[wi, c0:c0 + t.size] = z[np.arange(t.size), et] - lse
        base = ll[0]
        gi.append((base - lp0[e[te]]).mean() / np.log(2))
        pp = par[te]
        fr = np.bincount(S[m_tr], minlength=nS)[S[te]] >= FREQ_MIN
        ff.append(fr.mean())
        for sub, acc in ((np.ones(te.size, bool), gc), (fr, gf)):
            g2 = []
            for sel_p in (0, 1):
                a_ = sub & (pp == sel_p)
                ev = sub & (pp != sel_p)
                if a_.sum() == 0 or ev.sum() == 0:
                    continue
                wsel = np.argmax(ll[:, a_].mean(1))
                g2.append((ll[wsel, ev] - base[ev]).mean() / np.log(2))
                if acc is gc:
                    ws.append(WGRID[wsel])
            acc.append(np.mean(g2) if g2 else np.nan)
    return float(np.mean(gi)), float(np.mean(gc)), float(np.mean(ws)), float(np.mean(gf)), float(np.mean(ff))


def halves(seq, pos):
    start = np.r_[True, seq[1:] != seq[:-1]]
    sidx = np.cumsum(start) - 1
    ln = np.bincount(sidx)
    fold = (pos >= ln[sidx] / 2).astype(np.int64)
    par = (sidx % 2).astype(np.int64)
    return fold, par


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", choices=["d184", "d180"])
    ap.add_argument("--model")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--pc", action="store_true")
    args = ap.parse_args()
    t0 = time.time()

    if args.pc:
        # same synthetic generator as e185_pc_cond.py (seed 7), OLMoE D184 arrays
        tm = dict(np.load(f"{CACHE}/e184/olmoe/tokmeta.npz"))
        keep = tm["nxt"] >= 0
        seq = (tm["seq"].astype(np.int64) + 100000 * tm["corpus"])[keep]
        inp = tm["inp"][keep].astype(np.int64)
        pred = tm["pred"][keep].astype(np.int64)
        pos = tm["pos"][keep].astype(np.int64)
        posb = np.where(pos < 4, pos, np.minimum(np.floor(np.log2(np.maximum(pos, 1))).astype(int) + 2, 10))
        corpus = tm["corpus"][keep].astype(np.int64)
        start = np.r_[True, seq[1:] != seq[:-1]]
        prev = np.where(start, -1, np.r_[-1, inp[:-1]])
        fold, par = halves(seq, pos)
        pc = json.load(open(f"{RES}/pc_cond.json"))
        E = 64
        rng = np.random.default_rng(7)
        p0 = rng.dirichlet(np.ones(E))
        S = dense(inp)
        N = S.size
        out = {}
        for name, x in [("seq", seq), ("pred", pred), ("prev", prev), ("pos", posb), ("corpus", corpus)]:
            X = dense(x)
            f = rng.integers(0, E, S.max() + 1)
            g = rng.integers(0, E, X.max() + 1)
            for a, b in [(.4, .2), (.4, .05)]:
                r = rng.random(N)
                e = np.where(r < a, f[S], np.where(r < a + b, g[X], rng.choice(E, N, p=p0)))
                gi, gc, w, gfq, ffq = G_one(e, S, X, fold, par, E)
                true = pc[f"{name}|inp a={a} b={b}"]["true"]
                out[f"{name}|inp a={a} b={b}"] = dict(true=true, G=gc, ratio=gc / true, w=w, G_freq=gfq,
                                                      ratio_freq=gfq / true, frac_freq=ffq,
                                                      plugin_hat_ratio=pc[f"{name}|inp a={a} b={b}"]["ratio"])
                print(name, a, b, f"true {true:.4f} G {gc:.4f} ratio {gc / true:.2f} G_freq {gfq:.4f} "
                      f"ratio {gfq / true:.2f} (plug-in ratio {pc[f'{name}|inp a={a} b={b}']['ratio']:.2f}) w {w}",
                      flush=True)
        # back-off control: X = a coarse deterministic function of inp (no information beyond inp by construction)
        for nc in (17, 200):
            X = dense(rng.integers(0, nc, S.max() + 1)[S])
            f = rng.integers(0, E, S.max() + 1)
            e = np.where(rng.random(N) < .4, f[S], rng.choice(E, N, p=p0))
            # make the coarse class predictive of the token's expert: experts shared within class
            cls_exp = rng.integers(0, E, nc)
            f2 = cls_exp[X]
            e = np.where(rng.random(N) < .4, f2, rng.choice(E, N, p=p0))
            gi, gc, w, gfq, ffq = G_one(e, S, X, fold, par, E)
            out[f"backoff X=f(inp) nclass={nc}"] = dict(true=0.0, G=gc, G_freq=gfq, frac_freq=ffq, w=w)
            print("backoff", nc, f"true 0 G {gc:.4f} G_freq {gfq:.4f} frac {ffq:.2f}", flush=True)
        jdump(f"{RES}/pc_crossfit.json", out)
        sys.exit()

    src = {"d184": "e184", "d180": "e180"}[args.data]
    base = f"{CACHE}/{src}/{args.model}"
    meta = json.load(open(f"{base}/meta.json"))
    tm = dict(np.load(f"{base}/tokmeta.npz"))
    L, E = meta["L"], meta["E"]
    TOPK = f"{base}/topk.npy"
    if args.data == "d184":
        seq_all = tm["seq"].astype(np.int64) + 100000 * tm["corpus"].astype(np.int64)
        keep = np.where(tm["nxt"] >= 0)[0]
        seq = seq_all[keep]
        inp = tm["inp"][keep].astype(np.int64)
        pos = tm["pos"][keep].astype(np.int64)
        start_all = np.r_[True, seq_all[1:] != seq_all[:-1]]
        prev = np.where(start_all, -1, np.r_[-1, tm["inp"][:-1]])[keep]
        posb = np.where(pos < 4, pos, np.minimum(np.floor(np.log2(np.maximum(pos, 1))).astype(int) + 2, 10))
        facs = {"seq": seq, "prev": prev, "pred": tm["pred"][keep], "nxt": tm["nxt"][keep], "pos": posb,
                "corpus": tm["corpus"][keep].astype(np.int64)}
        upos = tm["upos"][keep].astype(np.int64)
        routers = ["T"] + [f"N_A{i}" for i in range(8)] + [f"N_B{i}" for i in range(8)]
    else:
        keep = np.arange(tm["inp"].size)
        seq = tm["lang"].astype(np.int64) * 100000 + tm["sid"]
        inp = tm["inp"].astype(np.int64)
        pos = tm["pos"].astype(np.int64)
        langs = meta["langs"]
        lang_of = np.array([lg.split("_")[0] for lg in langs])
        scr_of = np.array([lg.split("_")[1] for lg in langs])
        side = tm["lang"].astype(np.int64)
        facs = {"sid": tm["sid"].astype(np.int64), "inst": seq, "pred": tm["pred"].astype(np.int64),
                "lang": np.unique(lang_of, return_inverse=True)[1][side],
                "script": np.unique(scr_of, return_inverse=True)[1][side]}
        upos = None
        routers = meta["topk_routers"]
    fold, par = halves(seq, pos)
    S = dense(inp)
    Xd = {k: dense(np.asarray(v).astype(np.int64)) for k, v in facs.items()}
    if upos is not None:
        ud = upos >= 0
        S_ud = dense(inp[ud])
        X_ud = dense(upos[ud])

    def work(l):
        arr = np.load(TOPK, mmap_mode="r")
        blk = np.asarray(arr[l][keep, :, 0]).astype(np.int64)
        out = {}
        for r in range(blk.shape[1]):
            e = blk[:, r]
            for k, X in Xd.items():
                out[(k, r)] = G_one(e, S, X, fold, par, E)
            if upos is not None:
                out[("upos", r)] = G_one(e[ud], S_ud, X_ud, fold[ud], par[ud], E)
        return l, out

    res = {}
    names = list(Xd) + (["upos"] if upos is not None else [])
    with get_context("fork").Pool(args.procs) as pool:
        for l, out in pool.imap_unordered(work, range(L)):
            for (k, r), v in out.items():
                res.setdefault(k, np.full((L, len(routers), 5), np.nan))[l, r] = v
            print(f"[{time.time() - t0:.0f}s] layer {l}", flush=True)
    np.savez_compressed(f"{OUT}/cf_{args.data}_{args.model}.npz", **res)
    json.dump({"routers": routers, "L": L, "factors": names}, open(f"{OUT}/cf_{args.data}_{args.model}.json", "w"))
    print("saved", flush=True)
