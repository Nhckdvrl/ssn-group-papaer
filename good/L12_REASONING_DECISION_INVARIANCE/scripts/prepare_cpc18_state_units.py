#!/usr/bin/env python3
"""Freeze 48 CPC18 opposite-decision trace pairs before state substitution."""

import hashlib
import json

import numpy as np

from cpc18_common import CONFIG, ROOT


SEED = 131
PER_EV_GAP_TERTILE = 16


def main():
    source = ROOT / CONFIG["result_dir"] / "raw" / "olmo_think_sft.jsonl"
    rows = [json.loads(line) for line in source.open()]
    valid = [
        row for row in rows
        if row["valid"] and row.get("stripped_trace")
        and row.get("removed_terminal_segments")
    ]
    explicit = {
        (row["problem"], row["order"], row["sample_index"]): row
        for row in valid if row["presentation"] == "explicit"
    }
    candidates = []
    for history in valid:
        if history["presentation"] != "history":
            continue
        key = (history["problem"], history["order"], history["sample_index"])
        target = explicit.get(key)
        if target is None or target["shown_choice"] == history["shown_choice"]:
            continue
        candidates.append({
            "problem": history["problem"],
            "order": history["order"],
            "history_id": history["history_id"],
            "sample_index": history["sample_index"],
            "explicit_choice": target["shown_choice"],
            "history_choice": history["shown_choice"],
            "relative_ev_gap": history["relative_ev_gap"],
            "support_dominance": history["support_dominance"],
        })

    by_problem = {}
    rng = np.random.default_rng(SEED)
    for problem in sorted({row["problem"] for row in candidates}):
        choices = [row for row in candidates if row["problem"] == problem]
        by_problem[problem] = choices[int(rng.integers(len(choices)))]
    ordered = sorted(by_problem.values(), key=lambda row: row["relative_ev_gap"])
    bins = np.array_split(ordered, 3)
    selected = []
    for index, values in enumerate(bins):
        indexes = rng.choice(len(values), PER_EV_GAP_TERTILE, replace=False)
        for item_index in sorted(indexes):
            selected.append({"ev_gap_tertile": index + 1, **values[item_index]})
    selected.sort(key=lambda row: row["problem"])

    payload = {
        "design": "L12-E19 CPC18 pre-answer decision-state mediation",
        "seed": SEED,
        "model": next(
            spec for spec in CONFIG["regimes"] if spec["name"] == "olmo_think_sft"
        ),
        "source_result_dir": CONFIG["result_dir"],
        "selection_rule": (
            "one strict opposite-choice explicit/history pair per problem; "
            "uniform candidate selection within problem; 16 problems sampled "
            "from each candidate-relative-EV-gap rank tertile"
        ),
        "n_candidate_problems": len(by_problem),
        "n_selected_base_decisions": len(selected),
        "layer_stride": 1,
        "bootstrap_samples": 5000,
        "result_dir": "results/cpc18_state_seed131",
        "selected_units": selected,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    output = ROOT / "configs/cpc18_state_substitution.json"
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "output": str(output),
        "candidate_problems": len(by_problem),
        "selected_problems": len(selected),
        "tertile_counts": {
            str(value): sum(row["ev_gap_tertile"] == value for row in selected)
            for value in [1, 2, 3]
        },
    }, indent=2))


if __name__ == "__main__":
    main()
