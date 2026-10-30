#!/usr/bin/env python3
"""E167: run analyze_functional for one fingerprint kind at one token count over the pre-registered groups.

Usage: summarize_functional.py KIND TOKENS     (KIND: drop | route | habl)
"""
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

kind, tok = sys.argv[1], int(float(sys.argv[2]))
D = Path("/home/xiang/mechpop_cache/e167_analysis") / ("heads" if kind == "habl" else "functional")
OUT = Path(__file__).resolve().parents[1] / "results/e167"


def ok(r):
    f = D / f"{r}__ckpt_{tok}.npz"
    if not f.exists():
        return False
    return kind != "drop" or "drop_fp" in np.load(f).files


d0 = [f"I{i}D0" for i in range(6) if ok(f"I{i}D0")]
groups = {"init": list(itertools.combinations(d0, 2)),
          "order": [(f"I{i}D0", f"I{i}D1") for i in (0, 1) if ok(f"I{i}D0") and ok(f"I{i}D1")],
          "both": [(a, b) for a, b in (("I0D1", "I1D0"), ("I1D1", "I0D0")) if ok(a) and ok(b)]}
specs = [f"{a}__ckpt_{tok}.npz:{b}__ckpt_{tok}.npz" for g in groups.values() for a, b in g]
out = OUT / f"functional_{kind}_{tok}.json"
subprocess.run([sys.executable, "-B", str(Path(__file__).parent / "analyze_functional.py"), kind, str(D), str(out)] + specs, check=True)
R = {(r["A"].split("__")[0], r["B"].split("__")[0]): r for r in json.loads(out.read_text())["results"]}
summ = {}
for g, pairs in groups.items():
    rows = [R[p] for p in pairs if p in R]
    if rows:
        L = len(rows[0]["layers"])
        summ[g] = {m: [float(np.mean([r["layers"][l][m] for r in rows])) for l in range(L)] for m in ("matched", "ratio", "reliab_A")}
        summ[g]["random_hi"] = [float(np.mean([r["layers"][l]["random95"][1] for r in rows])) for l in range(L)]
        summ[g]["n_pairs"] = len(rows)
(OUT / f"functional_{kind}_summary_{tok}.json").write_text(json.dumps(summ, indent=1))
for g, v in summ.items():
    print(f"{g:6s} n={v['n_pairs']:2d} matched " + " ".join(f"{x:.3f}" for x in v["matched"]))
    print(f"{'':12s}ratio   " + " ".join(f"{x:.3f}" for x in v["ratio"]))
    print(f"{'':12s}rand95hi " + " ".join(f"{x:.3f}" for x in v["random_hi"]))
