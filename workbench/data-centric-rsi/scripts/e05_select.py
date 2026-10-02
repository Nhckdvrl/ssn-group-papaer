"""E05 exact cell and approximate length control for E04 retrieval data."""

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from dataenvgym.gym.tasks.math.MATH.scoring import render_solution_for_scoring


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def length(row: dict) -> int:
    return len(row["instruction"]) + len(row["response"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    retrieval = read_jsonl(args.retrieval)
    retrieved_ids = {row["record_id"] for row in retrieval}
    candidates = defaultdict(list)
    for raw in read_jsonl(args.pool):
        if raw["record_id"] in retrieved_ids:
            continue
        row = {
            "record_id": raw["record_id"], "instruction": raw["problem"],
            "response": render_solution_for_scoring(raw["solution"], raw["answer"]),
            "problem_hash": raw["problem_hash"],
            "level": raw["level"], "type": raw["type"],
        }
        candidates[(row["level"], row["type"])].append(row)
    selected = []
    length_deltas = []
    for target in retrieval:
        cell = (target["level"], target["type"])
        if not candidates[cell]:
            raise ValueError(f"No remaining candidate in {cell}")
        target_length = math.log1p(length(target))
        index = min(
            range(len(candidates[cell])),
            key=lambda i: (
                abs(math.log1p(length(candidates[cell][i])) - target_length),
                candidates[cell][i]["record_id"],
            ),
        )
        row = candidates[cell].pop(index)
        selected.append(row)
        length_deltas.append(length(row) - length(target))
    if len(selected) != 120 or len({row["record_id"] for row in selected}) != 120:
        raise AssertionError("Control must have 120 unique rows")
    if Counter((row["level"], row["type"]) for row in selected) != Counter(
        (row["level"], row["type"]) for row in retrieval
    ):
        raise AssertionError("Exact level/type cell matching failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as handle:
        for row in selected:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    manifest = {
        "policy": "same level/type as retrieval; nearest log total character length; no error input",
        "pool_sha256": sha256(args.pool),
        "retrieval_sha256": sha256(args.retrieval),
        "output_sha256": sha256(args.output),
        "count": len(selected), "overlap_retrieval": len(
            {row["record_id"] for row in selected} & retrieved_ids
        ),
        "mean_total_chars": sum(length(row) for row in selected) / len(selected),
        "retrieval_mean_total_chars": sum(length(row) for row in retrieval) / len(retrieval),
        "mean_signed_total_char_diff": sum(length_deltas) / len(length_deltas),
        "mean_absolute_total_char_diff": sum(abs(delta) for delta in length_deltas) / len(length_deltas),
        "selected_ids": [row["record_id"] for row in selected],
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "selected_ids"}, indent=2))


if __name__ == "__main__":
    main()
