#!/usr/bin/env python3
"""Summarize E10 causal control with base decisions as clusters."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def effects(frame):
    index = ["prospect", "order", "sample_index"]
    cells = frame.pivot_table(
        index=index,
        columns=["prompt_frame", "trajectory_frame"],
        values="p_gain_choice",
    )
    trajectory_control = (
        (cells[("gain", "gain")] - cells[("gain", "loss")])
        + (cells[("loss", "gain")] - cells[("loss", "loss")])
    ) / 2
    prompt_control = (
        (cells[("gain", "gain")] - cells[("loss", "gain")])
        + (cells[("gain", "loss")] - cells[("loss", "loss")])
    ) / 2
    result = pd.DataFrame(index=cells.index)
    result["trajectory_control"] = trajectory_control.to_numpy()
    result["prompt_control"] = prompt_control.to_numpy()
    result["trajectory_minus_prompt"] = (
        trajectory_control - prompt_control
    ).to_numpy()
    return result


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    draws = values[indexes].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def main():
    control_dir = OUT / "control"
    frames = {
        branch: pd.read_json(control_dir / f"{branch}.jsonl", lines=True)
        for branch in ["instruct_sft", "think_sft"]
    }
    unit = {branch: effects(frame) for branch, frame in frames.items()}
    base = {
        branch: value.groupby("prospect").mean()
        for branch, value in unit.items()
    }
    summary = {
        "design": "L12-E10 independent-decision prompt-by-trajectory control"
    }
    for offset, branch in enumerate(["instruct_sft", "think_sft"]):
        summary[branch] = {
            "n_trace_pairs": int(len(unit[branch])),
            "n_base_decisions": int(len(base[branch])),
        }
        for index, metric in enumerate([
            "trajectory_control", "prompt_control", "trajectory_minus_prompt"
        ]):
            values = base[branch][metric]
            summary[branch][metric] = {
                "mean_probability_effect": float(values.mean()),
                "base_decision_bootstrap_ci95": bootstrap(
                    values, CONFIG["seed"] + offset * 10 + index
                ),
                "positive_base_decision_fraction": float((values > 0).mean()),
            }

    joined = base["think_sft"].join(
        base["instruct_sft"], lsuffix="_think", rsuffix="_instruct"
    )
    for metric in ["trajectory_control", "prompt_control", "trajectory_minus_prompt"]:
        joined[f"{metric}_difference"] = (
            joined[f"{metric}_think"] - joined[f"{metric}_instruct"]
        )
    summary["think_minus_instruct"] = {}
    for index, metric in enumerate([
        "trajectory_control_difference",
        "trajectory_minus_prompt_difference",
    ]):
        values = joined[metric]
        summary["think_minus_instruct"][metric] = {
            "mean_probability_effect": float(values.mean()),
            "base_decision_bootstrap_ci95": bootstrap(
                values, CONFIG["seed"] + 100 + index
            ),
            "positive_base_decision_fraction": float((values > 0).mean()),
        }

    behavior = pd.read_json(OUT / "behavior_unit_metrics.jsonl", lines=True)
    bridge = joined.reset_index().merge(
        behavior[["prospect", "frame_consistency_difference"]], on="prospect"
    ).dropna(subset=[
        "trajectory_minus_prompt_difference", "frame_consistency_difference"
    ])
    association = spearmanr(
        bridge.frame_consistency_difference,
        bridge.trajectory_minus_prompt_difference,
    )
    summary["exploratory_mechanism_behavior_association"] = {
        "n_base_decisions": int(len(bridge)),
        "spearman_rho": float(association.statistic),
        "p_value": float(association.pvalue),
        "interpretation": "secondary and not required for C3",
    }

    with (control_dir / "base_decision_effects.jsonl").open("w") as handle:
        for row in joined.reset_index().to_dict(orient="records"):
            handle.write(json.dumps(row) + "\n")
    (control_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
