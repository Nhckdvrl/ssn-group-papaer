"""E185 positive control: recovery of conditional MI I(e; X | inp) with the real D184 (OLMoE) inp / X arrays and a
synthetic expert e ~ a*delta(f(inp)) + b*delta(g(X)) + (1-a-b)*p0 (exact 'true' value with the empirical (inp, X)
joint as population).  Writes results/e185/pc_cond.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import CACHE, Plan, mi_cond, mi_marg, dense, jdump
tm = dict(np.load(f"{CACHE}/e184/olmoe/tokmeta.npz"))
keep = tm["nxt"] >= 0
seq = (tm["seq"].astype(np.int64) + 100000 * tm["corpus"])[keep]
inp = tm["inp"][keep].astype(np.int64); pred = tm["pred"][keep].astype(np.int64)
pos = tm["pos"][keep]; posb = np.where(pos < 4, pos, np.minimum(np.floor(np.log2(np.maximum(pos, 1))).astype(int) + 2, 10))
corpus = tm["corpus"][keep].astype(np.int64)
start = np.r_[True, seq[1:] != seq[:-1]]
prev = np.where(start, -1, np.r_[-1, inp[:-1]])
E = 64
rng = np.random.default_rng(7)
p0 = rng.dirichlet(np.ones(E))
S = dense(inp); N = S.size
out = {}
def H(p):
    p = p[p > 0]; return float(-(p * np.log2(p)).sum())
for name, x in [("seq", seq), ("pred", pred), ("prev", prev), ("pos", posb), ("corpus", corpus)]:
    X = dense(x)
    f = rng.integers(0, E, S.max() + 1); g = rng.integers(0, E, X.max() + 1)
    for a, b in [(.4, .2), (.4, .05)]:
        # exact I(e;X|S) with empirical joint as population
        # p(e|s,x) = a d_f(s) + b d_g(x) + (1-a-b) p0 ; p(e|s) = a d_f(s) + b sum_x p(x|s) d_g(x) + (1-a-b) p0
        SX = S * (X.max() + 1) + X
        u, inv, cnt = np.unique(SX, return_inverse=True, return_counts=True)
        su, xu = u // (X.max() + 1), u % (X.max() + 1)
        Hsx = 0.0
        # H(e|s,x) depends only on whether f(s)==g(x)
        same = f[su] == g[xu]
        def Hmix(fs, gx):
            p = (1 - a - b) * p0.copy(); p[fs] += a; p[gx] += b; return H(p)
        Hsx = np.sum(cnt * np.array([Hmix(fs, gx) for fs, gx in zip(f[su], g[xu])])) / N
        # H(e|s)
        ns = np.bincount(S)
        Ps = np.zeros((S.max() + 1, E))
        np.add.at(Ps, (su, g[xu]), b * cnt / ns[su])
        Ps += (1 - a - b) * p0[None]
        Ps[np.arange(S.max() + 1), f] += a
        Hs = np.sum(ns * np.array([H(p) for p in Ps])) / N
        true = Hs - Hsx
        # sample e
        r = rng.random(N)
        e = np.where(r < a, f[S], np.where(r < a + b, g[X], rng.choice(E, N, p=p0)))
        pl = Plan(np.arange(N)); pl.add_cond("c", x, inp)
        Ih, Ip, sd, He = mi_cond(e, pl.cond["c"], E)
        out[f"{name}|inp a={a} b={b}"] = dict(true=true, hat=Ih, plugin=Ip, ratio=Ih / true if true > 0 else None, H_e=He)
        print(name, a, b, f"true {true:.4f} hat {Ih:.4f} plugin {Ip:.4f} ratio {Ih/true:.2f}", flush=True)
jdump(os.path.join(os.path.dirname(__file__), "..", "results", "e185", "pc_cond.json"), out)
