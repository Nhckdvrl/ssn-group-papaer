"""E185 token-id context dependence: H(e | id) at equal n (30 occurrences, 5 subsamples), per layer and router.

usage: e185_tokens.py --data {d184,d180} --model M
D184: T + 8 N_A + 8 N_B, FLORES + UD English pooled (all tokens).  D180: T, N_A0, N_B0, 20 FLORES sides.
writes ~/mechpop_cache/atlas_e185/tok_<data>_<model>.npz and results/e185/tok_<data>_<model>.json (rankings,
categories, raw example contexts)."""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import CACHE, BANDS, tokclass_table, jdump  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True, choices=["d184", "d180"])
ap.add_argument("--model", required=True)
args = ap.parse_args()
NMIN, NSUB = 30, 5
OUT = os.environ.get("E185_OUT", os.path.expanduser("~/mechpop_cache/atlas_e185"))
RES = os.environ.get("E185_RES", os.path.join(os.path.dirname(__file__), "..", "results", "e185"))
src = {"d184": "e184", "d180": "e180"}[args.data]
base = f"{CACHE}/{src}/{args.model}"
meta = json.load(open(f"{base}/meta.json"))
tm = dict(np.load(f"{base}/tokmeta.npz"))
L, E, K = meta["L"], meta["E"], meta["K"]
topk = np.load(f"{base}/topk.npy", mmap_mode="r")
R = topk.shape[2]
inp = tm["inp"].astype(np.int64)
N = inp.size
seq = (tm["seq"].astype(np.int64) + 100000 * tm["corpus"]) if args.data == "d184" else \
    tm["lang"].astype(np.int64) * 100000 + tm["sid"]
pos = tm["pos"].astype(np.int64)
rng = np.random.default_rng(185)
cnt = np.bincount(inp)
ids = np.where(cnt >= NMIN)[0]
order = np.argsort(inp, kind="stable")
starts = np.searchsorted(inp[order], ids)
sub = np.stack([np.stack([order[s + rng.choice(cnt[x], NMIN, replace=False)] for _ in range(NSUB)])
                for x, s in zip(ids, starts)])          # [nx, NSUB, NMIN] token indices
nx = len(ids)
print(args.data, args.model, "ids with n>=30:", nx, "covering", cnt[ids].sum() / N, flush=True)

Hx = np.zeros((L, R, nx), np.float32)
P1 = np.zeros((L, R, nx), np.float32)      # top-1 purity at equal n (share of most common expert)
rows = np.repeat(np.arange(nx * NSUB), NMIN)
for l in range(L):
    blk = np.asarray(topk[l, :, :, 0])                     # [N, R] top-1
    for r in range(R):
        e = blk[:, r].astype(np.int64)[sub].reshape(-1)
        c = np.bincount(rows * E + e, minlength=nx * NSUB * E).reshape(nx, NSUB, E).astype(np.float64) / NMIN
        with np.errstate(divide="ignore", invalid="ignore"):
            h = -np.nansum(np.where(c > 0, c * np.log2(c), 0), -1)
        Hx[l, r] = h.mean(1)
        P1[l, r] = c.max(-1).mean(1)
np.savez_compressed(f"{OUT}/tok_{args.data}_{args.model}.npz", Hx=Hx, P1=P1, ids=ids, cnt=cnt[ids])

# ---------------------------------------------------------------- categories and rankings
tok, strs, clsv = tokclass_table(args.model)
edge, mid = BANDS[args.model]
if args.data == "d184":
    rT, rA, rB = [0], list(range(1, 9)), list(range(9, 17))
else:
    names = meta["topk_routers"]
    rT, rA, rB = [names.index("T")], [names.index("N_A0")], [names.index("N_B0")]
Hmid = Hx[mid].mean(0)            # [R, nx]
Hlast = Hx[L - 1]
HT, HB, HA = Hmid[rT].mean(0), Hmid[rB].mean(0), Hmid[rA].mean(0)
CLOSED = {"ADP", "AUX", "CCONJ", "DET", "PART", "PRON", "SCONJ"}
OPEN = {"NOUN", "VERB", "ADJ", "ADV", "PROPN", "NUM"}
cats = {}
s_of = [strs[i] for i in ids]
cl = clsv[ids]
lead = np.array([s[:1] in (" ", "\n", "\t") for s in s_of])
cats["punct/symbol (no letter, no digit)"] = (cl == 2) & ~np.array([any(ch.isdigit() for ch in s) for s in s_of])
cats["digit"] = (cl == 2) & np.array([any(ch.isdigit() for ch in s) for s in s_of])
cats["letter, word-initial (leading space)"] = (cl == 1) & lead
cats["letter, no leading space (continuation / sentence-initial)"] = (cl == 1) & ~lead
cats["capitalised"] = (cl == 1) & np.array([s.strip()[:1].isupper() for s in s_of])
cats["byte fragment"] = cl == 3
upos_major = {}
if args.data == "d184":
    upos = tm["upos"].astype(np.int64)
    UP = meta["upos"]
    m = upos >= 0
    byid = {}
    for x, u in zip(inp[m], upos[m]):
        byid.setdefault(int(x), Counter())[UP[u]] += 1
    for x in ids:
        c = byid.get(int(x))
        if c:
            u, n = c.most_common(1)[0]
            if n / sum(c.values()) >= .5:
                upos_major[int(x)] = u
    maj = np.array([upos_major.get(int(x), "") for x in ids])
    cats["function word (UD majority closed-class)"] = np.isin(maj, list(CLOSED))
    cats["content word (UD majority open-class)"] = np.isin(maj, list(OPEN))
    cats["never word-final in UD (word-internal piece)"] = np.array([int(x) not in byid for x in ids]) & (cl == 1)
else:
    side = tm["lang"].astype(np.int64)
    langs = meta["langs"]
    scr = np.array([lg.split("_")[1] for lg in langs])[side]
    # dominant script of each id's occurrences
    dom = []
    for x, s0 in zip(ids, starts):
        c = Counter(scr[order[s0:s0 + cnt[x]]])
        dom.append(c.most_common(1)[0][0] if c.most_common(1)[0][1] / cnt[x] >= .9 else "mixed")
    dom = np.array(dom)
    for sc in sorted(set(dom)):
        for cn, cv in [("LET", 1), ("NON", 2), ("frag", 3)]:
            mm = (dom == sc) & (cl == cv)
            if mm.sum() >= 5:
                cats[f"script={sc} class={cn}"] = mm


def catrow(mask):
    return dict(n=int(mask.sum()), T=float(HT[mask].mean()), N_B=float(HB[mask].mean()), N_A=float(HA[mask].mean()),
                T_minus_NB=float((HT - HB)[mask].mean()),
                T_last=float(Hlast[rT].mean(0)[mask].mean()), NB_last=float(Hlast[rB].mean(0)[mask].mean()))


from scipy.stats import spearmanr  # noqa: E402
lf = np.log(cnt[ids])
out = {"data": args.data, "model": args.model, "n_ids": int(nx), "token_coverage": float(cnt[ids].sum() / N),
       "nmin": NMIN, "mid_band": [mid[0], mid[-1]], "maxH": float(np.log2(min(NMIN, E))),
       "overall": catrow(np.ones(nx, bool)),
       "categories": {k: catrow(v) for k, v in cats.items() if v.sum() > 0},
       "spearman_H_logfreq": {"T": float(spearmanr(HT, lf)[0]), "N_B": float(spearmanr(HB, lf)[0])},
       "spearman_T_NB_over_ids": float(spearmanr(HT, HB)[0]),
       "layer_profile": {"T": Hx[:, rT].mean((1, 2)).tolist(), "N_B": Hx[:, rB].mean((1, 2)).tolist(),
                         "N_A": Hx[:, rA].mean((1, 2)).tolist()}}
lstar = mid[len(mid) // 2]


def examples(j, n=3):
    x = ids[j]
    occ = order[starts[j]:starts[j] + cnt[x]]
    e = np.asarray(topk[lstar, occ, rT[0], 0]).astype(int)
    exs = []
    for ex, _ in Counter(e).most_common(n):
        t = occ[e == ex][0]
        a = max(t - 8, 0)
        while seq[a] != seq[t]:
            a += 1
        b = t + 1
        while b < N and b < t + 4 and seq[b] == seq[t]:
            b += 1
        ctx = tok.decode(inp[a:t].tolist()) + "⟦" + tok.decode([int(x)]) + "⟧" + tok.decode(inp[t + 1:b].tolist())
        exs.append({"expert": int(ex), "share": float((e == ex).mean()), "context": ctx.replace("\n", "⏎")})
    return exs


def rowfor(j):
    d = {"id": int(ids[j]), "str": s_of[j], "n": int(cnt[ids[j]]), "H_T_mid": float(HT[j]), "H_NB_mid": float(HB[j]),
         "H_NA_mid": float(HA[j]), "purity_T_mid": float(P1[mid][:, rT].mean((0, 1))[j]),
         "upos": upos_major.get(int(ids[j]), ""), "examples": examples(j)}
    return d


rk = np.argsort(-HT)
out["most_context_dependent"] = [rowfor(j) for j in rk[:15]]
out["least_context_dependent"] = [rowfor(j) for j in rk[::-1][:15]]
dd = HT - HB
rk2 = np.argsort(dd)
out["T_more_lexical_than_NB"] = [rowfor(j) for j in rk2[:10]]
out["T_more_contextual_than_NB"] = [rowfor(j) for j in rk2[::-1][:10]]
out["lstar_examples"] = int(lstar)
jdump(os.path.join(RES, f"tok_{args.data}_{args.model}.json"), out)
print("done", args.data, args.model, json.dumps(out["overall"]), flush=True)
