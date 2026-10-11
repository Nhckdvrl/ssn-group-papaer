"""Frozen nested 960-example gold SFT baseline for E10.

Only MATH train-pool rows are selected. The first 120 rows are byte-equivalent
to E00's static SFT set; the remaining rows use cell-balanced seeded sampling.
"""

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from dataenvgym.gym.tasks.math.MATH.scoring import render_solution_for_scoring


EXPECTED = {
    "train_pool.jsonl": "73d48edff350169563df2a5dd68f77dcab9d28753f08860f76119ce8e3f6fe5c",
    "static_120.jsonl": "17e5d5e58f82662a54ba9dca54f6c2aba805c67d54e92d3d0696490c5be27e08",
    "dev.jsonl": "33999c27214e4727c13686a3f47f3ed5ec9ec57aa529f0e2dfd9c0229268d8dc",
    "test_problem_hashes.txt": "abf39a90286cfa7a468ec197fba8839c1671bc9b2744c7c43f8a5067d8d69557",
}
SEED = 20261002


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.manifest.exists():
        raise FileExistsError("E10 output/manifest already exists")
    for name, expected in EXPECTED.items():
        observed = digest(args.data_dir / name)
        if observed != expected:
            raise ValueError(f"{name} hash mismatch: {observed}")
    pool = read_jsonl(args.data_dir / "train_pool.jsonl")
    static = read_jsonl(args.data_dir / "static_120.jsonl")
    dev_hashes = {r["problem_hash"] for r in read_jsonl(args.data_dir / "dev.jsonl")}
    test_hashes = set((args.data_dir / "test_problem_hashes.txt").read_text().splitlines())
    if len(static) != 120 or len({r["problem_hash"] for r in static}) != 120:
        raise ValueError("Static reference is not the frozen 120 unique examples")
    chosen_hashes = {r["problem_hash"] for r in static}
    chosen_ids = {r["record_id"] for r in static}
    if chosen_hashes & (dev_hashes | test_hashes):
        raise ValueError("Static reference has dev/test contamination")
    cells = defaultdict(list)
    unique_pool_hashes = set()
    for row in pool:
        hash_ = row["problem_hash"]
        if hash_ in unique_pool_hashes or hash_ in chosen_hashes:
            continue
        unique_pool_hashes.add(hash_)
        if hash_ in dev_hashes or hash_ in test_hashes:
            raise ValueError(f"Pool contamination: {row['record_id']}")
        cells[(row["level"], row["type"])].append(row)
    rng = random.Random(SEED)
    for cell in sorted(cells):
        cells[cell].sort(key=lambda r: r["record_id"])
        rng.shuffle(cells[cell])
    selected = list(static)
    position = 0
    while len(selected) < 960:
        progress = False
        for cell in sorted(cells):
            if position >= len(cells[cell]):
                continue
            row = cells[cell][position]
            selected.append({
                "record_id": row["record_id"],
                "instruction": row["problem"],
                "response": render_solution_for_scoring(row["solution"], row["answer"]),
                "problem_hash": row["problem_hash"],
                "level": row["level"],
                "type": row["type"],
            })
            progress = True
            if len(selected) == 960:
                break
        if not progress:
            raise ValueError("Pool exhausted before selecting 960")
        position += 1
    if len({r["record_id"] for r in selected}) != 960 or len({r["problem_hash"] for r in selected}) != 960:
        raise AssertionError("Selected records or questions repeat")
    if not chosen_ids <= {r["record_id"] for r in selected}:
        raise AssertionError("Original static examples missing")
    if {r["problem_hash"] for r in selected} & (dev_hashes | test_hashes):
        raise AssertionError("Selected train/dev/test question overlap")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        for row in selected:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    manifest = {
        "policy": "static120 original order + cell-round-robin 840; per-cell sorted ID then seeded shuffle",
        "seed": SEED,
        "input_sha256": EXPECTED,
        "output_sha256": digest(args.output),
        "selected_count": len(selected),
        "original_static_count": len(static),
        "cell_counts": {f"{level}::{type_}": n for (level, type_), n in sorted(Counter((r["level"], r["type"]) for r in selected).items())},
        "selected_ids": [r["record_id"] for r in selected],
        "dev_overlap": 0,
        "test_overlap": 0,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "selected_ids"}, indent=2))


if __name__ == "__main__":
    main()
