#!/usr/bin/env python3
"""Summarize E15 with base-decision clustered uncertainty."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/deepseek_state_substitution.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def interval(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main():
    frame = pd.read_json(OUT / "raw.jsonl", lines=True)
    layers = sorted(frame.layer.unique())
    profiles = []
    for layer in layers:
        unit = frame[frame.layer == layer].groupby("prospect").agg(
            donor_shift=("donor_shift", "mean"),
            flip_rate=("patched_flipped_to_donor", "mean"),
            patched_margin=("patched_target_margin", "mean"),
        )
        profiles.append({
            "layer": int(layer),
            "mean_donor_shift": float(unit.donor_shift.mean()),
            "base_decision_bootstrap_ci95": interval(unit.donor_shift, CONFIG["seed"] + int(layer)),
            "positive_base_decision_fraction": float((unit.donor_shift > 0).mean()),
            "donor_flip_rate": float(unit.flip_rate.mean()),
            "mean_patched_target_margin": float(unit.patched_margin.mean()),
        })
    final = profiles[-1]
    summary = {
        "design": "L12-E15 DeepSeek pre-answer decision-state mediation",
        "n_base_decisions": int(frame.prospect.nunique()),
        "n_directional_pairs": int(len(frame[frame.layer == layers[0]])),
        "scan_layers": [int(x) for x in layers],
        "final_layer": final,
        "layer_profile": profiles,
        "identification_boundary": "within-model state substitution under constructed natural-trajectory prefixes",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
