"""P0 readout: T vs H token gaps, Delta = nll_T - nll_H (> 0 = hybrid better).
usage: analyze_p0.py TAG_T TAG_H   -> prints tables, writes results/p0_<TAG_T>_<TAG_H>.json
CIs: 1000-sample bootstrap over 8192-token windows (the cluster unit).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tag import FAMILIES, CONTENT, FUNCTION, PROSE

PFX = os.environ.get("SHAPE_PACK", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMS = ["pg19", "ccnews", "wikipedia", "arxiv", "python", "html", "latex"]
PAPER_OPEN_CLOSE = dict(pg19=0.068, ccnews=0.077, wikipedia=0.049, arxiv=0.028, python=0.017,
                        html=0.010, latex=0.064)
rng = np.random.default_rng(0)


def boot(delta, mask, B=1000):
    """window-cluster bootstrap of the masked mean. delta, mask: (S, L)."""
    s = (delta * mask).sum(1); n = mask.sum(1)
    if n.sum() == 0:
        return float("nan"), float("nan"), float("nan"), 0
    idx = rng.integers(0, len(s), (B, len(s)))
    bs = s[idx].sum(1) / np.maximum(n[idx].sum(1), 1)
    return float(s.sum() / n.sum()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), int(n.sum())


def fmt(r):
    return f"{r[0]:+.4f} [{r[1]:+.4f},{r[2]:+.4f}] n={r[3]}"


def main(tt, th):
    out = {}
    D, T = {}, {}
    for d in DOMS:
        D[d] = np.load(f"{ROOT}/scores/{tt}/{d}.npy") - np.load(f"{ROOT}/scores/{th}/{d}.npy")
        T[d] = np.load(f"{ROOT}/data/tags_{PFX}{d}.npz")
    print("== mean Delta per domain (all tokens)")
    for d in DOMS:
        out[f"all/{d}"] = r = boot(D[d], np.ones_like(D[d], bool))
        print(f"{d:10s} {fmt(r)}")
    # prose families, pooled over prose domains (multi-tag attribution)
    pd_ = [d for d in DOMS if d in PROSE]
    cat = lambda f: np.concatenate(f, 0)
    Dp = cat([D[d] for d in pd_])
    p1 = cat([T[d]["pos1"] for d in pd_]); p2 = cat([T[d]["pos2"] for d in pd_])
    print("== prose coarse families (raw Delta, pooled prose)")
    fam = {}
    for k, f in enumerate(FAMILIES):
        fam[f] = boot(Dp, (p1 == k) | (p2 == k))
    for f, r in sorted(fam.items(), key=lambda x: -np.nan_to_num(x[1][0], nan=-9)):
        print(f"{f:14s} {fmt(r)}"); out[f"fam/{f}"] = r
    idx = lambda S: [FAMILIES.index(f) for f in S]
    member = lambda S: np.isin(p1, idx(S)) | np.isin(p2, idx(S))
    content, function = member(CONTENT), member(FUNCTION)
    other = ((p1 >= 0) | (p2 >= 0)) & ~content & ~function
    for name, m, paper in (("content", content, 0.0384), ("function", function, 0.0238), ("other", other, None)):
        out[f"agg/{name}"] = r = boot(Dp, m)
        print(f"AGG {name:9s} {fmt(r)}  paper {paper}")
    print("== open vs close brackets per domain")
    for d in DOMS:
        o = boot(D[d], T[d]["open"]); c = boot(D[d], T[d]["close"])
        # gap CI by bootstrapping the difference jointly
        so, no = (D[d] * T[d]["open"]).sum(1), T[d]["open"].sum(1)
        sc, nc = (D[d] * T[d]["close"]).sum(1), T[d]["close"].sum(1)
        ix = rng.integers(0, len(so), (1000, len(so)))
        g = so[ix].sum(1) / no[ix].sum(1) - sc[ix].sum(1) / nc[ix].sum(1)
        gap = (o[0] - c[0], float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5)))
        out[f"bracket/{d}"] = dict(open=o, close=c, gap=gap)
        print(f"{d:10s} open {o[0]:+.4f} (n={o[3]}) close {c[0]:+.4f} (n={c[3]}) gap {gap[0]:+.4f} "
              f"[{gap[1]:+.4f},{gap[2]:+.4f}]  paper gap {PAPER_OPEN_CLOSE[d]}")
    for d in ("html", "latex"):
        o = boot(D[d], T[d]["htag"] == 1); c = boot(D[d], T[d]["htag"] == 2)
        out[f"htag/{d}"] = dict(open=o, close=c)
        print(f"{d} open-tag/begin {fmt(o)}  close-tag/end {fmt(c)}")
    print("== repeated n-gram events (rep >= n), pooled all domains")
    Da = cat([D[d] for d in DOMS]); ra = cat([T[d]["rep"] for d in DOMS])
    for n in (1, 2, 3, 4, 5, 6, 8, 12, 16):
        out[f"rep/{n}"] = r = boot(Da, ra >= n)
        print(f"n>={n:2d} {fmt(r)}")
    out["rep/none"] = r = boot(Da, ra == 0)
    print(f"no repeat (rep=0) {fmt(r)}")
    print("== Delta by target position (pooled all domains); T SWA window = 4096")
    NT = cat([np.load(f"{ROOT}/scores/{tt}/{d}.npy") for d in DOMS])
    pos = np.arange(Da.shape[1])[None].repeat(Da.shape[0], 0)
    for a in range(0, Da.shape[1], 1024):
        m = (pos >= a) & (pos < a + 1024)
        r = boot(Da, m)
        out[f"pos/{a}"] = dict(delta=r, nll_T=float(NT[m].mean()))
        print(f"pos [{a:4d},{a + 1024:4d}) nll_T {NT[m].mean():.3f}  Delta {fmt(r)}")
    for lo, hi in ((1024, 4096), (4096, 8191)):   # same windows, same docs: paired contrast
        m1 = (pos >= lo) & (pos < hi)
        print(f"  [{lo},{hi}) Delta {fmt(boot(Da, m1))}")
    json.dump(out, open(f"{ROOT}/results/p0_{tt}_{th}.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
