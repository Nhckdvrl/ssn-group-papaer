"""E185 routing variance atlas (CPU only).  Card: division/experiments/E185-routing-variance-atlas.md

usage: e185_atlas.py --data {d184,d180,d182} --model M [--procs 20]
writes ~/mechpop_cache/atlas_e185/<data>_<model>.npz  (arrays: <view>|<kind>|<name> -> [L, R, 4] = I_hat, I_plugin,
floor_sd, H(e); kind in marg, cond, smarg, scond (s = full top-k slot version)); and a json with plan metadata.
Input stores are opened read-only (mmap)."""
import argparse
import json
import os
import sys
import time
from multiprocessing import get_context

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from e185_lib import CACHE, Plan, mi_marg, mi_cond, tokclass_table  # noqa: E402

OUT = os.environ.get("E185_OUT", os.path.expanduser("~/mechpop_cache/atlas_e185"))
SCRIPT = {"Cyrl": "Cyrl", "Latn": "Latn", "Deva": "Deva", "Arab": "Arab", "Hans": "Hans", "Hant": "Hant"}

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True, choices=["d184", "d180", "d182"])
ap.add_argument("--model", required=True)
ap.add_argument("--procs", type=int, default=20)
args = ap.parse_args()
os.makedirs(OUT, exist_ok=True)
t0 = time.time()


def log(*a):
    print(f"[{time.time() - t0:7.1f}s]", *a, flush=True)


src = {"d184": "e184", "d180": "e180", "d182": "e182"}[args.data]
base = f"{CACHE}/{src}/{args.model}"
meta = json.load(open(f"{base}/meta.json"))
tm = dict(np.load(f"{base}/tokmeta.npz"))
L, E, K = meta["L"], meta["E"], meta["K"]
if args.data == "d182":
    TOPK = f"{base}/topk_T.npy"
    ROUTERS = ["T"]
else:
    TOPK = f"{base}/topk.npy"
    ROUTERS = (["T"] + [f"N_A{i}" for i in range(8)] + [f"N_B{i}" for i in range(8)]) if args.data == "d184" \
        else meta["topk_routers"]
shape = np.load(TOPK, mmap_mode="r").shape
log("store", TOPK, shape, "routers", ROUTERS)

# ---------------------------------------------------------------- token streams and factors
if args.data == "d184":
    seq = tm["seq"].astype(np.int64) + 100000 * tm["corpus"].astype(np.int64)
else:
    seq = tm["lang"].astype(np.int64) * 100000 + tm["sid"]
N = seq.size
assert N == shape[1], (N, shape)
start = np.r_[True, seq[1:] != seq[:-1]]
end = np.r_[seq[1:] != seq[:-1], True]
inp = tm["inp"].astype(np.int64)
prev = np.where(start, -1, np.r_[-1, inp[:-1]])
nxt = tm["nxt"].astype(np.int64) if "nxt" in tm else np.where(end, -1, np.r_[inp[1:], -1])
pred = tm["pred"].astype(np.int64)
pos = tm["pos"].astype(np.int64)
posb = np.where(pos < 4, pos, np.minimum(np.floor(np.log2(np.maximum(pos, 1))).astype(np.int64) + 2, 10))
plans = {}
if args.data == "d184":
    upos = tm["upos"].astype(np.int64)
    base_idx = np.where(nxt >= 0)[0]                      # E184 R4 positions (sequence-final excluded)
    corpus = tm["corpus"].astype(np.int64)
    ud = upos >= 0
    views = {"full": base_idx, "h0": base_idx[seq[base_idx] % 2 == 0], "h1": base_idx[seq[base_idx] % 2 == 1]}
    for vn, vi in views.items():
        p = Plan(vi)
        for nm, x in [("inp", inp), ("prev", prev), ("nxt", nxt), ("pred", pred), ("pos", posb), ("seq", seq),
                      ("corpus", corpus)]:
            p.add_marg(nm, x)
        p.add_marg("upos", upos, sub=ud)
        p.add_marg("inp@ud", inp, sub=ud)
        for nm, x in [("prev", prev), ("nxt", nxt), ("pred", pred), ("pos", posb), ("seq", seq), ("corpus", corpus)]:
            p.add_cond(f"{nm}|inp", x, inp)
        p.add_cond("upos|inp", upos, inp, sub=ud)
        if vn == "full":
            p.add_cond("inp|pred", inp, pred)
            p.add_cond("inp|prev", inp, prev)
            p.add_cond("nxt|pred", nxt, pred)
            p.add_cond("pred|nxt", pred, nxt)
            p.add_cond("pred|inp,prev", pred, inp * 1_000_003 + prev + 1)
            p.add_cond("pos|inp,prev", posb, inp * 1_000_003 + prev + 1)
            # residual (a) strata: prediction correct / incorrect; input-frequency terciles
            corr = pred == nxt
            freq = np.bincount(dense_inp := np.unique(inp[vi], return_inverse=True)[1])[dense_inp]
            fr = np.zeros(N, np.int64)
            fr[vi] = np.digitize(freq, np.quantile(freq, [1 / 3, 2 / 3]))
            for tag, m in [("corr", corr), ("wrong", ~corr), ("f0", fr == 0), ("f1", fr == 1), ("f2", fr == 2)]:
                mm = m.copy()
                mm[np.setdiff1d(np.arange(N), vi)] = False
                p.add_marg(f"inp@{tag}", inp, sub=mm)
                p.add_marg(f"pred@{tag}", pred, sub=mm)
                p.add_cond(f"pred|inp@{tag}", pred, inp, sub=mm)
                p.add_cond(f"inp|pred@{tag}", inp, pred, sub=mm)
        plans[vn] = p
        log("plan", vn, len(vi), {k: v["nX"] for k, v in p.marg.items()})
else:
    langs = meta["langs"]
    lang_of = np.array([lg.split("_")[0] for lg in langs])
    scr_of = np.array([lg.split("_")[1] for lg in langs])
    _, langcode = np.unique(lang_of, return_inverse=True)
    _, scrcode = np.unique(scr_of, return_inverse=True)
    side = tm["lang"].astype(np.int64)
    lang = langcode[side].astype(np.int64)
    script = scrcode[side].astype(np.int64)
    sid = tm["sid"].astype(np.int64)
    inst = side * 10000 + sid
    tok, strs, clsv = tokclass_table(args.model)
    cls = clsv[inp].astype(np.int64)
    nonfinal = nxt >= 0
    allidx = np.arange(N)
    views = {"full": allidx, "LET": allidx[cls == 1], "NON": allidx[cls == 2]}
    for vn, vi in views.items():
        p = Plan(vi)
        mlist = [("inp", inp), ("side", side), ("lang", lang), ("script", script)]
        clist = [("side|inp", side), ("lang|inp", lang), ("script|inp", script), ("sid|inp", sid),
                 ("pred|inp", pred)]
        if vn == "full":
            mlist += [("prev", prev), ("pred", pred), ("pos", posb), ("sid", sid), ("inst", inst), ("cls", cls)]
            clist += [("inst|inp", inst), ("prev|inp", prev), ("pos|inp", posb)]
        for nm, x in mlist:
            p.add_marg(nm, x)
        if vn == "full":
            p.add_marg("nxt", nxt, sub=nonfinal)
            p.add_cond("nxt|inp", nxt, inp, sub=nonfinal)
        for nm, x in clist:
            p.add_cond(nm, x, inp)
        p.add_cond("lang|inp,script", lang, inp * 16 + script)
        p.add_cond("script|inp,lang", script, inp * 64 + lang)
        plans[vn] = p
        log("plan", vn, len(vi), {k: v["nX"] for k, v in p.marg.items()},
            {k: round(v["cov"], 3) for k, v in p.cond.items()})

SLOT_MARG = {"d184": ["inp", "prev", "nxt", "pred", "pos", "seq", "corpus", "upos"],
             "d180": ["inp", "side", "lang", "script"], "d182": ["inp", "side", "lang", "script"]}[args.data]
SLOT_COND = {"d184": ["prev|inp", "nxt|inp", "pred|inp", "pos|inp", "seq|inp", "corpus|inp", "upos|inp"],
             "d180": ["side|inp", "lang|inp", "script|inp"], "d182": ["side|inp", "lang|inp", "script|inp"]}[args.data]


def work(l):
    arr = np.load(TOPK, mmap_mode="r")
    blk = np.asarray(arr[l])                       # [N, R, K] or [N, K]
    if blk.ndim == 2:
        blk = blk[:, None, :]
    out = {}
    for r in range(blk.shape[1]):
        top1 = blk[:, r, 0].astype(np.int64)
        slots = blk[:, r, :].astype(np.int64)
        for vn, p in plans.items():
            for nm, f in p.marg.items():
                out[(vn, "marg", nm, r)] = mi_marg(top1[f["idx"]], f, E)
            for nm, f in p.cond.items():
                out[(vn, "cond", nm, r)] = mi_cond(top1[f["idx"]], f, E)
            if vn == "full":
                for nm in SLOT_MARG:
                    f = p.marg[nm]
                    out[(vn, "smarg", nm, r)] = mi_marg(slots[f["idx"]], f, E)
                for nm in SLOT_COND:
                    f = p.cond[nm]
                    out[(vn, "scond", nm, r)] = mi_cond(slots[f["idx"]], f, E)
    return l, out


R = len(ROUTERS)
res = {}
with get_context("fork").Pool(args.procs) as pool:
    for l, out in pool.imap_unordered(work, range(L)):
        for (vn, kind, nm, r), v in out.items():
            key = f"{vn}|{kind}|{nm}"
            if key not in res:
                res[key] = np.full((L, R, 4), np.nan)
            res[key][l, r] = v
        log("layer", l, "done")
np.savez_compressed(f"{OUT}/{args.data}_{args.model}.npz", **res)
info = {"data": args.data, "model": args.model, "routers": ROUTERS, "L": L, "E": E, "K": K, "N": int(N),
        "views": {vn: int(len(p.idx)) for vn, p in plans.items()},
        "n": {f"{vn}|{nm}": int(len(f["idx"])) for vn, p in plans.items() for nm, f in {**p.marg, **p.cond}.items()},
        "card": {f"{vn}|{nm}": int(f["nX"]) for vn, p in plans.items() for nm, f in p.marg.items()},
        "cov": {f"{vn}|{nm}": f["cov"] for vn, p in plans.items() for nm, f in p.cond.items()},
        "wall_s": time.time() - t0}
json.dump(info, open(f"{OUT}/{args.data}_{args.model}.json", "w"), indent=1)
log("saved")
