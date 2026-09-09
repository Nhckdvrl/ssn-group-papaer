#!/usr/bin/env python3
"""Summarize E10 behavior with base decisions as independent units."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def unit_metrics(frame):
    valid = frame.dropna(subset=["underlying_choice"]).copy()
    valid["choose_a"] = (valid.underlying_choice == "A").astype(float)
    rates = valid.groupby(["prospect", "frame", "order"]).choose_a.mean()
    units = []
    for prospect in sorted(frame.prospect.unique()):
        gain = np.mean([rates.get((prospect, "gain", order), np.nan) for order in CONFIG["orders"]])
        loss = np.mean([rates.get((prospect, "loss", order), np.nan) for order in CONFIG["orders"]])
        order_consistency = np.mean([
            1 - abs(
                rates.get((prospect, framing, "ab"), np.nan)
                - rates.get((prospect, framing, "ba"), np.nan)
            )
            for framing in CONFIG["frames"]
        ])
        part = valid[valid.prospect == prospect]
        units.append({
            "prospect": prospect,
            "frame_consistency": float(1 - abs(gain - (1 - loss))),
            "order_consistency": float(order_consistency),
            "ev_consistent_rate": float(
                (part.underlying_choice == part.gold_underlying).mean()
            ),
            "valid_rate": float(
                frame[frame.prospect == prospect].underlying_choice.notna().mean()
            ),
            "ev_gap_stratum": frame[frame.prospect == prospect].ev_gap_stratum.iloc[0],
            "probability_gap_stratum": frame[
                frame.prospect == prospect
            ].probability_gap_stratum.iloc[0],
            "payoff_scale": frame[frame.prospect == prospect].payoff_scale.iloc[0],
        })
    return pd.DataFrame(units)


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    draws = values[indexes].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def main():
    frames = {
        branch: pd.read_json(OUT / branch / "raw.jsonl", lines=True)
        for branch in ["instruct_sft", "think_sft"]
    }
    units = {branch: unit_metrics(frame) for branch, frame in frames.items()}
    summary = {"design": "L12-E10 independent-decision behavioral breadth"}
    for offset, branch in enumerate(["instruct_sft", "think_sft"]):
        summary[branch] = {
            "n_generations": int(len(frames[branch])),
            "n_base_decisions": int(len(units[branch])),
            "n_analyzable_base_decisions": int(
                units[branch].frame_consistency.notna().sum()
            ),
            "valid_rate": float(frames[branch].underlying_choice.notna().mean()),
            "complete_cell_rate": float(
                (
                    frames[branch]
                    .groupby(["prospect", "frame", "order"])
                    .underlying_choice.count()
                    == CONFIG["samples_per_cell"]
                ).mean()
            ),
            **{
                metric: {
                    "mean": float(units[branch][metric].mean()),
                    "base_decision_bootstrap_ci95": bootstrap(
                        units[branch][metric], CONFIG["seed"] + offset * 10 + index
                    ),
                }
                for index, metric in enumerate([
                    "frame_consistency", "order_consistency", "ev_consistent_rate"
                ])
            },
        }
    paired = units["think_sft"].merge(
        units["instruct_sft"], on="prospect", suffixes=("_think", "_instruct")
    )
    paired["frame_consistency_difference"] = (
        paired.frame_consistency_think - paired.frame_consistency_instruct
    )
    observed = paired.frame_consistency_difference.dropna()
    missing = paired.frame_consistency_think.isna()
    lower = paired.frame_consistency_difference.copy()
    upper = paired.frame_consistency_difference.copy()
    lower.loc[missing] = -paired.loc[missing, "frame_consistency_instruct"]
    upper.loc[missing] = 1 - paired.loc[missing, "frame_consistency_instruct"]
    summary["think_minus_instruct"] = {
        "frame_consistency": {
            "n_analyzable_base_decisions": int(len(observed)),
            "mean": float(observed.mean()),
            "base_decision_bootstrap_ci95": bootstrap(
                observed, CONFIG["seed"] + 100
            ),
            "positive_unit_fraction": float(
                (observed > 0).mean()
            ),
            "missing_unit_worst_case_mean_bounds": [
                float(lower.mean()), float(upper.mean())
            ],
        }
    }
    with (OUT / "behavior_unit_metrics.jsonl").open("w") as handle:
        for row in paired.to_dict(orient="records"):
            handle.write(json.dumps(row) + "\n")
    (OUT / "behavior_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
