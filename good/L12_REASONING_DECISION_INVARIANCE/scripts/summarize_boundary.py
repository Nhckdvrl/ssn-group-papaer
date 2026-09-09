#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/boundary.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def frame_consistency_by_prospect(frame):
    rows = []
    valid = frame.dropna(subset=["underlying_choice"]).copy()
    valid["is_a"] = (valid.underlying_choice == "A").astype(float)
    rates = valid.groupby(["prospect", "fact_variant", "frame", "order"]).is_a.mean()
    for prospect in sorted(frame.prospect.unique()):
        values = []
        for fact_variant in ["base", "counterfactual"]:
            gain = np.mean([rates.get((prospect, fact_variant, "gain", order), np.nan) for order in ["ab", "ba"]])
            loss = np.mean([rates.get((prospect, fact_variant, "loss", order), np.nan) for order in ["ab", "ba"]])
            values.append(1 - abs(gain - (1 - loss)))
        rows.append(np.nanmean(values))
    return np.asarray(rows, dtype=float)


def relevant_accuracy_by_prospect(frame):
    return (
        frame.groupby("prospect").ev_correct.mean()
        .reindex(sorted(frame.prospect.unique()))
        .to_numpy(dtype=float)
    )


def bootstrap_mean(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(CONFIG["bootstrap_samples"], len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def bootstrap_paired_diff(left, right, seed):
    diff = np.asarray(left) - np.asarray(right)
    return {
        "mean": float(diff.mean()),
        "ci95": bootstrap_mean(diff, seed),
        "per_prospect": [float(x) for x in diff],
    }


def main():
    branch_data = {}
    per = {}
    for branch in ["instruct_sft", "think_sft"]:
        path = OUT / branch / "raw.jsonl"
        frame = pd.read_json(path, lines=True)
        inv = frame_consistency_by_prospect(frame)
        rel = relevant_accuracy_by_prospect(frame)
        per[branch] = {"irrelevant": inv, "relevant": rel}
        branch_data[branch] = {
            "n": int(len(frame)),
            "valid_rate": float(frame.strict_valid.mean()),
            "equivalent_frame_consistency": float(inv.mean()),
            "equivalent_frame_consistency_ci95": bootstrap_mean(inv, CONFIG["seed"] + 1),
            "decision_relevant_ev_accuracy": float(rel.mean()),
            "decision_relevant_ev_accuracy_ci95": bootstrap_mean(rel, CONFIG["seed"] + 2),
            "per_prospect": {
                "equivalent_frame_consistency": [float(x) for x in inv],
                "decision_relevant_ev_accuracy": [float(x) for x in rel],
            },
        }

    contrasts = {
        "think_minus_instruct_equivalent_invariance": bootstrap_paired_diff(
            per["think_sft"]["irrelevant"], per["instruct_sft"]["irrelevant"], CONFIG["seed"] + 10
        ),
        "think_minus_instruct_decision_relevant_accuracy": bootstrap_paired_diff(
            per["think_sft"]["relevant"], per["instruct_sft"]["relevant"], CONFIG["seed"] + 11
        ),
    }
    summary = {
        "design": "E07a relevant-vs-irrelevant boundary",
        "n_base_prospects": len(CONFIG["prospects"]),
        "warning": "three-prospect route-selection pilot; do not claim final external generalization",
        "branches": branch_data,
        "contrasts": contrasts,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
