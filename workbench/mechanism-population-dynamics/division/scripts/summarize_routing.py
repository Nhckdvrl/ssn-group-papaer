#!/usr/bin/env python3
"""E167: run analyze_routing on the pre-registered pair groups at one token count and print a per-layer table.

Groups: init (only init differs, D0: I0..I5), order (same init, D0 vs D1), both (init and order differ),
floor (two different inits at token 0). Usage: summarize_routing.py TOKENS [--perm]
"""
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

CAP = Path("/home/xiang/mechpop_cache/e167_analysis/routing")
OUT = Path(__file__).resolve().parents[1] / "results/e167"
tok = int(float(sys.argv[1]))
have = lambda r, t: (CAP / f"{r}__ckpt_{t}.npz").exists()
d0 = [f"I{i}D0" for i in range(6) if have(f"I{i}D0", tok)]
groups = {"init": list(itertools.combinations(d0, 2)),
          "order": [(f"I{i}D0", f"I{i}D1") for i in (0, 1) if have(f"I{i}D0", tok) and have(f"I{i}D1", tok)],
          "both": [(a, b) for a, b in (("I0D1", "I1D0"), ("I1D1", "I0D0")) if have(a, tok) and have(b, tok)]}
specs = [f"{a}__ckpt_{tok}.npz:{b}__ckpt_{tok}.npz" for g in groups.values() for a, b in g]
if have("I0D0", 0) and have("I1D0", 0):
    specs.append("I0D0__ckpt_0.npz:I1D0__ckpt_0.npz")
OUT.mkdir(parents=True, exist_ok=True)
out = OUT / f"routing_{tok}.json"
env = dict(os.environ, E167_NPERM="100" if "--perm" in sys.argv else "0")
subprocess.run([sys.executable, "-B", str(Path(__file__).parent / "analyze_routing.py"), str(CAP), str(out)] + specs, check=True, env=env)
R = json.loads(out.read_text())["results"]
lookup = {(r["A"].split("__")[0], r["B"].split("__")[0], r["tokens_A"]): r for r in R}
summary = {}
for g, pairs in list(groups.items()) + [("floor_t0", [("I0D0", "I1D0")])]:
    t = 0 if g == "floor_t0" else tok
    rows = [lookup[(a, b, t)] for a, b in pairs if (a, b, t) in lookup]
    if not rows:
        continue
    L = len(rows[0]["layers"])
    summary[g] = {m: [float(np.mean([r["layers"][l][m] for r in rows])) for l in range(L)] for m in ("T_ctx", "T_D", "T_h", "T_lex")}
    summary[g]["n_pairs"] = len(rows)
(OUT / f"routing_summary_{tok}.json").write_text(json.dumps(summary, indent=1))
for g, v in summary.items():
    print(f"{g:9s} n={v['n_pairs']:2d}  T_D " + " ".join(f"{x:.3f}" for x in v["T_D"]))
    print(f"{'':9s}       T_ctx " + " ".join(f"{x:.3f}" for x in v["T_ctx"]))
    print(f"{'':9s}       T_h " + " ".join(f"{x:.3f}" for x in v["T_h"]))
