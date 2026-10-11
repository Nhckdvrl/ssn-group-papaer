"""Cheap lexical-overlap audit for E08's frozen real-label data actions."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", type=Path, required=True)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--matched", type=Path, required=True)
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    actions = {
        name: read_jsonl(getattr(args, name))
        for name in ("static", "retrieval", "matched")
    }
    smoke_ids = {r["record_id"] for r in read_jsonl(args.smoke)}
    heldout = [r for r in read_jsonl(args.dev) if r["record_id"] not in smoke_ids]
    if len(heldout) != 1668 or len(smoke_ids) != 72 or any(
        len(rows) != 120 for rows in actions.values()
    ):
        raise ValueError("Frozen action/heldout counts changed")
    all_actions = [r for rows in actions.values() for r in rows]
    tfidf = TfidfVectorizer(
        analyzer="char", ngram_range=(3, 5), min_df=2,
        max_features=100_000, sublinear_tf=True, dtype=np.float32,
    )
    matrix = tfidf.fit_transform(
        [r["instruction"] for r in all_actions] + [r["problem"] for r in heldout]
    )
    targets = matrix[len(all_actions):]
    report = {
        "experiment": "E08", "metric": "max heldout1668 char 3-5 gram TF-IDF cosine",
        "threshold": 0.8,
        "file_sha256": {
            name: file_hash(getattr(args, name))
            for name in ("static", "retrieval", "matched", "dev", "smoke")
        },
        "actions": {},
    }
    start = 0
    for name, rows in actions.items():
        sims = (matrix[start:start + len(rows)] @ targets.T).toarray()
        start += len(rows)
        maxima = sims.max(axis=1)
        best_index = sims.argmax(axis=1)
        top = np.argsort(-maxima, kind="stable")[:10]
        report["actions"][name] = {
            "n": len(rows),
            "median_max_similarity": float(np.median(maxima)),
            "p90_max_similarity": float(np.quantile(maxima, 0.9)),
            "at_least_0_8_count": int((maxima >= 0.8).sum()),
            "top_pairs": [
                {
                    "train_id": rows[i]["record_id"],
                    "heldout_id": heldout[int(best_index[i])]["record_id"],
                    "similarity": float(maxima[i]),
                }
                for i in top
            ],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["actions"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
