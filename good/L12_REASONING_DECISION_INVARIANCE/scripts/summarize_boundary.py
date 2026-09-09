#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/boundary.json").read_text())
OUT = ROOT / CONFIG["result_dir"]
PROSPECTS = [x["id"] for x in CONFIG["prospects"]]


def choice_rates(frame):
    valid = frame.dropna(subset=["underlying_choice"]).copy()
    valid["is_a"] = (valid.underlying_choice == "A").astype(float)
    return valid.groupby(["prospect", "context_variant", "frame", "order"]).is_a.mean()


def parent_frame_consistency(frame):
    rates = choice_rates(frame)
    values = []
    for prospect in PROSPECTS:
        gain = np.mean([rates.get((prospect, "none", "gain", order), np.nan) for order in ["ab", "ba"]])
        loss = np.mean([rates.get((prospect, "none", "loss", order), np.nan) for order in ["ab", "ba"]])
        values.append(1 - abs(gain - (1 - loss)))
    return np.asarray(values, dtype=float)


def redundant_consistency(frame):
    rates = choice_rates(frame)
    values = []
    for prospect in PROSPECTS:
        scores = []
        for framing in ["gain", "loss"]:
            for order in ["ab", "ba"]:
                raw = rates.get((prospect, "none", framing, order), np.nan)
                redundant = rates.get((prospect, "redundant", framing, order), np.nan)
                scores.append(1 - abs(raw - redundant))
        values.append(np.nanmean(scores))
    return np.asarray(values, dtype=float)


def correction_uptake(frame):
    values = []
    for prospect in PROSPECTS:
        cell_deltas = []
        for framing in ["gain", "loss"]:
            for order in ["ab", "ba"]:
                corrected = frame[
                    (frame.prospect == prospect)
                    & (frame.context_variant == "correction")
                    & (frame.frame == framing)
                    & (frame.order == order)
                ]
                redundant = frame[
                    (frame.prospect == prospect)
                    & (frame.context_variant == "redundant")
                    & (frame.frame == framing)
                    & (frame.order == order)
                ]
                target = corrected.expected_underlying.iloc[0]
                corrected_rate = float((corrected.underlying_choice == target).mean())
                redundant_rate = float((redundant.underlying_choice == target).mean())
                cell_deltas.append(corrected_rate - redundant_rate)
        values.append(np.mean(cell_deltas))
    return np.asarray(values, dtype=float)


def correction_accuracy(frame):
    part = frame[frame.context_variant == "correction"]
    return part.groupby("prospect").ev_correct.mean().reindex(PROSPECTS).to_numpy(dtype=float)


def bootstrap_mean(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(CONFIG["bootstrap_samples"], len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def paired_diff(left, right, seed):
    diff = np.asarray(left) - np.asarray(right)
    return {
        "mean": float(diff.mean()),
        "ci95": bootstrap_mean(diff, seed),
        "per_prospect": [float(x) for x in diff],
    }


def main():
    branch_summary = {}
    metrics = {}

    for branch in ["instruct_sft", "think_sft"]:
        frame = pd.read_json(OUT / branch / "raw.jsonl", lines=True)
        parent_inv = parent_frame_consistency(frame)
        redundant_inv = redundant_consistency(frame)
        uptake = correction_uptake(frame)
        corrected_acc = correction_accuracy(frame)

        metrics[branch] = {
            "redundant": redundant_inv,
            "uptake": uptake,
        }
        branch_summary[branch] = {
            "n": int(len(frame)),
            "valid_rate": float(frame.strict_valid.mean()),
            "parent_frame_consistency_none": float(parent_inv.mean()),
            "irrelevant_context_invariance": float(redundant_inv.mean()),
            "irrelevant_context_invariance_ci95": bootstrap_mean(redundant_inv, CONFIG["seed"] + 1),
            "relevant_context_uptake": float(uptake.mean()),
            "relevant_context_uptake_ci95": bootstrap_mean(uptake, CONFIG["seed"] + 2),
            "correction_ev_accuracy": float(corrected_acc.mean()),
            "per_prospect": {
                "parent_frame_consistency_none": [float(x) for x in parent_inv],
                "irrelevant_context_invariance": [float(x) for x in redundant_inv],
                "relevant_context_uptake": [float(x) for x in uptake],
                "correction_ev_accuracy": [float(x) for x in corrected_acc],
            },
        }

    summary = {
        "design": "L12-E07 semantic-relevance boundary",
        "n_base_prospects": len(PROSPECTS),
        "headline": {
            "irrelevant_context": "none vs redundant: behavior should stay the same",
            "relevant_context": "redundant vs correction: choice probability should move toward the new EV-optimal target",
        },
        "branches": branch_summary,
        "contrasts": {
            "think_minus_instruct_irrelevant_context_invariance": paired_diff(
                metrics["think_sft"]["redundant"],
                metrics["instruct_sft"]["redundant"],
                CONFIG["seed"] + 10,
            ),
            "think_minus_instruct_relevant_context_uptake": paired_diff(
                metrics["think_sft"]["uptake"],
                metrics["instruct_sft"]["uptake"],
                CONFIG["seed"] + 11,
            ),
        },
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
