"""Freeze an auditable MATH split for the DataEnvGym E00 local adaptation.

Run with PYTHONPATH pointing to the pinned DataEnvGym/src checkout. Large JSONL
files stay outside git; only the manifest is copied into results/.
"""

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

from datasets import load_dataset
from dataenvgym.gym.tasks.math.MATH.scoring import process_docs, render_solution_for_scoring


CONFIGS = (
    "algebra",
    "counting_and_probability",
    "geometry",
    "intermediate_algebra",
    "number_theory",
    "prealgebra",
    "precalculus",
)
DATASET_REVISION = "21a5633873b6a120296cce3e2df9d5550074f4a3"
SEED = 20261002


def content_hash(problem: str) -> str:
    return hashlib.sha256(" ".join(problem.split()).encode()).hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> str:
    digest = hashlib.sha256()
    with path.open("w") as output:
        for row in rows:
            line = json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"
            output.write(line)
            digest.update(line.encode())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    splits: dict[str, list[dict]] = {"train": [], "test": []}
    for config in CONFIGS:
        dataset = load_dataset(
            "EleutherAI/hendrycks_math", config, revision=DATASET_REVISION
        )
        for split in splits:
            processed = process_docs(dataset[split])
            for index, item in enumerate(processed):
                row = dict(item)
                row["record_id"] = f"MATH_{split}_{config}_{index}"
                row["problem_hash"] = content_hash(row["problem"])
                splits[split].append(row)

    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in splits["train"]:
        cells[(row["level"], row["type"])].append(row)
    dev = [row for cell in sorted(cells) for row in cells[cell][:50]]
    dev_360 = [row for cell in sorted(cells) for row in cells[cell][:10]]
    smoke = [row for cell in sorted(cells) for row in cells[cell][:2]]
    dev_hashes = {row["problem_hash"] for row in dev}
    test_hashes = {row["problem_hash"] for row in splits["test"]}
    pool_cells: dict[tuple[str, str], list[dict]] = {}
    rng = random.Random(SEED)
    for cell, rows in sorted(cells.items()):
        available = [
            row for row in rows
            if row["problem_hash"] not in dev_hashes
            and row["problem_hash"] not in test_hashes
        ]
        rng.shuffle(available)
        pool_cells[cell] = available

    # Round robin makes the first 120 examples cover all populated cells.
    static: list[dict] = []
    index = 0
    while len(static) < 120:
        advanced = False
        for cell in sorted(pool_cells):
            if index < len(pool_cells[cell]):
                static.append(pool_cells[cell][index])
                advanced = True
                if len(static) == 120:
                    break
        if not advanced:
            raise RuntimeError("Fewer than 120 non-overlapping training examples")
        index += 1

    supervised = [
        {
            "record_id": row["record_id"],
            "instruction": row["problem"],
            "response": render_solution_for_scoring(row["solution"], row["answer"]),
            "problem_hash": row["problem_hash"],
            "level": row["level"],
            "type": row["type"],
        }
        for row in static
    ]
    eligible_pool = [
        row for row in splits["train"]
        if row["problem_hash"] not in dev_hashes
        and row["problem_hash"] not in test_hashes
    ]
    output_hashes = {
        "dev.jsonl": write_jsonl(args.out / "dev.jsonl", dev),
        "dev_360.jsonl": write_jsonl(args.out / "dev_360.jsonl", dev_360),
        "smoke.jsonl": write_jsonl(args.out / "smoke.jsonl", smoke),
        "static_120.jsonl": write_jsonl(args.out / "static_120.jsonl", supervised),
        "train_pool.jsonl": write_jsonl(args.out / "train_pool.jsonl", eligible_pool),
    }
    test_hash_path = args.out / "test_problem_hashes.txt"
    test_hash_path.write_text("\n".join(sorted(test_hashes)) + "\n")
    output_hashes["test_problem_hashes.txt"] = hashlib.sha256(
        test_hash_path.read_bytes()
    ).hexdigest()
    # Seal the test IDs/hashes now; create no test predictions or score.
    manifest = {
        "dataset": "EleutherAI/hendrycks_math",
        "revision": DATASET_REVISION,
        "seed": SEED,
        "config_order": CONFIGS,
        "counts": {
            "train": len(splits["train"]),
            "test": len(splits["test"]),
            "dev": len(dev),
            "dev_360": len(dev_360),
            "smoke": len(smoke),
            "static": len(static),
            "train_pool": len(eligible_pool),
            "cells": len(cells),
        },
        "overlap": {
            "train_test_problem_hashes": len(
                {row["problem_hash"] for row in splits["train"]} & test_hashes
            ),
            "static_dev_problem_hashes": len(
                {row["problem_hash"] for row in static} & dev_hashes
            ),
            "static_test_problem_hashes": len(
                {row["problem_hash"] for row in static} & test_hashes
            ),
        },
        "sha256": output_hashes,
        "data_dir": str(args.out.resolve()),
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
