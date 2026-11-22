#!/usr/bin/env python3
"""E194 figures from summary.json. Usage: e194_plot.py RESULT_DIR"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = Path(sys.argv[1])
S = json.loads((d / "summary.json").read_text())
R1, R2, R3 = S["R1"], S["R2"], S["R3"]
L = R1["layers"]
col = {"H": "#c0392b", "T": "#2c6fbb", "H0": "#e6a5a0", "T0": "#9fbde0"}
MS = [2, 3, 4, 5, 6]

fig, axes = plt.subplots(2, 5, figsize=(17, 6.4), sharex=True)
for j, m in enumerate(MS):
    ax = axes[0, j]
    for key in ["H0", "T0", "H", "T"]:
        c = R1["curves"][key][f"split{m}"]
        ax.plot(L, c["acc"], color=col[key], lw=2 if len(key) == 1 else 1, label=key)
        ax.fill_between(L, c["lo"], c["hi"], color=col[key], alpha=.15, lw=0)
    for key in ["H", "T"]:
        c = R1["curves"][key][f"last{m}"]
        ax.plot(L, c["acc"], color=col[key], lw=1, ls=":")
    ax.axvline(2.5, color="k", lw=.8, ls="--")
    ax.axhline(R1["chance"], color="grey", lw=.6)
    ax.set_title(f"R1 split into m={m} (dotted: last piece only)", fontsize=9)
    ax.set_ylim(0, 1.02)
    ax.set_xlim(-1.5, 31.5)
    if j == 0:
        ax.legend(fontsize=7, loc="lower right"); ax.set_ylabel("top-1 own word among 32")
    ax = axes[1, j]
    for key in ["H", "T"]:
        if m >= 3:
            b = R1["binding"][f"{key}/m{m}"]
            ax.plot(L, b["diff"], color=col[key], lw=1.5, label=f"{key} binding (split - shuffled prefix)")
            ax.fill_between(L, b["lo"], b["hi"], color=col[key], alpha=.15, lw=0)
        if key in R2 and f"S/m{m}" in R2[key]["by"]:
            r = R2[key]["by"][f"S/m{m}"]
            ax.plot(R2[key]["layers"], r["acc"], color=col[key], lw=1.5, ls="--", marker="o", ms=2.5, label=f"{key} R2 Patchscopes")
    ax.axvline(2.5, color="k", lw=.8, ls="--"); ax.axhline(0, color="grey", lw=.6)
    ax.set_xlabel("decoder layer (-1 = embedding); dashed line: first full attention")
    if j == 0:
        ax.legend(fontsize=6.5, loc="upper right")
fig.suptitle("E194  OLMo-Hybrid-7B (H: GDN x3 + attention) vs OLMo-3-7B (T: attention every layer), end of pretraining; H0/T0 = step 0", fontsize=10)
fig.tight_layout()
fig.savefig(d / "fig_r1_r2.png", dpi=130)

fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
for j, st in enumerate(["2", "3", "4+"]):
    ax = axes[j]
    for key in ["H0", "T0", "H", "T"]:
        if key in R3 and f"{st}/last" in R3[key]:
            ax.plot(L, R3[key][f"{st}/last"]["acc"], color=col[key], lw=2 if len(key) == 1 else 1, label=f"{key} last")
        if key in ("H", "T") and key in R3 and f"{st}/penult" in R3[key]:
            ax.plot(L, R3[key][f"{st}/penult"]["acc"], color=col[key], lw=1, ls=":", label=f"{key} penult")
    for key in ["H", "T"]:
        if key in R2 and f"N/{st}" in R2[key]["by"]:
            r = R2[key]["by"][f"N/{st}"]
            ax.plot(R2[key]["layers"], r["acc"], color=col[key], ls="--", marker="o", ms=2.5, lw=1.2, label=f"{key} R2")
    ax.axvline(2.5, color="k", lw=.8, ls="--"); ax.axhline(.5, color="grey", lw=.6)
    ax.set_title(f"natural words, m={st}: R3 word vs nonword (kNN), R2", fontsize=9)
    ax.set_xlabel("decoder layer")
    if j == 0:
        ax.legend(fontsize=6.5)
fig.tight_layout()
fig.savefig(d / "fig_r3_natural.png", dpi=130)
print("ok")
