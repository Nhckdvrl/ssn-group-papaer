#!/usr/bin/env python3
"""Summarize E14 behavior with base decisions as independent units."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/llama_external_validation.json").read_text())
OUT = ROOT / CONFIG["result_dir"]


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    means = values[indexes].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def units(frame):
    valid = frame.dropna(subset=["underlying_choice"]).copy()
    valid["choose_a"] = (valid.underlying_choice == "A").astype(float)
    rates = valid.groupby(["prospect", "frame", "order"]).choose_a.mean()
    rows = []
    for prospect in sorted(frame.prospect.unique()):
        frame_consistency = np.mean([
            1 - abs(
                rates.get((prospect, "gain", order), np.nan)
                - (1 - rates.get((prospect, "loss", order), np.nan))
            )
            for order in CONFIG["orders"]
        ])
        part = valid[valid.prospect == prospect]
        rows.append({
            "prospect": prospect,
            "frame_consistency": float(frame_consistency),
            "ev_consistent_rate": float((part.underlying_choice == part.gold_underlying).mean()),
        })
    return pd.DataFrame(rows)


def main():
    summary = {"design": "L12-E14 Llama-ecosystem behavior gate"}
    unit_frames = {}
    for index, spec in enumerate(CONFIG["models"]):
        frame = pd.read_json(OUT / f"{spec['branch']}.jsonl", lines=True)
        unit = units(frame)
        unit_frames[spec["branch"]] = unit
        summary[spec["branch"]] = {
            "n_generations": int(len(frame)),
            "n_analyzable_base_decisions": int(unit.frame_consistency.notna().sum()),
            "valid_rate": float(frame.underlying_choice.notna().mean()),
            "frame_consistency": {
                "mean": float(unit.frame_consistency.mean()),
                "base_decision_bootstrap_ci95": bootstrap(unit.frame_consistency, CONFIG["seed"] + index),
            },
            "ev_consistent_rate": {
                "mean": float(unit.ev_consistent_rate.mean()),
                "base_decision_bootstrap_ci95": bootstrap(unit.ev_consistent_rate, CONFIG["seed"] + 10 + index),
            },
        }
    paired = unit_frames["deepseek_r1"].merge(
        unit_frames["llama_instruct"], on="prospect", suffixes=("_deepseek", "_llama")
    )
    difference = paired.frame_consistency_deepseek - paired.frame_consistency_llama
    summary["deepseek_minus_llama"] = {
        "frame_consistency": {
            "n_analyzable_base_decisions": int(difference.notna().sum()),
            "mean": float(difference.mean()),
            "base_decision_bootstrap_ci95": bootstrap(difference, CONFIG["seed"] + 100),
            "positive_base_decision_fraction": float((difference.dropna() > 0).mean()),
        }
    }
    (OUT / "behavior_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
