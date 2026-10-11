"""Count E12 selected supervision under the released LLaVA chat template.

This avoids decoding 50k images, and first proves its token counts agree with
the released trainer's actual image-processor path on 11 fixed real rows.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
from pathlib import Path

from transformers import AutoProcessor

from e12_index_audit import expected_turns
from e12_make_subsets import POLICIES, hash_lines, policies_from_sources, select_positions


TRAIN_SCRIPT = Path(
    "/home/xiang/.cache/research/data-centric-rsi/CurationBench/vendor/curation-train/"
    "src/curation_train/train_llava15.py"
)


def load_trainer():
    spec = importlib.util.spec_from_file_location("e12_llava_trainer_token_audit", TRAIN_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import released LLaVA trainer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def summarize(values: list[int]) -> dict[str, int | float]:
    ordered = sorted(values)
    return {
        "sum": sum(values), "mean": round(statistics.mean(values), 2),
        "median": ordered[len(ordered) // 2], "p95": ordered[int(len(ordered) * 0.95)],
        "min": ordered[0], "max": ordered[-1],
    }


def token_counts(row: dict, processor) -> dict[str, int | bool]:
    turns = expected_turns(row)
    if turns is None:
        raise RuntimeError(f"Odd turn count in original JSON row {row.get('id')}")
    conversation = []
    for i, turn in enumerate(turns):
        user_content = ([{"type": "image"}] if i == 0 else []) + [
            {"type": "text", "text": turn["user"]}
        ]
        conversation.append({"role": "user", "content": user_content})
        conversation.append({"role": "assistant", "content": [{"type": "text", "text": turn["assistant"]}]})
    encoded = processor.tokenizer.apply_chat_template(
        conversation, add_generation_prompt=False, tokenize=True,
        return_dict=True, return_assistant_tokens_mask=True,
    )
    pre_ids = encoded["input_ids"]
    pre_mask = encoded["assistant_masks"]
    image_token_id = processor.tokenizer.convert_tokens_to_ids("<image>")
    image_seq_len = int(getattr(processor, "image_seq_length", 576))
    expanded_ids = []
    expanded_mask = []
    for tok, flag in zip(pre_ids, pre_mask):
        if tok == image_token_id:
            expanded_ids.extend([tok] * image_seq_len)
            expanded_mask.extend([0] * image_seq_len)
        else:
            expanded_ids.append(tok)
            expanded_mask.append(int(flag))
    bos_id = processor.tokenizer.bos_token_id
    if bos_id is not None:
        expanded_ids.insert(0, bos_id)
        expanded_mask.insert(0, 0)
    if len(expanded_ids) != len(expanded_mask):
        raise RuntimeError("Token/label alignment failed")
    full_len = len(expanded_ids)
    ids = expanded_ids[:2048]
    mask = expanded_mask[:2048]
    supervised_ids = [tok for tok, flag in zip(ids, mask) if flag]
    return {
        "full_input_tokens": full_len,
        "input_tokens": len(ids),
        "supervised_tokens": len(supervised_ids),
        "truncated": full_len > 2048,
        "last_supervised_token_is_eos": bool(
            supervised_ids and supervised_ids[-1] == processor.tokenizer.eos_token_id
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--sentinel", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--policies", nargs="+", choices=POLICIES, default=list(POLICIES))
    parser.add_argument("--sentinel-only", action="store_true")
    args = parser.parse_args()

    module = load_trainer()
    processor = AutoProcessor.from_pretrained(str(args.root / "llava_init"))
    processor.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    processor.tokenizer.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    original = json.loads((args.root / "llava_json/llava_v1_5_mix665k.json").read_text())
    sentinel = json.loads(args.sentinel.read_text())
    for reference in sentinel["rows"]:
        actual = token_counts(original[reference["position"]], processor)
        if actual["input_tokens"] != reference["input_tokens"] or actual["supervised_tokens"] != reference["supervised_tokens"] or actual["last_supervised_token_is_eos"] != reference["last_supervised_token_is_eos"]:
            raise RuntimeError(f"Token-only path disagrees with actual processor at row {reference['position']}: {actual} vs {reference}")
    print("Matched all 11 actual image-processor sentinel rows", flush=True)
    if args.sentinel_only:
        return

    pools = policies_from_sources(original, args.root)
    report = {"seed": args.seed, "processor": str(args.root / "llava_init"), "sentinel_matched": 11, "policies": {}}
    for policy in args.policies:
        positions = select_positions(original, pools, policy, args.seed)
        rows = [token_counts(original[i], processor) for i in positions]
        policy_report = {
            "selected_positions_sha256": hash_lines([str(i) for i in positions]),
            "rows": len(rows),
            "input_tokens": summarize([int(r["input_tokens"]) for r in rows]),
            "supervised_tokens": summarize([int(r["supervised_tokens"]) for r in rows]),
            "truncated_rows": sum(bool(r["truncated"]) for r in rows),
            "zero_supervised_rows": sum(r["supervised_tokens"] == 0 for r in rows),
            "rows_without_final_eos": sum(not r["last_supervised_token_is_eos"] for r in rows),
        }
        report["policies"][policy] = policy_report
        print(json.dumps({"policy": policy, **policy_report}), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
