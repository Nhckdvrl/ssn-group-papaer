#!/usr/bin/env python3
"""Key figure: word assembly (R1, split into m pieces) in three hybrids under conv / memory switches in the
recurrent layers before the first attention layer. Usage: e198_fig.py RESULTS_DIR OUT_PNG"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(sys.argv[1])
models = [("OLMo-Hybrid-7B (GDN, attn at 3)", R / "e196/r1_all_conditions.json", 3),
          ("Granite-4.0-H-Micro (Mamba-2, attn at 5)", R / "e198/r1_granite_h.json", 5),
          ("Qwen3.5-4B-Base (GDN, attn at 3)", R / "e198/r1_qwen35.json", 3)]
conds = [("none", "intact", "#222222", "-"), ("nomem", "memory off (conv only)", "#2c6fbb", "-"),
         ("noconv", "conv off (memory only)", "#c0392b", "-"), ("none_mix", "both off", "#e6a5a0", "--")]
fig, axes = plt.subplots(2, 3, figsize=(14, 6.6), sharey=True)
for j, (title, path, a) in enumerate(models):
    d = json.loads(path.read_text())
    L = d["none"]["layers"]
    keep = [i for i, l in enumerate(L) if l <= 12]
    xs = [L[i] for i in keep]
    for r, m in enumerate([2, 5]):
        ax = axes[r, j]
        for key, lab, col, ls in conds:
            c = d[key][f"split{m}"]
            ax.plot(xs, [c["acc"][i] for i in keep], color=col, ls=ls, lw=2, label=lab)
            ax.fill_between(xs, [c["lo"][i] for i in keep], [c["hi"][i] for i in keep], color=col, alpha=.12, lw=0)
        ax.plot(xs, [d["none"][f"last{m}"]["acc"][i] for i in keep], color="grey", ls=":", lw=1.5, label="last piece only")
        ax.axvspan(-1.5, a - 0.5, color="#f3e9d2", alpha=.6, lw=0)
        ax.axvline(a, color="k", lw=.8, ls="--")
        ax.set_ylim(0, 1.03); ax.set_xlim(-1.2, 12.2)
        if r == 0:
            ax.set_title(title, fontsize=10)
        if j == 0:
            ax.set_ylabel(f"word split into {m} pieces\nrecognised as the word (top-1 of 32)")
        if r == 1:
            ax.set_xlabel("layer (-1 = embedding)")
axes[0, 0].legend(fontsize=7.5, loc="lower right")
fig.suptitle("Word assembly needs the short convolution of the recurrent layers before the first attention layer (shaded = switched layers, dashed = first attention).\nWith the convolution off, 5-piece words are never assembled later; 2-piece words recover only partly.", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[2], dpi=140)
print("ok")
