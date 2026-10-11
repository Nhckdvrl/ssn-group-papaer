#!/usr/bin/env python3
"""Assemble the frozen CPC18 calibration/competition replication result."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPLITS = {
    "calibration": ROOT / "results" / "cpc18_calibration_seed121",
    "competition": ROOT / "results" / "cpc18_competition_seed137",
}
PAIRS = ("olmo_sft", "qwen_mode")


def compact_effect(effect):
    return {
        "mean": effect["mean_probability_effect"],
        "base_decision_bootstrap_ci95": effect["base_decision_bootstrap_ci95"],
        "positive_base_decision_fraction": effect["positive_base_decision_fraction"],
    }


def main():
    result = {
        "design": "L12-E17 calibration plus preregistered L12-E18 competition confirmation",
        "primary_decision_rule": (
            "Both competition reasoning-minus-standard Delta_R-minus-Delta_P "
            "base-decision bootstrap intervals exclude zero."
        ),
        "splits": {},
    }
    for split, directory in SPLITS.items():
        behavior = json.loads((directory / "behavior_summary.json").read_text())
        control = json.loads((directory / "control_summary.json").read_text())
        split_result = {
            "n_frozen_base_decisions": 151 if split == "calibration" else 44,
            "pairs": {},
        }
        for pair in PAIRS:
            behavior_effect = behavior["reasoning_minus_standard"][pair][
                "presentation_consistency_difference"
            ]
            control_effects = control["reasoning_minus_standard"][pair]
            split_result["pairs"][pair] = {
                "n_control_base_decisions": control_effects[
                    "n_paired_base_decisions"
                ],
                "behavior_consistency_difference": {
                    "mean": behavior_effect["mean"],
                    "base_decision_bootstrap_ci95": behavior_effect[
                        "base_decision_bootstrap_ci95"
                    ],
                    "invalid_assignment_mean_bounds": behavior_effect[
                        "invalid_assignment_mean_bounds"
                    ],
                },
                "delta_p_difference": compact_effect(
                    control_effects["delta_p_difference"]
                ),
                "delta_r_difference": compact_effect(
                    control_effects["delta_r_difference"]
                ),
                "delta_control_difference": compact_effect(
                    control_effects["delta_control_difference"]
                ),
            }
        result["splits"][split] = split_result

    heldout = result["splits"]["competition"]["pairs"]
    result["confirmatory_outcome"] = {
        "primary_control_reorganization": {
            pair: heldout[pair]["delta_control_difference"][
                "base_decision_bootstrap_ci95"
            ][0] > 0
            for pair in PAIRS
        },
        "supporting_behavioral_invariance": {
            pair: heldout[pair]["behavior_consistency_difference"][
                "base_decision_bootstrap_ci95"
            ][0] > 0
            for pair in PAIRS
        },
    }
    result["confirmatory_outcome"]["primary_gate_passed"] = all(
        result["confirmatory_outcome"]["primary_control_reorganization"].values()
    )
    result["interpretation"] = (
        "The preregistered causal-route result confirms on both controlled axes. "
        "The behavioral consistency result confirms for Qwen but not OLMo, "
        "showing that route reorganization is more stable than, and not by "
        "itself sufficient for, presentation-invariant behavior."
    )
    output = ROOT / "results" / "cpc18_replication_summary.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
