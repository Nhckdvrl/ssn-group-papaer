"""Audit E10 full-dev scores and freeze feedback-derived action overlap."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


NAMES = ("base", "static120", "static960")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired_ci(left: np.ndarray, right: np.ndarray) -> dict:
    diff = right.astype(np.int8) - left.astype(np.int8)
    rng = np.random.default_rng(20261002)
    samples = []
    for _ in range(10):
        index = rng.integers(0, len(diff), size=(1000, len(diff)))
        samples.extend(diff[index].mean(axis=1).tolist())
    lo, hi = np.quantile(samples, (0.025, 0.975))
    return {
        "difference_items": int(diff.sum()),
        "difference_pp": float(100 * diff.mean()),
        "item_bootstrap95_pp": [float(100 * lo), float(100 * hi)],
        "bootstrap_replicates": len(samples),
    }


def action_ids(
    pool: list[dict], smoke: list[dict], correct: dict[str, bool],
    rankings: dict[str, np.ndarray],
) -> tuple[list[str], int]:
    errors = [row for row in smoke if not correct[row["record_id"]]]
    if not errors:
        raise ValueError("No errors; no action can be selected")
    selected = []
    seen = set()
    while len(selected) < 120:
        for error in errors:
            ranking = rankings[error["record_id"]]
            candidate = next(int(i) for i in ranking if int(i) not in seen)
            seen.add(candidate)
            selected.append(pool[candidate]["record_id"])
            if len(selected) == 120:
                break
    return selected, len(errors)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    dev_path = args.data_dir / "dev.jsonl"
    smoke_path = args.data_dir / "smoke.jsonl"
    dev = read_jsonl(dev_path)
    smoke = read_jsonl(smoke_path)
    smoke_ids = {row["record_id"] for row in smoke}
    if len(dev) != 1740 or len(smoke) != 72 or not smoke_ids <= {r["record_id"] for r in dev}:
        raise ValueError("E10 dev/smoke split invalid")
    prediction_paths = {
        name: args.run_dir / f"{name}_zero_format_dev1740.jsonl" for name in NAMES
    }
    predictions = {}
    for name, path in prediction_paths.items():
        pred = read_jsonl(path)
        if len(pred) != len(dev):
            raise ValueError(f"{name} incomplete: {len(pred)}")
        for expected, actual in zip(dev, pred, strict=True):
            if (expected["record_id"], expected["problem_hash"]) != (
                actual["record_id"], actual["problem_hash"]
            ):
                raise ValueError(f"{name} prediction split/order mismatch")
        summary = json.loads(path.with_suffix(".summary.json").read_text())
        if sum(bool(row["correct"]) for row in pred) != summary["correct"]:
            raise ValueError(f"{name} summary score mismatch")
        if summary["data_sha256"] != sha256(dev_path) or not summary["enforce_eager"]:
            raise ValueError(f"{name} evaluation protocol mismatch")
        if summary["vllm_v1_multiprocessing"] != "0":
            raise ValueError(f"{name} vLLM scheduling mismatch")
        predictions[name] = pred
    heldout_index = [i for i, row in enumerate(dev) if row["record_id"] not in smoke_ids]
    if len(heldout_index) != 1668:
        raise AssertionError("Unexpected heldout size")
    score = {
        name: np.array([bool(row["correct"]) for row in predictions[name]], dtype=bool)
        for name in NAMES
    }
    summary = {}
    for name in NAMES:
        per_type = defaultdict(lambda: {"count": 0, "correct": 0})
        for i in heldout_index:
            item = per_type[dev[i]["type"]]
            item["count"] += 1
            item["correct"] += int(score[name][i])
        pred = predictions[name]
        summary[name] = {
            "full_correct": int(score[name].sum()),
            "heldout_correct": int(score[name][heldout_index].sum()),
            "heldout_n": len(heldout_index),
            "heldout_accuracy": float(score[name][heldout_index].mean()),
            "format_final_answer_count": sum("Final Answer: The final answer is" in row["prediction"] for row in pred),
            "boxed_count": sum("\\boxed" in row["prediction"] for row in pred),
            "per_type_heldout": dict(sorted(per_type.items())),
        }
    pairwise = {
        "static120_minus_base": paired_ci(score["base"][heldout_index], score["static120"][heldout_index]),
        "static960_minus_static120": paired_ci(score["static120"][heldout_index], score["static960"][heldout_index]),
        "static960_minus_base": paired_ci(score["base"][heldout_index], score["static960"][heldout_index]),
    }
    static960_path = args.data_dir / "static_960_e10.jsonl"
    trained = read_jsonl(static960_path)
    trained_ids = {row["record_id"] for row in trained}
    trained_hashes = {row["problem_hash"] for row in trained}
    pool = []
    candidate_hashes = set()
    for row in read_jsonl(args.data_dir / "train_pool.jsonl"):
        if row["record_id"] in trained_ids or row["problem_hash"] in trained_hashes:
            continue
        if row["problem_hash"] in candidate_hashes:
            continue
        candidate_hashes.add(row["problem_hash"])
        pool.append(row)
    if len(pool) < 120:
        raise ValueError("Insufficient unused MATH pool")
    vectorizer = TfidfVectorizer(
        analyzer="char", ngram_range=(3, 5), min_df=2,
        max_features=100_000, sublinear_tf=True, dtype=np.float32,
    )
    # Exactly one fit; every state is scored in the same feature space.
    mat = vectorizer.fit_transform(
        [row["problem"] for row in pool] + [row["problem"] for row in smoke]
    )
    sims = (mat[len(pool):] @ mat[:len(pool)].T).toarray()
    rankings = {
        row["record_id"]: np.argsort(-sims[i], kind="stable")
        for i, row in enumerate(smoke)
    }
    actions = {}
    errors = {}
    for name in NAMES:
        feedback = {row["record_id"]: bool(row["correct"]) for row in predictions[name]}
        actions[name], errors[name] = action_ids(pool, smoke, feedback, rankings)
    overlap = {}
    dev_index = {row["record_id"]: i for i, row in enumerate(dev)}
    for a, b in (("base", "static120"), ("base", "static960"), ("static120", "static960")):
        intersection = len(set(actions[a]) & set(actions[b]))
        error_a = {row["record_id"] for row in smoke if not score[a][dev_index[row["record_id"]]]}
        error_b = {row["record_id"] for row in smoke if not score[b][dev_index[row["record_id"]]]}
        error_intersection = len(error_a & error_b)
        overlap[f"{a}_vs_{b}"] = {
            "action_common": intersection,
            "action_jaccard": intersection / (240 - intersection),
            "error_common": error_intersection,
            "error_jaccard": error_intersection / len(error_a | error_b),
        }
    train_run_path = args.run_dir / "train960_seed17" / "run.json"
    train_run = json.loads(train_run_path.read_text())
    if train_run["data_sha256"] != sha256(static960_path):
        raise ValueError("Training data hash mismatch")
    result = {
        "protocol": "Gemma2 fixed zero-shot format, eager, V1 multiprocessing disabled, same A100, dev1740",
        "data_sha256": {
            "dev": sha256(dev_path), "smoke": sha256(smoke_path),
            "static960": sha256(static960_path),
        },
        "prediction_sha256": {name: sha256(path) for name, path in prediction_paths.items()},
        "summary": summary,
        "pairwise": pairwise,
        "feedback_error_count": errors,
        "action_overlap": overlap,
        "action_selected_ids": actions,
        "train_run": train_run,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "summary": {k: {m: v[m] for m in ("heldout_correct", "heldout_accuracy")} for k, v in summary.items()},
        "pairwise": pairwise,
        "feedback_error_count": errors,
        "action_overlap": overlap,
    }, indent=2))


if __name__ == "__main__":
    main()
