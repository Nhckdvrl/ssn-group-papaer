#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/upstream/mind-the-dh-gap/data/open_explicit.csv"
OUT = ROOT / "results/parent_audit"
MODELS = [
    "allenai/Olmo-3-7B-Instruct-SFT",
    "allenai/Olmo-3-7B-Think-SFT",
]


def bootstrap_frame_consistency(rows, rng, draws=5000):
    # Each CSV row contains the A-choice rate under both option orders.
    rows = rows.copy()
    # Gain/loss stimuli are sign-reflected versions of the same prospect.
    # Canonicalize signs before joining the two frames.
    for column in ["ev_a", "ev_b", "x_a", "x_b", "y_a", "y_b"]:
        rows[column] = rows[column].abs()
    keys = ["ev_a", "p_a", "ev_b", "p_b", "x_a", "x_b", "y_a", "y_b", "Prompt_Style"]
    pivot = rows.pivot_table(index=keys, columns="frame", values=["ratio_a_False", "ratio_a_True"])
    vals = []
    for _, row in pivot.dropna().iterrows():
        gain = np.mean([row[("ratio_a_False", "gain")], row[("ratio_a_True", "gain")]])
        loss = np.mean([row[("ratio_a_False", "loss")], row[("ratio_a_True", "loss")]])
        vals.append(1.0 - abs(gain - (1.0 - loss)))
    vals = np.asarray(vals, dtype=float)
    if len(vals) != 9:
        raise ValueError(f"expected 9 matched prospect/style cells, found {len(vals)}")
    boots = np.mean(rng.choice(vals, (draws, len(vals)), replace=True), axis=1)
    return {
        "n_matched_cells": int(len(vals)),
        "frame_consistency": float(vals.mean()),
        "ci95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
        "cell_values": vals.tolist(),
    }


def main():
    frame = pd.read_csv(SOURCE)
    rng = np.random.default_rng(29)
    report = {"source": str(SOURCE), "models": {}, "schema": list(frame.columns)}
    for model in MODELS:
        rows = frame[frame.Model == model].copy()
        report["models"][model] = {
            "rows": int(len(rows)),
            "valid_trials": int(rows.n_valid_total.sum()),
            "prompt_styles": sorted(rows.Prompt_Style.unique().tolist()),
            "audit": bootstrap_frame_consistency(rows, rng),
        }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
