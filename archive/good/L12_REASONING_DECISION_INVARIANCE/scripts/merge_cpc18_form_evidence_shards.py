#!/usr/bin/env python3
"""Merge disjoint E20 behavior shards with exact coverage validation."""

import argparse
import json

from cpc18_form_evidence_common import CONFIG, ROOT, load_problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", required=True)
    parser.add_argument("--num-shards", type=int, required=True)
    args = parser.parse_args()
    result_dir = ROOT / CONFIG["result_dir"]
    rows, metadata = [], []
    for index in range(args.num_shards):
        suffix = f".shard{index}of{args.num_shards}"
        with (result_dir / "raw" / f"{args.regime}{suffix}.jsonl").open() as handle:
            rows.extend(json.loads(line) for line in handle)
        metadata.append(json.loads((result_dir / f"{args.regime}{suffix}.model.json").read_text()))
    expected = {row["id"] for row in load_problems()}
    observed = {row["problem"] for row in rows}
    if observed != expected:
        raise ValueError(f"Problem coverage mismatch: missing={expected-observed}, extra={observed-expected}")
    keys = [
        (row["problem"], row["evidence_choice"], row["form"], row["order"], row["sample_index"])
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate E20 behavior keys across shards")
    rows.sort(key=lambda row: (
        row["problem"], row["evidence_choice"], row["form"],
        row["order"], row["sample_index"],
    ))
    with (result_dir / "raw" / f"{args.regime}.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    (result_dir / f"{args.regime}.model.json").write_text(json.dumps({
        **metadata[0], "n_problems": len(observed),
        "merged_shards": args.num_shards,
        "shard_problem_counts": [item["n_problems"] for item in metadata],
    }, indent=2) + "\n")
    print(json.dumps({
        "regime": args.regime, "n_rows": len(rows),
        "n_problems": len(observed), "duplicate_keys": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
