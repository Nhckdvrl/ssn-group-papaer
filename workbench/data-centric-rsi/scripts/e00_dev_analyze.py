"""Paired E00/E04 dev report, with feedback smoke excluded for E04."""

import argparse
import hashlib
import json
import random
from pathlib import Path


RUNS = ("base", "static_seed17", "static_seed29", "static_seed43")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def interval(deltas: list[int], seed: int = 20261002) -> list[float]:
    rng = random.Random(seed)
    n = len(deltas)
    values = sorted(
        sum(deltas[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(5000)
    )
    return [values[125], values[4875]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--suffix", default="_format_dev360.jsonl",
                        help="Filename suffix for the four E00 base/static reports")
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--extra", action="append", default=[],
                        help="Additional run as NAME=PATH (e.g. retrieval_seed17=file.jsonl)")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {name: args.runs / f"{name}{args.suffix}" for name in RUNS}
    for specification in args.extra:
        name, raw_path = specification.split("=", 1)
        if name in paths:
            raise ValueError(f"Duplicate run name: {name}")
        paths[name] = Path(raw_path)
    data = {
        name: {row["record_id"]: row for row in read_jsonl(path)}
        for name, path in paths.items()
    }
    all_ids = sorted(data["base"])
    if any(sorted(records) != all_ids for records in data.values()):
        raise ValueError("All reports must cover the same 352 frozen IDs")
    smoke_ids = {row["record_id"] for row in read_jsonl(args.smoke)}
    heldout_ids = [record_id for record_id in all_ids if record_id not in smoke_ids]
    if len(all_ids) != 352 or len(smoke_ids) != 72 or len(heldout_ids) != 280:
        raise ValueError("Unexpected frozen evaluation size")
    subsets = {"dev352": all_ids, "heldout280": heldout_ids}
    report = {
        "scope": "MATH train-derived dev; one student and 120 training items; item bootstrap is not seed CI",
        "source_file_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in paths.items()
        },
        "subsets": {},
    }
    for subset_name, ids in subsets.items():
        scores = {
            name: {
                "correct": sum(bool(rows[record_id]["correct"]) for record_id in ids),
                "accuracy": sum(bool(rows[record_id]["correct"]) for record_id in ids) / len(ids),
            }
            for name, rows in data.items()
        }
        differences = {}
        for name in data:
            if name.startswith("retrieval_seed") or name.startswith("matched_seed"):
                reference = "static_seed" + name.rsplit("seed", 1)[1]
            else:
                reference = "base"
            if name == "base":
                continue
            deltas = [
                int(data[name][rid]["correct"]) - int(data[reference][rid]["correct"])
                for rid in ids
            ]
            differences[f"{name}_minus_{reference}"] = {
                "delta_accuracy": sum(deltas) / len(deltas),
                "item_bootstrap_95_ci": interval(deltas),
                "improved_items": sum(delta > 0 for delta in deltas),
                "worsened_items": sum(delta < 0 for delta in deltas),
            }
        if "matched_seed17" in data and "retrieval_seed17" in data:
            deltas = [
                int(data["matched_seed17"][rid]["correct"])
                - int(data["retrieval_seed17"][rid]["correct"])
                for rid in ids
            ]
            differences["matched_seed17_minus_retrieval_seed17"] = {
                "delta_accuracy": sum(deltas) / len(deltas),
                "item_bootstrap_95_ci": interval(deltas),
                "improved_items": sum(delta > 0 for delta in deltas),
                "worsened_items": sum(delta < 0 for delta in deltas),
            }
        report["subsets"][subset_name] = {
            "n": len(ids), "scores": scores, "differences": differences,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["subsets"], indent=2))


if __name__ == "__main__":
    main()
