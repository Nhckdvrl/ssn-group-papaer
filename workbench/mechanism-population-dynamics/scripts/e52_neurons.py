"""E52: are specialized (high-kurtosis) MLP neurons inherited by index under a shared init? Protocol: E52 card.
Uses the E43 dumps (/home/xiang/mechpop_cache/e43/*.pt).  e52_neurons.py [--analyze]
"""
import argparse
import itertools
import json

import numpy as np
import torch

import mp_common as mc
from e43_basis import DUMP, keys

OUT = mc.RESULTS / "e52"
NQ = 10


def kurt(z):  # z [n, units] -> excess kurtosis per unit
    z = z - z.mean(0)
    v = z.pow(2).mean(0) + 1e-8
    return z.pow(4).mean(0) / v.pow(2) - 3


def std(z):
    z = z - z.mean(0)
    return z / (z.norm(dim=0, keepdim=True) + 1e-6)


@torch.no_grad()
def pair(A, B, dev="cuda"):
    na = A["mlp"][:, :, 1:].reshape(A["mlp"].shape[0], -1, A["mlp"].shape[-1])
    nb = B["mlp"][:, :, 1:].reshape(B["mlp"].shape[0], -1, B["mlp"].shape[-1])
    n = na.shape[1]
    idx_dec, best_dec, split_agree = np.zeros(NQ), np.zeros(NQ), []
    for l in range(na.shape[0]):
        a, b = na[l].to(dev).float(), nb[l].to(dev).float()
        k = (kurt(a) + kurt(b)) / 2
        k1 = (kurt(a[: n // 2]) + kurt(b[: n // 2])) / 2
        k2 = (kurt(a[n // 2:]) + kurt(b[n // 2:])) / 2
        dec = lambda x: torch.bucketize(x, torch.quantile(x, torch.linspace(0, 1, NQ + 1, device=dev)[1:-1]))
        d, d1, d2 = dec(k), dec(k1), dec(k2)
        top1, top2 = d1 == NQ - 1, d2 == NQ - 1
        split_agree.append(float((top1 & top2).sum() / max(1, int(top1.sum()))))
        za, zb = std(a), std(b)
        r_idx = (za * zb).sum(0)
        r_best = (za.T @ zb).max(1).values
        for q in range(NQ):
            m = d == q
            idx_dec[q] += float(r_idx[m].mean()) / na.shape[0]
            best_dec[q] += float(r_best[m].mean()) / na.shape[0]
    return {"index_by_decile": idx_dec.tolist(), "best_by_decile": best_dec.tolist(), "split_top_decile_agree": float(np.mean(split_agree))}


def run():
    K = keys()
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    P = list(itertools.combinations(K, 2))
    sel = [p for p in P if cls(*p) in ("SI", "SD")] + [p for p in P if cls(*p) == "DD"][::5]
    OUT.mkdir(exist_ok=True)
    cache = {}
    for a, b in sel:
        f = OUT / f"{a[0]}__{a[1]}--{b[0]}__{b[1]}.json"
        if f.exists():
            continue
        for k in (a, b):
            if k not in cache:
                for old in [c for c in cache if c not in (a, b)][: max(0, len(cache) - 2)]:
                    cache.pop(old)
                cache[k] = torch.load(DUMP / f"{k[0]}__{k[1]}.pt")
        f.write_text(json.dumps(pair(cache[a], cache[b])))
        print("pair", f.stem, flush=True)


def analyze():
    K = keys()
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    G = {"SI": [], "SD": [], "DD": []}
    for f in OUT.glob("*--*.json"):
        a, b = (tuple(x.split("__")) for x in f.stem.split("--"))
        G[cls(a, b)].append(json.loads(f.read_text()))
    out = {}
    for c, rows in G.items():
        if rows:
            out[c] = {k: np.mean([r[k] for r in rows], 0).tolist() for k in ("index_by_decile", "best_by_decile")}
            out[c]["split_top_decile_agree"] = float(np.mean([r["split_top_decile_agree"] for r in rows]))
            out[c]["n"] = len(rows)
    out["top_decile_SI_minus_SD"] = out["SI"]["index_by_decile"][-1] - out["SD"]["index_by_decile"][-1]
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    for c in ("SI", "SD", "DD"):
        if c in out:
            print(c, "index", np.round(out[c]["index_by_decile"], 3), "best", np.round(out[c]["best_by_decile"], 3),
                  "split", round(out[c]["split_top_decile_agree"], 2))
    print("top decile SI - SD:", round(out["top_decile_SI_minus_SD"], 3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else run()
