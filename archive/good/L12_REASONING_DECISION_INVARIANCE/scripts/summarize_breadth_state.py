#!/usr/bin/env python3
"""Summarize E11 state substitution over independent base decisions."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "configs/breadth_state_substitution.json").read_text()
)
OUT = ROOT / CONFIG["result_dir"]


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main():
    frame = pd.read_json(OUT / "raw.jsonl", lines=True)
    layers = []
    for layer, part in frame.groupby("layer"):
        base = part.groupby("prospect").agg(
            donor_shift=("donor_shift", "mean"),
            patched_target_margin=("patched_target_margin", "mean"),
            donor_flip=("patched_flipped_to_donor", "mean"),
        )
        layers.append({
            "layer": int(layer),
            "mean_donor_shift": float(base.donor_shift.mean()),
            "base_decision_bootstrap_ci95": bootstrap(
                base.donor_shift, CONFIG["seed"] + int(layer)
            ),
            "mean_patched_target_margin": float(
                base.patched_target_margin.mean()
            ),
            "donor_flip_rate": float(base.donor_flip.mean()),
            "positive_base_decision_fraction": float(
                (base.donor_shift > 0).mean()
            ),
        })
    baseline = frame.drop_duplicates(["prospect", "frame"])
    first_reversal = next(
        (row["layer"] for row in layers if row["mean_patched_target_margin"] <= 0),
        None,
    )
    summary = {
        "design": "L12-E11 stratified independent-decision state substitution",
        "n_rows": int(len(frame)),
        "n_base_decisions": int(frame.prospect.nunique()),
        "n_directional_pairs": int(len(baseline)),
        "n_layers": int(frame.layer.nunique()),
        "baseline_target_margin": float(baseline.baseline_target_margin.mean()),
        "baseline_target_accuracy": float(
            (baseline.baseline_prediction == baseline.target_choice).mean()
        ),
        "donor_prefix_accuracy": float(
            (baseline.donor_baseline_prediction == baseline.donor_choice).mean()
        ),
        "first_mean_margin_reversal_layer": first_reversal,
        "peak_layer": max(layers, key=lambda row: row["mean_donor_shift"]),
        "layer_profile": layers,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
