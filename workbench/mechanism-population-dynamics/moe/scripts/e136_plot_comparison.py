#!/usr/bin/env python3
"""Plot fixed E135 student and E136 assignment-oracle summaries."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e135-readout", type=Path, default=ROOT / "results/e135/readout.json")
    parser.add_argument("--e135-audit", type=Path, default=ROOT / "results/e135/functional_independent_audit.json")
    parser.add_argument("--e135-training", type=Path, default=ROOT / "results/e135/training_summary.json")
    parser.add_argument("--e136-readout", type=Path, default=ROOT / "results/e136/readout.json")
    parser.add_argument("--e136-training", type=Path, default=ROOT / "results/e136/training_summary.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e136/figures")
    args = parser.parse_args()
    e135 = json.loads(args.e135_readout.read_text())
    audit = json.loads(args.e135_audit.read_text())
    e135_train = json.loads(args.e135_training.read_text())
    e136 = json.loads(args.e136_readout.read_text())
    e136_train = json.loads(args.e136_training.read_text())
    if e135.get("status") != "complete" or e136.get("status") != "complete":
        raise ValueError("E135 and E136 readouts must be complete")
    if audit.get("status") != "complete":
        raise ValueError("E135 independent function audit must be complete")
    if e135_train.get("step") != 4096 or e136_train.get("step") != 4096:
        raise ValueError("Both registered training summaries must be at step 4096")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig = plt.figure(figsize=(16.0, 10.0))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.85])
    ax_dolma = fig.add_subplot(grid[0, 0])
    ax_pos = fig.add_subplot(grid[0, 1])
    ax_function = fig.add_subplot(grid[0, 2])
    ax_learning = fig.add_subplot(grid[1, :])

    model_data = [
        ("E135 trained student", e135["natural_predictors"]["conditions"]["final"]),
        ("E136 assignment oracle", e136["natural_predictors"]["conditions"]["oracle_final"]),
    ]
    model_colors = {"E135 trained student": "#4C78A8", "E136 assignment oracle": "#F58518"}
    for ax, dataset, title in (
        (ax_dolma, "Dolma", "Dolma held\n32 files; file bootstrap"),
        (ax_pos, "POS_held", "POS held\n512 items / 48 words; word bootstrap"),
    ):
        for i, (label, conditions) in enumerate(model_data):
            metric = conditions[dataset]["global"]["kl_teacher_to_student"]
            mean = float(metric["mean"])
            lo, hi = map(float, metric["ci95"])
            x = i
            ax.errorbar(x, mean, yerr=[[mean - lo], [hi - mean]], color=model_colors[label], marker="o", capsize=3, linewidth=0, linestyle="none", label=label)
        ax.set_xticks([0, 1], ["E135 final", "E136 final"], rotation=12, ha="right")
        ax.set_ylabel("KL(public teacher || model), nats/token")
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.2)

    # Fixed-cal correspondences plus the predesignated known-identity mapping.
    # Include both oracle initial and final states under each mapping so neither
    # mapping is selected after seeing its held readout; retain E135's own cal-U point.
    profiles = [
        ("E135 final\ncal-U", "E135", "cal_U", "#4C78A8"),
        ("E136 initial\ncal-U", "oracle_initial", "cal_U", "#9ECAE9"),
        ("E136 final\ncal-U", "oracle_final", "cal_U", "#F58518"),
        ("E136 initial\nknown identity", "oracle_initial", "known_identity", "#A1D99B"),
        ("E136 final\nknown identity", "oracle_final", "known_identity", "#59A14F"),
    ]
    for i, (label, model_key, corr_key, color) in enumerate(profiles):
        for metric, marker, shift in (("U", "o", -0.09), ("A", "s", 0.09)):
            if model_key == "E135":
                rec = audit["comparisons"]["final"]["function"][metric]
                point = float(rec["held_mean_rho"])
                ci = rec["bootstrap"].get("ci95")
            else:
                rec = e136["correspondences"][model_key][corr_key]["function"][metric]
                point = float(rec["held_conditional_columns"]["mean"])
                ci = rec.get("fixed_map_word_bootstrap_ci95")
            x = i + shift
            if ci is not None:
                lo, hi = map(float, ci)
                ax_function.vlines(x, lo, hi, color=color, linewidth=1.4)
            ax_function.plot(x, point, marker=marker, color=color, linestyle="none")
    ax_function.set_xticks(range(len(profiles)), [p[0] for p in profiles], rotation=15, ha="right", fontsize=7)
    ax_function.set_ylabel("Mean held expert-column ρ")
    ax_function.set_title("Cal-U and known-identity correspondences\nU circles · A squares · 95% held-word CI", fontsize=10)
    ax_function.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
    ax_function.grid(axis="y", alpha=0.2)

    # Existing fixed-energy events only; both summaries use the same train-energy denominator.
    for name, summary, color in (
        ("E135 trained student", e135_train, model_colors["E135 trained student"]),
        ("E136 assignment oracle", e136_train, model_colors["E136 assignment oracle"]),
    ):
        steps = [int(row["step"]) for row in summary["evaluations"]]
        train = [float(row["train"]["normalized_by_fixed_training_energy"]) for row in summary["evaluations"]]
        held = [float(row["held"]["normalized_by_fixed_training_energy"]) for row in summary["evaluations"]]
        ax_learning.plot(steps, train, color=color, marker="o", label=f"{name} · train")
        ax_learning.plot(steps, held, color=color, marker="s", linestyle="--", label=f"{name} · held")
    ax_learning.set_xlabel("Training updates")
    ax_learning.set_ylabel("MSE / shared fixed train energy")
    ax_learning.set_title("Existing training events (same fixed train-energy denominator)")
    ax_learning.grid(alpha=0.2)
    ax_learning.legend(frameon=False, ncol=2, fontsize=8)

    fig.suptitle("E135 student and E136 assignment-oracle readouts", fontsize=14, y=0.965)
    fig.text(
        0.5, 0.025,
        "q is the public teacher in predictor readouts. Precision: Dolma BF16 logits → FP32 log-softmax; POS BF16 backbone → genuine FP32 last-position vocabulary head/log-softmax. "
        "Dolma intervals are file-level; POS and function intervals are held-word measurement uncertainty, not seed uncertainty. "
        "Known identity is shown as a separately predesignated correspondence; E136 initial A is included as a baseline. One teacher/student per condition; no unique-role or knowledge-fraction claim. "
        "Held MSE uses the shared train-energy denominator, not held energy.",
        ha="center", fontsize=7.5, wrap=True,
    )
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.20, top=0.88, hspace=0.82, wspace=0.55)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, fmt in (("e135_e136_comparison.png", "png"), ("e135_e136_comparison.pdf", "pdf")):
        path = args.output_dir / name
        tmp = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(tmp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(tmp, path)
        paths.append(str(path))
    plt.close(fig)
    print(json.dumps({"status": "complete", "outputs": paths}, indent=2))


if __name__ == "__main__":
    main()
