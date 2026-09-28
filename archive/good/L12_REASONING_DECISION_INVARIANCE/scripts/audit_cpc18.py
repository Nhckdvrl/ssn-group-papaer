#!/usr/bin/env python3
"""Audit CPC18 calibration data and freeze a PII-free description/history corpus."""

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(os.environ.get("L12_CPC18_CONFIG", "configs/cpc18.json"))
if not CONFIG_PATH.is_absolute():
    CONFIG_PATH = ROOT / CONFIG_PATH
CONFIG = json.loads(CONFIG_PATH.read_text())


def digest(path, algorithm):
    value = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def distribution(row, option):
    values = []
    for index in range(1, 11):
        payoff = row[f"{option}v{index}"]
        probability = row[f"{option}p{index}"]
        if pd.notna(payoff) and pd.notna(probability) and probability > 0:
            values.append([float(payoff), float(probability)])
    return values


def normalized_history_distance(history, option_a, option_b):
    support = [value for value, _ in option_a + option_b]
    scale = max(max(support) - min(support), 1.0)
    a_values, a_weights = zip(*option_a)
    b_values, b_weights = zip(*option_b)
    empirical_a = [pair[0] for pair in history]
    empirical_b = [pair[1] for pair in history]
    return float((
        wasserstein_distance(a_values, empirical_a, u_weights=a_weights)
        + wasserstein_distance(b_values, empirical_b, u_weights=b_weights)
    ) / scale)


def support_dominance(option_a, option_b):
    a = [value for value, _ in option_a]
    b = [value for value, _ in option_b]
    return bool(
        (min(a) >= max(b) and max(a) > min(b))
        or (min(b) >= max(a) and max(b) > min(a))
    )


def quantiles(values):
    return {
        str(level): float(np.quantile(values, level))
        for level in [0, 0.05, 0.25, 0.5, 0.75, 0.95, 1]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problems", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    args = parser.parse_args()

    sources = CONFIG["calibration_sources"]
    checks = {
        "raw_md5": digest(args.raw, "md5"),
        "raw_bytes": args.raw.stat().st_size,
        "problem_sha256": digest(args.problems, "sha256"),
    }
    expected = {
        "raw_md5": sources["raw_md5"],
        "raw_bytes": sources["raw_bytes"],
        "problem_sha256": sources["problem_sha256"],
    }
    if checks != expected:
        raise ValueError(f"Source integrity failure: observed={checks}, expected={expected}")

    problems = pd.read_excel(args.problems)
    raw = pd.read_csv(args.raw, low_memory=False)
    if len(problems) != 210 or problems.GameID.nunique() != 210:
        raise ValueError("Expected exactly 210 unique calibration problems")
    if raw.GameID.nunique() != 210:
        raise ValueError("Raw calibration file does not contain all 210 problems")

    first, last = CONFIG["feedback_trials"]
    feedback = raw[
        (raw.Feedback == 1) & raw.Trial.between(first, last)
    ].sort_values(["GameID", "SubjID", "Trial"])
    counts = feedback.groupby(["GameID", "SubjID"]).size()
    expected_trials = last - first + 1
    if not (counts == expected_trials).all():
        raise ValueError("Incomplete participant histories in feedback trials")
    if feedback[["Apay", "Bpay"]].isna().any().any():
        raise ValueError("Missing realized payoffs in feedback histories")

    histories = {}
    unique_history_counts = {}
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
        unique_history_counts[int(game_id)] = len(candidates)

    flow = {"all_calibration": int(len(problems))}
    known = problems.Amb == 0
    flow["known_probability"] = int(known.sum())
    independent = known & (problems["Corr"] == 0)
    flow["known_probability_independent"] = int(independent.sum())

    records = []
    tie_count = 0
    probability_failures = []
    payoff_support_failures = []
    insufficient_histories = []
    for _, problem in problems.iterrows():
        game_id = int(problem.GameID)
        option_a = distribution(problem, "a")
        option_b = distribution(problem, "b")
        probability_ok = all(
            abs(sum(probability for _, probability in option) - 1)
            <= CONFIG["probability_tolerance"]
            for option in [option_a, option_b]
        )
        if not probability_ok:
            probability_failures.append(game_id)
        ev_a = sum(value * probability for value, probability in option_a)
        ev_b = sum(value * probability for value, probability in option_b)
        is_tie = abs(ev_a - ev_b) <= CONFIG["ev_tie_tolerance"]
        tie_count += int(is_tie and bool(independent.loc[problem.name]))
        enough_histories = (
            unique_history_counts[game_id]
            >= CONFIG["inclusion"]["minimum_unique_histories"]
        )
        if not enough_histories:
            insufficient_histories.append(game_id)

        included = bool(
            independent.loc[problem.name]
            and probability_ok
            and not is_tie
            and enough_histories
            and len(option_a) <= CONFIG["inclusion"]["maximum_outcomes_per_option"]
            and len(option_b) <= CONFIG["inclusion"]["maximum_outcomes_per_option"]
        )
        if not included:
            continue

        candidates = sorted(
            (
                normalized_history_distance(sequence, option_a, option_b),
                key,
                sequence,
            )
            for key, sequence in histories[game_id].items()
        )
        rng = np.random.default_rng(CONFIG["seed"] + game_id)
        selected = [
            candidates[index]
            for index in rng.choice(
                len(candidates), CONFIG["histories_per_problem"], replace=False
            )
        ]
        support_a = {value for value, _ in option_a}
        support_b = {value for value, _ in option_b}
        if any(
            a not in support_a or b not in support_b
            for _, _, sequence in selected for a, b in sequence
        ):
            payoff_support_failures.append(game_id)
        scale = max(
            max(value for value, _ in option_a + option_b)
            - min(value for value, _ in option_a + option_b),
            1.0,
        )
        records.append({
            "id": f"cpc18_{game_id:03d}",
            "game_id": game_id,
            "option_a": option_a,
            "option_b": option_b,
            "ev_a": ev_a,
            "ev_b": ev_b,
            "ev_choice": "A" if ev_a > ev_b else "B",
            "absolute_ev_gap": abs(ev_a - ev_b),
            "relative_ev_gap": abs(ev_a - ev_b) / scale,
            "support_dominance": support_dominance(option_a, option_b),
            "outcome_complexity": max(len(option_a), len(option_b)),
            "available_unique_histories": unique_history_counts[game_id],
            "histories": [
                {
                    "id": key[:16],
                    "draw_index": rank,
                    "distribution_distance": distance,
                    "outcomes": [[a, b] for a, b in sequence],
                }
                for rank, (distance, key, sequence) in enumerate(selected, start=1)
            ],
        })

    flow["after_ev_ties"] = flow["known_probability_independent"] - tie_count
    flow["after_history_and_integrity_checks"] = len(records)
    passed = len(records) >= CONFIG["minimum_clean_problems"]
    distances = [
        history["distribution_distance"]
        for record in records for history in record["histories"]
    ]
    empirical_direction_matches = []
    for record in records:
        for history in record["histories"]:
            empirical_a = np.mean([pair[0] for pair in history["outcomes"]])
            empirical_b = np.mean([pair[1] for pair in history["outcomes"]])
            empirical_direction_matches.append(
                (empirical_a > empirical_b) == (record["ev_choice"] == "A")
                if empirical_a != empirical_b else False
            )

    raw_blocks = raw.groupby(["GameID", "block"]).B.mean().unstack()
    aggregate_differences = []
    for _, problem in problems.iterrows():
        for block in range(1, 6):
            aggregate_differences.append(abs(
                float(problem[f"B.{block}"])
                - float(raw_blocks.loc[int(problem.GameID), block])
            ))

    audit = {
        "design": "L12-E16 CPC18 calibration audit",
        "frozen_config": CONFIG,
        "source_integrity": checks,
        "raw_shape": [int(raw.shape[0]), int(raw.shape[1])],
        "flow": flow,
        "gate": {
            "minimum": CONFIG["minimum_clean_problems"],
            "observed": len(records),
            "passed": passed,
        },
        "included_characteristics": {
            "support_dominance_count": int(sum(r["support_dominance"] for r in records)),
            "outcome_complexity_counts": {
                str(key): int(value)
                for key, value in pd.Series(
                    [r["outcome_complexity"] for r in records]
                ).value_counts().sort_index().items()
            },
            "relative_ev_gap_quantiles": quantiles(
                [r["relative_ev_gap"] for r in records]
            ),
            "available_unique_history_quantiles": quantiles(
                [r["available_unique_histories"] for r in records]
            ),
            "selected_history_distance_quantiles": quantiles(distances),
            "selected_history_empirical_ev_direction_match_rate": float(
                np.mean(empirical_direction_matches)
            ),
        },
        "validation": {
            "probability_failure_game_ids": probability_failures,
            "selected_history_payoff_support_failure_game_ids": payoff_support_failures,
            "fewer_than_three_unique_history_game_ids": insufficient_histories,
            "raw_vs_birds_eye_max_aggregate_b_rate_difference": float(
                max(aggregate_differences)
            ),
            "participant_game_histories_all_have_20_feedback_trials": True,
            "selected_histories_are_distinct_within_problem": True,
            "participant_identifiers_exported": False,
        },
        "decision": (
            "GO_CPC18_PRIMARY_BREADTH" if passed
            else "USE_CPC18_FOR_DESCRIPTION_HISTORY_AND_ADD_CHOICES13K"
        ),
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
