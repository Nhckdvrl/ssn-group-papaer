#!/usr/bin/env python3
"""E174 figure: granularity ladder, raw vs null-subtracted excess, for rerun / order / init pairs.

POS level  : route fingerprint (P(expert|UPOS)); excess = real - real A vs N1(B). rerun at 3.2B, order/init at final (no 3.2B hidden cache).
T_D level  : same-type context partition; excess = real - U-pool (type x UPOS) permutation null; 3.2B.
token level: per-token causal-role matched corr; excess = real - LU-pool (token id x UPOS) permutation null; 3.2B.
Deep layers L6-11. Error bars on init = min-max across pairs.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = Path(__file__).resolve().parents[1] / "results/e174"
G = ("rerun", "order", "init")
data = {}

# POS level
c = json.loads((R / "coarse_null.json").read_text())["results"]
cp = {}
for r in c:
    real = np.mean([x["real"] for x in r["layers"]]); nb = np.mean([x["nullB_mean"] for x in r["layers"]])
    a, b = r["A"].split("@")[0], r["B"].split("@")[0]
    g = "floor" if r["A"].endswith("@0") else "rerun" if b == a + "R" else "order" if a[:2] == b[:2] else "init"
    cp.setdefault(g, []).append((real, real - nb))
data["词类级 route 指纹\n(扣 N1；重跑 3.2B，其余终点)"] = cp

# T_D level
t = json.loads((R / "td_null_3200000000.json").read_text())["results"]
tp = {}
for r in t:
    x = r["pools"]["U_all"]["deep"]
    tp.setdefault(r["group"], []).append((x["real"], x["excess"]))
data["同词形分区 T_D\n(扣 词形×UPOS 格内置换；3.2B)"] = tp

# token level
k = json.loads((R / "token_null_3200000000.json").read_text())["results"]
kp = {}
for r in k:
    L = [x for x in r["layers"] if x["layer"] >= 6]
    real = np.mean([x["real"] for x in L]); ex = np.mean([x["pools"]["LU"]["excess"] for x in L])
    a, b = r["A"], r["B"]
    g = "rerun" if b == a + "R" else "order" if a[:2] == b[:2] else "init"
    kp.setdefault(g, []).append((real, ex))
data["逐 token 因果角色\n(扣 token id×UPOS 格内置换；3.2B)"] = kp

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
ladder = {"raw": [], "excess": []}
for ax, (title, d) in zip(axes, data.items()):
    xs = np.arange(3)
    for j, (key, col, lab) in enumerate(((0, "#9aa5b1", "原始值"), (1, "#2b6cb0", "扣零假设后的超出"))):
        m = [np.mean([v[key] for v in d[g]]) for g in G]
        lo = [m[i] - min(v[key] for v in d[g]) for i, g in enumerate(G)]
        hi = [max(v[key] for v in d[g]) - m[i] for i, g in enumerate(G)]
        ax.bar(xs + (j - .5) * .38, m, .36, color=col, label=lab, yerr=[lo, hi], capsize=3)
        for i in range(3):
            ax.text(xs[i] + (j - .5) * .38, m[i] + .015, f"{m[i]:.2f}", ha="center", fontsize=8)
        ladder["raw" if key == 0 else "excess"].append(m[2] / m[0])
    ax.set_xticks(xs, ["重跑", "只换顺序", "只换初始化"])
    ax.set_title(title, fontsize=10)
axes[0].set_ylabel("一致度（深层 L6–11 均值）")
axes[2].legend(fontsize=8, loc="upper right")
names = ["词类级", "同词形分区", "逐 token"]
txt = "初始化÷重跑　原始： " + " → ".join(f"{n} {v:.2f}" for n, v in zip(names, ladder["raw"])) + \
      "\n初始化÷重跑　扣除后： " + " → ".join(f"{n} {v:.2f}" for n, v in zip(names, ladder["excess"]))
fig.text(0.5, 0.01, txt, ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(R / "e174_ladder.png", dpi=150)
json.dump(ladder, open(R / "ladder.json", "w"), indent=1)
print(ladder)
