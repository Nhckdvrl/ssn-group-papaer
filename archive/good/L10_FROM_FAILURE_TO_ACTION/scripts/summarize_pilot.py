#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())
RAW = ROOT / CONFIG["result_dir"] / "raw.jsonl"


def ci(values, draws, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(draws, len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main():
    frame = pd.read_json(RAW, lines=True)
    conditions = {}
    for condition, part in frame.groupby("condition"):
        conditions[condition] = {
            "n": int(len(part)),
            "accuracy": float(part.correct.mean()),
            "accuracy_ci95": ci(part.correct.astype(float), CONFIG["bootstrap_samples"], CONFIG["seed"]),
            "strict_valid_rate": float(part.strict_valid.mean()),
            "bad_repeat_rate": float(part.bad_repeat.mean()) if condition.startswith("A") else None,
        }

    wide_correct = frame.pivot(index="task_id", columns="condition", values="correct")
    wide_bad = frame.pivot(index="task_id", columns="condition", values="bad_repeat")
    dissociation = (wide_correct["P"].astype(bool) & wide_bad["A0"].astype(bool)).astype(float)

    recovery = {}
    for i, condition in enumerate(["A1", "A2", "A3", "A4"]):
        good_delta = wide_correct[condition].astype(float) - wide_correct["A0"].astype(float)
        bad_delta = wide_bad[condition].astype(float) - wide_bad["A0"].astype(float)
        recovery[condition] = {
            "good_action_rate_delta_vs_A0": float(good_delta.mean()),
            "good_action_delta_ci95": ci(good_delta, CONFIG["bootstrap_samples"], CONFIG["seed"] + 10 + i),
            "bad_repeat_rate_delta_vs_A0": float(bad_delta.mean()),
            "bad_repeat_delta_ci95": ci(bad_delta, CONFIG["bootstrap_samples"], CONFIG["seed"] + 20 + i),
        }

    summary = {
        "model": CONFIG["model"],
        "n_items": int(frame.task_id.nunique()),
        "conditions": conditions,
        "policy_correct_and_raw_bad_repeat_rate": float(dissociation.mean()),
        "policy_action_dissociation_ci95": ci(dissociation, CONFIG["bootstrap_samples"], CONFIG["seed"] + 30),
        "intervention_recovery": recovery,
        "raw": str(RAW),
    }
    out = ROOT / CONFIG["result_dir"] / "summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
