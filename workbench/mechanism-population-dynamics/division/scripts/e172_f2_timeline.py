#!/usr/bin/env python3
"""E172 readout 3 (F2): E170's cell-mean decomposition at every checkpoint.
Same cells and cell-mean definition as e170_decompose.py (MIN_CELL=3, within-type-centred D = C - E_N1[C],
cell = (word type, X_a, X_b)); functions copied verbatim. For each variable X and checkpoint t:
cell_corr = corr(Dcell_A, Dcell_B), share = cov(Dcell_A, Dcell_B)/cov(D_A, D_B), resid_corr, total T_D,
averaged over the init-only pairs (all available), the order-only pairs, the rerun pair(s), and the untrained pair.
t80: first checkpoint from which the curve stays >= 80% of its value at the reference checkpoint (3.2B, all
9 runs present), linearly interpolated on log10(tokens) between that checkpoint and the previous one.

Usage: e172_f2_timeline.py   -> results/e172/f2_timeline.json
"""
import itertools
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
OUT = WB / "results/e172"
MIN_CELL = 3
TOKS = [25000000, 50000000, 100000000, 200000000, 400000000, 800000000, 1600000000, 3200000000, 3999793152]
REF = 3200000000
VARS_USED = ["upos", "feats", "sentpos", "prev_upos", "next_upos", "deprel", "head_upos", "genre"]

P = np.load(CAP / "pairs.npz")
pi, pj, ptype = P["i"], P["j"], P["type"]
aw = P["anchor_word"]
nT = int(ptype.max()) + 1
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
A = [ann[int(w)] for w in aw]


def posclass(a):
    return "init" if a["sent_init"] else ("final" if a["sent_final"] else "mid")


VARS = {"upos": [a["upos"] for a in A], "deprel": [a["deprel"] for a in A], "head_upos": [a["head_upos"] for a in A],
        "prev_upos": [a["prev_upos"] for a in A], "next_upos": [a["next_upos"] for a in A],
        "sentpos": [posclass(a) for a in A], "feats": [a["feats"] for a in A], "genre": [a["genre"] for a in A]}
ENC = {k: np.unique(np.array(v), return_inverse=True)[1] for k, v in VARS.items()}


def cw(x):
    s = np.bincount(ptype, x, nT)
    c = np.bincount(ptype, None, nT)
    return x - (s / np.maximum(c, 1))[ptype]


def cells_for(lab):
    la, lb = lab[pi], lab[pj]
    lo, hi = np.minimum(la, lb), np.maximum(la, lb)
    key = (ptype.astype(np.int64) * (lab.max() + 1) + lo) * (lab.max() + 1) + hi
    _, cid, cnt = np.unique(key, return_inverse=True, return_counts=True)
    return cid, cnt[cid]


def cell_mean(x, cid, cnt):
    s = np.bincount(cid, x)
    n = np.bincount(cid)
    m = (s / np.maximum(n, 1))[cid]
    m[cnt < MIN_CELL] = 0.0
    return m


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-30))


def cov(a, b):
    return float(((a - a.mean()) * (b - b.mean())).mean())


def have(r, t):
    return (CAP / f"{r}__ckpt_{t}.npz").exists()


CELLS = {k: cells_for(lab) for k, lab in ENC.items()}
expected = ["I0D0", "I1D0", "I2D0", "I3D0", "I4D0", "I5D0", "I0D1", "I1D1", "I4D0R", "I0D0R"]
missing = {t: [r for r in expected if not have(r, t)] for t in TOKS}


def decomp(xa, xb):
    out = {}
    for k, (cid, cnt) in CELLS.items():
        ma, mb = cell_mean(xa, cid, cnt), cell_mean(xb, cid, cnt)
        out[k] = (corr(ma, mb), cov(ma, mb) / cov(xa, xb), corr(xa - ma, xb - mb))
    out["_T"] = corr(xa, xb)
    return out


def load(run, t):
    Z = np.load(CAP / f"{run}__ckpt_{t}.npz")
    return [cw(Z[f"C{l}"].astype(np.float64) - Z[f"B{l}"].astype(np.float64)) for l in range(12)]


res = {"tokens": TOKS, "ref": REF, "missing": {str(t): m for t, m in missing.items()}, "vars": VARS_USED, "curves": {}}
# untrained floor
F = {r: load(r, 0) for r in ("I0D0", "I1D0")}
fl = [decomp(F["I0D0"][l], F["I1D0"][l]) for l in range(12)]
res["floor"] = {k: [fl[l][k][0] for l in range(12)] for k in VARS_USED}
res["floor_T"] = [fl[l]["_T"] for l in range(12)]
for t in TOKS:
    inits = [f"I{i}D0" for i in range(6) if have(f"I{i}D0", t)]
    groups = {"init": list(itertools.combinations(inits, 2)),
              "order": [(f"I{i}D0", f"I{i}D1") for i in (0, 1) if have(f"I{i}D1", t)],
              "rerun": [p for p in [("I4D0", "I4D0R"), ("I0D0", "I0D0R")] if have(p[0], t) and have(p[1], t)]}
    runs = sorted({r for ps in groups.values() for p in ps for r in p})
    M = {r: load(r, t) for r in runs}
    rec = {"n_pairs": {g: len(v) for g, v in groups.items()}, "pairs": groups}
    for g, ps in groups.items():
        if not ps:
            continue
        acc = {k: np.zeros((len(ps), 12, 3)) for k in VARS_USED}
        T = np.zeros((len(ps), 12))
        for pidx, (a, b) in enumerate(ps):
            for l in range(12):
                d = decomp(M[a][l], M[b][l])
                T[pidx, l] = d["_T"]
                for k in VARS_USED:
                    acc[k][pidx, l] = d[k]
        rec[g] = {"T_D": T.mean(0).tolist(),
                  **{k: {"cell": acc[k][:, :, 0].mean(0).tolist(), "share": acc[k][:, :, 1].mean(0).tolist(),
                         "resid": acc[k][:, :, 2].mean(0).tolist(),
                         "cell_deep_per_pair": acc[k][:, 6:, 0].mean(1).tolist()} for k in VARS_USED}}
    res["curves"][str(t)] = rec
    deep = lambda g, k: np.mean(rec[g][k]["cell"][6:]) if g in rec else float("nan")
    print(f"{t:>11d} n={rec['n_pairs']} | deep cell init/order: " + " ".join(f"{k} {deep('init', k):.3f}/{deep('order', k):.3f}" for k in VARS_USED), flush=True)


def t80(ts, ys, ref_val):
    """first index from which y stays >= .8*ref; interpolate on log10 t with the previous point."""
    thr = 0.8 * ref_val
    ok = [y >= thr for y in ys]
    for i in range(len(ys)):
        if all(ok[i:]):
            if i == 0:
                return float(ts[0]), True
            x0, x1 = np.log10(ts[i - 1]), np.log10(ts[i])
            y0, y1 = ys[i - 1], ys[i]
            f = (thr - y0) / (y1 - y0) if y1 != y0 else 1.0
            return float(10 ** (x0 + f * (x1 - x0))), False
    return None, False


# curves (deep mean and L11), ratio init/order, onset times; series up to REF (all 9 runs) — endpoint listed separately
series_t = [t for t in TOKS if t <= REF]
summ = {}
for k in VARS_USED + ["T_D"]:
    s = {}
    for lname, sel in (("deep", slice(6, 12)), ("L11", slice(11, 12))):
        def get(g, t):
            r = res["curves"][str(t)].get(g)
            if r is None:
                return float("nan")
            v = r["T_D"] if k == "T_D" else r[k]["cell"]
            return float(np.mean(v[sel]))
        ci = [get("init", t) for t in series_t]
        co = [get("order", t) for t in series_t]
        cr = [get("rerun", t) for t in series_t]
        ratio = [a / b for a, b in zip(ci, co)]
        end = {"init": get("init", TOKS[-1]), "order": get("order", TOKS[-1])}
        ta, ea = t80(series_t, ci, ci[-1])
        tr_, er = t80(series_t, ratio, ratio[-1])
        s[lname] = {"cell_init": ci, "cell_order": co, "cell_rerun": cr, "ratio_init_order": ratio, "endpoint": end,
                    "t80_ratio": tr_, "t80_ratio_at_first": er, "t80_init": ta, "t80_init_at_first": ea,
                    "floor": float(np.mean((res["floor_T"] if k == "T_D" else res["floor"][k])[sel]))}
    summ[k] = s
res["summary"] = summ
(OUT / "f2_timeline.json").write_text(json.dumps(res))
print("\nmissing caches:", {t: m for t, m in missing.items() if m})
for lname in ("deep", "L11"):
    print(f"\n== {lname}: t80 (ratio curve) | t80 (init cell curve) | init cell 25M→3.2B | ratio 25M→3.2B")
    for k in sorted(summ, key=lambda k: (summ[k][lname]["t80_ratio"] or 1e20)):
        s = summ[k][lname]
        print(f"{k:10s} {s['t80_ratio']/1e6 if s['t80_ratio'] else float('nan'):8.0f}M{'*' if s['t80_ratio_at_first'] else ' '} | "
              f"{s['t80_init']/1e6 if s['t80_init'] else float('nan'):8.0f}M{'*' if s['t80_init_at_first'] else ' '} | "
              + " ".join(f"{x:.2f}" for x in s["cell_init"]) + " | " + " ".join(f"{x:.2f}" for x in s["ratio_init_order"]))
print("saved", OUT / "f2_timeline.json")
