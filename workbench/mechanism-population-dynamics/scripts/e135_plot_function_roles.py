#!/usr/bin/env python3
"""Plot registered E135 functional, natural-predictor, and necessity readouts."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readout", type=Path, default=ROOT / "results/e135/readout.json")
    parser.add_argument("--audit", type=Path, default=ROOT / "results/e135/functional_independent_audit.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e135/figures/function_and_roles")
    args = parser.parse_args()
    readout = json.loads(args.readout.read_text())
    audit = json.loads(args.audit.read_text())
    if readout.get("experiment") != "E135" or readout.get("status") != "complete" or readout.get("errors"):
        raise ValueError("E135 readout must be complete and error-free")
    if audit.get("experiment") != "E135" or audit.get("status") != "complete":
        raise ValueError("E135 independent functional audit must be complete")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.1))
    colors = {"initial": "#E45756", "copy": "#72B7B2", "final": "#4C78A8"}
    names = {"initial": "Initial student", "copy": "Exact weight copy", "final": "Final student"}

    # Independent audit supplies the already-computed held-word bootstrap CIs.
    ax = axes[0]
    conds = ["initial", "copy", "final"]
    xs = np.arange(len(conds), dtype=float)
    for metric, label, shift in (("U", "U", -0.10), ("A", "A", 0.10)):
        for i, cond in enumerate(conds):
            rec = audit["comparisons"][cond]["function"][metric]
            mean = float(rec["held_mean_rho"])
            ci = rec["bootstrap"].get("ci95")
            x = xs[i] + shift
            if ci is not None:
                ax.vlines(x, float(ci[0]), float(ci[1]), color=colors[cond], linewidth=1.5)
            ax.plot(x, mean, marker="o" if metric == "U" else "s", color=colors[cond], linestyle="none")
            if ci is None:
                ax.annotate("CI unavailable", (x, mean), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=7)
        ax.plot([], [], marker="o" if metric == "U" else "s", color="#444444", linestyle="none", label=label)
    ax.set_xticks(xs, [names[c] for c in conds], rotation=15, ha="right")
    ax.set_ylim(-0.15, 1.08)
    ax.set_ylabel("Held-word mean column ρ")
    ax.set_title("U/A function matching\n999 held-word bootstrap draws")
    ax.legend(title="Readout", frameon=False)
    ax.grid(axis="y", alpha=0.2)

    # Natural predictor KL: Dolma file bootstrap and POS word bootstrap remain separate.
    ax = axes[1]
    datasets = [
        ("Dolma", "Dolma (file CI)", "#59A14F", -0.12),
        ("POS_held", "POS held (word CI)", "#B279A2", 0.12),
    ]
    for dataset, label, color, shift in datasets:
        means, lows, highs = [], [], []
        for cond in conds:
            g = readout["natural_predictors"]["conditions"][cond][dataset]["global"]
            metric = g["kl_teacher_to_student"]
            means.append(float(metric["mean"]))
            lows.append(float(metric["ci95"][0]))
            highs.append(float(metric["ci95"][1]))
        x = xs + shift
        ax.errorbar(x, means, yerr=[np.array(means) - lows, np.array(highs) - means], color=color, marker="o", capsize=3, linewidth=0, linestyle="none", label=label)
    ax.set_xticks(xs, [names[c] for c in conds], rotation=15, ha="right")
    ax.set_ylabel("Forward KL (nats/token)")
    ax.set_title("Natural predictor divergence")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.2)

    # Separate native references: the public teacher summary is embedded in
    # final_student_necessity.teacher_reference; the final student's own
    # native-referenced c/r/zero readout is in conditions.
    ax = axes[2]
    cases = ["c", "r", "zero"]
    case_labels = ["c", "r", "zero"]
    offsets = {"Teacher": -0.10, "Final student": 0.10}
    refs = readout["final_student_necessity"]["teacher_reference"]["conditions"]
    fin = readout["final_student_necessity"]["conditions"]
    for model, source, color in (
        ("Teacher", refs, "#F28E2B"),
        ("Final student", fin, "#4C78A8"),
    ):
        means, lows, highs = [], [], []
        for case in cases:
            g = source[case]["metrics"]["global"] if model == "Teacher" else source[case]["global"]
            metric = g["nll_gap"]
            means.append(float(metric["mean"]))
            lows.append(float(metric["ci95"][0]))
            highs.append(float(metric["ci95"][1]))
        x = np.arange(len(cases), dtype=float) + offsets[model]
        ax.errorbar(x, means, yerr=[np.array(means) - lows, np.array(highs) - means], color=color, marker="o", capsize=3, linewidth=0, linestyle="none", label=f"{model} (file CI)")
    ax.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
    ax.set_xticks(np.arange(len(cases)), case_labels)
    ax.set_ylabel("ΔNLL vs each model's native (nats/token)")
    ax.set_title("c / r / zero necessity readouts")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.2)

    fig.suptitle("E135 — Functional and predictor readouts", fontsize=14, y=1.01)
    fig.text(
        0.5,
        -0.02,
        "One native teacher and one trained student; intervals describe held-word or file-level measurement uncertainty, not seed variation. "
        "Dolma: BF16 logits → FP32 log-softmax. POS: BF16 backbone → genuine FP32 last-position vocabulary head/log-softmax. "
        "Exact weight copy stores the original BF16-valued weights in FP32. "
        "Remaining discrepancies are shown directly; no equivalence threshold or knowledge fraction is implied.",
        ha="center",
        fontsize=8,
        wrap=True,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.96], w_pad=2.0)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, fmt in (("function_and_roles.png", "png"), ("function_and_roles.pdf", "pdf")):
        path = args.output_dir / name
        tmp = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(tmp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(tmp, path)
    plt.close(fig)
    print(json.dumps({"status": "complete", "png": str(args.output_dir / "function_and_roles.png"), "pdf": str(args.output_dir / "function_and_roles.pdf")}, indent=2))


if __name__ == "__main__":
    main()
