#!/usr/bin/env python3
"""Plot the registered E139 free/fixed cohort summaries from stored JSON only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POPS = ("Dolma_held_positions", "POS_held_targets")
PAIRS = ("seed0_to_seed1", "seed0_to_seed2", "seed1_to_seed2")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric(record: dict, field: str) -> dict:
    value = record["summary"]["global"][field]
    if not isinstance(value, dict) or "point" not in value or len(value.get("ci95", [])) != 2:
        raise ValueError(f"Missing stored point/CI for {field}")
    return value


def add_ci(ax, x: float, value: dict, color: str, marker: str, label: str | None = None) -> None:
    point = float(value["point"])
    lo, hi = map(float, value["ci95"])
    ax.errorbar(x, point, yerr=[[point - lo], [hi - point]], color=color, marker=marker,
                linestyle="none", capsize=2.4, linewidth=1.0, markersize=5, label=label)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readout", type=Path, default=ROOT / "results/e139/readout.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/e139/figures")
    parser.add_argument("--table", type=Path, default=ROOT / "results/e139/readout_table.json")
    args = parser.parse_args()
    readout = json.loads(args.readout.read_text())
    if readout.get("experiment") != "E139" or readout.get("status") != "complete" or readout.get("errors"):
        raise ValueError("E139 readout must be complete and error-free")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    colors = {"teacher_error": "#4C78A8", "bias": "#F58518", "variance": "#54A24B"}
    protocols = ("free", "fixed")
    states = ("initial", "final")
    native_metrics = (
        ("native_mean_teacher_SSE_per_position", "Mean native Y error vs teacher", "teacher_error"),
        ("native_mean_bias_SSE_per_position", "Cohort mean bias²", "bias"),
        ("native_cohort_variance_per_position", "Within-cohort variance", "variance"),
    )
    component_metrics = (
        ("cohort_variance_per_position", "component_cohort_variance_per_position", "Σₑ Var(component)"),
        ("FP64_sum_cohort_variance_per_position", "FP64_sum_cohort_variance_per_position", "Var(FP64 component sum)"),
        ("component_cross_covariance_per_position", "component_cross_covariance_per_position", "Cross-covariance"),
    )
    categories = [(protocol, state) for protocol in protocols for state in states]
    labels = [f"{p.title()} {s}" for p, s in categories]
    fig, axes = plt.subplots(2, 2, figsize=(15.2, 9.2), squeeze=False)
    table = {
        "experiment": "E139",
        "readout_status": readout["status"],
        "readout_sha256": sha(args.readout),
        "cohort": ["seed0", "reused observed E135 seed1", "seed2"],
        "input_CI_scope": "File/word cluster bootstrap conditional on models and mappings; not seed uncertainty; pair intervals are dependent.",
        "components": {},
        "paired_free_minus_fixed": {},
        "natural_predictor_pairs": {},
        "A_pair_correspondence": {},
        "audit_state_at_plot_time": {
            "components": "results/e139/components_independent_audit.json",
            "predictor": "pending at plot time if no independent audit file exists",
            "A": "pending at plot time if no independent audit file exists",
        },
    }
    for col, pop in enumerate(POPS):
        ax_native, ax_component = axes[0, col], axes[1, col]
        x = np.arange(len(categories), dtype=float)
        table["components"][pop] = {}
        for j, (field, legend, color_key) in enumerate(native_metrics):
            for i, (protocol, state) in enumerate(categories):
                key = f"{protocol}_{state}_{pop}"
                val = metric(readout["components"][key], field)
                table["components"][pop].setdefault(key, {})[field] = val
                add_ci(ax_native, x[i] + (j - 1) * 0.16, val, colors[color_key], ("o", "s", "^")[j], legend if i == 0 else None)
        ax_native.set_title(f"{pop}: native Y error = cohort bias² + variance", fontsize=9)
        ax_native.set_xticks(x, labels, rotation=12, ha="right", fontsize=8)
        ax_native.set_ylabel("Squared native output units / position")
        ax_native.grid(axis="y", alpha=0.2)
        ax_native.legend(frameon=False, fontsize=7, loc="best")

        component_categories = []
        for protocol in ("free", "fixed"):
            component_categories.extend([(protocol, "calibration", state) for state in states])
        component_categories.extend([("fixed", "identity", state) for state in states])
        xc = np.arange(len(component_categories), dtype=float)
        table["components"][pop]["component_variance"] = {}
        for j, (cal_field, identity_field, legend) in enumerate(component_metrics):
            for i, (protocol, mapping, state) in enumerate(component_categories):
                if protocol == "fixed" and mapping == "identity":
                    base = readout["components"][f"fixed_{state}_{pop}"]["fixed_identity_reference"]
                    value = {"summary": base["summary"]}
                    key = f"fixed_identity_{state}_{pop}"
                    field = identity_field
                else:
                    key = f"{protocol}_{state}_{pop}"
                    value = readout["components"][key]
                    field = cal_field
                val = metric(value, field)
                table["components"][pop]["component_variance"][key if mapping == "calibration" else f"{key}_identity"] = {
                    "metric": val,
                    "mapping": mapping,
                }
                add_ci(ax_component, xc[i] + (j - 1) * 0.16, val, ("#4C78A8", "#F58518", "#54A24B")[j], ("o", "s", "^")[j], legend if i == 0 else None)
        ax_component.set_title(f"{pop}: components after the stated mapping", fontsize=9)
        ax_component.set_xticks(xc, [f"{p.title()}\n{m} {s}" for p, m, s in component_categories], rotation=10, ha="right", fontsize=7)
        ax_component.set_ylabel("Component variance / cross-covariance\n(squared output units / position)")
        ax_component.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
        ax_component.grid(axis="y", alpha=0.2)
        ax_component.legend(frameon=False, fontsize=7, loc="best")

        table["paired_free_minus_fixed"][pop] = {}
        for state in states:
            key = f"paired_free_minus_fixed_{state}_{pop}"
            table["paired_free_minus_fixed"][pop][state] = readout["components"][key]

    # Student-pair natural KL by protocol, and known-mapping A correlations.
    fig2, axes2 = plt.subplots(2, 2, figsize=(14.5, 8.8), squeeze=False)
    fixed_preds = readout["predictions"]["fixed_group_reference"]["predictions"]["populations"]
    group_specs = [
        ("Dolma_held_positions", axes2[0, 0], "Dolma held"),
        ("POS_held_targets", axes2[0, 1], "POS held"),
    ]
    table["natural_predictor_pairs"] = {}
    for pop, ax, title in group_specs:
        table["natural_predictor_pairs"][pop] = {}
        freepairs = readout["predictions"]["populations"][pop]["pairs"]
        fixedpairs = fixed_preds[pop]["pairs"]
        for pair_index, pair in enumerate(PAIRS):
            table["natural_predictor_pairs"][pop][pair] = {"free": freepairs[pair]["global"], "fixed": fixedpairs[pair]["global"]}
            base = pair_index
            for group, records, color, gshift in (
                ("free", freepairs, "#4C78A8", -0.16),
                ("fixed", fixedpairs, "#F58518", 0.16),
            ):
                for direction, field, marker, dshift in (
                    ("left||right", "kl_left_to_right", "o", -0.045),
                    ("right||left", "kl_right_to_left", "s", 0.045),
                ):
                    value = records[pair]["global"][field]
                    point, lo, hi = float(value["point"]), *map(float, value["ci95"])
                    ax.errorbar(base + gshift + dshift, point, yerr=[[point-lo],[hi-point]], color=color, marker=marker,
                                linestyle="none", capsize=2, linewidth=1, markersize=4,
                                label=f"{group} {direction}" if pair_index == 0 else None)
        ax.set_xticks(range(3), ["0–1", "0–2", "1–2"])
        ax.set_ylabel("Student-pair KL (nats/token)")
        ax.set_title(f"{title}: file/word input bootstrap", fontsize=9)
        ax.grid(axis="y", alpha=0.2)
        ax.legend(frameon=False, fontsize=7, ncol=2)

    ax = axes2[1, 0]
    table["A_pair_correspondence"] = {}
    A_specs = [
        ("Free Hcal map", readout["A"]["free_Hcal_component_map_pairs"], "#4C78A8", -0.22),
        ("Fixed Hcal map", readout["A"]["fixed_Hcal_component_map_pairs"], "#F58518", 0.0),
        ("Fixed known identity", readout["A"]["fixed_identity_reference"]["A"]["pairs"], "#54A24B", 0.22),
    ]
    for pair_index, pair in enumerate(PAIRS):
        table["A_pair_correspondence"][pair] = {}
        for label, records, color, shift in A_specs:
            rec = records[pair]
            value = rec["held_conditional_columns"]
            ci = rec.get("ci95")
            table["A_pair_correspondence"][pair][label] = {"point": value.get("mean"), "ci95": ci, "coverage_comparable": rec.get("coverage_comparable"), "n_valid_columns": value.get("n_valid_columns")}
            point, lo, hi = float(value["mean"]), *map(float, ci)
            ax.errorbar(pair_index + shift, point, yerr=[[point-lo],[hi-point]], color=color, marker="o", linestyle="none", capsize=2.5, markersize=4,
                        label=label if pair_index == 0 else None)
    ax.set_xticks(range(3), ["0–1", "0–2", "1–2"])
    ax.set_ylabel("Mean held expert-column ρ")
    ax.set_title("Mapped A correspondence (48-word bootstrap)\nFree Hcal=blue · Fixed Hcal=orange · Fixed identity=green", fontsize=9)
    ax.axhline(0, color="#555555", linestyle="--", linewidth=0.8)
    ax.grid(axis="y", alpha=0.2)
    ax = axes2[1, 1]
    ax.axis("off")
    ax.set_title("Scope")
    ax.text(0.02, 0.92,
            "Free-map alignment is fitted once per state on training-only Hcal using seed1 as the registered anchor. Fixed Hcal maps use the same procedure; known identity is separate.\n\n"
            "All intervals describe input-cluster uncertainty conditional on maps and the fixed three-student cohort, not seed uncertainty or uncertainty from refitting maps.\n\n"
            "Free vs fixed changes the complete protocol (teacher routing information, frozen gate and related gradient/regularization coupling); it is not an isolated routing-cause estimate.",
            transform=ax.transAxes, va="top", fontsize=8.5, wrap=True)

    fig.suptitle("E139 — Free/fixed finite-cohort output and component comparison", fontsize=14, y=0.98)
    fig.text(0.5, 0.018,
             "Three fixed students include the previously observed seed1 pilot. Native Y is mapping-independent; component panels separate free/fixed Hcal and fixed identity. "
             "POS zero target-on experts are retained: free seed0 11/57, free seed2 6, fixed 42/51/52. A-group differences include support/gate/mask/mapping and row-centered mean effects, not pure content. "
             "File/word CIs are not seed CIs; pair observations are dependent. No same-function or unique-role claim.",
             ha="center", fontsize=7.5, wrap=True)
    fig2.suptitle("E139 — Student-pair natural KL and A", fontsize=14, y=0.98)
    fig2.text(0.5, 0.018,
              "Dolma uses BF16 whole logits → FP32 log-softmax; POS uses BF16 backbone and genuine FP32 final head. CIs resample files/words, not student pairs or seeds.",
              ha="center", fontsize=7.5, wrap=True)
    for figx in (fig, fig2):
        figx.subplots_adjust(left=0.07, right=0.99, bottom=0.12, top=0.90, hspace=0.48, wspace=0.33)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for target, stems in ((fig, ("finite_cohort_components",)), (fig2, ("predictor_A",))):
        for stem in stems:
            for fmt in ("png", "pdf"):
                path = args.output_dir / f"{stem}.{fmt}"
                tmp = path.with_name(path.stem + ".partial" + path.suffix)
                target.savefig(tmp, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
                os.replace(tmp, path)
                outputs.append(str(path))
    plt.close(fig); plt.close(fig2)

    audit_paths = [ROOT / "results/e139/components_independent_audit.json", ROOT / "results/e139/predictor_independent_audit.json", ROOT / "results/e139/A_independent_audit.json"]
    audit_state = {}
    for path in audit_paths:
        audit_state[path.name] = json.loads(path.read_text()).get("status") if path.exists() else "pending"
    table["readout_status"] = readout["status"]
    table["source_readout_sha256"] = sha(args.readout)
    table["POS_support_and_A_interpretation"] = {
        "free_seed0_zero_target_on_experts": [11, 57],
        "free_seed2_zero_target_on_experts": [6],
        "fixed_zero_target_on_experts": [42, 51, 52],
        "all_columns_retained": True,
        "A_difference_caveat": "Free/fixed A difference includes support, gate, mask, mapping and row-centered mean effects; it is not a pure expert-content comparison.",
    }
    table["independent_audit_status_at_plot_time"] = audit_state
    table["archive_seal_ready"] = all(value not in ("pending", None) for value in audit_state.values())
    args.table.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.table.with_suffix(args.table.suffix + ".partial")
    tmp.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, args.table)
    print(json.dumps({"status": "complete", "outputs": outputs, "table": str(args.table), "archive_seal_ready": table["archive_seal_ready"]}, indent=2))


if __name__ == "__main__":
    main()
