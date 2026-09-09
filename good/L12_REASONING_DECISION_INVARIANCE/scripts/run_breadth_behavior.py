#!/usr/bin/env python3
"""Run the E10 sibling behavioral comparison on independent decisions."""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_model import parse_choice
from run_trajectory_takeover import make_prompt, split_trace, strip_terminal_conclusion


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())


def load_decisions():
    rows = []
    with (ROOT / CONFIG["output"]).open() as handle:
        for line in handle:
            row = json.loads(line)
            rows.append({
                "id": row["id"],
                "loss_a": row["amount_a"],
                "prob_a": row["prob_a"],
                "loss_b": row["amount_b"],
                "prob_b": row["prob_b"],
                "gain_optimal": row["gain_optimal"],
                "loss_optimal": row["loss_optimal"],
                "ev_gap_stratum": row["ev_gap_stratum"],
                "probability_gap_stratum": row["probability_gap_stratum"],
                "payoff_scale": row["payoff_scale"],
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=["instruct_sft", "think_sft"], required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    spec = next(item for item in CONFIG["models"] if item["branch"] == args.branch)
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"],
        revision=spec["revision"],
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()

    decisions = load_decisions()
    conditions = [
        (decision, frame, order)
        for decision in decisions
        for frame in CONFIG["frames"]
        for order in CONFIG["orders"]
    ]
    out = ROOT / CONFIG["result_dir"] / args.branch
    out.mkdir(parents=True, exist_ok=True)
    with (out / "raw.jsonl").open("w") as handle, torch.inference_mode():
        for condition_index, (decision, frame, order) in enumerate(conditions):
            prompt = make_prompt(decision, frame, order)
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
            batch = tokenizer(
                [rendered] * CONFIG["samples_per_cell"],
                padding=True,
                return_tensors="pt",
                return_token_type_ids=False,
            ).to(args.device)
            condition_seed = CONFIG["seed"] + condition_index
            torch.manual_seed(condition_seed)
            torch.cuda.manual_seed_all(condition_seed)
            generated = model.generate(
                **batch,
                do_sample=True,
                temperature=CONFIG["temperature"],
                top_p=CONFIG["top_p"],
                max_new_tokens=spec["max_new_tokens"],
                pad_token_id=tokenizer.pad_token_id,
            )
            continuations = generated[:, batch["input_ids"].shape[1]:]
            texts = tokenizer.batch_decode(continuations, skip_special_tokens=True)
            for sample_index, text in enumerate(texts):
                shown = parse_choice(
                    text, require_closed_think=(args.branch == "think_sft")
                )
                underlying = shown
                if shown is not None and order == "ba":
                    underlying = "B" if shown == "A" else "A"
                trace = split_trace(text) if args.branch == "think_sft" else None
                stripped, removed = (
                    strip_terminal_conclusion(trace)
                    if trace is not None else (None, [])
                )
                handle.write(json.dumps({
                    "model": spec["id"],
                    "revision": spec["revision"],
                    "branch": args.branch,
                    "prospect": decision["id"],
                    "frame": frame,
                    "order": order,
                    "sample_index": sample_index,
                    "seed": condition_seed,
                    "shown_choice": shown,
                    "underlying_choice": underlying,
                    "gold_underlying": decision[f"{frame}_optimal"],
                    "valid": shown is not None,
                    "trace": trace,
                    "stripped_trace": stripped,
                    "removed_terminal_segments": removed,
                    "continuation": text,
                    "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                    "ev_gap_stratum": decision["ev_gap_stratum"],
                    "probability_gap_stratum": decision["probability_gap_stratum"],
                    "payoff_scale": decision["payoff_scale"],
                }) + "\n")
            handle.flush()
    (out / "model.json").write_text(json.dumps(spec, indent=2) + "\n")


if __name__ == "__main__":
    main()
