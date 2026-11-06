#!/usr/bin/env python3
"""E173 add-on (11-06, main session): exact-rerun ceilings side by side at 0 / 1e8 / 2e8 / 4e8 / 8e8.
Pairs: (I0D0, I0D0R) [both RTX, stopped at 4e8], (I4D0, I4D0R) [both A100, E171], and (I0D0, BASE_I0)
[I0D0 on RTX, BASE_I0 on A100: same config, different GPU model; added 11-06 11:00], and (11-06 20:40, E173 run 2)
(G16_I0, G16_I0R) [A100 80GB PCIe fvcrc15:3 / fvcrc11:0], (G256_I0, G256_I0R) [both fvcrc11:1]; each pair appears at every token
count where both captures exist (G256 lands when G256_I0R's captures do). 11-06 21:40 (run 3): (G64K2_I0, G64K2_I0R) [fvcrc11:0 / fvcrc11:3],
the 64-expert top-2 single-variable control. Readouts unchanged:
T_D per layer (analyze_routing.py) -> L11, deep L6-11 mean; route fingerprint (analyze_functional.py route) -> deep matched.
Writes results/e173/rerun_ceiling.{json,md}. Usage: e173_rerun_ceiling.py
"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
S = WB / "scripts"
A = Path.home() / "mechpop_cache/e173_analysis"  # holds BASE_I0 plus links to the E167 caches
PY = str(Path.home() / ".venvs/mechpop/bin/python")
OUT = WB / "results/e173"
TOKS = [0, 100000000, 200000000, 400000000, 800000000]
PAIRS = {"I0D0-I0D0R": ("I0D0", "I0D0R"), "I4D0-I4D0R": ("I4D0", "I4D0R"), "I0D0-BASE_I0": ("I0D0", "BASE_I0"),
         "G16_I0-G16_I0R": ("G16_I0", "G16_I0R"), "G256_I0-G256_I0R": ("G256_I0", "G256_I0R"),
         "G64K2_I0-G64K2_I0R": ("G64K2_I0", "G64K2_I0R")}  # 11-06 21:40 run 3: single-variable control (64 experts top-2)
HW = {"I0D0-I0D0R": "RTX / RTX", "I4D0-I4D0R": "A100 / A100", "I0D0-BASE_I0": "RTX / A100",
      "G16_I0-G16_I0R": "A100 / A100，fvcrc15 / fvcrc11", "G256_I0-G256_I0R": "A100 / A100，同卡 fvcrc11:1",
      "G64K2_I0-G64K2_I0R": "A100 / A100，fvcrc11:0 / fvcrc11:3"}

_f = lambda d, r, t: A / d / f"{r}__ckpt_{t}.npz"
have = lambda d, r, t: _f(d, r, t).exists() and _f(d, r, t).stat().st_size > 0  # skip captures still being written
specs = [f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz" for a, b in PAIRS.values() for t in TOKS if have("routing", a, t) and have("routing", b, t)]
subprocess.run([PY, "-B", str(S / "analyze_routing.py"), str(A / "routing"), str(OUT / "rerun_ceiling_routing.json")] + specs,
               check=True, env=dict(os.environ, E167_NPERM="0"), stdout=subprocess.DEVNULL)
R = {(r["A"].split("__")[0], r["B"].split("__")[0], r["tokens_A"]): r for r in json.loads((OUT / "rerun_ceiling_routing.json").read_text())["results"]}
fspecs = [f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz" for a, b in PAIRS.values() for t in TOKS
          if have("functional", a, t) and have("functional", b, t)]
F = {}
if fspecs:
    subprocess.run([PY, "-B", str(S / "analyze_functional.py"), "route", str(A / "functional"), str(OUT / "rerun_ceiling_route.json")] + fspecs,
                   check=True, stdout=subprocess.DEVNULL)
    F = {(r["A"].split("__")[0], r["B"].split("__")[0], r["tokens_A"]): r for r in json.loads((OUT / "rerun_ceiling_route.json").read_text())["results"]}
out = {}
for name, (a, b) in PAIRS.items():
    for t in TOKS:
        if (a, b, t) not in R:
            continue
        r = R[(a, b, t)]["layers"]
        f = F.get((a, b, t))
        out.setdefault(name, {})[t] = {"L11": r[11]["T_D"], "L11_ci": r[11]["T_D_ci"], "deep": float(np.mean([r[l]["T_D"] for l in range(6, 12)])),
                                       "route_deep": float(np.mean([l["matched"] for l in f["layers"][6:]])) if f else None}
(OUT / "rerun_ceiling.json").write_text(json.dumps(out, indent=1))
f3 = lambda x: "—" if x is None else f"{x:.3f}"
names = list(PAIRS)
lines = ["| token | " + " | ".join(f"{n}（{HW[n]}）L11 / 深层 / route" for n in names) + " | 差（I0D0–BASE_I0 − I4D0–I4D0R）L11 / 深层 / route |",
         "|---|" + "---|" * (len(names) + 1)]
for t in TOKS:
    cells = []
    for n in names:
        v = out.get(n, {}).get(t)
        cells.append("—" if v is None else f"{f3(v['L11'])} / {f3(v['deep'])} / {f3(v['route_deep'])}")
    p, q = out.get("I0D0-BASE_I0", {}).get(t), out.get("I4D0-I4D0R", {}).get(t)
    d = "—" if p is None or q is None else " / ".join(("—" if p[k] is None or q[k] is None else f"{p[k] - q[k]:+.3f}") for k in ("L11", "deep", "route_deep"))
    lines.append(f"| {t/1e8:g}e8 | " + " | ".join(cells) + f" | {d} |")
(OUT / "rerun_ceiling.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
