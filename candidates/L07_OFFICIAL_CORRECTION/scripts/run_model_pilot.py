#!/usr/bin/env python3
"""Run E002 official-update arbitration conditions on one cached model."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DECISION = re.compile(r"\b([AB])\b", re.I)


def render(item: dict, condition: str, unrelated: dict, candidate_order: str) -> tuple[str, str, str]:
    if candidate_order == "old_first":
        candidate_a, candidate_b = item["old_candidate"], item["new_candidate"]
        choice_for = {"OLD": "A", "NEW": "B"}
    elif candidate_order == "new_first":
        candidate_a, candidate_b = item["new_candidate"], item["old_candidate"]
        choice_for = {"OLD": "B", "NEW": "A"}
    else:
        raise ValueError(candidate_order)
    header = (
        "Decide which candidate answers the question under the supplied scholarly record.\n"
        f"Question: {item['question']}\n"
        f"Candidate A: {candidate_a}\n"
        f"Candidate B: {candidate_b}\n"
    )
    original = f"ORIGINAL ARTICLE (PMID {item['original_pmid']}):\n{item['original_excerpt']}"
    correction = f"OFFICIAL CORRECTION (PMID {item['correction_pmid']}):\n{item['correction_excerpt']}"
    other = (
        f"OFFICIAL CORRECTION FOR A DIFFERENT ARTICLE (PMID {unrelated['correction_pmid']}):\n"
        f"{unrelated['correction_excerpt']}"
    )
    if condition == "original_only":
        evidence, expected_semantic = original, "OLD"
    elif condition == "correction_only":
        evidence, expected_semantic = correction, "NEW"
    elif condition == "original_then_correction":
        evidence, expected_semantic = f"{original}\n\n{correction}", "NEW"
    elif condition == "correction_then_original":
        evidence, expected_semantic = f"{correction}\n\n{original}", "NEW"
    elif condition == "explicit_update":
        evidence, expected_semantic = (
            "The official correction is an update operation: corrected content supersedes obsolete content in the original.\n\n"
            f"{original}\n\n{correction}"
        ), "NEW"
    elif condition == "unrelated_correction":
        evidence, expected_semantic = f"{original}\n\n{other}", "OLD"
    else:
        raise ValueError(condition)
    return (
        f"{header}\n{evidence}\n\nAnswer exactly A or B, with no explanation.",
        expected_semantic,
        choice_for[expected_semantic],
    )


def decision(output: str) -> str:
    choices = DECISION.findall(output)
    unique = {choice.upper() for choice in choices}
    return next(iter(unique)).upper() if len(unique) == 1 else "INVALID"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--run-id", default="e002b_counterbalanced")
    args = parser.parse_args()

    project = args.config.resolve().parent.parent
    config = json.loads(args.config.read_text())
    if args.model not in config["models"]:
        raise ValueError(f"Unknown model key: {args.model}")
    model_name = config["models"][args.model]
    items = list(map(json.loads, (project / "data/processed/e002/pilot_items.jsonl").read_text().splitlines()))
    if len(items) < 2:
        raise ValueError("Unrelated-correction control requires at least two items")

    prompts = []
    metadata = []
    for index, item in enumerate(items):
        unrelated = items[(index + 1) % len(items)]
        for condition in config["conditions"]:
            for candidate_order in ("old_first", "new_first"):
                prompt, expected_semantic, expected_choice = render(item, condition, unrelated, candidate_order)
                prompts.append(prompt)
                metadata.append({
                    "item_id": item["item_id"],
                    "condition": condition,
                    "candidate_order": candidate_order,
                    "expected_semantic": expected_semantic,
                    "expected_choice": expected_choice,
                    "unrelated_item_id": unrelated["item_id"] if condition == "unrelated_correction" else None,
                })

    tokenizer_kwargs = {"local_files_only": True}
    if model_name.startswith("mistralai/"):
        tokenizer_kwargs["fix_mistral_regex"] = True
    tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        local_files_only=True,
        dtype=torch.bfloat16,
        device_map={"": args.device},
    )
    model.eval()

    outputs = []
    for start in range(0, len(prompts), args.batch_size):
        batch_prompts = prompts[start : start + args.batch_size]
        chats = [[{"role": "user", "content": prompt}] for prompt in batch_prompts]
        rendered = tokenizer.apply_chat_template(chats, tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(rendered, return_tensors="pt", padding=True).to(args.device)
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                do_sample=bool(config["generation"]["do_sample"]),
                max_new_tokens=int(config["generation"]["max_new_tokens"]),
                pad_token_id=tokenizer.pad_token_id,
            )
        new_tokens = generated[:, encoded["input_ids"].shape[1] :]
        outputs.extend(tokenizer.batch_decode(new_tokens, skip_special_tokens=True))

    rows = []
    for meta, prompt, output in zip(metadata, prompts, outputs):
        predicted = decision(output)
        predicted_semantic = (
            ("OLD" if predicted == "A" else "NEW")
            if meta["candidate_order"] == "old_first" and predicted in {"A", "B"}
            else ("NEW" if predicted == "A" else "OLD")
            if predicted in {"A", "B"}
            else "INVALID"
        )
        rows.append({
            **meta,
            "predicted_choice": predicted,
            "predicted_semantic": predicted_semantic,
            "correct": predicted == meta["expected_choice"],
            "output": output,
            "prompt": prompt,
        })

    by_condition = defaultdict(list)
    for row in rows:
        by_condition[row["condition"]].append(row)
    by_condition_order = defaultdict(list)
    for row in rows:
        by_condition_order[(row["condition"], row["candidate_order"])].append(row)
    summary = {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "model_key": args.model,
        "model_name": model_name,
        "n_items": len(items),
        "n_predictions": len(rows),
        "condition_accuracy": {
            condition: sum(row["correct"] for row in values) / len(values)
            for condition, values in by_condition.items()
        },
        "condition_order_accuracy": {
            f"{condition}/{order}": sum(row["correct"] for row in values) / len(values)
            for (condition, order), values in by_condition_order.items()
        },
        "choice_counts": dict(Counter(row["predicted_choice"] for row in rows)),
        "semantic_counts": dict(Counter(row["predicted_semantic"] for row in rows)),
        "torch": torch.__version__,
    }
    result_dir = project / f"results/{args.run_id}" / args.model
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "predictions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    (result_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
