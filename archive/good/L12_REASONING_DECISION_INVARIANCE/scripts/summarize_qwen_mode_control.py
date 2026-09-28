#!/usr/bin/env python3
"""Summarize E13 route-dependent causal control over base decisions."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from summarize_breadth_control import effects


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/qwen_mode_validation.json").read_text())
OUT = ROOT / CONFIG["result_dir"] / "control"


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def describe(values, seed):
    return {
        "mean_probability_effect": float(values.mean()),
        "base_decision_bootstrap_ci95": bootstrap(values, seed),
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def main():
    frame = pd.read_json(OUT / "raw.jsonl", lines=True)
    base = {}
    for route in CONFIG["modes"]:
        route_effects = effects(
            frame[frame.route == route].drop(columns=["route"])
        )
        base[route] = route_effects.groupby("prospect").mean()
    metric = "trajectory_minus_prompt"
    difference = base["thinking"][metric] - base["non_thinking"][metric]
    summary = {
        "design": "L12-E13 Qwen3 native-route prompt-by-trajectory control",
        "n_trace_pairs": int(
            len(frame[frame.route == "thinking"]) / 4
        ),
        "n_base_decisions": int(len(difference)),
        "thinking": {
            name: describe(base["thinking"][name], CONFIG["seed"] + index)
            for index, name in enumerate([
                "trajectory_control", "prompt_control", metric
            ])
        },
        "non_thinking": {
            name: describe(base["non_thinking"][name], CONFIG["seed"] + 10 + index)
            for index, name in enumerate([
                "trajectory_control", "prompt_control", metric
            ])
        },
        "thinking_minus_non_thinking": describe(
            difference, CONFIG["seed"] + 2
        ),
        "identification_boundary": (
            "official routes necessarily place the same stripped text inside the "
            "reasoning channel versus after an empty closed reasoning channel; "
            "the contrast is route-dependent integration, not a latent mode variable"
        ),
    }
    with (OUT / "base_decision_effects.jsonl").open("w") as handle:
        joined = base["thinking"].join(
            base["non_thinking"], lsuffix="_thinking", rsuffix="_non_thinking"
        )
        for row in joined.reset_index().to_dict(orient="records"):
            handle.write(json.dumps(row) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
