#!/usr/bin/env python3
"""E172 figure: (A) deep T_D by type-majority UPOS — init (15 pairs, mean and range), order, rerun, floor;
(B) deep Spec per UPOS for each run (Antoine 2024 readout), and probe accuracy vs word-form baseline;
(C) F2: deep cell-mean cross-init correlation / order ratio vs training tokens per UD variable.
-> results/e172/e172_figure.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]
R = WB / "results/e172"
S = json.loads((R / "summary.json").read_text())
fig, ax = plt.subplots(1, 4, figsize=(19, 4.6), gridspec_kw={"width_ratios": [1.5, 1.3, 1, 1.3]})

# A
G = S["readout1"]["3200000000"]["groupings"]["type_majority_upos"]
order = ["NOUN", "VERB", "ADJ", "ADV", "PROPN", "ADP", "DET", "PRON", "AUX", "CCONJ", "SCONJ", "PUNCT", "NUM", "content", "function"]
x = np.arange(len(order))
a = ax[0]
ini = [G[g]["deep"]["init"] for g in order]
lo = [G[g]["deep"]["init"] - G[g]["deep"]["init_range"][0] for g in order]
hi = [G[g]["deep"]["init_range"][1] - G[g]["deep"]["init"] for g in order]
a.bar(x - .27, [G[g]["deep"]["rerun"] for g in order], .27, color="#9aa7b8", label="rerun (1 pair)")
a.bar(x, [G[g]["deep"]["order"] for g in order], .27, color="#c9b48a", label="order only (2)")
a.bar(x + .27, ini, .27, yerr=[lo, hi], color="#3b6ea5", capsize=2, label="init only (15; range)")
a.plot(x, [G[g]["deep"]["floor"] for g in order], "k_", ms=10, label="untrained floor")
a.axvline(12.5, color="k", lw=.6)
a.set_xticks(x); a.set_xticklabels(order, rotation=60, fontsize=8)
a.set_ylabel("T_D, mean L6–11 (3.2B tokens)"); a.set_title("A  Context-partition agreement by word class")
a.legend(fontsize=7, loc="upper right", ncol=2); a.set_ylim(0, .62)

# B
k = "readout2_3200000000"
if k in S:
    r2 = S[k]; PROF = r2["profile_upos"]
    sp = r2["init_spread"]
    m = np.array([sp["spec_upos_deep_mean"][u] for u in PROF]); sd = np.array([sp["spec_upos_deep_sd"][u] for u in PROF])
    o = np.argsort(-m)
    b = ax[1]
    b.bar(np.arange(len(PROF)), m[o], yerr=sd[o], color="#3b6ea5", capsize=2, label="6 init runs, mean ± SD")
    b.axhline(.125, color="k", ls="--", lw=.8, label="uniform U = 8/64")
    fl = r2.get("untrained_spec_upos_deep")
    if fl:
        b.plot(np.arange(len(PROF)), [fl[PROF[i]] for i in o], "_", color="#c0504d", ms=12, mew=2, label="untrained (step 0), mean of 2")
    b.set_xticks(np.arange(len(PROF))); b.set_xticklabels([PROF[i] for i in o], rotation=60, fontsize=8)
    b.set_ylabel("Spec (top-8 expert share), mean L6–11"); b.set_title("B  Antoine-style POS specialisation")
    b.legend(fontsize=7)
    c = ax[2]
    pm = r2["per_model"]
    names = [n for n in pm if not n.endswith("@0")]
    accs = [pm[n]["probe_acc"] for n in names]
    c.scatter(np.zeros(len(names)) + np.random.default_rng(0).uniform(-.08, .08, len(names)), accs, c="#3b6ea5", s=18, label="trained runs")
    c.scatter([1, 1], [pm[n]["probe_acc"] for n in pm if n.endswith("@0")], c="#999", s=18, label="untrained")
    c.axhline(r2["baseline_word_form"]["acc"], color="#c0504d", ls="--", label="word-form baseline")
    c.set_xticks([0, 1]); c.set_xticklabels(["3.2B", "step 0"]); c.set_xlim(-.5, 1.5)
    c.set_ylabel("UPOS accuracy (held-out 1/3)"); c.set_title("C  Routing-path probe"); c.legend(fontsize=7, loc="lower left")
# D
if "readout3" in S:
    sm = S["readout3"]["summary"]; toks = [t for t in S["readout3"]["tokens"] if t <= S["readout3"]["ref"]]
    d = ax[3]
    cols = {"upos": "#1f77b4", "feats": "#17becf", "sentpos": "#9467bd", "prev_upos": "#2ca02c", "next_upos": "#98df8a",
            "deprel": "#d62728", "head_upos": "#ff7f0e", "genre": "#7f7f7f"}
    for v, cc in cols.items():
        y = np.array(sm[v]["deep"]["cell_init"]); y = y / y[-1]
        d.plot(toks, y, "-o", ms=3, color=cc, label=v)
    d.axhline(.8, color="k", ls=":", lw=.8)
    d.set_xscale("log"); d.set_xlabel("training tokens"); d.set_ylabel("cross-init cell corr ÷ value at 3.2B, mean L6–11")
    d.set_title("D  When each distinction becomes init-reproducible"); d.legend(fontsize=7, ncol=2)
fig.tight_layout()
fig.savefig(R / "e172_figure.png", dpi=140)
print("saved", R / "e172_figure.png")
