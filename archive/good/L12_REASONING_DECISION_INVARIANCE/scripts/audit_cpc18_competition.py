#!/usr/bin/env python3
"""Audit CPC18 competition data under the preregistered E18 contract."""

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

from audit_cpc18 import normalized_history_distance, quantiles, support_dominance
from cpc18_common import CONFIG, ROOT


PARAMETERS = [
    "GameID", "Ha", "pHa", "La", "LotShapeA", "LotNumA",
    "Hb", "pHb", "Lb", "LotShapeB", "LotNumB", "Amb", "Corr",
]


def digest(path, algorithm):
    value = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def expand_lottery(high, p_high, low, shape, n_outcomes):
    high = float(high)
    p_high = float(p_high)
    low = float(low)
    n_outcomes = int(n_outcomes)
    values = []
    if shape == "-":
        values.append((high, p_high))
    elif shape == "Symm":
        k = n_outcomes - 1
        values.extend(
            (high - k / 2 + index, p_high * math.comb(k, index) * 0.5 ** k)
            for index in range(n_outcomes)
        )
    elif shape in {"R-skew", "L-skew"}:
        sign = 1 if shape == "R-skew" else -1
        center = -1 - n_outcomes if shape == "R-skew" else 1 + n_outcomes
        for index in range(1, n_outcomes + 1):
            probability = p_high / (2 ** index)
            if index == n_outcomes:
                probability *= 2
            values.append((high + center + sign * 2 ** index, probability))
    else:
        raise ValueError(f"Unknown lottery shape: {shape!r}")
    if p_high < 1:
        values.append((low, 1 - p_high))
    merged = defaultdict(float)
    for payoff, probability in values:
        merged[float(payoff)] += float(probability)
    return [[payoff, merged[payoff]] for payoff in sorted(merged)]


def workbook_distribution(row, option):
    values = defaultdict(float)
    for index in range(1, 11):
        payoff, probability = row[f"{option}v{index}"], row[f"{option}p{index}"]
        if pd.notna(payoff) and pd.notna(probability) and probability > 0:
            values[float(payoff)] += float(probability)
    return [[payoff, values[payoff]] for payoff in sorted(values)]


def validate_reconstruction(workbook):
    errors = []
    count = 0
    for _, row in workbook.iterrows():
        for lower, upper in [("a", "A"), ("b", "B")]:
            reconstructed = expand_lottery(
                row[f"H{lower}"], row[f"pH{lower}"], row[f"L{lower}"],
                row[f"LotShape{upper}"], row[f"LotNum{upper}"],
            )
            published = workbook_distribution(row, lower)
            if len(reconstructed) != len(published):
                raise ValueError(
                    f"Distribution length mismatch: game {row.GameID} option {upper}"
                )
            for observed, expected in zip(reconstructed, published):
                errors.extend([abs(observed[0] - expected[0]), abs(observed[1] - expected[1])])
            count += 1
    return {"options_checked": count, "maximum_absolute_cell_error": max(errors)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--calibration-workbook", type=Path, required=True)
    args = parser.parse_args()
    sources = CONFIG["competition_sources"]
    integrity = {
        "raw_md5": digest(args.raw, "md5"),
        "raw_sha256": digest(args.raw, "sha256"),
        "raw_bytes": args.raw.stat().st_size,
        "calibration_validation_workbook_sha256": digest(
            args.calibration_workbook, "sha256"
        ),
    }
    expected = {key: sources[key] for key in integrity}
    if integrity != expected:
        raise ValueError(f"Source integrity failure: {integrity} != {expected}")

    reconstruction = validate_reconstruction(pd.read_excel(args.calibration_workbook))
    if reconstruction["maximum_absolute_cell_error"] > CONFIG["probability_tolerance"]:
        raise ValueError(f"Lottery reconstruction failed: {reconstruction}")
    raw = pd.read_csv(args.raw, low_memory=False)
    competition = raw[raw.GameID.between(211, 270)].copy()
    parameters = competition[PARAMETERS].drop_duplicates()
    if len(parameters) != 60 or parameters.GameID.nunique() != 60:
        raise ValueError("Competition compact parameters are not unique for 60 games")

    first, last = CONFIG["feedback_trials"]
    feedback = competition[
        (competition.Feedback == 1) & competition.Trial.between(first, last)
    ].sort_values(["GameID", "SubjID", "Trial"])
    counts = feedback.groupby(["GameID", "SubjID"]).size()
    if not (counts == last - first + 1).all():
        raise ValueError("Incomplete competition feedback histories")
    if feedback[["Apay", "Bpay"]].isna().any().any():
        raise ValueError("Missing competition feedback payoffs")

    histories = {}
    for game_id, game in feedback.groupby("GameID"):
        candidates = {}
        for _, participant in game.groupby("SubjID"):
            sequence = tuple(
                (float(a), float(b))
                for a, b in zip(participant.Apay, participant.Bpay)
            )
            key = hashlib.sha256(
                json.dumps(sequence, separators=(",", ":")).encode()
            ).hexdigest()
            candidates.setdefault(key, sequence)
        histories[int(game_id)] = candidates

    flow = {"all_competition": 60}
    flow["known_probability"] = int((parameters.Amb == 0).sum())
    flow["known_probability_independent"] = int(
        ((parameters.Amb == 0) & (parameters.Corr == 0)).sum()
    )
    records = []
    tie_count = 0
    insufficient_histories = []
    support_failures = []
    for _, row in parameters.sort_values("GameID").iterrows():
        game_id = int(row.GameID)
        option_a = expand_lottery(
            row.Ha, row.pHa, row.La, row.LotShapeA, row.LotNumA
        )
        option_b = expand_lottery(
            row.Hb, row.pHb, row.Lb, row.LotShapeB, row.LotNumB
        )
        probability_ok = all(
            abs(sum(probability for _, probability in option) - 1)
            <= CONFIG["probability_tolerance"]
            for option in [option_a, option_b]
        )
        ev_a = sum(value * probability for value, probability in option_a)
        ev_b = sum(value * probability for value, probability in option_b)
        tie = abs(ev_a - ev_b) <= CONFIG["ev_tie_tolerance"]
        tie_count += int(tie and row.Amb == 0 and row.Corr == 0)
        enough = len(histories[game_id]) >= CONFIG["inclusion"]["minimum_unique_histories"]
        if not enough:
            insufficient_histories.append(game_id)
        included = bool(
            row.Amb == 0 and row.Corr == 0 and probability_ok and not tie and enough
            and len(option_a) <= CONFIG["inclusion"]["maximum_outcomes_per_option"]
            and len(option_b) <= CONFIG["inclusion"]["maximum_outcomes_per_option"]
        )
        if not included:
            continue
        candidates = sorted(
            (normalized_history_distance(sequence, option_a, option_b), key, sequence)
            for key, sequence in histories[game_id].items()
        )
        rng = np.random.default_rng(CONFIG["seed"] + game_id)
        selected = [
            candidates[index] for index in rng.choice(
                len(candidates), CONFIG["histories_per_problem"], replace=False
            )
        ]
        support_a = {value for value, _ in option_a}
        support_b = {value for value, _ in option_b}
        if any(
            a not in support_a or b not in support_b
            for _, _, sequence in selected for a, b in sequence
        ):
            support_failures.append(game_id)
        scale = max(
            max(value for value, _ in option_a + option_b)
            - min(value for value, _ in option_a + option_b), 1.0
        )
        records.append({
            "id": f"cpc18_{game_id:03d}", "game_id": game_id,
            "option_a": option_a, "option_b": option_b,
            "ev_a": ev_a, "ev_b": ev_b,
            "ev_choice": "A" if ev_a > ev_b else "B",
            "absolute_ev_gap": abs(ev_a - ev_b),
            "relative_ev_gap": abs(ev_a - ev_b) / scale,
            "support_dominance": support_dominance(option_a, option_b),
            "outcome_complexity": max(len(option_a), len(option_b)),
            "available_unique_histories": len(histories[game_id]),
            "histories": [
                {"id": key[:16], "draw_index": rank,
                 "distribution_distance": distance,
                 "outcomes": [[a, b] for a, b in sequence]}
                for rank, (distance, key, sequence) in enumerate(selected, start=1)
            ],
        })
    flow["after_ev_ties"] = flow["known_probability_independent"] - tie_count
    flow["after_history_and_integrity_checks"] = len(records)
    passed = len(records) >= CONFIG["minimum_clean_problems"]
    audit = {
        "design": "L12-E18 untouched CPC18 competition audit",
        "preregistration_commit": "9e4a532",
        "frozen_config": CONFIG,
        "source_integrity": integrity,
        "distribution_reconstruction_validation": reconstruction,
        "raw_shape": [int(raw.shape[0]), int(raw.shape[1])],
        "competition_raw_shape": [int(competition.shape[0]), int(competition.shape[1])],
        "flow": flow,
        "gate": {"minimum": CONFIG["minimum_clean_problems"],
                 "observed": len(records), "passed": passed},
        "included_characteristics": {
            "support_dominance_count": int(sum(row["support_dominance"] for row in records)),
            "relative_ev_gap_quantiles": quantiles(
                [row["relative_ev_gap"] for row in records]
            ),
            "available_unique_history_quantiles": quantiles(
                [row["available_unique_histories"] for row in records]
            ),
        },
        "validation": {
            "selected_history_payoff_support_failure_game_ids": support_failures,
            "fewer_than_three_unique_history_game_ids": insufficient_histories,
            "participant_game_histories_all_have_20_feedback_trials": True,
            "selected_histories_are_distinct_within_problem": True,
            "participant_identifiers_exported": False,
        },
        "decision": "GO_E18_CONFIRMATION" if passed else "E18_GATE_FAILED",
    }
    output = ROOT / CONFIG["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    (ROOT / CONFIG["audit_output"]).write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
