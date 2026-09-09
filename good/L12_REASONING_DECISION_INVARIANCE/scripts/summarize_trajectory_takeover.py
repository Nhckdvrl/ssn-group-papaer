#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/trajectory_takeover.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def prospect_means(frame, column):
    return frame.groupby("prospect")[column].mean().to_numpy(dtype=float)


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(CONFIG["bootstrap_samples"], len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def summarize_delta(frame, left, right, seed):
    tmp = frame.copy()
    name = f"{left}_minus_{right}"
    tmp[name] = tmp[left] - tmp[right]
    values = prospect_means(tmp, name)
    return {
        "mean": float(values.mean()),
        "ci95_prospect_bootstrap": bootstrap(values, seed),
        "per_prospect": [float(x) for x in values],
    }


def main():
    frame = pd.read_json(OUT / "raw.jsonl", lines=True)
    summary = {
        "design": "L12-E07 trajectory takeover after terminal-conclusion stripping",
        "n": int(len(frame)),
        "n_prospects": int(frame.prospect.nunique()),
        "trace_audit": {
            "terminal_conclusion_removed_rate": float(
                frame.target_removed_segments.map(bool).mean()
            ),
            "remaining_decision_marker_rate": float(
                frame.target_remaining_decision_marker.mean()
            ),
        },
        "readout_accuracy": {
            name: float(frame[f"{name}_correct"].mean())
            for name in ["own_full", "own_stripped", "opposite_stripped", "empty"]
        },
        "mean_margin": {
            name: float(frame[f"{name}_margin"].mean())
            for name in ["own_full", "own_stripped", "opposite_stripped", "empty"]
        },
        "primary_contrasts": {
            "own_stripped_minus_empty": summarize_delta(
                frame, "own_stripped_margin", "empty_margin", CONFIG["seed"] + 100
            ),
            "own_stripped_minus_opposite_stripped": summarize_delta(
                frame,
                "own_stripped_margin",
                "opposite_stripped_margin",
                CONFIG["seed"] + 101,
            ),
            "own_full_minus_own_stripped": summarize_delta(
                frame, "own_full_margin", "own_stripped_margin", CONFIG["seed"] + 102
            ),
        },
        "interpretation": {
            "trajectory_takeover_supported_if": (
                "own_stripped remains strongly target-directed versus empty and "
                "opposite-frame stripped traces after terminal choice/conclusion removal"
            ),
            "late_self_commitment_if": (
                "the large own-full effect collapses after terminal conclusion removal"
            ),
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
