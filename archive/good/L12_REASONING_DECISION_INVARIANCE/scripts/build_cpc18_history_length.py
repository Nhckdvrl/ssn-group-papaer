#!/usr/bin/env python3
"""Build frozen paired 20/100-draw histories from exact E18 distributions."""

import json
import os
from pathlib import Path

import numpy as np

from cpc18_common import CONFIG, ROOT


def draw(option, rng, size):
    values = [row[0] for row in option]
    probabilities = [row[1] for row in option]
    return rng.choice(values, size=size, p=probabilities).astype(float).tolist()


def main():
    source = ROOT / "data/cpc18_competition_v1.jsonl"
    problems = [json.loads(line) for line in source.open()]
    records = []
    agreement = {str(length): [] for length in CONFIG["history_lengths"]}
    for problem in problems:
        histories = []
        for replicate in range(CONFIG["histories_per_problem"]):
            rng = np.random.default_rng(CONFIG["seed"] + 100 * problem["game_id"] + replicate)
            a = draw(problem["option_a"], rng, max(CONFIG["history_lengths"]))
            b = draw(problem["option_b"], rng, max(CONFIG["history_lengths"]))
            for length in CONFIG["history_lengths"]:
                outcomes = [[x, y] for x, y in zip(a[:length], b[:length])]
                mean_a, mean_b = float(np.mean(a[:length])), float(np.mean(b[:length]))
                empirical = "A" if mean_a > mean_b else "B" if mean_b > mean_a else "tie"
                agreement[str(length)].append(empirical == problem["ev_choice"])
                histories.append({
                    "id": f"sim_{problem['game_id']}_{replicate}_{length}",
                    "replicate": replicate,
                    "length": length,
                    "empirical_choice": empirical,
                    "empirical_mean_a": mean_a,
                    "empirical_mean_b": mean_b,
                    "outcomes": outcomes,
                })
        records.append({**{k: v for k, v in problem.items() if k != "histories"}, "histories": histories})
    audit = {
        "design": "L12 supporting paired 20/100 history-length diagnostic",
        "frozen_config": CONFIG,
        "n_base_decisions": len(records),
        "histories_per_length_per_problem": CONFIG["histories_per_problem"],
        "empirical_ev_direction_agreement": {
            length: float(np.mean(values)) for length, values in agreement.items()
        },
        "validation": {
            "twenty_is_prefix_of_matched_hundred": all(
                next(h for h in row["histories"] if h["replicate"] == rep and h["length"] == 100)["outcomes"][:20]
                == next(h for h in row["histories"] if h["replicate"] == rep and h["length"] == 20)["outcomes"]
                for row in records for rep in range(CONFIG["histories_per_problem"])
            ),
            "model_outputs_used_in_construction": False,
        },
    }
    with (ROOT / CONFIG["output"]).open("w") as handle:
        for row in records:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (ROOT / CONFIG["audit_output"]).write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
