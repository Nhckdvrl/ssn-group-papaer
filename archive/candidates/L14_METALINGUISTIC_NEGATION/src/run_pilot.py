#!/usr/bin/env python3
"""L14 E01/E02 scorer.

Scores YES/NO answers under baseline and the preregistered warning intervention.
The script averages over two neutral-code mappings (A/B swapped) so a preferred
answer token cannot by itself create the DN/MN pattern.

Load-bearing pilot data must be independently human validated. By default this
script refuses rows whose `human_validated` field is not true.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

WARNING = "Pay attention to any negation and distractors (sentences which don't make sense)."
MAPPINGS = [
    {"A": "YES", "B": "NO"},
    {"A": "NO", "B": "YES"},
]
VALID_CONDITIONS = {"POS", "DN", "MN", "PARAPHRASE"}
VALID_GOLD = {"YES", "NO"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="HF model id or local path")
    p.add_argument("--data", required=True, type=Path, help="human-audited JSONL")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    p.add_argument("--device-map", default="auto")
    p.add_argument("--trust-remote-code", action="store_true")
    p.add_argument("--allow-unvalidated-exploratory", action="store_true")
    return p.parse_args()


def load_rows(path: Path, allow_unvalidated: bool) -> List[dict]:
    rows = []
    with path.open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            missing = [k for k in ("base_id", "subtype", "condition", "text", "target", "gold") if k not in row]
            if missing:
                raise ValueError(f"line {line_no}: missing {missing}")
            if row["condition"] not in VALID_CONDITIONS:
                raise ValueError(f"line {line_no}: invalid condition {row['condition']}")
            if row["gold"] not in VALID_GOLD:
                raise ValueError(f"line {line_no}: invalid gold {row['gold']}")
            if not allow_unvalidated and row.get("human_validated") is not True:
                raise ValueError(
                    f"line {line_no}: row is not independently human validated; "
                    "use --allow-unvalidated-exploratory only for non-claim debugging"
                )
            rows.append(row)
    if not rows:
        raise ValueError("no data rows")
    return rows


def dtype_from_name(name: str):
    return {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }[name]


def format_prompt(tokenizer, row: dict, mapping: Dict[str, str], warning: bool) -> str:
    options = "\n".join(f"{code} = {meaning}" for code, meaning in mapping.items())
    user = (
        f"Dialogue or statement:\n{row['text']}\n\n"
        f"Target statement:\n{row['target']}\n\n"
        "Based only on what the speaker means in the text above, is the target statement true?\n"
        f"{options}\n"
        "Answer with one option letter only."
    )
    if warning:
        user = WARNING + "\n\n" + user

    messages = [{"role": "user", "content": user}]
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return user + "\nAnswer:"


@torch.inference_mode()
def continuation_logprob(model, tokenizer, prompt: str, continuation: str) -> float:
    # Leading space is usually the natural completion after a generation prompt.
    cont = " " + continuation
    prompt_ids = tokenizer(prompt, add_special_tokens=False, return_tensors="pt").input_ids
    full_ids = tokenizer(prompt + cont, add_special_tokens=False, return_tensors="pt").input_ids
    n_prompt = prompt_ids.shape[1]
    if full_ids.shape[1] <= n_prompt:
        raise RuntimeError("continuation tokenization produced no added token")

    device = next(model.parameters()).device
    full_ids = full_ids.to(device)
    outputs = model(full_ids)
    logits = outputs.logits[:, :-1, :]
    targets = full_ids[:, 1:]
    token_lp = torch.log_softmax(logits.float(), dim=-1).gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    # Target token at original position n_prompt is predicted by logit n_prompt-1.
    start = max(n_prompt - 1, 0)
    return float(token_lp[0, start:].sum().cpu())


def normalized_probs(logps: Dict[str, float]) -> Dict[str, float]:
    m = max(logps.values())
    z = sum(math.exp(v - m) for v in logps.values())
    return {k: math.exp(v - m) / z for k, v in logps.items()}


def score_one(model, tokenizer, row: dict, warning: bool) -> dict:
    # Each mapping converts code probability back to semantic YES/NO probability.
    semantic_probs = {"YES": [], "NO": []}
    mapping_records = []
    for mapping_id, mapping in enumerate(MAPPINGS):
        prompt = format_prompt(tokenizer, row, mapping, warning)
        logps = {code: continuation_logprob(model, tokenizer, prompt, code) for code in mapping}
        code_probs = normalized_probs(logps)
        sem = {meaning: code_probs[code] for code, meaning in mapping.items()}
        for label in semantic_probs:
            semantic_probs[label].append(sem[label])
        mapping_records.append({
            "mapping_id": mapping_id,
            "mapping": mapping,
            "code_logprobs": logps,
            "code_probs": code_probs,
        })

    avg = {k: sum(v) / len(v) for k, v in semantic_probs.items()}
    pred = max(avg, key=avg.get)
    return {
        **row,
        "arm": "warning" if warning else "baseline",
        "p_yes": avg["YES"],
        "p_no": avg["NO"],
        "pred": pred,
        "correct": pred == row["gold"],
        "p_gold": avg[row["gold"]],
        "mapping_records": mapping_records,
    }


def main() -> None:
    args = parse_args()
    rows = load_rows(args.data, args.allow_unvalidated_exploratory)
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=args.trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype_from_name(args.dtype),
        device_map=args.device_map,
        trust_remote_code=args.trust_remote_code,
    )
    model.eval()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for i, row in enumerate(rows, 1):
            for warning in (False, True):
                rec = score_one(model, tokenizer, row, warning)
                rec["model"] = args.model
                rec["exploratory_unvalidated"] = args.allow_unvalidated_exploratory
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[{i}/{len(rows)}] {row['base_id']} {row['condition']}", flush=True)


if __name__ == "__main__":
    main()
