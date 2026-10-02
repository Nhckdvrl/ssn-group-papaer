"""Freeze equal-size E06 student datasets from all retained teacher calls."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from dataenvgym.gym.tasks.math.MATH.scoring import render_solution_for_scoring


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--max-per-arm", type=int, default=120)
    args = parser.parse_args()
    records = [record for path in args.input for record in read_jsonl(path)]
    by_key = {(record["arm"], record["index"]): record for record in records}
    if len(by_key) != len(records):
        raise ValueError("Teacher call index repeated across input files")
    indices = {
        arm: {index for record_arm, index in by_key if record_arm == arm}
        for arm in ("no_state", "with_state")
    }
    if indices["no_state"] != indices["with_state"]:
        raise ValueError("Teacher arms do not cover equal call indices")
    selected = {}
    duplicate_counts = {}
    for arm in ("no_state", "with_state"):
        seen = set()
        valid = []
        duplicate_count = 0
        for index in sorted(indices[arm]):
            record = by_key[(arm, index)]
            if not record["valid"]:
                continue
            if record["problem_hash"] in seen:
                duplicate_count += 1
                continue
            seen.add(record["problem_hash"])
            valid.append(record)
        selected[arm] = valid
        duplicate_counts[arm] = duplicate_count
    count = min(args.max_per_arm, *(len(selected[arm]) for arm in selected))
    if count <= 0:
        raise ValueError("No valid generated data for both arms")
    args.out.mkdir(parents=True, exist_ok=True)
    output_paths = {}
    for arm in ("no_state", "with_state"):
        path = args.out / f"{arm}_{count}.jsonl"
        with path.open("w") as handle:
            for record in selected[arm][:count]:
                spec = record["spec"]
                row = {
                    "record_id": f"e06-{arm}-{record['index']:03d}",
                    "instruction": spec["problem"],
                    "response": render_solution_for_scoring(
                        chain_of_thought=spec["chain_of_thought"],
                        final_answer=spec["final_answer"],
                    ),
                    "problem_hash": record["problem_hash"],
                    "teacher_call_index": record["index"],
                }
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        output_paths[arm] = path
    overlap = set(record["problem_hash"] for record in selected["no_state"][:count]) & set(
        record["problem_hash"] for record in selected["with_state"][:count]
    )
    report = {
        "source_files": {str(path): sha256(path) for path in args.input},
        "call_count_per_arm": len(indices["no_state"]),
        "schema_valid_per_arm": dict(Counter(record["arm"] for record in records if record["valid"])),
        "cross_batch_duplicates_per_arm": duplicate_counts,
        "selected_per_arm": count,
        "cross_arm_exact_problem_overlap": len(overlap),
        "student_files": {arm: {"path": str(path), "sha256": sha256(path)}
                          for arm, path in output_paths.items()},
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
