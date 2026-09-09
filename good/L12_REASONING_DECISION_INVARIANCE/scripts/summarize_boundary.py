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


def ev_accuracy(frame, variant):
    part = frame[frame.context_variant == variant]
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
        corrected_acc = ev_accuracy(frame, "correction")

        metrics[branch] = {
            "redundant": redundant_inv,
            "corrected": corrected_acc,
        }
        branch_summary[branch] = {
            "n": int(len(frame)),
            "valid_rate": float(frame.strict_valid.mean()),
            "parent_frame_consistency_none": float(parent_inv.mean()),
            "redundant_context_consistency": float(redundant_inv.mean()),
            "redundant_context_consistency_ci95": bootstrap_mean(redundant_inv, CONFIG["seed"] + 1),
            "correction_ev_accuracy": float(corrected_acc.mean()),
            "correction_ev_accuracy_ci95": bootstrap_mean(corrected_acc, CONFIG["seed"] + 2),
            "per_prospect": {
                "parent_frame_consistency_none": [float(x) for x in parent_inv],
                "redundant_context_consistency": [float(x) for x in redundant_inv],
                "correction_ev_accuracy": [float(x) for x in corrected_acc],
            },
        }

    summary = {
        "design": "L12-E07 matched redundant-vs-decision-relevant context",
        "n_base_prospects": len(PROSPECTS),
        "branches": branch_summary,
        "contrasts": {
            "think_minus_instruct_redundant_context_consistency": paired_diff(
                metrics["think_sft"]["redundant"],
                metrics["instruct_sft"]["redundant"],
                CONFIG["seed"] + 10,
            ),
            "think_minus_instruct_correction_ev_accuracy": paired_diff(
                metrics["think_sft"]["corrected"],
                metrics["instruct_sft"]["corrected"],
                CONFIG["seed"] + 11,
            ),
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
