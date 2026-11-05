#!/usr/bin/env python3
"""E174 granularity 1: the POS-level route fingerprint against a geometry-preserving random-router null (CPU).

The A2 within-UPOS-cell permutation leaves P(expert | UPOS) unchanged, so at this level that null equals
the real readout by construction. Substitute null: replace run B by its own N1 random router (rotation
inside the router readout subspace, singular values kept, bias re-fitted to the real loads) -- same
geometry, same POS sensitivity that the geometry gives, no learned partition.

Readout (as analyze_functional.py "route"): per expert, P(expert selected | UPOS) over UD words
(hidden cache rows = anchor + cal words); categories with >= 300 words in both halves; halves = documents
by hash parity; vectors centred across experts; Hungarian on the cal half, mean matched corr on held half.

Usage: e174_coarse_null.py OUT_JSON A@TOK:B@TOK [...]
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).parent))
import moe_measure as mm  # noqa: E402

torch.set_num_threads(8)
WB = Path(__file__).resolve().parents[1]
HID = Path.home() / "mechpop_cache/e167_analysis/hidden"
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
LAYERS = list(range(6, 12))
N_DRAW, K, N_FIT, MIN_TOK = 8, 8, 20000, 300
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())


def rowcorr(X, Y):
    X = X - X.mean(1, keepdims=True); Y = Y - Y.mean(1, keepdims=True)
    return (X * Y).sum(1) / np.sqrt((X * X).sum(1) * (Y * Y).sum(1) + 1e-30)


_cache = {}


def run_data(spec):
    """Real and N1 top-k sets over all hidden rows, deep layers."""
    if spec in _cache:
        return _cache[spec]
    run, t = spec.split("@")
    z = np.load(HID / f"{run}__ckpt_{t}.npz")
    widx = z["word_idx"]; na = int(z["n_anchor"])
    res = {"widx": widx, "real": {}, "null": {}}
    Sref = np.load(CAP / f"{run}__ckpt_{t}.npz")
    gen_fit = np.random.default_rng(1742)
    for l in LAYERS:
        H = torch.from_numpy(z[f"H{l}"].astype(np.float32))
        W = torch.from_numpy(z[f"W{l}"]); b = torch.from_numpy(z[f"b{l}"])
        S = (H @ W.T + b).topk(K, -1).indices
        res["real"][l] = S.numpy()
        if l == LAYERS[0] or l == 11:
            # hidden rows = all valid anchors (E169) + cal words; align the pre-registered anchors by word id
            pos = {int(x): i for i, x in enumerate(widx)}
            rows = np.array([pos[int(x)] for x in np.load(CAP / "pairs.npz")["anchor_word"]])
            ref = Sref[f"S{l}"]
            agree = np.mean([len(set(x) & set(y)) / K for x, y in zip(S[rows].numpy(), ref)])
            res.setdefault("check", {})[l] = float(agree)
        Hc = H[na:]
        fit = torch.from_numpy(gen_fit.choice(len(Hc), min(N_FIT, len(Hc)), replace=False))
        Hf = Hc[fit].double()
        Wd, bd = W.double(), b.double()
        target = mm.loads(mm.topk(Hc.double() @ Wd.T + bd, K), W.shape[0])
        st = mm.null_stats(Wd, Hc.double())
        gen = torch.Generator().manual_seed(174 + l)
        draws = []
        for _ in range(N_DRAW):
            Q = mm.haar(st["V"].shape[1], gen).to(Wd.dtype)
            Wn = mm.null_router(Wd, Hc.double(), "N1", Q, st)
            bn = mm.fit_bias(Hf, Wn, K, target)
            draws.append((H.double() @ Wn.T + bn).topk(K, -1).indices.numpy())
        res["null"][l] = draws
        print(spec, "layer", l, "done", flush=True)
    _cache[spec] = res
    return res


def fingerprint(S, cat, split, ncat):
    """E x 2 x ncat: P(expert selected | cat) per split."""
    E = 64
    out = np.zeros((2, ncat, E))
    for s in (0, 1):
        m = split == s
        oh = np.zeros((m.sum(), E)); np.put_along_axis(oh, S[m].astype(np.int64), 1, 1)
        out[s] = np.stack([oh[cat[m] == c].mean(0) if (cat[m] == c).any() else np.zeros(E) for c in range(ncat)])
    return np.transpose(out, (2, 0, 1))  # E,2,ncat


def matched(FA, FB):
    ac, ah = FA[:, 0] - FA[:, 0].mean(0), FA[:, 1] - FA[:, 1].mean(0)
    bc, bh = FB[:, 0] - FB[:, 0].mean(0), FB[:, 1] - FB[:, 1].mean(0)
    n = ac.shape[0]
    C = np.array([rowcorr(np.repeat(ac[i:i + 1], n, 0), bc) for i in range(n)])
    ri, ci = linear_sum_assignment(-C)
    return float(rowcorr(ah[ri], bh[ci]).mean())


out = {"layers": LAYERS, "n_draw": N_DRAW, "results": []}
for spec in sys.argv[2:]:
    a, b = spec.split(":")
    RA, RB = run_data(a), run_data(b)
    assert (RA["widx"] == RB["widx"]).all()
    widx = RA["widx"]
    up = np.array([ann[int(w)]["upos"] for w in widx])
    doc = np.array([zlib.crc32(str(ann[int(w)]["doc_id"]).encode()) % 2 for w in widx])
    cats, cat = np.unique(up, return_inverse=True)
    keep_c = [c for c in range(len(cats)) if min(((cat == c) & (doc == s)).sum() for s in (0, 1)) >= MIN_TOK]
    remap = {c: i for i, c in enumerate(keep_c)}
    m = np.isin(cat, keep_c)
    cat2 = np.array([remap[c] for c in cat[m]]); split = doc[m]
    rec = {"A": a, "B": b, "cats": [str(cats[c]) for c in keep_c], "check_A": RA.get("check"), "check_B": RB.get("check"), "layers": []}
    for l in LAYERS:
        fa = fingerprint(RA["real"][l][m], cat2, split, len(keep_c))
        fb = fingerprint(RB["real"][l][m], cat2, split, len(keep_c))
        real = matched(fa, fb)
        nB = [matched(fa, fingerprint(d[m], cat2, split, len(keep_c))) for d in RB["null"][l]]
        nAB = [matched(fingerprint(da[m], cat2, split, len(keep_c)), fingerprint(db[m], cat2, split, len(keep_c)))
               for da, db in zip(RA["null"][l], RB["null"][l])]
        rec["layers"].append({"layer": l, "real": real, "nullB_mean": float(np.mean(nB)), "nullB_lo": float(np.min(nB)),
                              "nullB_hi": float(np.max(nB)), "nullAB_mean": float(np.mean(nAB)),
                              "nullAB_lo": float(np.min(nAB)), "nullAB_hi": float(np.max(nAB))})
        print(a, b, l, f"real {real:.3f} realA-vs-N1(B) {np.mean(nB):.3f} N1-vs-N1 {np.mean(nAB):.3f}", flush=True)
    out["results"].append(rec)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
print("saved", flush=True)
