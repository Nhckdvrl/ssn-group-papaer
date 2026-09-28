#!/usr/bin/env python3
"""Summarize E13 behavior with base decisions as independent units."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/qwen_mode_validation.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def unit_metrics(frame):
    valid = frame.dropna(subset=["underlying_choice"]).copy()
    valid["choose_a"] = (valid.underlying_choice == "A").astype(float)
    rates = valid.groupby(["prospect", "frame", "order"]).choose_a.mean()
    rows = []
    for prospect in sorted(frame.prospect.unique()):
        frame_consistency = np.mean([
            1 - abs(
                rates.get((prospect, "gain", order), np.nan)
                - (1 - rates.get((prospect, "loss", order), np.nan))
            )
            for order in CONFIG["orders"]
        ])
        part = valid[valid.prospect == prospect]
        rows.append({
            "prospect": prospect,
            "frame_consistency": float(frame_consistency),
            "ev_consistent_rate": float(
                (part.underlying_choice == part.gold_underlying).mean()
            ),
            "valid_rate": float(
                frame[frame.prospect == prospect].underlying_choice.notna().mean()
            ),
        })
    return pd.DataFrame(rows)


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main():
    frames = {
        mode: pd.read_json(OUT / f"{mode}.jsonl", lines=True)
        for mode in CONFIG["modes"]
    }
    units = {mode: unit_metrics(frame) for mode, frame in frames.items()}
    summary = {"design": "L12-E13 Qwen3 same-weight hard-mode behavior"}
    for offset, mode in enumerate(CONFIG["modes"]):
        summary[mode] = {
            "n_generations": int(len(frames[mode])),
            "n_base_decisions": int(len(units[mode])),
            "n_analyzable_base_decisions": int(
                units[mode].frame_consistency.notna().sum()
            ),
            "valid_rate": float(frames[mode].underlying_choice.notna().mean()),
            "frame_consistency": {
                "mean": float(units[mode].frame_consistency.mean()),
                "base_decision_bootstrap_ci95": bootstrap(
                    units[mode].frame_consistency, CONFIG["seed"] + offset
                ),
            },
            "ev_consistent_rate": {
                "mean": float(units[mode].ev_consistent_rate.mean()),
                "base_decision_bootstrap_ci95": bootstrap(
                    units[mode].ev_consistent_rate, CONFIG["seed"] + 10 + offset
                ),
            },
        }
    paired = units["thinking"].merge(
        units["non_thinking"], on="prospect", suffixes=("_thinking", "_non_thinking")
    )
    paired["frame_consistency_difference"] = (
        paired.frame_consistency_thinking
        - paired.frame_consistency_non_thinking
    )
    values = paired.frame_consistency_difference.dropna()
    missing = paired.frame_consistency_thinking.isna()
    lower = paired.frame_consistency_difference.copy()
    upper = paired.frame_consistency_difference.copy()
    lower.loc[missing] = -paired.loc[missing, "frame_consistency_non_thinking"]
    upper.loc[missing] = 1 - paired.loc[missing, "frame_consistency_non_thinking"]
    summary["thinking_minus_non_thinking"] = {
        "frame_consistency": {
            "n_analyzable_base_decisions": int(len(values)),
            "mean": float(values.mean()),
            "base_decision_bootstrap_ci95": bootstrap(
                values, CONFIG["seed"] + 100
            ),
            "positive_base_decision_fraction": float((values > 0).mean()),
            "zero_difference_base_decisions": int((values == 0).sum()),
            "negative_difference_base_decisions": int((values < 0).sum()),
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
