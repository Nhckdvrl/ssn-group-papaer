#!/usr/bin/env python3
"""E175 POST-HOC A + B (2026-11-06) summary json + figure (x = layer).
Left: B natural word stream (hidden cache, all 112k words): G(input), G(true next) at endpoint, 3 seeds (band),
      untrained (dotted), and the E175 anchor-sample endpoint values (thin dashed) for comparison.
Right: A predicted next token (CPU forward): G(input), G(true next), G(predicted next) at endpoint / 800M / 200M.
Conditionals derived from the joint: G(y|z)* = G(y) + G(z|y) - G(z) where G(z|y) backs off to y's table
(the better-estimated direction, as in E175 crossfit); reported alongside.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]
RES = WB / "results/e175"
SEEDS = ["I0D0", "I1D0", "I2D0"]
NL = 12
END = "3999793152"
B = json.loads((RES / "posthoc_B.json").read_text())
Apath = RES / "posthoc_A.json"
A = json.loads(Apath.read_text()) if Apath.exists() else None
CF = {r: json.loads((RES / f"crossfit_{r}.json").read_text())["ckpts"] for r in SEEDS}


def stat(v):
    v = np.asarray(v)
    return {"mean": round(float(v.mean()), 4), "min": round(float(v.min()), 4), "max": round(float(v.max()), 4)}


def layers(src, name, key):
    return [src["ckpts"][name]["layers"][l][key] for l in range(NL)]


summ = {"note": "POST-HOC 2026-11-06 (added after seeing E175 results); bits; cross-fitted G as in E175 crossfit",
        "B": {"n_words": B["n_words"], "layers": {}}, "A": None}
for l in range(NL):
    d = {}
    for k in ["G_in_tok", "G_next_tok", "G_next_tok|in_tok"]:
        d[k] = stat([B["ckpts"][f"{r}__ckpt_{END}"]["layers"][l][k] for r in SEEDS])
    d["ratio_next_in"] = stat([B["ckpts"][f"{r}__ckpt_{END}"]["layers"][l]["G_next_tok"] / B["ckpts"][f"{r}__ckpt_{END}"]["layers"][l]["G_in_tok"] for r in SEEDS])
    d["anchor_sample_ratio"] = stat([CF[r][END][l]["G_next_tok"] / CF[r][END][l]["G_in_tok"] for r in SEEDS])
    d["untrained"] = {r: {k: round(B["ckpts"][f"{r}__ckpt_0"]["layers"][l][k], 4) for k in ["G_in_tok", "G_next_tok"]} for r in ["I0D0", "I1D0"]}
    d["rerun_3.2B_ratio"] = {r: round(B["ckpts"][f"{r}__ckpt_3200000000"]["layers"][l]["G_next_tok"] / B["ckpts"][f"{r}__ckpt_3200000000"]["layers"][l]["G_in_tok"], 4) for r in ["I4D0", "I4D0R"]}
    summ["B"]["layers"][l] = d
summ["B"]["routing_cache_top1_agreement_I0D0_end"] = B["ckpts"][f"I0D0__ckpt_{END}"].get("top1_agree_with_routing_cache")

if A:
    cks = sorted({k.split("__ckpt_")[1] for k in A["ckpts"]}, key=int)
    summ["A"] = {"n_words": A["n_words"], "ckpts": {}}
    for t in cks:
        names = [f"{r}__ckpt_{t}" for r in SEEDS if f"{r}__ckpt_{t}" in A["ckpts"]]
        T = {"runs": names, "top1_pred_acc": stat([A["ckpts"][n]["top1_pred_acc"] for n in names]), "layers": {}}
        for l in range(NL):
            row = {}
            for k in ["G_in_tok", "G_next_tok", "G_pred_tok", "G_next_tok|in_tok", "G_pred_tok|in_tok",
                      "G_pred_tok|next_tok", "G_next_tok|pred_tok"]:
                row[k] = stat([A["ckpts"][n]["layers"][l][k] for n in names])
            row["ratio_pred_in"] = stat([A["ckpts"][n]["layers"][l]["G_pred_tok"] / A["ckpts"][n]["layers"][l]["G_in_tok"] for n in names])
            row["ratio_next_in"] = stat([A["ckpts"][n]["layers"][l]["G_next_tok"] / A["ckpts"][n]["layers"][l]["G_in_tok"] for n in names])
            T["layers"][l] = row
        summ["A"]["ckpts"][t] = T
(RES / "e175_posthoc_summary.json").write_text(json.dumps(summ, indent=1))

C_IN, C_NX, C_PR = "#1f5fa8", "#c4452b", "#7b3fa0"
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
x = np.arange(NL)
ax = axs[0]
for k, c, lab in [("G_in_tok", C_IN, "input token"), ("G_next_tok", C_NX, "true next token")]:
    v = np.array([[B["ckpts"][f"{r}__ckpt_{END}"]["layers"][l][k] for l in range(NL)] for r in SEEDS])
    ax.fill_between(x, v.min(0), v.max(0), color=c, alpha=.25, lw=0)
    ax.plot(x, v.mean(0), color=c, lw=2, marker="o", ms=3, label=f"{lab} (all 112k words)")
    u = np.array([[B["ckpts"][f"{r}__ckpt_0"]["layers"][l][k] for l in range(NL)] for r in ["I0D0", "I1D0"]])
    ax.plot(x, u.mean(0), color=c, lw=1, ls=":", label=f"{lab}, untrained")
    a = np.array([[CF[r][END][l][k] for l in range(NL)] for r in SEEDS])
    ax.plot(x, a.mean(0), color=c, lw=1, ls="--", label=f"{lab}, E175 anchor sample")
ax.axhline(0, color="k", lw=.5)
ax.set_title("B: natural word stream vs E175 anchor sample (endpoint, 3 seeds)", fontsize=10)
ax.set_xlabel("layer"); ax.set_ylabel("held-out info about top-1 expert (bits)"); ax.legend(fontsize=7)
ax.grid(alpha=.3, lw=.5)
ax = axs[1]
if A:
    for t, ls, alpha in [(END, "-", 1.0), ("800000000", "--", .8), ("200000000", ":", .8)]:
        names = [f"{r}__ckpt_{t}" for r in SEEDS if f"{r}__ckpt_{t}" in A["ckpts"]]
        if not names:
            continue
        for k, c, lab in [("G_in_tok", C_IN, "input"), ("G_next_tok", C_NX, "true next"), ("G_pred_tok", C_PR, "predicted next")]:
            v = np.array([[A["ckpts"][n]["layers"][l][k] for l in range(NL)] for n in names])
            if t == END:
                ax.fill_between(x, v.min(0), v.max(0), color=c, alpha=.22, lw=0)
            tl = {END: "end", "800000000": "800M", "200000000": "200M"}[t]
            ax.plot(x, v.mean(0), color=c, lw=1.8 if t == END else 1.1, ls=ls, alpha=alpha, label=f"{lab} ({tl})")
    ax.set_title("A: predicted vs true next token (CPU fwd, 200 anchor passages, endpoint)", fontsize=10)
    ax.legend(fontsize=6.5, ncol=3, loc="upper right")
else:
    ax.text(.5, .5, "A (predicted next token) not run:\nCPU forward estimate > 2 h per checkpoint\n(stopped per request)",
            ha="center", va="center", transform=ax.transAxes, fontsize=9)
    ax.set_title("A: predicted next token", fontsize=10)
ax.axhline(0, color="k", lw=.5); ax.set_xlabel("layer"); ax.grid(alpha=.3, lw=.5)
fig.suptitle("E175 POST-HOC (2026-11-06): band = range over init seeds I0D0/I1D0/I2D0", fontsize=10)
fig.tight_layout()
fig.savefig(RES / "e175_posthoc_AB.png", dpi=150)
fig.savefig(RES / "e175_posthoc_AB.pdf")
print("ok")
