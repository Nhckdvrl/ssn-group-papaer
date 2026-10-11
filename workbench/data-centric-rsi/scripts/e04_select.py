"""E04's frozen error-following retrieval from genuinely labeled MATH train.

The feedback is the base model's formatted-prompt errors on E00 smoke.  Each
error gets two unused nearest train problems in two passes.  Evaluation must
exclude every smoke item used here.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from dataenvgym.gym.tasks.math.MATH.scoring import render_solution_for_scoring


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--feedback", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    pool = read_jsonl(args.pool)
    smoke = read_jsonl(args.smoke)
    feedback = {row["record_id"]: row for row in read_jsonl(args.feedback)}
    if set(feedback) != {row["record_id"] for row in smoke}:
        raise ValueError("Feedback and smoke IDs do not match")
    errors = [row for row in smoke if not feedback[row["record_id"]]["correct"]]
    if len(errors) != 60:
        raise ValueError(f"Expected frozen 60/72 errors, got {len(errors)}")
    vectorizer = TfidfVectorizer(
        analyzer="char", ngram_range=(3, 5), min_df=2,
        max_features=100_000, sublinear_tf=True, dtype=np.float32,
    )
    all_matrix = vectorizer.fit_transform(
        [row["problem"] for row in pool] + [row["problem"] for row in errors]
    )
    similarities = (all_matrix[len(pool):] @ all_matrix[:len(pool)].T).toarray()
    rankings = np.argsort(-similarities, axis=1, kind="stable")
    seen: set[int] = set()
    selected: list[tuple[int, int, float]] = []
    # Two passes ensure that every observed error contributes two unique items.
    for _pass in range(2):
        for error_index, ranking in enumerate(rankings):
            candidate = next(int(index) for index in ranking if int(index) not in seen)
            seen.add(candidate)
            selected.append((candidate, error_index, float(similarities[error_index, candidate])))
    if len(selected) != 120 or len(seen) != 120:
        raise AssertionError("Selection must contain 120 unique training rows")
    outputs = []
    for candidate, _error_index, _similarity in selected:
        row = pool[candidate]
        outputs.append({
            "record_id": row["record_id"],
            "instruction": row["problem"],
            "response": render_solution_for_scoring(row["solution"], row["answer"]),
            "problem_hash": row["problem_hash"],
            "level": row["level"], "type": row["type"],
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as handle:
        for row in outputs:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    manifest = {
        "policy": "two-nearest-per-base-error; char 3-5 gram TF-IDF",
        "pool_sha256": sha256(args.pool),
        "smoke_sha256": sha256(args.smoke),
        "feedback_sha256": sha256(args.feedback),
        "output_sha256": sha256(args.output),
        "pool_count": len(pool), "error_count": len(errors), "selected_count": len(outputs),
        "exact_overlap_with_feedback": len(
            {row["problem_hash"] for row in outputs} &
            {row["problem_hash"] for row in smoke}
        ),
        "similarity": {
            "min": min(score for _, _, score in selected),
            "mean": sum(score for _, _, score in selected) / len(selected),
            "max": max(score for _, _, score in selected),
        },
        "selected_level": dict(Counter(row["level"] for row in outputs)),
        "selected_type": dict(Counter(row["type"] for row in outputs)),
        "mean_problem_chars": sum(len(row["instruction"]) for row in outputs) / len(outputs),
        "mean_response_chars": sum(len(row["response"]) for row in outputs) / len(outputs),
        "selected_ids": [row["record_id"] for row in outputs],
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: value for key, value in manifest.items() if key != "selected_ids"}, indent=2))


if __name__ == "__main__":
    main()
