"""E187 读数 5 (routing): copied-layer agreement on the E182 store for Qwen3-30B-A3B Instruct vs Base, same tokens
(22 FLORES devtest language sides, ~1.58M tokens).  Expert map = each model's own router-row matching
(e187_wdrift.py).  Also same-layer Instruct-vs-Base agreement (identity map) as a reference for how much
post-training moved routing.  Writes results/e187/e182_base_vs_instruct.json."""
import json, os
import numpy as np

C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
L, E, K = 48, 128, 8
ST = {k: np.load(f"/home/xiang/mechpop_cache/e182/{d}/topk_T.npy", mmap_mode="r") for k, d in
      (("instruct", "qwen3"), ("base", "qwen3base"))}
ti = np.load("/home/xiang/mechpop_cache/e182/qwen3/tokmeta.npz"); tb = np.load("/home/xiang/mechpop_cache/e182/qwen3base/tokmeta.npz")
assert (ti["inp"] == tb["inp"]).all() and (ti["lang"] == tb["lang"]).all(), "E182 stores not token-aligned"
N = ti["inp"].size
from e187_common import RouterMatch
MT = {k: RouterMatch(k) for k in ST}
cache = {}


def S(k, l):
    if (k, l) not in cache:
        cache[(k, l)] = np.asarray(ST[k][l]).astype(np.int64)
    return cache[(k, l)]


def agree(a, b):
    t1 = float((a[:, 0] == b[:, 0]).mean())
    MA = np.zeros((a.shape[0], E), bool); MA[np.arange(a.shape[0])[:, None], a] = True
    return t1, float(MA[np.arange(a.shape[0])[:, None], b].sum(1).mean() / K)


out = {"N": int(N), "copy": [], "same_layer": []}
for lag in (12, 24, 1, 11, 13):
    for l in range(L - lag):
        m = l + lag
        if lag in (1, 11, 13) and not (6 <= l and m <= 41):
            continue
        rec = dict(l=l, m=m, lag=lag)
        for k in ST:
            p = MT[k][f"{l}_{m}_router"]
            rec[f"{k}_top1"], rec[f"{k}_top8"] = agree(S(k, l), p[S(k, m)])
        out["copy"].append(rec)
        print(l, m, round(rec["instruct_top1"], 3), round(rec["base_top1"], 3), flush=True)
for l in range(L):
    t1, t8 = agree(S("instruct", l), S("base", l))
    out["same_layer"].append(dict(l=l, top1=t1, top8=t8))
json.dump(out, open(f"{RES}/e182_base_vs_instruct.json", "w"), indent=0)
print("done")
