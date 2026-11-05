#!/usr/bin/env python3
"""E175 figure + summary table.
Figure: 12 small panels (one per layer), x = training tokens (log; step 0 drawn at the left edge),
y = excess MI (bits) with top-1 expert; two curves (input token, true next token) with the 3-seed range band
(I0D0, I1D0, I2D0) and the rerun pair I4D0/I4D0R as thin dashed lines; plus conditional dI(e; next | in).
Summary: results/e175/e175_summary.json (per layer x ckpt: 3-seed mean/min/max; crossings per seed).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]
R = json.loads((WB / "results/e175/e175_readouts.json").read_text())
SEEDS = ["I0D0", "I1D0", "I2D0"]
RERUN = ["I4D0", "I4D0R"]
NL = 12
KEYS = ["dI_in_tok", "dI_next_tok", "dcI_next_tok|in_tok", "dcI_in_tok|next_tok", "dI_in_tok^next_tok",
        "dI_in_form", "dI_next_form", "dI_in_upos", "dI_next_upos", "dcI_next_upos|in_upos", "dcI_in_upos|next_upos",
        "dI8_in_tok", "dI8_next_tok", "dIsub_in_tok", "dIsub_next_tok",
        "VS1_in_tok", "VS1_next_tok", "VS1floor_in_tok", "VS1floor_next_tok",
        "VS8_in_tok", "VS8_next_tok", "VS8floor_in_tok", "VS8floor_next_tok", "H_e",
        "floor_in_tok", "floor_next_tok", "I_in_tok", "I_next_tok"]


def series(run, key):
    d = R["runs"][run]
    ts = sorted(int(t) for t in d)
    return np.array(ts), np.array([[d[str(t)][l][key] for l in range(NL)] for t in ts])


ts = series("I0D0", "dI_in_tok")[0]
stack = {k: np.stack([series(r, k)[1] for r in SEEDS]) for k in KEYS}  # (3, T, L)


def crossing(a, b, ts):
    """first checkpoint index from which b >= a holds until the last checkpoint; None if never."""
    ok = b >= a
    for i in range(len(ts)):
        if ok[i:].all():
            return int(ts[i])
    return None


summ = {"tokens": ts.tolist(), "seeds": SEEDS, "layers": {}}
for l in range(NL):
    L = {}
    for k in KEYS:
        v = stack[k][:, :, l]
        L[k] = {"mean": v.mean(0).round(4).tolist(), "min": v.min(0).round(4).tolist(), "max": v.max(0).round(4).tolist()}
    L["crossing_next_ge_in_tok"] = {r: crossing(stack["dI_in_tok"][i, :, l], stack["dI_next_tok"][i, :, l], ts) for i, r in enumerate(SEEDS)}
    L["crossing_next_ge_in_form"] = {r: crossing(stack["dI_in_form"][i, :, l], stack["dI_next_form"][i, :, l], ts) for i, r in enumerate(SEEDS)}
    L["crossing_next_ge_in_upos"] = {r: crossing(stack["dI_in_upos"][i, :, l], stack["dI_next_upos"][i, :, l], ts) for i, r in enumerate(SEEDS)}
    L["crossing_next_ge_in_freqsub"] = {r: crossing(stack["dIsub_in_tok"][i, :, l], stack["dIsub_next_tok"][i, :, l], ts) for i, r in enumerate(SEEDS)}
    rr = {}
    for r in RERUN:
        t2, a = series(r, "dI_in_tok"); _, b = series(r, "dI_next_tok"); _, c = series(r, "dcI_next_tok|in_tok")
        rr[r] = {"tokens": t2.tolist(), "dI_in_tok": a[:, l].round(4).tolist(), "dI_next_tok": b[:, l].round(4).tolist(),
                 "dcI_next|in": c[:, l].round(4).tolist()}
    L["rerun"] = rr
    summ["layers"][l] = L
(WB / "results/e175/e175_summary.json").write_text(json.dumps(summ, indent=1))

# ---- figure
x = np.where(ts == 0, 1e7, ts).astype(float)
fig, axs = plt.subplots(3, 4, figsize=(13, 8.2), sharex=True)
C_IN, C_NX, C_C = "#1f5fa8", "#c4452b", "#6b6b6b"
for l in range(NL):
    ax = axs.flat[l]
    for k, c, lab in [("dI_in_tok", C_IN, "input token"), ("dI_next_tok", C_NX, "true next token"),
                      ("dcI_next_tok|in_tok", C_C, "next | input (conditional)")]:
        v = stack[k][:, :, l]
        ax.fill_between(x, v.min(0), v.max(0), color=c, alpha=.25, lw=0)
        ax.plot(x, v.mean(0), color=c, lw=1.8, label=lab, ls=":" if "dcI" in k else "-")
    for r in RERUN:
        t2, a = series(r, "dI_in_tok"); _, b = series(r, "dI_next_tok")
        x2 = np.where(t2 == 0, 1e7, t2).astype(float)
        ax.plot(x2, a[:, l], color=C_IN, lw=.7, ls="--", alpha=.8)
        ax.plot(x2, b[:, l], color=C_NX, lw=.7, ls="--", alpha=.8)
    ax.axvspan(1e7, 5.24e8, color="#eeeeee", zorder=0)
    ax.set_xscale("log")
    ax.set_title(f"layer {l}", fontsize=10)
    ax.grid(alpha=.3, lw=.5)
    if l % 4 == 0:
        ax.set_ylabel("excess MI (bits)")
    if l >= 8:
        ax.set_xlabel("training tokens (step 0 at left edge)")
axs.flat[0].legend(fontsize=7.5, loc="upper left")
fig.suptitle("E175: routing predictability from input token vs true next token (3 init seeds, band = range; "
             "dashed = rerun pair I4D0/I4D0R; grey = warmup)", fontsize=10)
fig.tight_layout()
fig.savefig(WB / "results/e175/e175_input_vs_next.png", dpi=150)
fig.savefig(WB / "results/e175/e175_input_vs_next.pdf")
print("ok")

# ---- POST-HOC: cross-fitted predictive information (scripts/e175_crossfit.py)
CF = {r: json.loads((WB / f"results/e175/crossfit_{r}.json").read_text())["ckpts"] for r in SEEDS + RERUN}


def cf(run, key):
    d = CF[run]
    t = sorted(int(k) for k in d)
    if key == "G_in|next*":
        v = [[d[str(s)][l]["G_joint"] - d[str(s)][l]["G_next_tok"] for l in range(NL)] for s in t]
    else:
        v = [[d[str(s)][l][key] for l in range(NL)] for s in t]
    return np.array(t), np.array(v)


CKEYS = ["G_in_tok", "G_next_tok", "G_next|in", "G_in|next*", "G_joint", "G_in_upos", "G_next_upos",
         "G_next_upos|in_tok", "G_next_form|in_tok", "G_next_upos|in_upos", "G_shuf_in_tok", "G_shuf_next_tok",
         "sub_G_in_tok", "sub_G_next_tok", "sub_G_next|in", "sub_G_next_upos|in_tok", "H_e_test"]
cst = {k: np.stack([cf(r, k)[1] for r in SEEDS]) for k in CKEYS}
summ["crossfit"] = {"note": "POST-HOC; bits; 2-fold cross-fitted log-loss gain of top-1 expert; G_in|next* = G_joint - G_next_tok",
                    "layers": {}}
for l in range(NL):
    L = {k: {"mean": cst[k][:, :, l].mean(0).round(4).tolist(), "min": cst[k][:, :, l].min(0).round(4).tolist(),
             "max": cst[k][:, :, l].max(0).round(4).tolist()} for k in CKEYS}
    L["crossing_next_ge_in_tok"] = {r: crossing(cst["G_in_tok"][i, :, l], cst["G_next_tok"][i, :, l], ts) for i, r in enumerate(SEEDS)}
    L["crossing_next_ge_in_upos"] = {r: crossing(cst["G_in_upos"][i, :, l], cst["G_next_upos"][i, :, l], ts) for i, r in enumerate(SEEDS)}
    L["rerun"] = {r: {k: cf(r, k)[1][:, l].round(4).tolist() for k in ["G_in_tok", "G_next_tok", "G_next|in", "G_next_upos|in_tok"]}
                  for r in RERUN}
    summ["crossfit"]["layers"][l] = L
(WB / "results/e175/e175_summary.json").write_text(json.dumps(summ, indent=1))

fig, axs = plt.subplots(3, 4, figsize=(13, 8.2), sharex=True, sharey=True)
C_U = "#2a8a4a"
for l in range(NL):
    ax = axs.flat[l]
    for k, c, ls, lab in [("G_in_tok", C_IN, "-", "input token"), ("G_next_tok", C_NX, "-", "true next token"),
                          ("G_next|in", C_NX, ":", "next token | input token"),
                          ("G_next_upos|in_tok", C_U, ":", "next-word UPOS | input token"),
                          ("G_in|next*", C_IN, ":", "input token | next token")]:
        v = cst[k][:, :, l]
        ax.fill_between(x, v.min(0), v.max(0), color=c, alpha=.22, lw=0)
        ax.plot(x, v.mean(0), color=c, lw=1.8 if ls == "-" else 1.4, ls=ls, label=lab)
    for r in RERUN:
        t2, a = cf(r, "G_in_tok"); _, b = cf(r, "G_next_tok")
        x2 = np.where(t2 == 0, 1e7, t2).astype(float)
        ax.plot(x2, a[:, l], color=C_IN, lw=.7, ls="--", alpha=.8)
        ax.plot(x2, b[:, l], color=C_NX, lw=.7, ls="--", alpha=.8)
    ax.axhline(0, color="k", lw=.5)
    ax.axvspan(1e7, 5.24e8, color="#eeeeee", zorder=0)
    ax.set_xscale("log"); ax.set_title(f"layer {l}", fontsize=10); ax.grid(alpha=.3, lw=.5)
    if l % 4 == 0:
        ax.set_ylabel("held-out info (bits)")
    if l >= 8:
        ax.set_xlabel("training tokens (step 0 at left edge)")
axs.flat[0].legend(fontsize=7, loc="upper left")
fig.suptitle("E175 (POST-HOC estimator): held-out information about the routed expert; 3 init seeds (band = range), "
             "dashed = rerun pair I4D0/I4D0R; grey = warmup", fontsize=10)
fig.tight_layout()
fig.savefig(WB / "results/e175/e175_crossfit.png", dpi=150)
fig.savefig(WB / "results/e175/e175_crossfit.pdf")
print("ok crossfit")
