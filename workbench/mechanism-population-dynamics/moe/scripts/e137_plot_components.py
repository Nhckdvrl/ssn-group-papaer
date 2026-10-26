#!/usr/bin/env python3
"""Plot E137 component statistics already present in the primary and independent summaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POPS = ("Dolma_held_positions", "POS_held_targets")
CONDITIONS = ("teacher", "copy", "oracle_initial", "oracle_final")
MEASURES = (
    "on_relative_teacher_energy", "off_relative_teacher_energy",
    "component_delta_SSE_per_position", "FP64_sum_delta_SSE_per_position", "cross_term_per_position", "FP64_reference_cross_term_per_position",
    "native_aggregate_delta_SSE_per_position", "native_minus_FP32_sum_delta_SSE_per_position",
    "FP32_subtract_reduce_path_difference_SSE_per_position", "FP32_minus_FP64_sum_delta_SSE_per_position",
    "condition_product_floor_SSE_per_position", "condition_sum_to_native_floor_SSE_per_position",
    "teacher_product_floor_SSE_per_position", "teacher_sum_to_native_floor_SSE_per_position",
    "teacher_query_on_shape_floor_MSE", "condition_query_on_shape_floor_MSE",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "results/e137/components.json")
    parser.add_argument("--audit", type=Path, default=ROOT / "results/e137/independent_audit.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e137/figures")
    parser.add_argument("--table", type=Path, default=ROOT / "results/e137/readout_table.json")
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    audit = json.loads(args.audit.read_text())
    if summary.get("experiment") != "E137" or summary.get("status") != "complete" or summary.get("errors"):
        raise ValueError("E137 component summary must be complete and error-free")
    if audit.get("experiment") != "E137" or audit.get("status") != "complete":
        raise ValueError("E137 independent audit must be complete")
    if audit.get("primary_summary_sha256") != sha(args.summary):
        raise ValueError("Independent audit is not bound to this summary")

    # Assemble a transparent table from the persisted cluster-bootstrap summaries;
    # no arrays are reloaded and no statistic or interval is recomputed here.
    table = {
        "experiment": "E137",
        "source_summary_sha256": sha(args.summary),
        "source_independent_audit_sha256": sha(args.audit),
        "scope": "Existing fixed-population pooled sufficient statistics; bootstrap resamples input clusters, not seeds.",
        "populations": {},
    }
    for pop in POPS:
        primary = summary["populations"][pop]
        independent = audit["populations"][pop]
        if primary.get("status") != "complete" or set(primary.get("conditions", {})) != {"copy", "oracle_initial", "oracle_final"}:
            raise ValueError(f"Incomplete persisted population: {pop}")
        table["populations"][pop] = {
            "positions": primary["positions"],
            "sequences": primary["sequences"],
            "cluster": independent["cluster"],
            "clusters": independent["clusters"],
            "counts_and_teacher_energy_per_occurrence": independent["conditions"]["copy"]["totals"],
            "zero_on_support_experts": independent["conditions"]["copy"]["zero_on_support_experts"],
            "conditions": {},
        }
        for condition in ("copy", "oracle_initial", "oracle_final"):
            pmetrics = primary["conditions"][condition]["global"]
            imetrics = independent["conditions"][condition]["global"]
            # The independent audit already verified each primary point and CI.
            row = {}
            for metric in MEASURES:
                x = imetrics[metric]
                row[metric] = {"point": x["point"], "ci95": x["ci95"], "defined_draws": x["defined_draws"]}
                primary_metric = pmetrics[metric]
                if abs(float(primary_metric["point"]) - float(x["point"])) > 1e-12:
                    raise ValueError(f"Primary/audit point differs: {pop}/{condition}/{metric}")
                if len(primary_metric["ci95"]) != 2 or len(x["ci95"]) != 2:
                    raise ValueError(f"Missing stored interval: {pop}/{condition}/{metric}")
            table["populations"][pop]["conditions"][condition] = row
        # Native teacher is the identity reference by construction, not a resampled condition.
        table["populations"][pop]["conditions"]["teacher_reference"] = {
            "identity_reference": True,
            "point_values": {metric: 0.0 for metric in MEASURES},
            "ci95": None,
            "note": "Native teacher against itself; exact zero identity reference, not an independently sampled condition.",
        }

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(2, 2, figsize=(15.5, 9.5), squeeze=False)
    pop_specs = [
        ("Dolma_held_positions", axes[0, 0], axes[1, 0], "Dolma held positions"),
        ("POS_held_targets", axes[0, 1], axes[1, 1], "POS held targets"),
    ]
    names = {"teacher": "Teacher\nreference", "copy": "Exact copy", "oracle_initial": "Oracle\ninitial", "oracle_final": "Oracle\nfinal"}
    colors = {"teacher": "#555555", "copy": "#72B7B2", "oracle_initial": "#E45756", "oracle_final": "#4C78A8"}

    for pop, ax_content, ax_decomp, title in pop_specs:
        info = table["populations"][pop]
        totals = info["counts_and_teacher_energy_per_occurrence"]
        ax_content.set_title(
            f"{title}: n={int(info['positions']):,}; {info['clusters']} {info['cluster']} clusters\n"
            f"on/off count={int(totals['on_count']):,}/{int(totals['off_count']):,}; "
            f"teacher energy/count={totals['on_teacher_energy_per_occurrence']:.3g}/{totals['off_teacher_energy_per_occurrence']:.3g}",
            fontsize=9,
        )
        ax_decomp.set_title(f"{title}: squared output units per position", fontsize=10)

        # Content error normalized by the corresponding on/off teacher energy.
        x = np.arange(len(CONDITIONS), dtype=float)
        for metric, label, marker, shift in (
            ("on_relative_teacher_energy", "On-support content SSE / teacher energy", "o", -0.11),
            ("off_relative_teacher_energy", "Off-support content SSE / teacher energy", "s", 0.11),
        ):
            for i, condition in enumerate(CONDITIONS):
                if condition == "teacher":
                    point, ci = 0.0, None
                else:
                    stat = table["populations"][pop]["conditions"][condition][metric]
                    point, ci = float(stat["point"]), stat["ci95"]
                xp = x[i] + shift
                if ci is not None:
                    lo, hi = map(float, ci)
                    ax_content.vlines(xp, lo, hi, color=colors[condition], linewidth=1.2)
                ax_content.plot(xp, point, marker=marker, color=colors[condition], linestyle="none")
            ax_content.plot([], [], color="#444444", marker=marker, linestyle="none", label=label)
        ax_content.set_xticks(x, [names[c] for c in CONDITIONS], fontsize=8)
        ax_content.set_ylabel("Pooled content error / its teacher energy (unitless)")
        ax_content.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
        ax_content.grid(axis="y", alpha=0.2)
        ax_content.legend(frameon=False, fontsize=7, loc="upper left")

        # Component energy identity, keeping all three quantities in matching units.
        series = [
            ("component_delta_SSE_per_position", "Σₑ ||δₑ||² / position", "o", -0.20),
            ("FP64_sum_delta_SSE_per_position", "||Σₑ δₑ||², FP64 / position", "s", 0.0),
            ("FP64_reference_cross_term_per_position", "FP64 cross-term / position", "^", 0.20),
        ]
        for metric, label, marker, shift in series:
            for i, condition in enumerate(CONDITIONS):
                if condition == "teacher":
                    point, ci = 0.0, None
                else:
                    stat = table["populations"][pop]["conditions"][condition][metric]
                    point, ci = float(stat["point"]), stat["ci95"]
                xp = x[i] + shift
                if ci is not None:
                    lo, hi = map(float, ci)
                    ax_decomp.vlines(xp, lo, hi, color=colors[condition], linewidth=1.1)
                ax_decomp.plot(xp, point, marker=marker, color=colors[condition], linestyle="none")
            ax_decomp.plot([], [], color="#444444", marker=marker, linestyle="none", label=label)
        ax_decomp.set_xticks(x, [names[c] for c in CONDITIONS], fontsize=8)
        ax_decomp.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
        ax_decomp.grid(axis="y", alpha=0.2)
        ax_decomp.legend(frameon=False, fontsize=7, loc="best")

    # Explicit support-boundary note; these experts remain in the data and table.
    pos_zero = table["populations"]["POS_held_targets"]["zero_on_support_experts"]
    fig.suptitle("E137 — Native-support component error and aggregation", fontsize=14, y=0.98)
    fig.text(
        0.5, 0.012,
        f"Intervals resample input clusters (Dolma source files; POS words), not seeds. Teacher is an exact identity reference; copy is measured. "
        f"POS experts {','.join(map(str, pos_zero))} have on_count=0 and remain included. POS values pool 512 targets; they are not equal-word averages or prior KL/NLL. "
        "Cross-term is the FP64 aggregate-minus-component covariance identity in matching squared-output units/position, not semantic collaboration. Native aggregate/product/shape rounding floors and FP32−FP64 sum residual are separate columns in readout_table.json.",
        ha="center", fontsize=7.5, wrap=True,
    )
    fig.subplots_adjust(left=0.065, right=0.99, bottom=0.13, top=0.90, hspace=0.56, wspace=0.34)
    for fmt, filename in (("png", "support_components.png"), ("pdf", "support_components.pdf")):
        args.output_dir.mkdir(parents=True, exist_ok=True)
        path = args.output_dir / filename
        tmp = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(tmp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(tmp, path)
    plt.close(fig)
    args.table.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.table.with_suffix(args.table.suffix + ".partial")
    tmp.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, args.table)
    print(json.dumps({"status": "complete", "png": str(args.output_dir / "support_components.png"), "pdf": str(args.output_dir / "support_components.pdf"), "table": str(args.table)}, indent=2))


if __name__ == "__main__":
    main()
