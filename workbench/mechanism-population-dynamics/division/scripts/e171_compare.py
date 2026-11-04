#!/usr/bin/env python3
"""E171 comparisons: the exact-rerun pair (I0D0, I0D0R) against only-order (I0D0, I0D1) and only-init
(I0D0, I1D0) pairs, on every E167 / E168 readout, from the analysis caches. Writes results/e171/*.json and
prints the tables. Re-uses analyze_routing.py, analyze_functional.py and token_roles.py compare unchanged.

Usage: e171_compare.py [RUN BASE END [routing_only]]   (default I4D0R I4D0 3200000000; 11-04 generalised)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
S = WB / "scripts"
A = Path.home() / "mechpop_cache/e167_analysis"
PY = str(Path.home() / ".venvs/mechpop/bin/python")
OUT = WB / "results/e171"
OUT.mkdir(parents=True, exist_ok=True)
RUN = sys.argv[1] if len(sys.argv) > 1 else "I4D0R"
BASE = sys.argv[2] if len(sys.argv) > 2 else "I4D0"
END = int(sys.argv[3]) if len(sys.argv) > 3 else 3200000000
ROUTING_ONLY = len(sys.argv) > 4 and sys.argv[4] == "routing_only"
TOKS = [25000000, 50000000, 100000000, 200000000, 400000000, 800000000, 1600000000, 3200000000, 3999793152]
# rerun pair, the two only-order pairs, the only-init pairs that share BASE, and the rerun model against another init
PAIRS = {"rerun": (BASE, RUN), "order": ("I0D0", "I0D1"), "order2": ("I1D0", "I1D1"), "init": (BASE, "I0D0"), "init2": (BASE, "I1D0"),
         "init_R": (RUN, "I0D0"), "init_R2": (RUN, "I1D0")}
if BASE == "I0D0":
    PAIRS["init"] = ("I0D0", "I1D0"); PAIRS["init2"] = ("I0D0", "I4D0"); PAIRS["init_R"] = (RUN, "I1D0"); PAIRS["init_R2"] = (RUN, "I4D0")


def have(d, r, t):
    return (A / d / f"{r}__ckpt_{t}.npz").exists()


# ---- routing (T_ctx, T_D, T_h, T_lex) at every checkpoint where both captures exist
specs, idx = [], []
for t in TOKS:
    for name, (a, b) in PAIRS.items():
        if have("routing", a, t) and have("routing", b, t):
            specs.append(f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz"); idx.append((name, t))
env = dict(os.environ, E167_NPERM="0")
subprocess.run([PY, "-B", str(S / "analyze_routing.py"), str(A / "routing"), str(OUT / "routing.json")] + specs, check=True, env=env,
               stdout=subprocess.DEVNULL)
R = json.loads((OUT / "routing.json").read_text())["results"]
print("ROUTING  T_D by layer (L0..L11); last columns: L11 T_ctx, T_h")
for (name, t), r in zip(idx, R):
    L = r["layers"]
    print(f"{name:8s} {t:>11d} " + " ".join(f"{l['T_D']:.3f}" for l in L) + f" | {L[11]['T_ctx']:.3f} {L[11]['T_h']:.3f}")
# ratios at the endpoint and 3.2B
for t in sorted({END, 3200000000, 3999793152}):
    d = {name: r for (name, tt), r in zip(idx, R) if tt == t}
    if "rerun" in d and "order" in d and "init" in d:
        deep = lambda n: np.mean([d[n]["layers"][l]["T_D"] for l in range(6, 12)])
        print(f"\n{t}: deep T_D rerun {deep('rerun'):.3f} | order {deep('order'):.3f} | init {deep('init'):.3f} -> init/rerun {deep('init')/deep('rerun'):.2f}, order/rerun {deep('order')/deep('rerun'):.2f}, init/order {deep('init')/deep('order'):.2f}"
              + "".join(f" | {n} {deep(n):.3f}" for n in ("order2", "init2", "init_R", "init_R2") if n in d))

if ROUTING_ONLY:
    print("\nsaved to", OUT); sys.exit(0)
# ---- functional fingerprints at the endpoint
t = END
for kind in ("route", "drop"):
    specs2, idx2 = [], []
    for name, (a, b) in PAIRS.items():
        if have("functional", a, t) and have("functional", b, t) and (kind == "route" or all(
                "drop_fp" in np.load(A / "functional" / f"{r}__ckpt_{t}.npz").files for r in (a, b))):
            specs2.append(f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz"); idx2.append(name)
    if not specs2:
        continue
    subprocess.run([PY, "-B", str(S / "analyze_functional.py"), kind, str(A / "functional"), str(OUT / f"functional_{kind}.json")] + specs2,
                   check=True, stdout=subprocess.DEVNULL)
    F = json.loads((OUT / f"functional_{kind}.json").read_text())["results"]
    print(f"\nFUNCTIONAL {kind}: matched held corr by layer; deep mean")
    for name, r in zip(idx2, F):
        m = [l["matched"] for l in r["layers"]]
        print(f"{name:8s} " + " ".join(f"{x:.2f}" for x in m) + f" | deep {np.mean(m[6:]):.3f}")

# ---- token-level causal roles at the endpoint
specs3, idx3 = [], []
for name, (a, b) in PAIRS.items():
    if have("token_roles", a, t) and have("token_roles", b, t):
        specs3.append(f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz"); idx3.append(name)
if specs3:
    subprocess.run([PY, "-B", str(S / "token_roles.py"), "compare", str(A / "token_roles"), str(OUT / "token_roles.json"), "2,3,6,7,8,9,10,11"] + specs3,
                   check=True, stdout=subprocess.DEVNULL)
    T = json.loads((OUT / "token_roles.json").read_text())["results"]
    print("\nTOKEN ROLES: matched corr by layer (2,3,6..11); deep mean")
    for name, r in zip(idx3, T):
        m = [l["matched"] for l in r["layers"]]
        print(f"{name:8s} " + " ".join(f"{x:.3f}" for x in m) + f" | deep {np.mean(m[2:]):.3f}")

# ---- heads (attention-pattern fingerprints) at 1.6B
t = 1600000000
specs4, idx4 = [], []
for name, (a, b) in PAIRS.items():
    if have("heads_attn", a, t) and have("heads_attn", b, t):
        specs4.append(f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz"); idx4.append(name)
if specs4:
    subprocess.run([PY, "-B", str(S / "analyze_functional.py"), "hattn", str(A / "heads_attn"), str(OUT / "heads_attn.json")] + specs4,
                   check=True, stdout=subprocess.DEVNULL)
    H = json.loads((OUT / "heads_attn.json").read_text())["results"]
    print("\nHEADS attn fingerprints (1.6B): matched by layer")
    for name, r in zip(idx4, H):
        print(f"{name:8s} " + " ".join(f"{l['matched']:.2f}" for l in r["layers"]))
print("\nsaved to", OUT)
