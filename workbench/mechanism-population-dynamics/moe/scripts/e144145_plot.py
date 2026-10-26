"""Fixed four-panel readout of E144/E145; export PNG/PDF without new model calls."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WB = Path(__file__).resolve().parents[1]


def interval(ax, x, row, color, label=None, crossed=False, marker="o"):
    lo, hi = row["crossed_file_source_ci95" if crossed else "input_file_ci95"]
    ax.vlines(x, lo, hi, colors=color, linewidth=1.5)
    ax.plot(x, row["point"], marker=marker, color=color, label=label, markersize=6, linestyle="none")


def main():
    a = json.loads((WB / "results/e144/summary.json").read_text())
    b = json.loads((WB / "results/e145/summary.json").read_text())
    plt.rcParams.update({"font.size": 10, "axes.spines.right": False, "axes.spines.top": False,
                         "pdf.fonttype": 42, "figure.dpi": 150})
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2))
    blue, red, gray = "#2166AC", "#B2182B", "#6A6A6A"
    ax = axes[0, 0]
    for x, (key, label) in enumerate((("delta_mu_to_variant_kl", "KL from common reference"), ("delta_nll", "Label NLL"))):
        interval(ax, x, a["effects"][key], blue if x == 0 else red, crossed=True)
    ax.axhline(0, color=gray, linewidth=.8)
    ax.set(xticks=[0, 1], xticklabels=["KL", "NLL"], ylabel="Recombined minus intact (nats / token)",
           title="A  Fixed-gate recombination: actual predictions", xlim=(-.5, 1.5))
    ax.text(.02, .97, "24 banks; 8 independent source-map units", transform=ax.transAxes, va="top", fontsize=9)
    ax = axes[0, 1]
    interval(ax, 0, a["moments"]["C_minus_V"], gray)
    interval(ax, 1, a["effects"]["delta_sum64_teacher_sse"], blue, crossed=True)
    interval(ax, 2, a["effects"]["delta_native_teacher_sse"], red, crossed=True)
    ax.axhline(0, color=gray, linewidth=.8)
    ax.set(xticks=[0, 1, 2], xticklabels=["Expected iid\nC - V", "Observed\nFP64 sum", "Observed\nnative BF16"],
           ylabel="Layer squared-risk increase / position", title="B  Geometry and finite source sampling", xlim=(-.5, 2.5))
    ax = axes[1, 0]
    for j, (field, color, marker, label) in enumerate((("A_to_bank_kl", blue, "o", "Bank only"),
                                                      ("A_to_gate_kl", red, "s", "Gate only"),
                                                      ("A_to_donor_native_kl", gray, "^", "Donor intact"))):
        for x, donor in enumerate(("R0", "R2", "S0", "S2")):
            interval(ax, x + (j-1)*.19, b["donors"][donor][field], color,
                     label=label if x == 0 else None, marker=marker)
    ax.set(xticks=range(4), xticklabels=["R0", "R2", "S0", "S2"], ylabel="KL from the same receiver A (nats / token)",
           title="C  Legal gate x bank crosses", xlim=(-.5, 3.5))
    ax.legend(frameon=False, fontsize=8)
    ax = axes[1, 1]
    for group, color, offset in (("R", red, -.12), ("S", blue, .12)):
        for x, kind in enumerate(("native_moments", "common_gate_moments")):
            interval(ax, x + offset, b[kind][group]["C"], color, label=group if x == 0 else None)
    ax.set(xticks=[0, 1], xticklabels=["Own native gates", "Common receiver gate"], ylabel="Component variance / position",
           title="D  What persists under a common gate", xlim=(-.5, 1.5))
    ax.legend(frameon=False, fontsize=9)
    for ax in axes.flat:
        ax.grid(axis="y", alpha=.16)
    fig.tight_layout(rect=(0, .06, 1, 1), h_pad=2, w_pad=2)
    fig.text(.5, .015, "Intervals: fixed-cohort input-file bootstrap; panels A / B observed risks also resample source maps.\n"
             "One teacher layer, one shared receiver, two paired donors; intervals do not represent a population of training seeds.",
             ha="center", fontsize=8, color=gray)
    output = WB / "results/e145/figures"
    output.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf"):
        fig.savefig(output / ("recombination_and_history." + suffix), bbox_inches="tight")
    print(str(output / "recombination_and_history.png"))


if __name__ == "__main__":
    main()
