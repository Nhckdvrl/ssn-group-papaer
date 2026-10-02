"""Paired E06 utility analysis on frozen smoke-disjoint MATH dev items."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired_delta(target: dict, reference: dict, ids: list[str]) -> dict:
    values = np.asarray(
        [int(target[rid]["correct"]) - int(reference[rid]["correct"]) for rid in ids],
        dtype=np.int8,
    )
    rng = np.random.default_rng(20261002)
    replicates = np.asarray([
        values[rng.integers(0, len(values), size=len(values))].mean()
        for _ in range(3000)
    ])
    return {
        "delta_correct": int(values.sum()),
        "delta_accuracy": float(values.mean()),
        "paired_item_bootstrap_95_ci": [float(v) for v in np.quantile(replicates, [0.025, 0.975])],
        "improved_items": int((values > 0).sum()),
        "worsened_items": int((values < 0).sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--run", action="append", required=True,
                        help="NAME=prediction-file.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    gold_rows = read_jsonl(args.dev)
    gold = {row["record_id"]: row for row in gold_rows}
    smoke_ids = {row["record_id"] for row in read_jsonl(args.smoke)}
    if len(gold_rows) != 1740 or len(gold) != 1740 or len(smoke_ids) != 72:
        raise ValueError("Unexpected frozen MATH dev or smoke set")
    # The dev360 subset is saved independently by the frozen preparation script.
    dev360_path = args.dev.with_name("dev_360.jsonl")
    dev360_ids = {row["record_id"] for row in read_jsonl(dev360_path)}
    paths = {}
    for spec in args.run:
        name, raw_path = spec.split("=", 1)
        if name in paths:
            raise ValueError(f"Duplicate run name {name}")
        paths[name] = Path(raw_path)
    data = {}
    for name, path in paths.items():
        rows = read_jsonl(path)
        by_id = {row["record_id"]: row for row in rows}
        if len(rows) != 1740 or len(by_id) != 1740 or set(by_id) != set(gold):
            raise ValueError(f"Incomplete or duplicate evaluation items for {name}")
        if any(row["problem_hash"] != gold[row["record_id"]]["problem_hash"] for row in rows):
            raise ValueError(f"Evaluation problem hash mismatch for {name}")
        data[name] = by_id
    subsets = {
        "heldout1668": sorted(set(gold) - smoke_ids),
        "heldout280": sorted(dev360_ids - smoke_ids),
    }
    if len(subsets["heldout1668"]) != 1668 or len(subsets["heldout280"]) != 280:
        raise ValueError("Frozen heldout counts changed")
    report = {
        "scope": "MATH train-derived dev; feedback smoke excluded; paired item CI is not seed CI",
        "dev_sha256": sha256(args.dev),
        "smoke_sha256": sha256(args.smoke),
        "run_sha256": {name: sha256(path) for name, path in paths.items()},
        "subsets": {},
    }
    for subset_name, ids in subsets.items():
        scores = {
            name: {"correct": sum(int(by_id[rid]["correct"]) for rid in ids),
                   "n": len(ids)}
            for name, by_id in data.items()
        }
        comparisons = {}
        for name, by_id in data.items():
            if name == "base":
                continue
            if name.startswith("static_seed"):
                reference = "base"
            elif name.startswith("retrieval_seed"):
                reference = name.replace("retrieval", "static", 1)
            elif name.startswith("matched_seed"):
                reference = name.replace("matched", "retrieval", 1)
            elif name.startswith("with_state_seed"):
                reference = name.replace("with_state", "no_state", 1)
            elif name.startswith("no_state_seed"):
                reference = name.replace("no_state", "static", 1)
            else:
                raise ValueError(f"Unknown run name {name}")
            if reference in data:
                comparisons[f"{name}_minus_{reference}"] = paired_delta(
                    by_id, data[reference], ids
                )
            if name.startswith("with_state_seed"):
                static = name.replace("with_state", "static", 1)
                if static in data:
                    comparisons[f"{name}_minus_{static}"] = paired_delta(
                        by_id, data[static], ids
                    )
            if name.startswith("matched_seed"):
                static = name.replace("matched", "static", 1)
                if static in data:
                    comparisons[f"{name}_minus_{static}"] = paired_delta(
                        by_id, data[static], ids
                    )
        report["subsets"][subset_name] = {
            "n": len(ids), "scores": scores, "comparisons": comparisons,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["subsets"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
