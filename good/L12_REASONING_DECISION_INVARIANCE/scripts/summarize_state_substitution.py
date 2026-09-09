#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/state_substitution.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def bootstrap_prospect_mean(values, groups, seed):
    values = np.asarray(values, dtype=float)
    groups = np.asarray(groups)
    unique = np.unique(groups)
    rng = np.random.default_rng(seed)
    draws = np.empty(CONFIG["bootstrap_samples"], dtype=float)

    for i in range(CONFIG["bootstrap_samples"]):
        sampled_groups = rng.choice(unique, size=len(unique), replace=True)
        sampled_values = []
        for group in sampled_groups:
            group_values = values[groups == group]
            sampled_values.append(rng.choice(group_values))
        draws[i] = np.mean(sampled_values)

    return [
        float(np.quantile(draws, 0.025)),
        float(np.quantile(draws, 0.975)),
    ]


def main():
    frame = pd.read_json(OUT / "raw.jsonl", lines=True)

    layers = []
    for layer, part in frame.groupby("layer"):
        per_prospect = (
            part.groupby("prospect")
            .donor_shift.mean()
            .reset_index()
        )
        values = per_prospect.donor_shift.to_numpy(dtype=float)
        groups = per_prospect.prospect.to_numpy()

        layers.append({
            "layer": int(layer),
            "mean_donor_shift": float(part.donor_shift.mean()),
            "prospect_bootstrap_ci95": bootstrap_prospect_mean(
                values,
                groups,
                CONFIG.get("seed", 43) + int(layer),
            ),
            "mean_patched_target_margin": float(part.patched_target_margin.mean()),
            "flip_to_donor_rate": float(part.patched_flipped_to_donor.mean()),
            "per_prospect_donor_shift": {
                str(row.prospect): float(row.donor_shift)
                for row in per_prospect.itertuples()
            },
        })

    peak = max(layers, key=lambda x: x["mean_donor_shift"])
    pair_frame = frame.drop_duplicates(
        ["prospect", "frame", "order", "sample_index"]
    )

    summary = {
        "design": "L12-E08 pre-answer decision-state causal substitution",
        "n_rows": int(len(frame)),
        "n_trace_pairs": int(len(pair_frame)),
        "n_layers_scanned": int(frame.layer.nunique()),
        "baseline_target_margin": float(pair_frame.baseline_target_margin.mean()),
        "decision_marker_audit": {
            "target_remaining_marker_rate": float(
                pair_frame.target_remaining_decision_marker.mean()
            ),
            "donor_remaining_marker_rate": float(
                pair_frame.donor_remaining_decision_marker.mean()
            ),
        },
        "peak_layer": peak,
        "layer_profile": layers,
        "interpretation": {
            "positive_signature": (
                "a coherent set of layers shows positive donor_shift and increased "
                "flips toward the matched opposite-frame donor decision"
            ),
            "claim": (
                "the stripped natural reasoning trajectory constructs an internal "
                "pre-answer state that causally carries decision control"
            ),
        },
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
