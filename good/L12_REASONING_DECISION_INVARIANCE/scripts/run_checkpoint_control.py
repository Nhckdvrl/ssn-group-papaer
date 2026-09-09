#!/usr/bin/env python3
"""Run the E12 DPO checkpoint prompt-by-trajectory factorial."""

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_breadth_control import load_decisions, load_units
from run_control_reorganization import answer_prefix
from run_trajectory_takeover import make_prompt, shown_label


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/checkpoint_validation.json").read_text())
BREADTH = json.loads((ROOT / "configs/breadth.json").read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    spec = next(item for item in CONFIG["models"] if item["branch"] == args.branch)
    decisions = load_decisions()
    units = load_units()
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    label_ids = [
        tokenizer.encode(label, add_special_tokens=False)[0] for label in ["A", "B"]
    ]
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"],
        revision=spec["revision"],
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()
    pending = []
    for unit in units:
        decision = decisions[unit["prospect"]]
        gain_choice = shown_label(decision["gain_optimal"], unit["order"])
        for prompt_frame in BREADTH["frames"]:
            prompt = make_prompt(decision, prompt_frame, unit["order"])
            for trajectory_frame in BREADTH["frames"]:
                pending.append({
                    "prospect": unit["prospect"],
                    "order": unit["order"],
                    "sample_index": unit["sample_index"],
                    "prompt_frame": prompt_frame,
                    "trajectory_frame": trajectory_frame,
                    "gain_choice": gain_choice,
                    "prefix": answer_prefix(
                        tokenizer,
                        "think_sft" if spec["template_mode"] == "think" else "instruct_sft",
                        prompt,
                        unit[f"{trajectory_frame}_trace"],
                    ),
                })
    out = ROOT / CONFIG["result_dir"]
    out.mkdir(parents=True, exist_ok=True)
    with (out / f"{args.branch}.jsonl").open("w") as handle, torch.inference_mode():
        for start in range(0, len(pending), args.batch_size):
            rows = pending[start:start + args.batch_size]
            encoded = tokenizer(
                [row["prefix"] for row in rows],
                padding=True,
                return_tensors="pt",
                return_token_type_ids=False,
            ).to(args.device)
            logits = model(**encoded, use_cache=False).logits[:, -1, label_ids].float()
            probabilities = torch.softmax(logits, dim=1).cpu()
            for row, probability in zip(rows, probabilities):
                gain_index = 0 if row["gain_choice"] == "A" else 1
                result = {key: value for key, value in row.items() if key != "prefix"}
                result.update({
                    "branch": spec["branch"],
                    "model": spec["id"],
                    "revision": spec["revision"],
                    "p_gain_choice": float(probability[gain_index]),
                })
                handle.write(json.dumps(result) + "\n")
            handle.flush()


if __name__ == "__main__":
    main()
