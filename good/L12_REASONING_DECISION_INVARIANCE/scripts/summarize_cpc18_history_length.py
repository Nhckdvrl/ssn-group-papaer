#!/usr/bin/env python3
"""Summarize the paired 20/100 finite-evidence diagnostic."""

import json

import numpy as np
import pandas as pd

from cpc18_history_length_common import CONFIG, ROOT


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))].mean(axis=1)
    return [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))]


def cell(cell):
    total = len(cell); a = int((cell.underlying_choice == "A").sum()); valid = int(cell.underlying_choice.notna().sum())
    return (a / valid if valid else np.nan), a / total, (a + total - valid) / total


def consistency(x, y):
    observed = 1 - abs(x[0] - y[0])
    lower = 1 - max(abs(x[1] - y[2]), abs(x[2] - y[1]))
    upper = 1 - max(0.0, x[1] - y[2], y[1] - x[2])
    return observed, lower, upper


def units(frame):
    rows = []
    for problem, part in frame.groupby("problem"):
        for length in CONFIG["history_lengths"]:
            values = []
            for replicate in range(CONFIG["histories_per_problem"]):
                for order in CONFIG["orders"]:
                    explicit = cell(part[(part.presentation == "explicit") & (part.order == order)])
                    history = cell(part[(part.history_length == length) & (part.history_replicate == replicate) & (part.order == order)])
                    values.append(consistency(explicit, history))
            values = np.asarray(values).mean(axis=0)
            rows.append({
                "problem": problem, "history_length": length,
                "presentation_consistency": float(values[0]),
                "presentation_consistency_lower": float(values[1]),
                "presentation_consistency_upper": float(values[2]),
                "valid_rate": float(part[(part.presentation == "explicit") | (part.history_length == length)].valid.mean()),
            })
    return pd.DataFrame(rows)


def report(values, seed):
    return {"mean": float(values.mean()), "base_decision_bootstrap_ci95": bootstrap(values, seed), "positive_base_decision_fraction": float((values > 0).mean())}


def main():
    output = ROOT / CONFIG["result_dir"]
    unit = {}
    summary = {"design": "L12 paired 20/100 finite-evidence diagnostic"}
    for offset, spec in enumerate(CONFIG["regimes"]):
        name = spec["name"]
        raw = pd.read_json(output / "raw" / f"{name}.jsonl", lines=True)
        unit[name] = units(raw)
        summary[name] = {"pair": spec["pair"], "role": spec["role"], "n_generations": int(len(raw)), "valid_rate": float(raw.valid.mean()), "history_lengths": {}}
        for index, length in enumerate(CONFIG["history_lengths"]):
            part = unit[name][unit[name].history_length == length]
            entry = report(part.presentation_consistency, CONFIG["seed"] + offset * 10 + index)
            entry["invalid_assignment_mean_bounds"] = [float(part.presentation_consistency_lower.mean()), float(part.presentation_consistency_upper.mean())]
            summary[name]["history_lengths"][str(length)] = entry
    summary["reasoning_minus_standard"] = {}
    rows = []
    for pair_index, pair in enumerate(("olmo_sft", "qwen_mode")):
        specs = [item for item in CONFIG["regimes"] if item["pair"] == pair]
        reasoning = next(item["name"] for item in specs if item["role"] == "reasoning")
        standard = next(item["name"] for item in specs if item["role"] == "standard")
        pair_summary = {"reasoning_regime": reasoning, "standard_regime": standard, "history_lengths": {}}
        differences = {}
        for index, length in enumerate(CONFIG["history_lengths"]):
            r = unit[reasoning][unit[reasoning].history_length == length]
            s = unit[standard][unit[standard].history_length == length]
            joined = r.merge(s, on=["problem", "history_length"], suffixes=("_reasoning", "_standard"))
            values = joined.presentation_consistency_reasoning - joined.presentation_consistency_standard
            entry = report(values, CONFIG["seed"] + 100 + pair_index * 10 + index)
            entry["invalid_assignment_mean_bounds"] = [
                float((joined.presentation_consistency_lower_reasoning - joined.presentation_consistency_upper_standard).mean()),
                float((joined.presentation_consistency_upper_reasoning - joined.presentation_consistency_lower_standard).mean()),
            ]
            pair_summary["history_lengths"][str(length)] = entry
            differences[length] = joined.set_index("problem").presentation_consistency_reasoning - joined.set_index("problem").presentation_consistency_standard
            rows.extend({"pair": pair, **row} for row in joined.to_dict(orient="records"))
        change = differences[100] - differences[20]
        pair_summary["difference_100_minus_20"] = report(change, CONFIG["seed"] + 120 + pair_index)
        summary["reasoning_minus_standard"][pair] = pair_summary
    with (output / "behavior_unit_metrics.jsonl").open("w") as handle:
        for row in rows: handle.write(json.dumps(row) + "\n")
    (output / "behavior_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
