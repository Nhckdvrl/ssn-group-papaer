"""E186 estimator positive control on a new E (card: 阳性对照 "合成恢复对照在新 E 上重跑"): same generator as
e185_pc_cond.py / e185_crossfit.py --pc (seed 7; e = a·δ(f(inp)) + b·δ(g(X)) + rest p0), but with the (inp, X) arrays of
an E186 English view and that model's E.  Reports the exact I(e;X|inp), the plug-in Î ratio, and the G_freq ratio,
plus the back-off control (X = coarse function of inp; truth 0).  usage: e186_pc.py KEY  (needs E185_CACHE = views)"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import CACHE, Plan, mi_cond, dense, jdump
from e185_crossfit import G_one, halves
key = sys.argv[1]
tm = dict(np.load(f"{CACHE}/e184/{key}/tokmeta.npz"))
E = json.load(open(f"{CACHE}/e184/{key}/meta.json"))["E"]
keep = tm["nxt"] >= 0
seq = (tm["seq"].astype(np.int64) + 100000 * tm["corpus"])[keep]
inp = tm["inp"][keep].astype(np.int64); pred = tm["pred"][keep].astype(np.int64)
pos = tm["pos"][keep].astype(np.int64)
posb = np.where(pos < 4, pos, np.minimum(np.floor(np.log2(np.maximum(pos, 1))).astype(int) + 2, 10))
corpus = tm["corpus"][keep].astype(np.int64)
start = np.r_[True, seq[1:] != seq[:-1]]
prev = np.where(start, -1, np.r_[-1, inp[:-1]])
fold, par = halves(seq, pos)
rng = np.random.default_rng(7)
p0 = rng.dirichlet(np.ones(E))
S = dense(inp); N = S.size
out = {"key": key, "E": E, "N": int(N)}


def H(p):
    p = p[p > 0]; return float(-(p * np.log2(p)).sum())


for name, x in [("seq", seq), ("pred", pred), ("prev", prev), ("pos", posb), ("corpus", corpus)]:
    X = dense(x)
    f = rng.integers(0, E, S.max() + 1); g = rng.integers(0, E, X.max() + 1)
    for a, b in [(.4, .2), (.4, .05)]:
        SX = S * (X.max() + 1) + X
        u, inv, cnt = np.unique(SX, return_inverse=True, return_counts=True)
        su, xu = u // (X.max() + 1), u % (X.max() + 1)

        def Hmix(fs, gx):
            p = (1 - a - b) * p0.copy(); p[fs] += a; p[gx] += b; return H(p)
        Hsx = np.sum(cnt * np.array([Hmix(fs, gx) for fs, gx in zip(f[su], g[xu])])) / N
        ns = np.bincount(S)
        Ps = np.zeros((S.max() + 1, E))
        np.add.at(Ps, (su, g[xu]), b * cnt / ns[su])
        Ps += (1 - a - b) * p0[None]
        Ps[np.arange(S.max() + 1), f] += a
        Hs = np.sum(ns * np.array([H(p) for p in Ps])) / N
        true = Hs - Hsx
        r = rng.random(N)
        e = np.where(r < a, f[S], np.where(r < a + b, g[X], rng.choice(E, N, p=p0)))
        pl = Plan(np.arange(N)); pl.add_cond("c", x, inp)
        Ih, Ip, sd, He = mi_cond(e, pl.cond["c"], E)
        gi, gc, w, gfq, ffq = G_one(e, S, X, fold, par, E)
        out[f"{name}|inp a={a} b={b}"] = dict(true=true, plugin_hat_ratio=Ih / true, G_freq=gfq, ratio_freq=gfq / true,
                                              frac_freq=ffq)
        print(name, a, b, f"true {true:.4f} plug-in ratio {Ih / true:.2f} G_freq {gfq:.4f} ratio {gfq / true:.2f}", flush=True)
for nc in (17, 200):
    X = dense(rng.integers(0, nc, S.max() + 1)[S])
    cls_exp = rng.integers(0, E, nc)
    e = np.where(rng.random(N) < .4, cls_exp[X], rng.choice(E, N, p=p0))
    gi, gc, w, gfq, ffq = G_one(e, S, X, fold, par, E)
    out[f"backoff nclass={nc}"] = dict(true=0.0, G=gc, G_freq=gfq)
    print("backoff", nc, f"G {gc:.4f} G_freq {gfq:.4f}", flush=True)
jdump(os.path.join(os.path.dirname(__file__), "..", "results", "e186", f"pc_{key}.json"), out)
