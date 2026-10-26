#!/usr/bin/env python3
"""Plot fixed E138 cohort summaries without recomputing any statistic."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POPS = ("Dolma_held_positions", "POS_held_targets")
STATES = ("initial", "final")
PAIRS = ("seed0_to_seed1", "seed0_to_seed2", "seed1_to_seed2")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_value(record: dict, field: str) -> dict:
    value = record["summary"]["global"][field]
    if not isinstance(value, dict) or "point" not in value or len(value.get("ci95", [])) != 2:
        raise ValueError(f"Missing stored point/CI: {field}")
    return value


def add_point_ci(ax, x: float, metric: dict, *, color: str, marker: str, label: str | None = None, capsize: float = 2.5) -> None:
    point = float(metric["point"])
    lo, hi = map(float, metric["ci95"])
    ax.errorbar(x, point, yerr=[[point - lo], [hi - point]], color=color, marker=marker,
                linestyle="none", capsize=capsize, linewidth=1.1, markersize=5, label=label)


def plot_components(readout: dict, output_dir: Path, table_path: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    names = {
        "initial": "E138 initial",
        "final": "E138 final",
    }
    pop_names = {
        "Dolma_held_positions": "Dolma held positions",
        "POS_held_targets": "POS held targets",
    }
    native_fields = (
        ("native_mean_teacher_SSE_per_position", "Mean student error vs teacher"),
        ("native_mean_bias_SSE_per_position", "Cohort mean bias²"),
        ("native_cohort_variance_per_position", "Within-cohort variance"),
    )
    component_fields = (
        ("component_cohort_variance_per_position", "Σₑ Var(cohort component)"),
        ("FP64_sum_cohort_variance_per_position", "Var(FP64 sum of components)"),
        ("component_cross_covariance_per_position", "Cross-covariance"),
    )
    colors = ("#4C78A8", "#F58518", "#54A24B")
    markers = ("o", "s", "^")
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 8.8), squeeze=False)
    table = {
        "experiment": "E138",
        "scope": readout["scope"],
        "cohort": "seed0, reused observed E136 seed1, seed2; pair/cluster intervals describe input uncertainty, not seed CI",
        "source_readout_sha256": None,
        "populations": {},
        "natural_predictor_and_A": {},
    }
    for col, pop in enumerate(POPS):
        table["populations"][pop] = {"initial": {}, "final": {}}
        ax_native, ax_component = axes[0, col], axes[1, col]
        x = np.arange(len(STATES), dtype=float)
        for j, (field, label) in enumerate(native_fields):
            for i, state in enumerate(STATES):
                record = readout["components"][f"{state}_{pop}"]
                metric = get_value(record, field)
                table["populations"][pop][state][field] = metric
                add_point_ci(ax_native, x[i] + (j - 1) * 0.17, metric, color=colors[j], marker=markers[j], label=label if i == 0 else None)
        for j, (field, label) in enumerate(component_fields):
            for i, state in enumerate(STATES):
                record = readout["components"][f"{state}_{pop}"]
                metric = get_value(record, field)
                table["populations"][pop][state][field] = metric
                add_point_ci(ax_component, x[i] + (j - 1) * 0.17, metric, color=colors[j], marker=markers[j], label=label if i == 0 else None)

        records = [readout["components"][f"final_{pop}"]["summary"], readout["components"][f"initial_{pop}"]["summary"]]
        nclusters = records[0]["input_clusters"]
        population_n = readout["components"][f"final_{pop}"]["sequences"]
        unit = "squared output units / position"
        if pop == "Dolma_held_positions":
            population_note = f"262,144 positions in {population_n:,} sequences; {nclusters} file clusters"
        else:
            population_note = f"{population_n:,} target positions; {nclusters} word clusters"
        ax_native.set_title(f"{pop_names[pop]}: mean student teacher error = bias² + cohort variance\n{population_note}", fontsize=9)
        ax_native.set_xticks(x, [names[s] for s in STATES])
        ax_native.set_ylabel(unit)
        ax_native.grid(axis="y", alpha=0.2)
        ax_native.legend(frameon=False, fontsize=7, loc="best")
        ax_component.set_title(f"{pop_names[pop]}: component variance identity", fontsize=10)
        ax_component.set_xticks(x, [names[s] for s in STATES])
        ax_component.set_ylabel(unit)
        ax_component.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
        ax_component.grid(axis="y", alpha=0.2)
        ax_component.legend(frameon=False, fontsize=7, loc="best")

    # Persist only already-reported natural KL and A pair summaries for the companion plot/table.
    for pop in POPS:
        table["natural_predictor_and_A"][pop] = {
            "precision": readout["predictions"]["populations"][pop]["precision"],
            "pairs": {},
        }
        for pair in PAIRS:
            table["natural_predictor_and_A"][pop]["pairs"][pair] = readout["predictions"]["populations"][pop]["pairs"][pair]["global"]
    table["natural_predictor_and_A"]["known_identity_A"] = {
        pair: {
            "point": readout["A"]["pairs"][pair]["held_conditional_columns"]["mean"],
            "ci95": readout["A"]["pairs"][pair]["ci95"],
            "n_valid_columns": readout["A"]["pairs"][pair]["held_conditional_columns"]["n_valid_columns"],
            "coverage_comparable": readout["A"]["pairs"][pair]["coverage_comparable"],
            "scope": readout["A"]["pairs"][pair]["scope"],
        }
        for pair in PAIRS
    }
    fig.suptitle("E138 — Fixed finite-cohort bias, variance and component covariance", fontsize=14, y=0.98)
    fig.text(
        0.5, 0.018,
        "Three fixed students (seed0, reused E136 seed1, seed2); intervals resample held input clusters, not seeds or the three dependent student pairs. "
        "Each population has its own units: Dolma files vs POS words/targets. Native aggregate rounding, product rounding, and FP32−FP64 summation floors are separate in the readout table. "
        "Component covariance is an arithmetic interaction in output vectors, not semantic collaboration; no same-function or unique-role claim.",
        ha="center", fontsize=7.5, wrap=True,
    )
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.12, top=0.90, hspace=0.43, wspace=0.32)
    output_dir.mkdir(parents=True, exist_ok=True)
    component_paths = []
    for fmt, name in (("png", "finite_cohort_components.png"), ("pdf", "finite_cohort_components.pdf")):
        path = output_dir / name
        tmp = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(tmp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(tmp, path)
        component_paths.append(path)
    plt.close(fig)
    return component_paths, table


def plot_predictor_A(readout: dict, output_dir: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(2, 2, figsize=(14.5, 8.5), squeeze=False)
    pair_labels = ["0–1", "0–2", "1–2"]
    pairs = list(PAIRS)
    pop_specs = [
        ("Dolma_held_positions", axes[0, 0], "Dolma held", "32-file bootstrap"),
        ("POS_held_targets", axes[0, 1], "POS held", "48-word bootstrap"),
    ]
    for pop, ax, title, interval_label in pop_specs:
        records = readout["predictions"]["populations"][pop]["pairs"]
        for direction, field, marker, shift in (
            ("left||right", "kl_left_to_right", "o", -0.10),
            ("right||left", "kl_right_to_left", "s", 0.10),
        ):
            for i, pair in enumerate(pairs):
                metric = records[pair]["global"][field]
                point, lo, hi = float(metric["point"]), *map(float, metric["ci95"])
                ax.errorbar(i + shift, point, yerr=[[point - lo], [hi - point]], color="#4C78A8" if direction == "left||right" else "#F58518",
                            marker=marker, linestyle="none", capsize=2.5, linewidth=1.1, markersize=5,
                            label=f"KL({direction})" if i == 0 else None)
        ax.set_xticks(range(3), pair_labels)
        ax.set_ylabel("Student-to-student KL (nats/token)")
        ax.set_title(f"{title}: {interval_label}")
        ax.grid(axis="y", alpha=0.2)
        ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    colors = {"seed0_to_seed1": "#4C78A8", "seed0_to_seed2": "#F58518", "seed1_to_seed2": "#54A24B"}
    for i, pair in enumerate(pairs):
        rec = readout["A"]["pairs"][pair]
        point, lo, hi = float(rec["held_conditional_columns"]["mean"]), *map(float, rec["ci95"])
        ax.errorbar(i, point, yerr=[[point - lo], [hi - point]], color=colors[pair], marker="o", linestyle="none", capsize=3)
    ax.set_xticks(range(3), pair_labels)
    ax.set_ylabel("Mean held expert-column ρ")
    ax.set_title("Known-identity A correspondence\n48-word bootstrap; all 64 columns retained")
    ax.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
    ax.grid(axis="y", alpha=0.2)

    ax = axes[1, 1]
    ax.axis("off")
    ax.set_title("Precision and interval scope")
    ax.text(
        0.02, 0.91,
        "Dolma: BF16 whole logits → FP32 log-softmax; 32 source-file clusters.\n\n"
        "POS: BF16 backbone, genuine FP32 final vocabulary head; 48 held words/512 targets.\n\n"
        "A: imposed known-identity correspondence; 64 expert columns, held-word bootstrap.\n\n"
        "All CIs describe input-cluster uncertainty only, not uncertainty over the three students or independent seed pairs.",
        transform=ax.transAxes, va="top", fontsize=9, wrap=True,
    )
    fig.suptitle("E138 — Natural predictor KL and known-identity A", fontsize=14, y=0.98)
    fig.text(0.5, 0.018, "Student pair intervals are dependent because there are only three fixed students; no pair is treated as an independent seed sample.", ha="center", fontsize=8)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.12, top=0.90, hspace=0.43, wspace=0.32)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fmt, name in (("png", "predictor_A.png"), ("pdf", "predictor_A.pdf")):
        path = output_dir / name
        tmp = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(tmp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(tmp, path)
        paths.append(path)
    plt.close(fig)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readout", type=Path, default=ROOT / "results/e138/readout.json")
    parser.add_argument("--audit", type=Path, default=ROOT / "results/e138/independent_audit.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e138/figures")
    parser.add_argument("--table", type=Path, default=ROOT / "results/e138/readout_table.json")
    args = parser.parse_args()
    readout = json.loads(args.readout.read_text())
    audit = json.loads(args.audit.read_text())
    if readout.get("experiment") != "E138" or readout.get("status") != "complete" or readout.get("errors"):
        raise ValueError("E138 readout must be complete and error-free")
    if audit.get("experiment") != "E138" or audit.get("summary_sha256") != sha(args.readout):
        raise ValueError("Independent audit must bind to the complete E138 readout")
    main_paths, table = plot_components(readout, args.output_dir, args.table)
    predictor_paths = plot_predictor_A(readout, args.output_dir)
    table["source_readout_sha256"] = sha(args.readout)
    table["source_independent_audit_sha256"] = sha(args.audit)
    tmp = args.table.with_suffix(args.table.suffix + ".partial")
    tmp.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, args.table)
    outputs = main_paths + predictor_paths
    print(json.dumps({"status": "complete", "figures": [str(x) for x in outputs], "table": str(args.table)}, indent=2))


if __name__ == "__main__":
    main()
