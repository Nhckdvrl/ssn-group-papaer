#!/usr/bin/env python3
"""Summarize E19 with CPC18 base decisions as bootstrap units."""

import json
import hashlib

import numpy as np
import pandas as pd

from cpc18_common import ROOT


CONFIG = json.loads((ROOT / "configs/cpc18_state_substitution.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def interval(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main():
    raw_path = OUT / "raw.jsonl"
    frame = pd.read_json(raw_path, lines=True)
    profile = []
    for layer, part in frame.groupby("layer"):
        units = part.groupby("problem").agg(
            donor_shift=("donor_shift", "mean"),
            patched_margin=("patched_target_margin", "mean"),
            flip_rate=("patched_flipped_to_donor", "mean"),
        )
        profile.append({
            "layer": int(layer),
            "mean_donor_shift": float(units.donor_shift.mean()),
            "base_decision_bootstrap_ci95": interval(
                units.donor_shift, CONFIG["seed"] + int(layer)
            ),
            "positive_base_decision_fraction": float(
                (units.donor_shift > 0).mean()
            ),
            "mean_patched_target_margin": float(units.patched_margin.mean()),
            "donor_flip_rate": float(units.flip_rate.mean()),
        })
    profile.sort(key=lambda row: row["layer"])
    first_reversal = next(
        (row["layer"] for row in profile if row["mean_patched_target_margin"] <= 0),
        None,
    )
    summary = {
        "design": CONFIG["design"],
        "n_base_decisions": int(frame.problem.nunique()),
        "n_directional_pairs": int(
            len(frame[frame.layer == frame.layer.min()])
        ),
        "first_mean_margin_reversal_layer": first_reversal,
        "final_layer": profile[-1],
        "layer_profile": profile,
        "identification_boundary": (
            "within-model last-token residual-state substitution between matched "
            "natural explicit/history trajectories that produced opposite choices"
        ),
        "raw_artifact": {
            "path": str(raw_path.relative_to(ROOT)),
            "bytes": raw_path.stat().st_size,
            "rows": int(len(frame)),
            "sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
            "git_policy": "ignored regenerable intervention output",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
