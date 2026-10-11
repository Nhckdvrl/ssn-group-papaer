#!/usr/bin/env python3
"""Mechanically merge and validate disjoint CPC18 behavior shards."""

import argparse
import json
from pathlib import Path

from cpc18_common import CONFIG, ROOT, load_problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", required=True)
    parser.add_argument("--num-shards", type=int, required=True)
    parser.add_argument("--result-dir")
    args = parser.parse_args()
    result_dir = Path(args.result_dir) if args.result_dir else ROOT / CONFIG["result_dir"]
    raw_dir = result_dir / "raw"
    rows = []
    metadata = []
    for index in range(args.num_shards):
        suffix = f".shard{index}of{args.num_shards}"
        with (raw_dir / f"{args.regime}{suffix}.jsonl").open() as handle:
            rows.extend(json.loads(line) for line in handle)
        metadata.append(json.loads(
            (result_dir / f"{args.regime}{suffix}.model.json").read_text()
        ))
    expected_problems = {row["id"] for row in load_problems()}
    observed_problems = {row["problem"] for row in rows}
    if observed_problems != expected_problems:
        raise ValueError(
            f"Shard coverage mismatch: missing={expected_problems-observed_problems}, "
            f"extra={observed_problems-expected_problems}"
        )
    keys = [
        (row["problem"], row["presentation"], row["history_id"],
         row["order"], row["sample_index"])
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("Behavior shards contain duplicate condition keys")
    rows.sort(key=lambda row: (
        row["problem"], row["presentation"], row["history_id"] or "",
        row["order"], row["sample_index"]
    ))
    with (raw_dir / f"{args.regime}.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    merged = {
        **metadata[0],
        "n_problems": len(observed_problems),
        "merged_shards": args.num_shards,
        "shard_problem_counts": [item["n_problems"] for item in metadata],
    }
    (result_dir / f"{args.regime}.model.json").write_text(
        json.dumps(merged, indent=2) + "\n"
    )
    print(json.dumps({
        "regime": args.regime,
        "n_rows": len(rows),
        "n_problems": len(observed_problems),
        "duplicate_keys": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
