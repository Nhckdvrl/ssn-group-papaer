#!/usr/bin/env python3
"""Summarize E14 external causal-control replication."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from summarize_breadth_control import effects


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/llama_external_validation.json").read_text())
OUT = ROOT / CONFIG["result_dir"] / "control"


def describe(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))
    boot = values[indexes].mean(axis=1)
    return {
        "mean_probability_effect": float(values.mean()),
        "base_decision_bootstrap_ci95": [
            float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))
        ],
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def main():
    base = {}
    retained_trace_pairs = None
    trace_rows = [
        json.loads(line)
        for line in (ROOT / CONFIG["result_dir"] / "deepseek_r1.jsonl").open()
    ]
    valid_trace_rows = {
        (row["prospect"], row["frame"], row["order"], row["sample_index"]): row
        for row in trace_rows if row["valid"] and row.get("stripped_trace")
    }
    valid_pair_keys = {
        (prospect, order, sample)
        for prospect in {row["prospect"] for row in trace_rows}
        for order in CONFIG["orders"]
        for sample in range(CONFIG["samples_per_cell"])
        if (prospect, "gain", order, sample) in valid_trace_rows
        and (prospect, "loss", order, sample) in valid_trace_rows
    }
    unstripped_keys = {
        (row["prospect"], row["order"], row["sample_index"])
        for row in trace_rows
        if row["valid"] and row.get("stripped_trace")
        and not row.get("removed_terminal_segments")
    }
    clean_base = {}
    for spec in CONFIG["models"]:
        frame = pd.read_json(OUT / f"{spec['branch']}.jsonl", lines=True)
        primary_keep = [
            (prospect, order, int(sample)) in valid_pair_keys
            for prospect, order, sample in zip(
                frame.prospect, frame.order, frame.sample_index
            )
        ]
        base[spec["branch"]] = effects(
            frame[primary_keep].drop(columns=["branch"])
        ).groupby("prospect").mean()
        clean_keep = [
            primary and (prospect, order, int(sample)) not in unstripped_keys
            for primary, prospect, order, sample in zip(
                primary_keep, frame.prospect, frame.order, frame.sample_index
            )
        ]
        retained_trace_pairs = int(sum(clean_keep) / 4)
        clean_base[spec["branch"]] = effects(
            frame[clean_keep].drop(columns=["branch"])
        ).groupby("prospect").mean()
    metric = "trajectory_minus_prompt"
    difference = base["deepseek_r1"][metric] - base["llama_instruct"][metric]
    summary = {
        "design": "L12-E14 Llama-ecosystem external causal-control replication",
        "n_valid_trace_pairs": len(valid_pair_keys),
        "n_base_decisions": int(len(difference)),
        "deepseek_r1": {
            name: describe(base["deepseek_r1"][name], CONFIG["seed"] + index)
            for index, name in enumerate(["trajectory_control", "prompt_control", metric])
        },
        "llama_instruct": {
            name: describe(base["llama_instruct"][name], CONFIG["seed"] + 10 + index)
            for index, name in enumerate(["trajectory_control", "prompt_control", metric])
        },
        "deepseek_minus_llama": describe(difference, CONFIG["seed"] + 100),
        "strict_terminal_removed_sensitivity": {
            "excluded_trace_pairs": len(valid_pair_keys) - retained_trace_pairs,
            "retained_trace_pairs": retained_trace_pairs,
            "deepseek_minus_llama": describe(
                clean_base["deepseek_r1"][metric]
                - clean_base["llama_instruct"][metric],
                CONFIG["seed"] + 200,
            ),
        },
        "attribution_boundary": (
            "external replication across unmatched post-training pipelines and native templates; "
            "not one-variable training attribution"
        ),
    }
    joined = base["deepseek_r1"].join(
        base["llama_instruct"], lsuffix="_deepseek", rsuffix="_llama"
    )
    with (OUT / "base_decision_effects.jsonl").open("w") as handle:
        for row in joined.reset_index().to_dict(orient="records"):
            handle.write(json.dumps(row) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
