#!/usr/bin/env python3
"""Plot E135's registered train/held function-MSE events (no extra evaluation)."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = ROOT / "results/e135/training_summary.json"
DEFAULT_OUTPUT = ROOT / "results/e135/figures/function_learning"
EXPECTED_STEPS = list(range(0, 4097, 512))


def load_events(path: Path) -> dict:
    summary = json.loads(path.read_text())
    if summary.get("experiment") != "E135" or summary.get("status") != "complete":
        raise ValueError(f"E135 training summary is not complete: {summary.get('status')!r}")
    if summary.get("step") != 4096 or summary.get("planned_steps") != 4096:
        raise ValueError("Expected the fixed 4096-update E135 run")
    evaluations = summary.get("evaluations", [])
    steps = [row.get("step") for row in evaluations]
    if steps != EXPECTED_STEPS:
        raise ValueError(f"Expected the nine registered MSE events at {EXPECTED_STEPS}, got {steps}")
    for row in evaluations:
        for split in ("train", "held"):
            metrics = row.get(split, {})
            for key in ("MSE", "normalized_by_fixed_training_energy", "relative_to_own_split_teacher_energy"):
                value = metrics.get(key)
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError(f"Missing/non-finite {split}.{key} at step {row.get('step')}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output-prefix", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    summary = load_events(args.summary)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    steps = [row["step"] for row in summary["evaluations"]]
    train = [row["train"]["normalized_by_fixed_training_energy"] for row in summary["evaluations"]]
    held = [row["held"]["normalized_by_fixed_training_energy"] for row in summary["evaluations"]]
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.plot(steps, train, marker="o", linewidth=1.8, markersize=4.5, color="#4C78A8", label="Train")
    ax.plot(steps, held, marker="s", linewidth=1.8, markersize=4.5, color="#F58518", label="Held")
    ax.set_title("E135 student fit to cached native function (seed 1)")
    ax.set_xlabel("Update step")
    ax.set_ylabel("Function MSE / fixed training energy")
    ax.set_xlim(0, 4096)
    ax.set_xticks(EXPECTED_STEPS)
    ax.grid(alpha=0.25, linewidth=0.7)
    ax.legend(frameon=False)
    fig.text(
        0.5,
        0.015,
        "Both curves use the same fixed training-energy denominator. Held own-energy normalization is recorded separately in training_summary.json.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=[0.02, 0.07, 0.99, 0.97])
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    for suffix, fmt in ((".png", "png"), (".pdf", "pdf")):
        output = args.output_prefix.with_suffix(suffix)
        partial = output.with_name(output.stem + ".partial" + output.suffix)
        fig.savefig(partial, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(partial, output)
    plt.close(fig)
    print(json.dumps({
        "summary": str(args.summary),
        "summary_status": summary["status"],
        "steps": steps,
        "png": str(args.output_prefix.with_suffix(".png")),
        "pdf": str(args.output_prefix.with_suffix(".pdf")),
        "mse_denominator": "fixed train energy for both splits",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
