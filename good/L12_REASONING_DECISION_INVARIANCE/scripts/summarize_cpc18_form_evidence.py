#!/usr/bin/env python3
"""Summarize preregistered E20 selective sensitivity by base decision."""

import json

import numpy as np
import pandas as pd

from cpc18_form_evidence_common import CONFIG, ROOT


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def cell_stats(cell):
    total = len(cell)
    a_count = int((cell.underlying_choice == "A").sum())
    valid = int(cell.underlying_choice.notna().sum())
    conditional = a_count / valid if valid else np.nan
    return conditional, a_count / total, (a_count + total - valid) / total


def abs_difference(x, y):
    observed = abs(x[0] - y[0])
    lower = max(0.0, x[1] - y[2], y[1] - x[2])
    upper = max(abs(x[1] - y[2]), abs(x[2] - y[1]))
    return observed, lower, upper


def signed_difference(a, b):
    return a[0] - b[0], a[1] - b[2], a[2] - b[1]


def unit_metrics(frame):
    rows = []
    for problem, part in frame.groupby("problem"):
        cells = {}
        for evidence in ("A", "B"):
            for form in ("raw", "summary"):
                for order in CONFIG["orders"]:
                    cells[evidence, form, order] = cell_stats(part[
                        (part.evidence_choice == evidence)
                        & (part.form == form)
                        & (part.order == order)
                    ])
        form_effects = [
            abs_difference(cells[evidence, "raw", order], cells[evidence, "summary", order])
            for evidence in ("A", "B") for order in CONFIG["orders"]
        ]
        evidence_effects = [
            signed_difference(cells["A", form, order], cells["B", form, order])
            for form in ("raw", "summary") for order in CONFIG["orders"]
        ]
        form_values = np.asarray(form_effects).mean(axis=0)
        evidence_values = np.asarray(evidence_effects).mean(axis=0)
        rows.append({
            "problem": problem,
            "source_split": part.source_split.iloc[0],
            "form_sensitivity": float(form_values[0]),
            "form_sensitivity_lower": float(form_values[1]),
            "form_sensitivity_upper": float(form_values[2]),
            "evidence_sensitivity": float(evidence_values[0]),
            "evidence_sensitivity_lower": float(evidence_values[1]),
            "evidence_sensitivity_upper": float(evidence_values[2]),
            "selective_sensitivity": float(evidence_values[0] - form_values[0]),
            "selective_sensitivity_lower": float(evidence_values[1] - form_values[2]),
            "selective_sensitivity_upper": float(evidence_values[2] - form_values[1]),
            "valid_rate": float(part.valid.mean()),
        })
    return pd.DataFrame(rows)


def summarize_metric(values, seed):
    return {
        "mean": float(values.mean()),
        "base_decision_bootstrap_ci95": bootstrap(values, seed),
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def main():
    output = ROOT / CONFIG["result_dir"]
    units = {}
    frames = {}
    summary = {
        "design": "L12-E20 preregistered form-by-evidence decomposition",
        "unit_of_analysis": "base decision",
    }
    metrics = ("form_sensitivity", "evidence_sensitivity", "selective_sensitivity")
    for offset, spec in enumerate(CONFIG["regimes"]):
        name = spec["name"]
        frames[name] = pd.read_json(output / "raw" / f"{name}.jsonl", lines=True)
        units[name] = unit_metrics(frames[name])
        summary[name] = {
            "pair": spec["pair"], "role": spec["role"],
            "n_generations": int(len(frames[name])),
            "n_base_decisions": int(len(units[name])),
            "valid_rate": float(frames[name].valid.mean()),
        }
        for index, metric in enumerate(metrics):
            summary[name][metric] = summarize_metric(
                units[name][metric], CONFIG["seed"] + offset * 10 + index
            )
            summary[name][metric]["invalid_assignment_mean_bounds"] = [
                float(units[name][f"{metric}_lower"].mean()),
                float(units[name][f"{metric}_upper"].mean()),
            ]

    output_rows = []
    summary["reasoning_minus_standard"] = {}
    for pair_index, pair in enumerate(("olmo_sft", "qwen_mode")):
        specs = [item for item in CONFIG["regimes"] if item["pair"] == pair]
        reasoning = next(item["name"] for item in specs if item["role"] == "reasoning")
        standard = next(item["name"] for item in specs if item["role"] == "standard")
        joined = units[reasoning].merge(
            units[standard], on=["problem", "source_split"],
            suffixes=("_reasoning", "_standard"),
        )
        pair_summary = {
            "reasoning_regime": reasoning,
            "standard_regime": standard,
            "n_paired_base_decisions": int(len(joined)),
        }
        for index, metric in enumerate(metrics):
            values = joined[f"{metric}_reasoning"] - joined[f"{metric}_standard"]
            pair_summary[f"{metric}_difference"] = summarize_metric(
                values, CONFIG["seed"] + 100 + pair_index * 10 + index
            )
            pair_summary[f"{metric}_difference"]["invalid_assignment_mean_bounds"] = [
                float((joined[f"{metric}_lower_reasoning"] - joined[f"{metric}_upper_standard"]).mean()),
                float((joined[f"{metric}_upper_reasoning"] - joined[f"{metric}_lower_standard"]).mean()),
            ]
        summary["reasoning_minus_standard"][pair] = pair_summary
        output_rows.extend({"pair": pair, **row} for row in joined.to_dict(orient="records"))

    with (output / "behavior_unit_metrics.jsonl").open("w") as handle:
        for row in output_rows:
            handle.write(json.dumps(row) + "\n")
    (output / "behavior_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
