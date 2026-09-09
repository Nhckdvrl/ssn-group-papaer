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
    scores = []
    for prospect in PROSPECTS:
        gain = np.mean([rates.get((prospect, "none", "gain", order), np.nan) for order in ["ab", "ba"]])
        loss = np.mean([rates.get((prospect, "none", "loss", order), np.nan) for order in ["ab", "ba"]])
        scores.append(1 - abs(gain - (1 - loss)))
    return np.asarray(scores, dtype=float)


def redundant_context_consistency(frame):
    rates = choice_rates(frame)
    scores = []
    for prospect in PROSPECTS:
        cell_scores = []
        for framing in ["gain", "loss"]:
            for order in ["ab", "ba"]:
                raw = rates.get((prospect, "none", framing, order), np.nan)
                redundant = rates.get((prospect, "redundant", framing, order), np.nan)
                cell_scores.append(1 - abs(raw - redundant))
        scores.append(np.nanmean(cell_scores))
    return np.asarray(scores, dtype=float)


def ev_accuracy_by_prospect(frame, variant):
    part = frame[frame.context_variant == variant]
    return (
        part.groupby("prospect").ev_correct.mean()
        .reindex(PROSPECTS)
        .to_numpy(dtype=float)
    )


def bootstrap_mean(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indices = rng.integers(
        0,
        len(values),
        size=(CONFIG["bootstrap_samples"], len(values)),
    )
    means = values[indices].mean(axis=1)
    return [
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    ]


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
        redundant_inv = redundant_context_consistency(frame)
        base_acc = ev_accuracy_by_prospect(frame, "none")
        correction_acc = ev_accuracy_by_prospect(frame, "correction")

        metrics[branch] = {
            "redundant_inv": redundant_inv,
            "correction_acc": correction_acc,
        }

        branch_summary[branch] = {
            "n": int(len(frame)),
            "valid_rate": float(frame.strict_valid.mean()),
            "parent_frame_consistency_none": float(parent_inv.mean()),
            "redundant_context_consistency": float(redundant_inv.mean()),
            "redundant_context_consistency_ci95": bootstrap_mean(
                redundant_inv, CONFIG["seed"] + 1
            ),
            "base_ev_accuracy": float(base_acc.mean()),
            "correction_ev_accuracy": float(correction_acc.mean()),
            "correction_ev_accuracy_ci95": bootstrap_mean(
                correction_acc, CONFIG["seed"] + 2
            ),
            "per_prospect": {
                "parent_frame_consistency_none": [float(x) for x in parent_inv],
                "redundant_context_consistency": [float(x) for x in redundant_inv],
                "base_ev_accuracy": [float(x) for x in base_acc],
                "correction_ev_accuracy": [float(x) for x in correction_acc],
            },
        }

    summary = {
        "design": "E07 matched redundant-vs-corrective contextual note",
        "n_base_prospects": len(PROSPECTS),
        "branches": branch_summary,
        "contrasts": {
            "think_minus_instruct_redundant_context_consistency": paired_diff(
                metrics["think_sft"]["redundant_inv"],
                metrics["instruct_sft"]["redundant_inv"],
                CONFIG["seed"] + 10,
            ),
            "think_minus_instruct_correction_ev_accuracy": paired_diff(
                metrics["think_sft"]["correction_acc"],
                metrics["instruct_sft"]["correction_acc"],
                CONFIG["seed"] + 11,
            ),
        },
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
