#!/usr/bin/env python3
"""Freeze E21 units for a form-by-evidence pre-answer state intervention."""

import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np

from cpc18_form_evidence_common import CONFIG, ROOT, load_problems


SEED = 173
PER_STRENGTH_QUARTILE = 8


def main():
    source = ROOT / CONFIG["result_dir"] / "raw" / "olmo_think_sft.jsonl"
    rows = [json.loads(line) for line in source.open()]
    eligible = [
        row for row in rows
        if row["valid"] and row.get("stripped_trace")
        and row.get("removed_terminal_segments")
        and row["underlying_choice"] == row["evidence_choice"]
    ]
    grouped = {}
    for row in eligible:
        key = (row["problem"], row["form"], row["order"], row["evidence_choice"])
        if key not in grouped or row["sample_index"] < grouped[key]["sample_index"]:
            grouped[key] = row

    problems = {row["id"]: row for row in load_problems()}
    candidates = []
    for problem_id in sorted(problems):
        complete_orders = [
            order for order in CONFIG["orders"]
            if all(
                (problem_id, form, order, evidence) in grouped
                for form in ("raw", "summary") for evidence in ("A", "B")
            )
        ]
        if not complete_orders:
            continue
        rng = np.random.default_rng(
            SEED + int(hashlib.sha256(problem_id.encode()).hexdigest()[:8], 16)
        )
        order = complete_orders[int(rng.integers(len(complete_orders)))]
        evidence = {item["evidence_choice"]: item for item in problems[problem_id]["evidence"]}
        candidates.append({
            "problem": problem_id,
            "source_split": problems[problem_id]["source_split"],
            "order": order,
            "mean_evidence_strength": float(np.mean([
                evidence["A"]["normalized_empirical_gap"],
                evidence["B"]["normalized_empirical_gap"],
            ])),
            "sample_indices": {
                form: {
                    choice: grouped[(problem_id, form, order, choice)]["sample_index"]
                    for choice in ("A", "B")
                }
                for form in ("raw", "summary")
            },
        })

    rng = np.random.default_rng(SEED)
    bins = np.array_split(
        sorted(candidates, key=lambda row: (row["mean_evidence_strength"], row["problem"])),
        4,
    )
    selected = []
    for quartile, values in enumerate(bins, start=1):
        indexes = rng.choice(len(values), PER_STRENGTH_QUARTILE, replace=False)
        for index in sorted(indexes):
            selected.append({"strength_quartile": quartile, **values[index]})
    selected.sort(key=lambda row: row["problem"])

    model = next(item for item in CONFIG["regimes"] if item["name"] == "olmo_think_sft")
    payload = {
        "design": "L12-E21 selective pre-answer state mediation",
        "frozen_at": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds"),
        "seed": SEED,
        "model": model,
        "source_result_dir": CONFIG["result_dir"],
        "selection_rule": (
            "require strict terminal-stripped OLMo Think trajectories that naturally "
            "follow both evidence directions in both forms under one displayed order; "
            "choose an eligible order by a problem-keyed seed; sample eight problems "
            "from each model-independent mean-evidence-strength quartile"
        ),
        "outcome_blind_selection_boundary": (
            "trace validity and natural evidence-following determine intervention "
            "eligibility; no margin, hidden state, layer, patch, or E21 result enters selection"
        ),
        "n_candidate_problems": len(candidates),
        "n_selected_base_decisions": len(selected),
        "scan_layers": [0, 8, 16, 24, 31],
        "layer_selection": (
            "sparse early/middle/late checkpoints fixed from the prior 32-layer E19 "
            "profile; E21 tests carrier content rather than localizing a privileged layer"
        ),
        "primary_metric": (
            "state_selectivity = donor_evidence_effect - donor_form_sensitivity at layer 31"
        ),
        "primary_decision_rule": (
            "final-layer state_selectivity and donor_evidence_effect have base-decision "
            "bootstrap 95% intervals above zero; report donor-form sensitivity and all layers"
        ),
        "unit_of_analysis": "base decision; target conditions, donor conditions, and layers are nested",
        "bootstrap_samples": 5000,
        "result_dir": "results/cpc18_selective_state_seed173",
        "selected_units": selected,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    output = ROOT / "configs/cpc18_selective_state.json"
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "output": str(output),
        "candidate_problems": len(candidates),
        "selected_problems": len(selected),
        "split_counts": {
            split: sum(row["source_split"] == split for row in selected)
            for split in sorted({row["source_split"] for row in selected})
        },
        "quartile_counts": {
            str(q): sum(row["strength_quartile"] == q for row in selected)
            for q in range(1, 5)
        },
    }, indent=2))


if __name__ == "__main__":
    main()
