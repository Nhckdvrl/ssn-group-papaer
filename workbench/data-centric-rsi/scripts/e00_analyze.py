"""Paired item-level E00 smoke diagnostics; not training-seed evidence."""

import argparse
import hashlib
import json
import random
from pathlib import Path


NAMES = (
    "base_smoke",
    "static_seed17_smoke",
    "base_format_smoke",
    "static_seed17_format_smoke",
)


def load(path: Path) -> dict[str, dict]:
    records = [json.loads(line) for line in path.read_text().splitlines()]
    return {record["record_id"]: record for record in records}


def interval(deltas: list[int], seed: int = 20261002) -> tuple[float, float]:
    rng = random.Random(seed)
    count = len(deltas)
    replicas = sorted(
        sum(deltas[rng.randrange(count)] for _ in range(count)) / count
        for _ in range(5000)
    )
    return replicas[125], replicas[4875]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {name: args.runs / f"{name}.jsonl" for name in NAMES}
    data = {name: load(path) for name, path in paths.items()}
    ids = sorted(data[NAMES[0]])
    if any(sorted(run) != ids for run in data.values()):
        raise ValueError("Paired evaluation requires identical record IDs")
    conditions = {}
    for name, run in data.items():
        predictions = [run[record_id]["prediction"] for record_id in ids]
        conditions[name] = {
            "n": len(ids),
            "correct": sum(run[record_id]["correct"] for record_id in ids),
            "boxed": sum("\\boxed" in prediction for prediction in predictions),
            "expected_prefix": sum(
                "Final Answer: The final answer is" in prediction
                for prediction in predictions
            ),
            "raw_sha256": hashlib.sha256(paths[name].read_bytes()).hexdigest(),
        }
    comparisons = {}
    for key, a, b in (
        ("static_minus_base_original", "base_smoke", "static_seed17_smoke"),
        ("static_minus_base_format", "base_format_smoke", "static_seed17_format_smoke"),
        ("base_format_minus_original", "base_smoke", "base_format_smoke"),
        ("static_format_minus_original", "static_seed17_smoke", "static_seed17_format_smoke"),
    ):
        deltas = [int(data[b][rid]["correct"]) - int(data[a][rid]["correct"]) for rid in ids]
        comparisons[key] = {
            "delta_accuracy": sum(deltas) / len(deltas),
            "item_bootstrap_95_ci": interval(deltas),
            "improved_items": sum(delta > 0 for delta in deltas),
            "worsened_items": sum(delta < 0 for delta in deltas),
        }
    result = {
        "scope": "E00 smoke; one train seed and 72 dev items; item bootstrap does not measure train-seed variation",
        "conditions": conditions,
        "comparisons": comparisons,
        "raw_dir": str(args.runs.resolve()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
