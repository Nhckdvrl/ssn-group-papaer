"""Balanced same-vocabulary fact swaps, with a fixed no-context query control."""
import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

from frozen_probe import Scorer

ROOT = Path(__file__).resolve().parents[1]
NAMES = [("Alice", "Bob"), ("Mary", "John"), ("Emma", "David"), ("Tom", "Anna")]
LOCATIONS = [("kitchen", "厨房"), ("garden", "花园"), ("bedroom", "卧室"),
             ("office", "办公室"), ("bathroom", "浴室"), ("park", "公园")]


def build_items():
    rows = []
    pair = 0
    for names in NAMES:
        for locations in combinations(LOCATIONS, 2):
            for target in [0, 1]:
                for order in [0, 1]:
                    for context_language in ["en", "zh"]:
                        for answer_language in ["en", "zh"]:
                            twins = []
                            for swap in [0, 1]:
                                sentences = []
                                for person in [order, 1-order]:
                                    location = locations[person ^ swap][0 if context_language == "en" else 1]
                                    sentences.append(f"{names[person]} is in the {location}." if context_language == "en"
                                                     else f"{names[person]}在{location}。")
                                query = f"{names[target]} is in the" if answer_language == "en" else f"{names[target]}在"
                                story = " ".join(sentences)
                                row = {"pair_id": pair, "swap": swap, "context_language": context_language,
                                       "answer_language": answer_language, "target": target, "fact_order": order,
                                       "names": names, "location_en": [loc[0] for loc in locations], "story": story,
                                       "query": query, "context": story + "\n" + query, "gold": target ^ swap,
                                       "options": [" " + loc[0 if answer_language == "en" else 1] for loc in locations]}
                                rows.append(row)
                                twins.append(row)
                            assert Counter(twins[0]["story"]) == Counter(twins[1]["story"])
                            assert twins[0]["gold"] != twins[1]["gold"]
                            assert twins[0]["options"] == twins[1]["options"]
                    pair += 1
    assert len(rows) == 1920 and pair == 240
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["noswitch", "switch", "par"], required=True)
    parser.add_argument("--seed", type=int, choices=[42, 43, 44], default=42)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "artifacts/model_manifests" / f"macaroni__{args.condition}__s{args.seed}.json").read_text())
    rows = build_items()
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    output = ROOT / "artifacts/p3" / f"macaroni_{args.condition}_s{args.seed}_location.jsonl"
    if output.exists():
        raise FileExistsError(output)
    scorer = Scorer(manifest["path"], 32, compute_dtype="fp32", weight_dtype="fp32")
    requests = [(r["context"], option) for r in rows for option in r["options"]]
    max_length = max(len(scorer.encode(*r)[0]) for r in requests)
    assert max_length <= scorer.model.config.max_position_embeddings
    controls = list(dict.fromkeys((r["query"], option) for r in rows for option in r["options"]))
    control_scores = dict(zip(controls, scorer.score(controls)))
    start = time.time()
    scores = scorer.score(requests)
    with output.open("w") as target:
        for i, row in enumerate(rows):
            target.write(json.dumps({**row, "scores": scores[2*i:2*i+2],
                                     "control_scores": [control_scores[(row["query"], option)] for option in row["options"]]}, ensure_ascii=False) + "\n")
    output.with_suffix(".meta.json").write_text(json.dumps({"model": manifest, "args": vars(args),
        "items_sha256": digest, "expected_items": len(rows), "max_tokens": max_length,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "weight_dtype": "fp32", "compute_dtype": "fp32", "elapsed_seconds": time.time()-start}, indent=2) + "\n")
    print(json.dumps({"output": str(output), "rows": len(rows), "max_tokens": max_length}), flush=True)


if __name__ == "__main__":
    main()
