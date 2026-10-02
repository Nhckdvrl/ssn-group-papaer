"""Audit E06 teacher novelty and overlap before training any student."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def problem_hash(problem: str) -> str:
    return hashlib.sha256(" ".join(problem.split()).encode()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = read_jsonl(args.raw)
    prompts = {(row["arm"], row["index"]): row for row in read_jsonl(args.prompts)}
    reference = {
        row["record_id"]: row for path in (args.pool, args.dev)
        for row in read_jsonl(path)
    }
    pool_hashes = {row["problem_hash"] for row in read_jsonl(args.pool)}
    dev_hashes = {row["problem_hash"] for row in read_jsonl(args.dev)}
    per_arm = defaultdict(Counter)
    index = {}
    parsed_hashes = defaultdict(list)
    for row in rows:
        arm = row["arm"]
        count = per_arm[arm]
        count["calls"] += 1
        count["schema_accepted"] += int(row["valid"])
        count["prompt_contains_asy"] += int("[asy]" in prompts[(arm, row["index"])]["prompt"])
        count["prompt_tokens"] += row["prompt_tokens"]
        count["generated_tokens"] += row["generated_tokens"]
        count["finish_" + str(row["finish_reason"])] += 1
        try:
            spec = row.get("spec") or json.loads(row["raw"])[0]
            problem = spec["problem"]
        except Exception:
            count["unparseable"] += 1
            continue
        count["parseable"] += 1
        digest = problem_hash(problem)
        parsed_hashes[arm].append(digest)
        count["exact_pool_problem"] += int(digest in pool_hashes)
        count["exact_dev_problem"] += int(digest in dev_hashes)
        source_ids = row["common_ids"] + row["extra_ids"]
        count["exact_prompt_copy"] += int(any(
            problem_hash(reference[source_id]["problem"]) == digest
            for source_id in source_ids
        ))
        count["problem_under_45_chars"] += int(len(problem) < 45)
        count["problem_mentions_diagram_or_asy"] += int(
            "diagram" in problem.lower() or "figure" in problem.lower()
            or "[asy]" in problem or "\\asy" in problem
        )
        index[(arm, row["index"])] = digest
    shared = len(set(parsed_hashes["no_state"]) & set(parsed_hashes["with_state"]))
    report = {
        "raw_sha256": sha256(args.raw),
        "prompts_sha256": sha256(args.prompts),
        "pool_sha256": sha256(args.pool),
        "dev_sha256": sha256(args.dev),
        "per_arm": {
            arm: {
                **dict(counts),
                "unique_parseable_problem": len(set(parsed_hashes[arm])),
                "duplicate_parseable_problem": len(parsed_hashes[arm]) - len(set(parsed_hashes[arm])),
            }
            for arm, counts in per_arm.items()
        },
        "cross_arm_exact_problem_overlap": shared,
        "same_index_cross_arm_exact_problem_overlap": sum(
            index.get(("no_state", idx)) == index.get(("with_state", idx))
            and ("no_state", idx) in index and ("with_state", idx) in index
            for idx in range(120)
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
