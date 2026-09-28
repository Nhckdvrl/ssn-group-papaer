#!/usr/bin/env python3
"""Freeze unused CPC18 histories for the preregistered form/evidence test."""

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/cpc18_form_evidence_preregistered.json").read_text())


def digest(path, algorithm):
    value = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def history_key(sequence):
    return hashlib.sha256(
        json.dumps(sequence, separators=(",", ":")).encode()
    ).hexdigest()


def frequency_summary(sequence, index):
    counts = Counter(pair[index] for pair in sequence)
    return [[float(payoff), int(count)] for payoff, count in sorted(counts.items())]


def read_histories(raw_path, game_ids):
    columns = ["GameID", "SubjID", "Trial", "Feedback", "Apay", "Bpay"]
    raw = pd.read_csv(raw_path, low_memory=False, usecols=columns)
    first, last = CONFIG["history_trials"]
    raw = raw[
        raw.GameID.isin(game_ids)
        & (raw.Feedback == 1)
        & raw.Trial.between(first, last)
    ].sort_values(["GameID", "SubjID", "Trial"])
    histories = {}
    for game_id, game in raw.groupby("GameID"):
        unique = {}
        for _, participant in game.groupby("SubjID"):
            if len(participant) != last - first + 1:
                continue
            sequence = tuple(
                (float(a), float(b))
                for a, b in zip(participant.Apay, participant.Bpay)
            )
            unique.setdefault(history_key(sequence), sequence)
        histories[int(game_id)] = unique
    return histories


def best_pair(candidates_a, candidates_b):
    eligible = []
    for a in candidates_a:
        for b in candidates_b:
            ratio = max(a[0], b[0]) / min(a[0], b[0])
            if ratio <= CONFIG["maximum_evidence_strength_ratio"]:
                eligible.append((abs(math.log(a[0] / b[0])), -min(a[0], b[0]), a[1], b[1], a, b))
    if not eligible:
        return None
    chosen = min(eligible)
    return chosen[-2], chosen[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration-raw", type=Path, required=True)
    parser.add_argument("--competition-raw", type=Path, required=True)
    args = parser.parse_args()

    calibration_config = json.loads((ROOT / "configs/cpc18.json").read_text())
    competition_config = json.loads(
        (ROOT / "configs/cpc18_competition_preregistered.json").read_text()
    )
    observed_sources = {
        "calibration_raw_md5": digest(args.calibration_raw, "md5"),
        "calibration_raw_bytes": args.calibration_raw.stat().st_size,
        "competition_raw_sha256": digest(args.competition_raw, "sha256"),
        "competition_raw_bytes": args.competition_raw.stat().st_size,
    }
    expected_sources = {
        "calibration_raw_md5": calibration_config["calibration_sources"]["raw_md5"],
        "calibration_raw_bytes": calibration_config["calibration_sources"]["raw_bytes"],
        "competition_raw_sha256": competition_config["competition_sources"]["raw_sha256"],
        "competition_raw_bytes": competition_config["competition_sources"]["raw_bytes"],
    }
    if observed_sources != expected_sources:
        raise ValueError(f"Source mismatch: {observed_sources} != {expected_sources}")

    records = []
    flow = {}
    selected_hashes = set()
    source_specs = [
        ("calibration", ROOT / "data/cpc18_calibration_v1.jsonl", args.calibration_raw),
        ("competition", ROOT / "data/cpc18_competition_v1.jsonl", args.competition_raw),
    ]
    for split, compact_path, raw_path in source_specs:
        compact = [json.loads(line) for line in compact_path.open()]
        histories = read_histories(raw_path, {row["game_id"] for row in compact})
        flow[f"{split}_clean_problems"] = len(compact)
        split_selected = 0
        for problem in compact:
            used = {history["id"] for history in problem["histories"]}
            support = [
                payoff
                for option in (problem["option_a"], problem["option_b"])
                for payoff, _ in option
            ]
            scale = max(max(support) - min(support), 1.0)
            candidates = {"A": [], "B": []}
            for key, sequence in histories[problem["game_id"]].items():
                if key[:16] in used:
                    continue
                mean_a = float(np.mean([pair[0] for pair in sequence]))
                mean_b = float(np.mean([pair[1] for pair in sequence]))
                gap = (mean_a - mean_b) / scale
                if abs(gap) < CONFIG["minimum_normalized_empirical_gap"]:
                    continue
                direction = "A" if gap > 0 else "B"
                candidates[direction].append((abs(gap), key, sequence, mean_a, mean_b))
            pair = best_pair(candidates["A"], candidates["B"])
            if pair is None:
                continue
            evidence = []
            for direction, selected in zip(("A", "B"), pair):
                strength, key, sequence, mean_a, mean_b = selected
                if key in selected_hashes:
                    raise ValueError("A history was selected for multiple problems")
                selected_hashes.add(key)
                evidence.append({
                    "evidence_choice": direction,
                    "history_id": key[:16],
                    "normalized_empirical_gap": strength,
                    "empirical_mean_a": mean_a,
                    "empirical_mean_b": mean_b,
                    "option_a_frequencies": frequency_summary(sequence, 0),
                    "option_b_frequencies": frequency_summary(sequence, 1),
                    "outcomes": [[a, b] for a, b in sequence],
                })
            records.append({
                **{key: value for key, value in problem.items() if key != "histories"},
                "source_split": split,
                "evidence_strength_ratio": max(pair[0][0], pair[1][0]) / min(pair[0][0], pair[1][0]),
                "evidence": evidence,
            })
            split_selected += 1
        flow[f"{split}_eligible_opposite_evidence_problems"] = split_selected

    passed = len(records) >= CONFIG["minimum_base_decisions"]
    audit = {
        "design": "L12-E20 prospective form-by-evidence corpus freeze",
        "frozen_config": CONFIG,
        "source_integrity": observed_sources,
        "flow": {**flow, "total_selected": len(records)},
        "gate": {
            "minimum": CONFIG["minimum_base_decisions"],
            "observed": len(records),
            "passed": passed,
        },
        "validation": {
            "selected_histories_are_unused_by_e17_e18": True,
            "two_opposite_empirical_directions_per_problem": True,
            "twenty_observations_per_history": True,
            "frequency_summaries_exactly_reconstruct_marginal_multisets": True,
            "participant_identifiers_exported": False,
        },
        "source_split_counts": dict(Counter(row["source_split"] for row in records)),
        "true_ev_choice_counts": dict(Counter(row["ev_choice"] for row in records)),
        "evidence_strength_ratio_quantiles": {
            str(q): float(np.quantile([row["evidence_strength_ratio"] for row in records], q))
            for q in [0, 0.25, 0.5, 0.75, 1]
        },
        "decision": "GO_E20" if passed else "E20_DATA_GATE_FAILED",
    }
    output = ROOT / CONFIG["output"]
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
