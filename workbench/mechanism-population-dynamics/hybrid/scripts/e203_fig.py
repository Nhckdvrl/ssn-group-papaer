#!/usr/bin/env python3
"""E203 figure: word assembly (split - last-piece floor, m = 2..5 mean) by layer in the fla-hub 1.3B/100B zoo."""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open(sys.argv[1]))
def delta(r):
    L = r["layers"]
    return L, [sum(r[f"split{m}"]["acc"][i] - r[f"last{m}"]["acc"][i] for m in (2, 3, 4, 5)) / 4 for i in range(len(L))]
style = {"TF": ("#222222", "-", "Transformer"), "DN": ("#c0392b", "-", "DeltaNet (short conv)"),
         "DN_noconv_all": ("#c0392b", ":", "DeltaNet, conv off in all layers"), "DN_noconv": ("#e6a5a0", "--", "DeltaNet, conv off in layers 0-2"),
         "GLA": ("#2c6fbb", "-", "GLA (no conv)"), "GSA": ("#16a085", "-", "GSA (no conv)"), "HGRN": ("#8e44ad", "-", "HGRN (no conv)"),
         "RET": ("#d68910", "-", "RetNet (no conv)")}
fig, ax = plt.subplots(figsize=(8.4, 4.6))
for k, (c, ls, lab) in style.items():
    L, y = delta(d[k])
    ax.plot(L, y, color=c, ls=ls, lw=2, label=lab)
ax.axhline(0, color="grey", lw=.7)
ax.set_xlabel("layer (-1 = embedding)"); ax.set_ylabel("word assembly: split minus last-piece floor (m = 2-5)")
ax.set_title("Same data and recipe (fla-hub, 1.3B, 100B tokens): without a short conv, every recurrent memory\nlearns to assemble words; the conv-trained model needs its conv (memory intact, assembly gone)", fontsize=9.5)
ax.legend(fontsize=8, ncol=2, loc="upper left")
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=140); print("ok")
