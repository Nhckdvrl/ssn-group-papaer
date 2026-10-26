"""Standalone E148 figures from complete summaries; no model or input selection."""
from pathlib import Path
import json
import numpy as np
from e144145_analyze import input_stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WB = Path(__file__).resolve().parents[1]


def point(ax, x, row, color, marker="o", label=None):
    lo, hi = row["input_file_ci95"]
    ax.vlines(x, lo, hi, color=color, linewidth=1)
    ax.plot(x, row["point"], color=color, marker=marker, label=label, linestyle="none", markersize=5)


def main():
    d = json.loads((WB / "results/e148/summary.json").read_text())
    if d["status"] != "complete": raise ValueError("Complete planned readouts required")
    plan = json.loads((WB / "results/e148/plan.json").read_text())
    records = {n: json.loads((WB / f"results/e148/{n}.json").read_text()) for n in ("parent", "A", "B", "A-repeat")}
    parent_nll = np.array(records["parent"]["evaluations"][0]["nll_rows"])
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.5), dpi=150)
    blue, red, gray = "#2166AC", "#B2182B", "#777777"
    ax = axes[0, 0]
    for branch, color, marker in (("A", blue, "o"), ("B", red, "s"), ("A-repeat", gray, "x")):
        steps = [32, 160, 288, 608, 672]
        rows = [input_stats(np.zeros(64), plan["selected"], 148001)]+[
            input_stats(np.array(next(e for e in records[branch]["evaluations"] if e["step"] == s)["nll_rows"])-parent_nll,
                        plan["selected"], 148001) for s in steps[1:]]
        ax.plot(steps, [r["point"] for r in rows], color=color, linewidth=1, linestyle="--" if branch == "A-repeat" else "-", label=branch)
        for x, row in zip(steps, rows): point(ax, x, row, color, marker)
    ax.set(title="A  Native full-model learning", xlabel="Controlled continuation updates (shared parent = 32)", ylabel="NLL minus shared parent (nats / token)")
    ax.legend(frameon=False, fontsize=8)
    ax = axes[0, 1]
    for right, color, marker in (("B", red, "s"), ("A-repeat", gray, "x")):
        steps = [160, 608, 672]
        rows = [d["pairs"][f"A_{s}_to_{right}_{s}"]["forward_kl"] for s in steps]
        ax.plot(steps, [r["point"] for r in rows], color=color, linewidth=1, label=f"A to {right}")
        for x, row in zip(steps, rows): point(ax, x, row, color, marker)
    for branch, color, offset in (("A", blue, -7), ("B", gray, 7)):
        row = d["pairs"][f"{branch}_608_to_{branch}_672"]["forward_kl"]
        point(ax, 672+offset, row, color, "^", f"{branch} late to final")
    ax.set(title="B  Order effect and same-stream replay", xlabel="Controlled continuation updates", ylabel="Full-vocabulary KL (nats / token)")
    ax.axhline(0, color="#BBBBBB", linewidth=.6)
    ax.legend(frameon=False, fontsize=8)
    labels = [(160, "A"), (160, "B"), (672, "A"), (672, "B")]
    variants = (("bank_only", blue, "o", "Bank only"), ("gate_only", red, "s", "Gate only"),
                ("complete_L9_graft", gray, "^", "Complete L9"))
    for panel, field, title, ylabel in ((axes[1, 0], "delta_nll", "C  Reciprocal legal L9 grafts", "Graft minus receiver NLL (nats / token)"),
                                       (axes[1, 1], "native_to_variant_kl", "D  Native receiver to graft", "Full-vocabulary KL (nats / token)")):
        for j, (variant, color, marker, label) in enumerate(variants):
            for x, (step, receiver) in enumerate(labels):
                row = d["grafts"][f"step{step}_{receiver}"][variant][field]
                point(panel, x+(j-1)*.17, row, color, marker, label if x == 0 else None)
        for x, receiver in ((2, "A"), (3, "B")):
            row = d["grafts"][f"step672_{receiver}"]["own_late_bank"][field]
            point(panel, x+.34, row, "#238B45", "x", "Own late bank" if x == 2 else None)
        panel.set(xticks=range(4), xticklabels=[f"{s}: {r}" for s, r in labels], xlabel="Snapshot: receiving backbone", title=title, ylabel=ylabel)
        panel.axhline(0, color="#BBBBBB", linewidth=.6)
        panel.legend(frameon=False, fontsize=8)
    for ax in axes.flat: ax.grid(axis="y", alpha=.15)
    fig.tight_layout(rect=(0, .07, 1, 1), w_pad=2, h_pad=2)
    fig.text(.5, .015, "One pretrained parent; A/B reorder the same 128 complete batches, then receive 512 identical updates.\n"
             "All intervals resample input files, not training seeds. Complete L9 grafts keep the receiver's backbone, not the donor's.", ha="center", fontsize=8, color=gray)
    out = WB / "results/e148/figures"
    out.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf"): fig.savefig(out / ("native_order_and_compatibility."+suffix), bbox_inches="tight")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), dpi=150)
    for branch, color, marker in (("A", blue, "o"), ("B", red, "s"), ("A-repeat", gray, "x")):
        steps = [160, 288, 608, 672]
        rows = [d["routing"][branch][str(s)] for s in steps]
        axes[0].plot(steps, [r["L9_top8_overlap_with_parent"] for r in rows], color=color, marker=marker, label=branch)
        axes[1].plot(steps, [r["L9_gate_only_affinity_frobenius_change"] for r in rows], color=color, marker=marker, label=branch)
    axes[0].set(title="L9 native Top-8 overlap with shared parent", ylabel="Overlap fraction", xlabel="Controlled continuation updates", ylim=(0, 1.02))
    axes[1].set(title="L9 native weighted coactivation change", ylabel="Affinity Frobenius distance", xlabel="Controlled continuation updates")
    for ax in axes: ax.legend(frameon=False, fontsize=8); ax.grid(axis="y", alpha=.15)
    fig.tight_layout(rect=(0, .08, 1, 1))
    fig.text(.5, .015, "Fixed calibration texts; native hidden states and gates both evolve. Physical slots follow the shared ancestor, not inferred semantic roles.", ha="center", fontsize=8, color=gray)
    for suffix in ("png", "pdf"): fig.savefig(out / ("native_route_trajectory."+suffix), bbox_inches="tight")
    print(str(out / "native_order_and_compatibility.png"))


if __name__ == "__main__":
    main()
