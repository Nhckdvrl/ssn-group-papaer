"""Reuse-gate decomposition of a paired loss gap (written before any lpin/lpout data existed).

For each target x_t, class c_t = IN if x_t's type occurs in the visible prefix, else OUT
(identical to tags rep >= 1). For model M (exact, no approximation):
    nll_M = gate_M + within_M,   gate_M = -log P_M(c_t),   within_M = -log P_M(x_t | c_t)
where P_M(IN) = sum of M's next-token probability over the prefix's token types (lpin/lpout).
Δ = nll_A - nll_B = Δ_gate + Δ_within.  Question: where does the architecture gap live?

usage: SHAPE_PACK=... gate.py A B [DOMAINS|all]
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_p0 import boot, fmt, ROOT, PFX

ALL = ["pg19", "ccnews", "wikipedia", "arxiv", "python", "html", "latex"]


def parts(tag, d, cin):
    nll = np.load(f"{ROOT}/scores/{tag}/{d}.npy")
    lpin = np.load(f"{ROOT}/scores/{tag}/{d}_lpin.npy"); lpout = np.load(f"{ROOT}/scores/{tag}/{d}_lpout.npy")
    gate = -np.where(cin, lpin, lpout)
    return nll, gate, nll - gate, np.exp(lpin)


def main(A, B, doms):
    rows = {}
    for d in doms:
        r = np.load(f"{ROOT}/data/tags_{PFX}{d}.npz")["rep"]; cin = r >= 1
        a, b = parts(A, d, cin), parts(B, d, cin)
        rows[d] = dict(r=r, cin=cin, D=a[0] - b[0], G=a[1] - b[1], W=a[2] - b[2], pA=a[3], pB=b[3])
    cat = lambda k: np.concatenate([rows[d][k] for d in doms])
    r, cin, D, G, W, pA, pB = (cat(k) for k in ("r", "cin", "D", "G", "W", "pA", "pB"))
    print(f"== {A} vs {B}  (Δ = nll_{A} - nll_{B}; > 0 means {B} better)  domains={','.join(doms)}")
    print(f"{'stratum':12s} {'Δ total':>28s} {'Δ gate':>28s} {'Δ within':>28s}")
    for name, m in (("all", np.ones_like(cin)), ("OUT(novel)", ~cin), ("IN (rep>=1)", cin), ("rep=1", r == 1),
                    ("rep>=2", r >= 2), ("rep>=4", r >= 4), ("rep>=8", r >= 8), ("rep>=16", r >= 16)):
        print(f"{name:12s} {fmt(boot(D, m))[:28]:>28s} {fmt(boot(G, m))[:28]:>28s} {fmt(boot(W, m))[:28]:>28s}")
    print("== gate calibration: mean P(IN) vs empirical IN-rate")
    print(f"empirical IN rate {cin.mean():.4f} | mean P_{A}(IN) {pA.mean():.4f} | mean P_{B}(IN) {pB.mean():.4f}")
    print(f"  on OUT targets: P_{A}(IN) {pA[~cin].mean():.4f}  P_{B}(IN) {pB[~cin].mean():.4f}")
    print(f"  on IN  targets: P_{A}(IN) {pA[cin].mean():.4f}  P_{B}(IN) {pB[cin].mean():.4f}")
    edges = np.array([0, .2, .4, .6, .8, .9, .95, .99, 1.0001])
    for name, p in ((A, pA), (B, pB)):
        k = np.digitize(p, edges) - 1
        print(f"  reliability {name}: " + " ".join(f"[{edges[i]:.2f},{edges[i+1]:.2f}) pred {p[k == i].mean():.3f} obs {cin[k == i].mean():.3f} n={int((k == i).sum())}" for i in range(len(edges) - 1) if (k == i).any()))
    print("== per domain: Δ total | Δ gate | Δ within")
    for d in doms:
        x = rows[d]; one = np.ones_like(x["cin"])
        print(f"{d:10s} {boot(x['D'], one)[0]:+.4f} | {boot(x['G'], one)[0]:+.4f} | {boot(x['W'], one)[0]:+.4f}"
              f"   novel: {boot(x['D'], ~x['cin'])[0]:+.4f} = {boot(x['G'], ~x['cin'])[0]:+.4f} + {boot(x['W'], ~x['cin'])[0]:+.4f}"
              f"   reuse: {boot(x['D'], x['cin'])[0]:+.4f} = {boot(x['G'], x['cin'])[0]:+.4f} + {boot(x['W'], x['cin'])[0]:+.4f}")


if __name__ == "__main__":
    A, B = sys.argv[1], sys.argv[2]
    arg = sys.argv[3] if len(sys.argv) > 3 else "pg19,wikipedia,python"
    main(A, B, ALL if arg == "all" else arg.split(","))
