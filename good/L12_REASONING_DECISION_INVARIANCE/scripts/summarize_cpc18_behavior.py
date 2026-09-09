#!/usr/bin/env python3
"""Summarize CPC18 presentation behavior with base decisions as clusters."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from cpc18_common import CONFIG, ROOT


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    draws = values[indexes].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def unit_metrics(frame):
    valid = frame.dropna(subset=["underlying_choice"]).copy()
    valid["choose_a"] = (valid.underlying_choice == "A").astype(float)
    valid["choose_ev"] = (
        valid.underlying_choice == valid.ev_choice
    ).astype(float)
    rates = valid.groupby(
        ["problem", "presentation", "history_id", "order"], dropna=False
    ).choose_a.mean()
    rows = []
    for problem in sorted(frame.problem.unique()):
        part = frame[frame.problem == problem]
        histories = sorted(part.history_id.dropna().unique())
        consistencies = []
        for history in histories:
            for order in CONFIG["orders"]:
                explicit = rates.get((problem, "explicit", np.nan, order), np.nan)
                if np.isnan(explicit):
                    explicit_rows = valid[
                        (valid.problem == problem)
                        & (valid.presentation == "explicit")
                        & (valid.order == order)
                    ]
                    explicit = explicit_rows.choose_a.mean()
                experienced = rates.get((problem, "history", history, order), np.nan)
                consistencies.append(1 - abs(explicit - experienced))
        order_consistencies = []
        for presentation, history in [("explicit", None)] + [
            ("history", value) for value in histories
        ]:
            subset = valid[
                (valid.problem == problem)
                & (valid.presentation == presentation)
            ]
            if history is not None:
                subset = subset[subset.history_id == history]
            order_rates = subset.groupby("order").choose_a.mean()
            order_consistencies.append(
                1 - abs(order_rates.get("ab", np.nan) - order_rates.get("ba", np.nan))
            )
        valid_part = valid[valid.problem == problem]
        rows.append({
            "problem": problem,
            "presentation_consistency": float(np.nanmean(consistencies)),
            "order_consistency": float(np.nanmean(order_consistencies)),
            "explicit_ev_rate": float(
                valid_part[valid_part.presentation == "explicit"].choose_ev.mean()
            ),
            "history_ev_rate": float(
                valid_part[valid_part.presentation == "history"].choose_ev.mean()
            ),
            "valid_rate": float(part.valid.mean()),
            "support_dominance": bool(part.support_dominance.iloc[0]),
            "outcome_complexity": int(part.outcome_complexity.iloc[0]),
            "relative_ev_gap": float(part.relative_ev_gap.iloc[0]),
        })
    return pd.DataFrame(rows)


def main():
    out = ROOT / CONFIG["result_dir"]
    frames = {}
    units = {}
    for spec in CONFIG["regimes"]:
        path = out / "raw" / f"{spec['name']}.jsonl"
        frames[spec["name"]] = pd.read_json(path, lines=True)
        units[spec["name"]] = unit_metrics(frames[spec["name"]])

    summary = {"design": "L12-E17 CPC18 description/history behavioral breadth"}
    metrics = [
        "presentation_consistency", "order_consistency",
        "explicit_ev_rate", "history_ev_rate",
    ]
    for offset, spec in enumerate(CONFIG["regimes"]):
        name = spec["name"]
        summary[name] = {
            "pair": spec["pair"],
            "role": spec["role"],
            "n_generations": int(len(frames[name])),
            "n_base_decisions": int(len(units[name])),
            "valid_rate": float(frames[name].valid.mean()),
        }
        for metric_index, metric in enumerate(metrics):
            values = units[name][metric]
            summary[name][metric] = {
                "mean": float(values.mean()),
                "base_decision_bootstrap_ci95": bootstrap(
                    values, CONFIG["seed"] + offset * 10 + metric_index
                ),
            }

    summary["reasoning_minus_standard"] = {}
    unit_output = []
    for pair_index, pair in enumerate(sorted({s["pair"] for s in CONFIG["regimes"]})):
        members = [s for s in CONFIG["regimes"] if s["pair"] == pair]
        reasoning = next(s for s in members if s["role"] == "reasoning")["name"]
        standard = next(s for s in members if s["role"] == "standard")["name"]
        joined = units[reasoning].merge(
            units[standard], on="problem", suffixes=("_reasoning", "_standard")
        )
        joined["presentation_consistency_difference"] = (
            joined.presentation_consistency_reasoning
            - joined.presentation_consistency_standard
        )
        values = joined.presentation_consistency_difference
        summary["reasoning_minus_standard"][pair] = {
            "reasoning_regime": reasoning,
            "standard_regime": standard,
            "n_paired_base_decisions": int(len(joined)),
            "presentation_consistency_difference": {
                "mean": float(values.mean()),
                "base_decision_bootstrap_ci95": bootstrap(
                    values, CONFIG["seed"] + 100 + pair_index
                ),
                "positive_base_decision_fraction": float((values > 0).mean()),
            },
        }
        for row in joined.to_dict(orient="records"):
            unit_output.append({"pair": pair, **row})

    with (out / "behavior_unit_metrics.jsonl").open("w") as handle:
        for row in unit_output:
            handle.write(json.dumps(row) + "\n")
    (out / "behavior_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
