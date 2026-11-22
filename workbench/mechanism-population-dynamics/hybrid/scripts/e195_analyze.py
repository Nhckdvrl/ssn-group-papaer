#!/usr/bin/env python3
"""E195/E196 analysis of R1 outputs: split / shuffled / last-only curves and binding scores with type bootstrap.

Usage: e195_analyze.py OUT_JSON KEY=PATH_TO_S.pt[:ITEMS_JSON] ...
Binding (card): acc(split_m) - acc(shuf_m), averaged over m = 3..6, at each decoder layer; 95% CI from 1000
resamples of word types. Layer index -1 = embedding output.
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch

B, SEED, MS = 1000, 194, [2, 3, 4, 5, 6]


def main():
    out = Path(sys.argv[1])
    res = {}
    for arg in sys.argv[2:]:
        key, rest = arg.split("=", 1)
        spath, ipath = rest.split(":") if ":" in rest else (rest, None)
        d = torch.load(spath)
        top1 = (d["ranks"] == 0).float().numpy()  # [items, L+1, Q]
        q = d["qnames"]
        n = top1.shape[0]
        if ipath:
            forms = [it["form"].lower() for it in json.loads(Path(ipath).read_text())["S"]][:n]
        else:
            forms = [str(i) for i in range(n)]
        uniq = sorted(set(forms)); occ = {t: [] for t in uniq}
        for i, t in enumerate(forms):
            occ[t].append(i)
        rng = np.random.default_rng(SEED)
        boots = [np.concatenate([occ[uniq[k]] for k in rng.integers(0, len(uniq), len(uniq))]) for _ in range(B)]
        L = top1.shape[1]
        layers = list(range(-1, L - 1))
        js = [q.index(f"split{m}") for m in [3, 4, 5, 6]]; jh = [q.index(f"shuf{m}") for m in [3, 4, 5, 6]]
        bind_items = top1[:, :, js].mean(-1) - top1[:, :, jh].mean(-1)  # [items, L+1]
        bb = np.stack([bind_items[b].mean(0) for b in boots])
        r = {"layers": layers, "binding": bind_items.mean(0).round(4).tolist(),
             "binding_lo": np.percentile(bb, 2.5, 0).round(4).tolist(), "binding_hi": np.percentile(bb, 97.5, 0).round(4).tolist()}
        for name in q:
            j = q.index(name)
            cb = np.stack([top1[b, :, j].mean(0) for b in boots])
            r[name] = {"acc": top1[:, :, j].mean(0).round(4).tolist(),
                       "lo": np.percentile(cb, 2.5, 0).round(4).tolist(), "hi": np.percentile(cb, 97.5, 0).round(4).tolist()}
        res[key] = r
    out.write_text(json.dumps(res))
    for key, r in res.items():
        L = r["layers"]
        sel = [l for l in (0, 1, 2, 3, 4, 5, 8, 12) if l in L]
        print(key, "binding(m3-6):", "  ".join(f"L{l} {r['binding'][L.index(l)]:.2f}[{r['binding_lo'][L.index(l)]:.2f},{r['binding_hi'][L.index(l)]:.2f}]" for l in sel))
        print("   split2:", " ".join(f"{r['split2']['acc'][L.index(l)]:.2f}" for l in sel),
              "| split4:", " ".join(f"{r['split4']['acc'][L.index(l)]:.2f}" for l in sel),
              "| last4:", " ".join(f"{r['last4']['acc'][L.index(l)]:.2f}" for l in sel))


if __name__ == "__main__":
    main()
