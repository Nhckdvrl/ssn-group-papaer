#!/usr/bin/env python3
"""Summarize E002b while keeping candidate-position robustness explicit."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--run-id", default="e002b_counterbalanced")
    args = parser.parse_args()
    project = args.project.resolve()
    run_dir = project / "results" / args.run_id
    model_dirs = sorted(path for path in run_dir.iterdir() if (path / "predictions.jsonl").exists())
    if not model_dirs:
        raise ValueError(f"No model outputs under {run_dir}")

    output = {"run_id": args.run_id, "models": {}}
    for model_dir in model_dirs:
        rows = list(map(json.loads, (model_dir / "predictions.jsonl").read_text().splitlines()))
        by_condition = defaultdict(list)
        by_pair = defaultdict(dict)
        for row in rows:
            by_condition[row["condition"]].append(row)
            by_pair[(row["item_id"], row["condition"])][row["candidate_order"]] = row

        robust = {}
        disagreement = {}
        for condition in by_condition:
            pairs = [value for (item_id, name), value in by_pair.items() if name == condition]
            if not all(set(pair) == {"old_first", "new_first"} for pair in pairs):
                raise ValueError(f"Incomplete position pair for {model_dir.name}/{condition}")
            robust[condition] = sum(
                pair["old_first"]["correct"] and pair["new_first"]["correct"] for pair in pairs
            ) / len(pairs)
            disagreement[condition] = sum(
                pair["old_first"]["predicted_semantic"] != pair["new_first"]["predicted_semantic"]
                for pair in pairs
            ) / len(pairs)

        condition_accuracy = {
            condition: sum(row["correct"] for row in values) / len(values)
            for condition, values in by_condition.items()
        }
        flat_accuracy = (
            condition_accuracy["original_then_correction"]
            + condition_accuracy["correction_then_original"]
        ) / 2
        flat_robust = (
            robust["original_then_correction"] + robust["correction_then_original"]
        ) / 2
        output["models"][model_dir.name] = {
            "n_predictions": len(rows),
            "condition_accuracy": condition_accuracy,
            "position_robust_accuracy": robust,
            "position_semantic_disagreement_rate": disagreement,
            "flat_accuracy_mean_orders": flat_accuracy,
            "flat_position_robust_mean_orders": flat_robust,
            "explicit_minus_flat_accuracy": condition_accuracy["explicit_update"] - flat_accuracy,
            "unrelated_false_override_rate": 1 - condition_accuracy["unrelated_correction"],
        }

    model_values = list(output["models"].values())
    output["macro_across_models"] = {
        "flat_accuracy_mean_orders": sum(m["flat_accuracy_mean_orders"] for m in model_values) / len(model_values),
        "flat_position_robust_mean_orders": sum(m["flat_position_robust_mean_orders"] for m in model_values) / len(model_values),
        "explicit_update_accuracy": sum(m["condition_accuracy"]["explicit_update"] for m in model_values) / len(model_values),
        "correction_only_accuracy": sum(m["condition_accuracy"]["correction_only"] for m in model_values) / len(model_values),
        "original_only_accuracy": sum(m["condition_accuracy"]["original_only"] for m in model_values) / len(model_values),
        "unrelated_correction_accuracy": sum(m["condition_accuracy"]["unrelated_correction"] for m in model_values) / len(model_values),
    }
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
