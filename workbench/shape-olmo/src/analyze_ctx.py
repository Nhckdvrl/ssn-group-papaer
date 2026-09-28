"""Readout for ctx_ablation (pre-registered in RESEARCH_LOG before data).
far-use(d)   = NLL(drop_d)  - NLL(full)
order-use(d) = NLL(cshuf_d) - NLL(full)
bag-use(d)   = NLL(drop_d)  - NLL(tshuf_d)
Reported per model for all / novel (rep 0) / reused (rep >= 2) targets, with a window bootstrap CI.
Kill-rule ratios: for pair (A worse, B better), extra far-use of B over A on novel targets divided by
the novel-target NLL gap (A - B) at full context; compared across architecture pairs and scale pairs.
usage: analyze_ctx.py
"""
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS = [32, 128, 512, 1024]
rng = np.random.default_rng(0)


def load(tag):
    f = f"{ROOT}/results/ctx/{tag}.npz"
    return dict(np.load(f)) if os.path.exists(f) else None


def boot(x, m):
    s = (x * m).sum(1); n = m.sum(1)
    idx = rng.integers(0, len(s), (1000, len(s)))
    b = s[idx].sum(1) / np.maximum(n[idx].sum(1), 1)
    return s.sum() / max(n.sum(), 1), np.percentile(b, 2.5), np.percentile(b, 97.5)


M = {t: load(t) for t in ["PPT", "PPH", "PPR", "PY14", "PY28", "M2_13"]}
M = {k: v for k, v in M.items() if v is not None}
for t, z in M.items():
    rep = z["rep"]
    print(f"== {t}: full NLL all {z['full'].mean():.3f}")
    for name, m in (("all", np.ones_like(rep, bool)), ("novel", rep == 0), ("reused", rep >= 2)):
        cells = []
        for d in DS:
            f = boot(z[f"drop_{d}"] - z["full"], m)[0]; o = boot(z[f"cshuf_{d}"] - z["full"], m)[0]
            b = boot(z[f"drop_{d}"] - z[f"tshuf_{d}"], m)[0]
            cells.append(f"d{d}: far {f:+.3f} ord {o:+.3f} bag {b:+.3f}")
        print(f"  {name:6s} " + " | ".join(cells))


def ratio(A, B, d):
    """(far-use_B - far-use_A) on novel / (NLL_A - NLL_B) on novel at full context."""
    a, b = M[A], M[B]
    m = a["rep"] == 0
    gap = boot(a["full"] - b["full"], m)
    extra = boot((b[f"drop_{d}"] - b["full"]) - (a[f"drop_{d}"] - a["full"]), m)
    return gap, extra, extra[0] / gap[0]


print("== kill-rule ratios on NOVEL targets: extra far-use of the better model / its full-context gap")
pairs = [("PPT", "PPH", "arch T->H"), ("PPR", "PPH", "arch R->H"), ("PPT", "PPR", "arch T->R"),
         ("PY14", "PY28", "scale Pythia"), ("M2_13", "PPR", "scale Mamba-2")]
for A, B, lab in pairs:
    if A in M and B in M:
        row = []
        for d in DS:
            gap, extra, r = ratio(A, B, d)
            row.append(f"d{d}: extra {extra[0]:+.3f} [{extra[1]:+.3f},{extra[2]:+.3f}] ratio {r:+.2f}")
        print(f"{lab:14s} gap {gap[0]:+.3f}  " + " | ".join(row))
