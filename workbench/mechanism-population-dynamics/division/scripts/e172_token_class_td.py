#!/usr/bin/env python3
"""E172 readout 1: E167's T_D (within-word-type centred D = C - E_N1[C], cross-model Pearson) restricted to
groups of word types: by the type's majority UPOS (content / function / PUNCT / NUM / other), and by the
type's frequency in the full UD EWT text (tertiles). Secondary: pairs whose two anchors share a UPOS.
T_D definition and N1 floor are E167's (analyze_routing.py), unchanged.

Usage: e172_token_class_td.py [TOKENS ...]   -> results/e172/token_class_td_<TOKENS>.json (+ untrained floor)
"""
import collections
import itertools
import json
import sys
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
OUT = WB / "results/e172"
OUT.mkdir(parents=True, exist_ok=True)
CONTENT = ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]
FUNCTION = ["ADP", "DET", "PRON", "AUX", "CCONJ", "SCONJ", "PART"]
MIN_TYPES, MIN_PAIRS = 5, 3000

P = np.load(CAP / "pairs.npz")
pi, pj, pt = P["i"], P["j"], P["type"]
nT = int(pt.max()) + 1
aupos = P["anchor_upos"]
atype = P["anchor_type"]
types, tinv = np.unique(atype, return_inverse=True)
assert len(types) == nT
# pair type id == unique index of anchor_type? check
assert (tinv[pi] == pt).all() and (tinv[pj] == pt).all(), "type ids differ from anchor_type order"

# majority UPOS per type
maj = {}
for t in range(nT):
    c = collections.Counter(aupos[tinv == t])
    maj[t] = c.most_common(1)[0][0]
maj_arr = np.array([maj[t] for t in range(nT)])
# frequency per type in the full UD EWT text
words = json.loads((WB / "results/e167/passages.json").read_text())["words"]
freq_all = collections.Counter(w[3].lower() for w in words)
tfreq = np.array([freq_all[t] for t in types])
assert tfreq.min() >= 6, tfreq.min()
q1, q2 = np.percentile(tfreq, [100 / 3, 200 / 3])
fbin = np.where(tfreq <= q1, "low", np.where(tfreq <= q2, "mid", "high"))

pair_upos = maj_arr[pt]
pair_fbin = fbin[pt]
same = aupos[pi] == aupos[pj]
pair_upos_same = np.where(same, aupos[pi], "MIXED")


def groups_from(labels_per_pair, type_label):
    """Return {group: pair mask}. Merge small UPOS groups into their class."""
    g = {}
    for u in CONTENT + FUNCTION + ["PUNCT", "NUM"]:
        m = labels_per_pair == u
        n_types = int((type_label == u).sum()) if type_label is not None else int(len(np.unique(pt[m])))
        if m.sum() >= MIN_PAIRS and n_types >= MIN_TYPES:
            g[u] = m
    g["content"] = np.isin(labels_per_pair, CONTENT)
    g["function"] = np.isin(labels_per_pair, FUNCTION)
    g["other(INTJ/SYM/X)"] = np.isin(labels_per_pair, ["INTJ", "SYM", "X"])
    g["all"] = np.ones(len(labels_per_pair), bool)
    return g


G_upos = groups_from(pair_upos, maj_arr)
G_same = groups_from(pair_upos_same, None)
G_freq = {b: pair_fbin == b for b in ("high", "mid", "low")}
G_cross = {f"{c}|{b}": (np.isin(pair_upos, CONTENT if c == "content" else FUNCTION) & (pair_fbin == b))
           for c in ("content", "function") for b in ("high", "mid", "low")}


def cw(x):
    s = np.bincount(pt, x, nT)
    c = np.bincount(pt, None, nT)
    return x - (s / np.maximum(c, 1))[pt]


def load(run, t):
    Z = np.load(CAP / f"{run}__ckpt_{t}.npz")
    return {l: {"D": cw(Z[f"C{l}"].astype(np.float64) - Z[f"B{l}"].astype(np.float64)),
                "C": cw(Z[f"C{l}"].astype(np.float64))} for l in range(12)}


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-30))


def have(r, t):
    return (CAP / f"{r}__ckpt_{t}.npz").exists()


def run_for(tok):
    inits = [f"I{i}D0" for i in range(6) if have(f"I{i}D0", tok)]
    pairs = {"init": list(itertools.combinations(inits, 2)),
             "order": [(f"I{i}D0", f"I{i}D1") for i in (0, 1) if have(f"I{i}D1", tok)],
             "rerun": [p for p in [("I4D0", "I4D0R"), ("I0D0", "I0D0R")] if have(p[0], tok) and have(p[1], tok)]}
    runs = sorted({r for ps in pairs.values() for p in ps for r in p})
    M = {r: load(r, tok) for r in runs}
    F = {r: load(r, 0) for r in ("I0D0", "I1D0")}
    out = {"tokens": tok, "pairs": {k: v for k, v in pairs.items()}, "freq_tertiles": [float(q1), float(q2)],
           "content": CONTENT, "function": FUNCTION, "groupings": {}}
    for gname, G in (("type_majority_upos", G_upos), ("pair_same_upos", G_same), ("type_freq", G_freq), ("class_x_freq", G_cross)):
        rec = {}
        for g, m in G.items():
            n_pairs = int(m.sum())
            if n_pairs == 0:
                continue
            r = {"n_pairs": n_pairs, "n_types": int(len(np.unique(pt[m]))), "layers": []}
            for l in range(12):
                row = {"layer": l}
                for q in ("D", "C"):
                    for k, ps in list(pairs.items()) + [("floor", [("I0D0", "I1D0")])]:
                        vals = [corr((F if k == "floor" else M)[a][l][q][m], (F if k == "floor" else M)[b][l][q][m]) for a, b in ps]
                        row[f"{q}_{k}"] = float(np.mean(vals)) if vals else None
                        if k == "init" and vals:
                            row[f"{q}_init_min"] = float(min(vals)); row[f"{q}_init_max"] = float(max(vals))
                            row[f"{q}_init_pairs"] = [float(v) for v in vals]
                            # seed jackknife: drop each seed, mean over remaining pairs
                            jk = [np.mean([v for (a, b), v in zip(ps, vals) if s not in (a, b)]) for s in inits]
                            row[f"{q}_init_jkse"] = float(np.sqrt((len(inits) - 1) / len(inits) * ((np.array(jk) - np.mean(jk)) ** 2).sum()))
                r["layers"].append(row)
            rec[g] = r
        out["groupings"][gname] = rec
    return out


if __name__ == "__main__":
    toks = [int(float(x)) for x in sys.argv[1:]] or [3200000000, 3999793152, 400000000]
    for tok in toks:
        o = run_for(tok)
        (OUT / f"token_class_td_{tok}.json").write_text(json.dumps(o))
        print(f"\n=== {tok}  pairs {dict((k, len(v)) for k, v in o['pairs'].items())}")
        for gname, rec in o["groupings"].items():
            print(f"-- {gname}")
            print(f"{'group':20s} {'n_pairs':>8s} {'nty':>5s} | deep L6-11: init  (min–max) rerun order floor | L11: init rerun order | init/rerun deep")
            for g, r in rec.items():
                L = r["layers"]
                d = lambda k: np.mean([L[l][k] for l in range(6, 12)]) if L[6].get(k) is not None else float("nan")
                print(f"{g:20s} {r['n_pairs']:8d} {r['n_types']:5d} | {d('D_init'):.3f} ({d('D_init_min'):.3f}–{d('D_init_max'):.3f}) {d('D_rerun'):.3f} {d('D_order'):.3f} {d('D_floor'):.3f} | "
                      f"{L[11]['D_init']:.3f} {L[11]['D_rerun'] if L[11]['D_rerun'] is not None else float('nan'):.3f} {L[11]['D_order'] if L[11]['D_order'] is not None else float('nan'):.3f} | {d('D_init')/d('D_rerun'):.2f}")
    print("saved to", OUT)
