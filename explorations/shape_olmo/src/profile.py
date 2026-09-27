"""Feature profiles of a paired loss difference d(x) = nll_A(x) - nll_B(x) (> 0: B better), and
comparisons between profiles. Fixed feature set, written before the stage-1 / placebo data existed.

usage:
  profile.py pair A B [DOMAINS]                     profile of nll_A - nll_B
  profile.py change A1 B1 A2 B2 [DOMAINS]           D = (A2-B2) - (A1-B1), e.g. final gap minus stage-1 gap
  profile.py placebo  T H  Te Tl  [He Hl] [DOMAINS] d_HT = T-H vs d_TT = Te-Tl (and d_HH = He-Hl):
                                                    profiles, and residual r of d_HT ~ alpha*d_TT
DOMAINS default: pg19,wikipedia,python (diagnostic three); 'all' = seven domains.
Tag names refer to scores/<TAG>/<domain>.npy.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tag import FAMILIES, CONTENT, FUNCTION, PROSE
from analyze_p0 import boot, ROOT

ALL = ["pg19", "ccnews", "wikipedia", "arxiv", "python", "html", "latex"]


def load(tag, d):
    return np.load(f"{ROOT}/scores/{tag}/{d}.npy")


def masks(d):
    t = np.load(f"{ROOT}/data/tags_{d}.npz"); r = t["rep"]; p1 = t["pos1"]
    fid = lambda S: [FAMILIES.index(f) for f in S]
    con, fun = np.isin(p1, fid(CONTENT)), np.isin(p1, fid(FUNCTION))
    m = {"all": np.ones_like(r, bool), "novel(rep0)": r == 0, "rep1": r == 1, "rep>=2": r >= 2,
         "rep>=4": r >= 4, "rep>=8": r >= 8, "rep>=16": r >= 16,
         "open": t["open"], "close": t["close"]}
    if d in PROSE:
        m.update({"content|rep0": con & (r == 0), "function|rep0": fun & (r == 0),
                  "content|rep>=1": con & (r >= 1), "function|rep>=1": fun & (r >= 1)})
    return m


def profile(dmats, doms):
    """dmats: {domain: (S, L-1) array}. Returns {feature: (mean, lo, hi, n)} pooled over doms,
    plus per-domain 'all' and 'open-close'."""
    out = {}
    M = {d: masks(d) for d in doms}
    feats = sorted({f for d in doms for f in M[d]}, key=lambda f: list(M[[d for d in doms if f in M[d]][0]]).index(f))
    for f in feats:
        ds = [d for d in doms if f in M[d]]
        out[f] = boot(np.concatenate([dmats[d] for d in ds]), np.concatenate([M[d][f] for d in ds]))
    oc = []
    for d in doms:
        out[f"{d}:all"] = boot(dmats[d], M[d]["all"])
        o, c = boot(dmats[d], M[d]["open"])[0], boot(dmats[d], M[d]["close"])[0]
        out[f"{d}:open-close"] = (o - c, np.nan, np.nan, 0)
    return out


def show(title, profs):
    """profs: list of (name, profile). Prints features as rows, profiles as columns."""
    print(f"== {title}")
    names = [n for n, _ in profs]
    print(f"{'feature':18s} " + " ".join(f"{n:>22s}" for n in names))
    for f in profs[0][1]:
        cells = []
        for _, p in profs:
            m, lo, hi, n = p.get(f, (np.nan,) * 4)
            cells.append(f"{m:+.4f}" + (f" [{lo:+.3f},{hi:+.3f}]" if not np.isnan(lo) else " " * 16))
        print(f"{f:18s} " + " ".join(f"{c:>22s}" for c in cells))


def main():
    mode, args = sys.argv[1], sys.argv[2:]
    doms = ALL if args and args[-1] == "all" else (args[-1].split(",") if args and "," in args[-1] else ["pg19", "wikipedia", "python"])
    tags = [a for a in args if a != "all" and "," not in a]
    diff = lambda a, b: {d: load(a, d) - load(b, d) for d in doms}
    if mode == "pair":
        show(f"{tags[0]} - {tags[1]}", [(f"{tags[0]}-{tags[1]}", profile(diff(*tags[:2]), doms))])
    elif mode == "change":
        a1, b1, a2, b2 = tags[:4]
        g1, g2 = diff(a1, b1), diff(a2, b2)
        show("change-point", [(f"{a1}-{b1}", profile(g1, doms)), (f"{a2}-{b2}", profile(g2, doms)),
                              ("D = second - first", profile({d: g2[d] - g1[d] for d in doms}, doms))])
    elif mode == "placebo":
        T, H, Te, Tl = tags[:4]
        dHT, dTT = diff(T, H), diff(Te, Tl)
        profs = [("d_HT = T-H", profile(dHT, doms)), (f"d_TT = {Te}-{Tl}", profile(dTT, doms))]
        if len(tags) >= 6:
            profs.append((f"d_HH = {tags[4]}-{tags[5]}", profile(diff(tags[4], tags[5]), doms)))
        x = np.concatenate([dTT[d].ravel() for d in doms]); y = np.concatenate([dHT[d].ravel() for d in doms])
        alpha = float((x * y).sum() / (x * x).sum())
        rho = float(np.corrcoef(x, y)[0, 1])
        print(f"token-level: corr(d_HT, d_TT) = {rho:+.3f}; OLS alpha (no intercept) = {alpha:+.3f}")
        profs.append(("residual r", profile({d: dHT[d] - alpha * dTT[d] for d in doms}, doms)))
        show("placebo: architecture gap vs same-architecture improvement", profs)


if __name__ == "__main__":
    main()
