#!/usr/bin/env python3
"""E175 POST-HOC estimator: cross-fitted predictive information (bits) of the top-1 expert.

Why (written after seeing the pre-registered plug-in readouts): the plug-in excess MI saturates for sparse x
(the in_tok^next_tok upper bound came out BELOW dI(in_tok), an internal-consistency failure), and the shuffle
floor (~1.9 bits for in_tok) is larger than most of the signal.  Cross-fitting avoids both: estimate p(e|x) on
one half of the anchors, score log-loss on the other half, swap, average.  Rare / unseen x fall back to the
marginal (or to the coarser variable), so sparsity can only lower an estimate, never inflate it.

  p(e)           = (N_e + 1) / (N + E)                                    (train half)
  p(e|x)         = (N_{x,e} + A p(e)) / (N_x + A)                          A = 8 (fixed, single choice)
  p(e|in,next)   = (N_{in,next,e} + A p(e|in)) / (N_{in,next} + A)        backoff to input   (and symmetric)
  G(x)           = CE[p(e)] - CE[p(e|x)]
  G(next|in)     = CE[p(e|in)] - CE[p(e|in,next) backoff in]               (incremental info of next given input)
  G(in|next)     = CE[p(e|next)] - CE[p(e|next,in) backoff next]
  G(joint)       = max of the two backoff orders vs CE[p(e)]
  NOTE: the stored G(in|next) (backoff to next) is a weak bound because joint cells are sparse; the figure /
  summary use G(joint) - G(next) for "input given next" and G(joint) - G(in) for "next given input".
  G(next_upos|in_tok), G(next_form|in_tok): backoff to the input-token table.
Controls: x shuffled once (should be <= 0); step-0 (untrained) checkpoints; frequency subset (in_tok and
next_tok both >= 20 in the anchor set).
Usage: e175_crossfit.py RUN [RUN ...]  -> results/e175/crossfit_<RUN>.json
"""
import json
import sys
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
OUT = WB / "results/e175"
E, NL, A, SEED = 64, 12, 8.0, 175


def codes(v):
    return np.unique(np.asarray(v), return_inverse=True)[1].astype(np.int64)


def cond_table(e, x, nx, prior):
    """smoothed p(e|x) table (nx, E) with per-row prior (nx, E) or (E,)."""
    N = np.bincount(x * E + e, minlength=nx * E).reshape(nx, E).astype(np.float64)
    return (N + A * prior) / (N.sum(1, keepdims=True) + A)


def ce(p):
    return float(-np.log2(p).mean())


def gains(e, X, tr, te):
    """X: dict of code arrays incl. in_tok, next_tok, joint (in,next); returns gains on te with model fit on tr."""
    etr, ete = e[tr], e[te]
    pm = (np.bincount(etr, minlength=E) + 1.0) / (len(etr) + E)
    out, base = {}, ce(pm[ete])
    P = {}
    for name in ["in_tok", "next_tok", "in_form", "next_form", "in_upos", "next_upos", "shuf_in_tok", "shuf_next_tok"]:
        x = X[name]; nx = int(x.max()) + 1
        T = cond_table(etr, x[tr], nx, pm)
        P[name] = T
        out[f"G_{name}"] = base - ce(T[x[te], ete])
    # joint with backoff
    j = X["joint"]; nj = int(j.max()) + 1
    jin = np.zeros(nj, np.int64); jin[j] = X["in_tok"]
    jnx = np.zeros(nj, np.int64); jnx[j] = X["next_tok"]
    Tj_in = cond_table(etr, j[tr], nj, P["in_tok"][jin])
    Tj_nx = cond_table(etr, j[tr], nj, P["next_tok"][jnx])
    ce_in, ce_nx = ce(P["in_tok"][X["in_tok"][te], ete]), ce(P["next_tok"][X["next_tok"][te], ete])
    ce_j_in, ce_j_nx = ce(Tj_in[j[te], ete]), ce(Tj_nx[j[te], ete])
    out["G_next|in"] = ce_in - ce_j_in
    out["G_in|next"] = ce_nx - ce_j_nx
    out["G_joint"] = base - min(ce_j_in, ce_j_nx)
    for y, z in [("next_upos", "in_upos"), ("in_upos", "next_upos")]:
        jj = codes(X[y] * 1000 + X[z]); n2 = int(jj.max()) + 1
        jz = np.zeros(n2, np.int64); jz[jj] = X[z]
        T2 = cond_table(etr, jj[tr], n2, P[z][jz])
        out[f"G_{y}|{z}"] = ce(P[z][X[z][te], ete]) - ce(T2[jj[te], ete])
    # does the next word's class / form add routing information beyond the input token identity?
    for y in ["next_upos", "next_form"]:
        jj = codes(X["in_tok"] * 10 ** 5 + X[y]); n2 = int(jj.max()) + 1
        jz = np.zeros(n2, np.int64); jz[jj] = X["in_tok"]
        T2 = cond_table(etr, jj[tr], n2, P["in_tok"][jz])
        out[f"G_{y}|in_tok"] = ce_in - ce(T2[jj[te], ete])
    out["H_e_test"] = base
    return out


def main():
    P = json.loads((WB / "results/e167/passages.json").read_text())
    words = P["words"]
    meta = json.loads((OUT / "e175_rows.json").read_text())  # rows + token ids written by the main script's data step
    rows = np.array(meta["rows"])
    X = {"in_tok": codes(meta["in_tok"]), "next_tok": codes(meta["next_tok"]), "in_form": codes(meta["in_form"]),
         "next_form": codes(meta["next_form"]), "in_upos": codes(meta["in_upos"]), "next_upos": codes(meta["next_upos"])}
    X["joint"] = codes(X["in_tok"] * 10 ** 6 + X["next_tok"])
    rng = np.random.default_rng(SEED)
    X["shuf_in_tok"] = X["in_tok"][rng.permutation(len(rows))]
    X["shuf_next_tok"] = X["next_tok"][rng.permutation(len(rows))]
    m = len(rows)
    perm = rng.permutation(m)
    folds = [np.sort(perm[: m // 2]), np.sort(perm[m // 2:])]
    cnt_in, cnt_nx = np.bincount(X["in_tok"])[X["in_tok"]], np.bincount(X["next_tok"])[X["next_tok"]]
    sub = (cnt_in >= 20) & (cnt_nx >= 20)
    for run in sys.argv[1:]:
        res = {}
        for f in sorted(CAP.glob(f"{run}__ckpt_*.npz"), key=lambda f: int(f.stem.split("_")[-1])):
            t = int(f.stem.split("_")[-1])
            Z = np.load(f)
            per = []
            for l in range(NL):
                e = Z[f"S{l}"][rows, 0].astype(np.int64)
                acc = {}
                for k in range(2):
                    tr, te = folds[k], folds[1 - k]
                    g = gains(e, X, tr, te)
                    gs = gains(e, X, tr, te[sub[te]])  # same fit, scored on the frequency subset
                    for key, v in g.items():
                        acc[key] = acc.get(key, 0) + v / 2
                    for key in ["G_in_tok", "G_next_tok", "G_next|in", "G_in|next", "G_joint", "G_next_upos|in_tok"]:
                        acc["sub_" + key] = acc.get("sub_" + key, 0) + gs[key] / 2
                per.append(acc)
            res[str(t)] = per
            print(run, t, "L11 G in=%.3f next=%.3f next|in=%.3f in|next=%.3f joint=%.3f shuf=%.3f" % tuple(
                per[11][k] for k in ["G_in_tok", "G_next_tok", "G_next|in", "G_in|next", "G_joint", "G_shuf_in_tok"]), flush=True)
        (OUT / f"crossfit_{run}.json").write_text(json.dumps({"A": A, "seed": SEED, "n": int(m), "n_sub": int(sub.sum()), "ckpts": res}))


if __name__ == "__main__":
    main()
