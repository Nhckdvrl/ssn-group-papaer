#!/usr/bin/env python3
"""Summarize E12 against the frozen E10 SFT comparator."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from summarize_breadth_control import effects


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/checkpoint_validation.json").read_text())
BREADTH = json.loads((ROOT / "configs/breadth.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def load_base(path):
    return effects(pd.read_json(path, lines=True)).groupby("prospect").mean()


def describe(values, seed):
    return {
        "mean_probability_effect": float(values.mean()),
        "base_decision_bootstrap_ci95": bootstrap(values, seed),
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def main():
    dpo = {
        name: load_base(OUT / f"{name}.jsonl")
        for name in ["instruct_dpo", "think_dpo"]
    }
    sft_dir = ROOT / BREADTH["result_dir"] / "control"
    sft = {
        name: load_base(sft_dir / f"{name}.jsonl")
        for name in ["instruct_sft", "think_sft"]
    }
    metric = "trajectory_minus_prompt"
    dpo_difference = dpo["think_dpo"][metric] - dpo["instruct_dpo"][metric]
    sft_difference = sft["think_sft"][metric] - sft["instruct_sft"][metric]
    summary = {
        "design": "L12-E12 documented DPO-lineage checkpoint validation",
        "n_base_decisions": int(len(dpo_difference)),
        "instruct_dpo": describe(dpo["instruct_dpo"][metric], CONFIG["seed"]),
        "think_dpo": describe(dpo["think_dpo"][metric], CONFIG["seed"] + 1),
        "think_minus_instruct_dpo": describe(
            dpo_difference, CONFIG["seed"] + 2
        ),
        "frozen_sft_branch_difference": describe(
            sft_difference, CONFIG["seed"] + 3
        ),
        "dpo_minus_sft_change_in_branch_difference": describe(
            dpo_difference - sft_difference, CONFIG["seed"] + 4
        ),
        "attribution_boundary": (
            "persistence over documented branch continuations; not one-variable "
            "attribution of the original SFT divergence"
        ),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
