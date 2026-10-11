"""Re-score complete E00/E04/E05 predictions with pinned DataEnvGym scorer."""

import argparse
import hashlib
import json
from pathlib import Path

from dataenvgym.gym.tasks.math.MATH.scoring import score_candidate_answer


MAIN_RUNS = (
    ("e00", "base"),
    ("e00", "static_seed17"),
    ("e00", "static_seed29"),
    ("e00", "static_seed43"),
    ("e04", "retrieval_seed17"),
    ("e04", "retrieval_seed29"),
    ("e04", "retrieval_seed43"),
    ("e05", "matched_seed17"),
)

AUDIT_RUNS = tuple(
    (experiment, name, "_zero_format_dev360", True, True, True)
    for experiment, name in MAIN_RUNS
) + tuple(
    ("e00", name, "_source_dev360", name != "base", False, False)
    for name in ("base", "static_seed17", "static_seed29", "static_seed43")
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", action="store_true",
                        help="Verify 8 zero-shot-format plus 4 source-prompt audit runs")
    args = parser.parse_args()
    dev = read_jsonl(args.data)
    ids = {row["record_id"] for row in dev}
    if len(dev) != 352 or len(ids) != 352:
        raise AssertionError("Frozen dev set must have 352 distinct IDs")
    gold = {row["record_id"]: row for row in dev}
    data_sha = sha256(args.data)
    report = {"data_sha256": data_sha, "runs": {}}
    cases = AUDIT_RUNS if args.audit else [
        (experiment, name, "_format_dev360", None, True, None)
        for experiment, name in MAIN_RUNS
    ]
    for experiment, name, suffix, expected_zero_shot, expected_format, expected_generation_prompt in cases:
        root = args.runs / experiment
        raw_path = root / f"{name}{suffix}.jsonl"
        summary_path = root / f"{name}{suffix}.summary.json"
        rows = read_jsonl(raw_path)
        summary = json.loads(summary_path.read_text())
        row_ids = [row["record_id"] for row in rows]
        if len(rows) != 352 or len(set(row_ids)) != 352 or set(row_ids) != ids:
            raise AssertionError(f"Missing/duplicate/wrong predictions in {name}")
        if summary["data_sha256"] != data_sha or summary["count"] != 352:
            raise AssertionError(f"Wrong data hash/count in {name} summary")
        if summary["format_instruction"] != expected_format:
            raise AssertionError(f"Wrong format prompt in {name}{suffix}")
        if expected_zero_shot is not None and summary["zero_shot"] != expected_zero_shot:
            raise AssertionError(f"Wrong few-shot mode in {name}{suffix}")
        # The earlier zero-shot audit script always added the generation prefix
        # but did not yet write this flag to its summary.  Preserve that
        # recorded protocol instead of rejecting valid, immutable raw runs.
        actual_generation_prompt = summary.get("generation_prompt", True)
        if expected_generation_prompt is not None and actual_generation_prompt != expected_generation_prompt:
            raise AssertionError(f"Wrong chat template mode in {name}{suffix}")
        hash_mismatch = [
            row["record_id"] for row in rows
            if row["problem_hash"] != gold[row["record_id"]]["problem_hash"]
        ]
        if hash_mismatch:
            raise AssertionError(f"Problem hash mismatch in {name}: {hash_mismatch[:3]}")
        score_mismatch = [
            row["record_id"] for row in rows
            if bool(row["correct"]) != bool(score_candidate_answer(
                gold[row["record_id"]]["answer"], row["prediction"]
            ))
        ]
        if score_mismatch:
            raise AssertionError(f"Rescoring mismatch in {name}: {score_mismatch[:3]}")
        correct = sum(bool(row["correct"]) for row in rows)
        if correct != summary["correct"] or correct / 352 != summary["accuracy"]:
            raise AssertionError(f"Summary score mismatch in {name}")
        report["runs"][name + suffix] = {
            "count": len(rows), "correct": correct,
            "raw_sha256": sha256(raw_path), "summary_sha256": sha256(summary_path),
            "rescored_items": len(rows), "score_mismatches": 0,
        }
    report["status"] = "PASS: all IDs, hashes, prompt flags, rescored items and summaries match"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"])
    for name, item in report["runs"].items():
        print(name, item["correct"], "/", item["count"])


if __name__ == "__main__":
    main()
