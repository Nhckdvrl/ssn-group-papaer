#!/usr/bin/env python3
"""Plot registered E131 trajectory summaries; refuses incomplete endpoints."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUNCTIONAL_BATCH = ROOT / "results/e131/functional_batch.json"
PREDICTOR_ROOT = ROOT / "results/e131/predictor_comparison"
OUTPUT_DIR = ROOT / "results/e131/figures/history_trajectory"
POINTS = [
    (5120, "ordered_vs_permuted_pulse"),
    (24576, "ordered_vs_permuted_common24576"),
    (62500, "ordered_vs_permuted_final"),
]
PREDICTOR_FILES = {step: PREDICTOR_ROOT / f"step{step:06d}.json" for step, _ in POINTS}


def read_complete_inputs(functional_batch: Path, predictor_root: Path) -> tuple[dict, dict[int, dict]]:
    if not functional_batch.is_file():
        raise FileNotFoundError(functional_batch)
    functional = json.loads(functional_batch.read_text())
    pairs = functional.get("pairs")
    if (
        functional.get("status") != "complete"
        or functional.get("expected_pairs") != 15
        or functional.get("completed_pairs") != 15
        or not isinstance(pairs, dict)
        or len(pairs) != 15
    ):
        raise ValueError("E131 functional_batch is not yet complete with the registered 15 pairs")

    selected = {}
    for step, key in POINTS:
        pair = pairs.get(key)
        if not isinstance(pair, dict) or pair.get("status") != "complete":
            raise ValueError(f"Missing complete cross-branch pair: {key}")
        intervals = pair.get("word_intervals")
        if not isinstance(intervals, dict):
            intervals = {}
        for name in ("U", "A"):
            interval = intervals.get(name)
            if interval is None:
                continue
            mean = interval.get("observed_mean")
            ci = interval.get("ci95")
            if mean is not None and (not isinstance(mean, (int, float)) or not math.isfinite(float(mean))):
                raise ValueError(f"Invalid held-word point estimate for {key}/{name}")
            if ci is not None and (
                not isinstance(ci, list) or len(ci) != 2
                or not all(isinstance(x, (int, float)) and math.isfinite(float(x)) for x in ci)
            ):
                raise ValueError(f"Invalid held-word CI for {key}/{name}")
        selected[step] = pair

    predictor = {}
    for step, _ in POINTS:
        path = predictor_root / f"step{step:06d}.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        summary = json.loads(path.read_text())
        if summary.get("experiment") != "E131" or summary.get("status") != "complete" or summary.get("step") != step:
            raise ValueError(f"Predictor summary not complete for step {step}")
        groups = summary.get("groups", {})
        for group in ("Dolma", "POS_plan_held"):
            record = groups.get(group)
            if not isinstance(record, dict):
                raise ValueError(f"Missing predictor group {group} at step {step}")
            metrics = record.get("global", {})
            for field in ("kl_teacher_to_student", "nll_gap"):
                value = metrics.get(field)
                if not isinstance(value, dict) or not isinstance(value.get("ci95"), list) or len(value["ci95"]) != 2:
                    raise ValueError(f"Missing {field} interval for {group} at step {step}")
                if not all(math.isfinite(float(x)) for x in [value.get("mean"), *value["ci95"]]):
                    raise ValueError(f"Non-finite {field} interval for {group} at step {step}")
        predictor[step] = summary
    return selected, predictor


def plot(functional: dict, predictor: dict[int, dict], output_dir: Path) -> tuple[Path, Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    steps = [step for step, _ in POINTS]
    x = np.arange(len(steps), dtype=float)
    fig, axes = plt.subplots(2, 2, figsize=(12.4, 8.0), squeeze=False)

    # Panel 1: fixed-cal, held-word cross-branch U/A correlations.
    ax = axes[0, 0]
    for metric, label, color, marker, offset in (
        ("U", "U", "#4C78A8", "o", -0.055),
        ("A", "A", "#F58518", "s", 0.055),
    ):
        means, low, high, available, notes = [], [], [], [], []
        for step, _ in POINTS:
            value = functional[step].get("word_intervals", {}).get(metric, {})
            mean, ci = value.get("observed_mean"), value.get("ci95")
            means.append(float(mean) if mean is not None else float("nan"))
            valid_ci = (
                mean is not None and isinstance(ci, list) and len(ci) == 2
                and all(isinstance(v, (int, float)) and math.isfinite(float(v)) for v in ci)
            )
            available.append(valid_ci)
            low.append(float(ci[0]) if valid_ci else float("nan"))
            high.append(float(ci[1]) if valid_ci else float("nan"))
            mapped = value.get("mapped_columns")
            words = value.get("held_words")
            coverage = value.get("valid_column_coverage")
            note = f"{coverage} valid cols" if coverage is not None else (
                f"{mapped} mapped cols" if mapped is not None else "coverage unavailable"
            )
            if words is not None:
                note += f", {words} words"
            notes.append(note)
        xs = x + offset
        for i in range(len(steps)):
            if available[i]:
                ax.vlines(xs[i], low[i], high[i], color=color, linewidth=1.5)
            if math.isfinite(means[i]):
                ax.plot(xs[i], means[i], marker=marker, color=color, linestyle="none")
                if not available[i]:
                    ax.annotate(f"CI unavailable\n{notes[i]}", (xs[i], means[i]), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=6, color=color)
            else:
                ax.annotate(f"point unavailable\n{notes[i]}", (xs[i], 0.04 + (0.09 if metric == "A" else 0)), xycoords=("data", "axes fraction"), ha="center", va="bottom", fontsize=6, color=color)
        ax.plot([], [], marker=marker, color=color, linewidth=1.5, label=f"{label} (held-word CI when defined)")
    ax.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
    ax.set_title("Cross-branch U/A ρ")
    ax.set_ylabel("Held-word correlation")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.2)

    group_specs = [
        (axes[0, 1], "kl_teacher_to_student", "Native→student KL", "nats/token"),
        (axes[1, 0], "nll_gap", "Ground-truth NLL gap (student − native)", "nats/token"),
    ]
    colors = {"Dolma": "#54A24B", "POS_plan_held": "#B279A2"}
    markers = {"Dolma": "o", "POS_plan_held": "s"}
    for ax, field, title, unit in group_specs:
        for group in ("Dolma", "POS_plan_held"):
            mean, low, high = [], [], []
            meta = []
            for step in steps:
                rec = predictor[step]["groups"][group]
                metric = rec["global"][field]
                mean.append(float(metric["mean"]))
                low.append(float(metric["ci95"][0]))
                high.append(float(metric["ci95"][1]))
                meta.append(rec)
            label = "Dolma held (file bootstrap 95% CI)" if group == "Dolma" else "POS plan held (word bootstrap 95% CI)"
            for i in range(len(steps)):
                ax.vlines(x[i], low[i], high[i], color=colors[group], linewidth=1.5)
            ax.plot(x, mean, marker=markers[group], color=colors[group], linewidth=1.5, label=label)
        ax.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
        ax.set_title(title)
        ax.set_ylabel(unit)
        ax.legend(frameon=False, fontsize=7)
        ax.grid(axis="y", alpha=0.2)

    # Panel 4: benchmark granularity/precision text and no cross-population conflation.
    ax = axes[1, 1]
    p0 = predictor[steps[0]]["groups"]
    dolma_precision = p0["Dolma"].get("precision", "precision unspecified")
    pos_precision = p0["POS_plan_held"].get("precision", "precision unspecified")
    dolma_files = p0["Dolma"]["global"].get("files")
    pos_items = p0["POS_plan_held"]["global"].get("items")
    pos_words = p0["POS_plan_held"]["global"].get("words")
    ax.axis("off")
    ax.set_title("Population and precision")
    ax.text(
        0.02,
        0.88,
        f"Dolma: {dolma_precision}\n{dolma_files} files; file-bootstrap CI\n\nPOS plan held: {pos_precision}\n{pos_items} items / {pos_words} words; word-bootstrap CI",
        va="top",
        fontsize=9,
        transform=ax.transAxes,
        wrap=True,
    )

    labels = [f"{step:,}" for step in steps]
    for ax in axes.flat:
        if ax.axison:
            ax.set_xticks(x, labels)
            ax.set_xlabel("Training checkpoint step")
    fig.suptitle("E131 — Transient order pulse and common-suffix readout", fontsize=13, y=0.985)
    fig.text(
        0.5,
        0.015,
        "One step-4096 parent; a short equal-exposure order pulse is followed by shared training. Error bars are file- or word-level CIs, not seed CIs. This plot does not assert cross-run function equivalence.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=[0.02, 0.065, 0.99, 0.94], w_pad=1.0, h_pad=1.2)
    output_dir.mkdir(parents=True, exist_ok=True)
    png, pdf = output_dir / "trajectory.png", output_dir / "trajectory.pdf"
    for path, fmt in ((png, "png"), (pdf, "pdf")):
        temp = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(temp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(temp, path)
    plt.close(fig)
    return png, pdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--functional-batch", type=Path, default=FUNCTIONAL_BATCH)
    parser.add_argument("--predictor-root", type=Path, default=PREDICTOR_ROOT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    functional, predictor = read_complete_inputs(args.functional_batch, args.predictor_root)
    png, pdf = plot(functional, predictor, args.output_dir)
    print(json.dumps({"status": "complete", "pairs": 15, "steps": [step for step, _ in POINTS], "png": str(png), "pdf": str(pdf)}, indent=2))


if __name__ == "__main__":
    main()
