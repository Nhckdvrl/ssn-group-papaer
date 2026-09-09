#!/usr/bin/env python3
"""Run E13 prompt-by-trajectory control under Qwen3's two native routes."""

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_qwen_mode_behavior import load_decisions
from run_trajectory_takeover import make_prompt, shown_label


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/qwen_mode_validation.json").read_text())


def load_units():
    path = ROOT / CONFIG["result_dir"] / "thinking.jsonl"
    with path.open() as handle:
        rows = [json.loads(line) for line in handle]
    valid = {
        (row["prospect"], row["frame"], row["order"], row["sample_index"]): row
        for row in rows
        if row["valid"] and row.get("stripped_trace")
    }
    units = []
    for prospect in sorted({row["prospect"] for row in rows}):
        for order in CONFIG["orders"]:
            for sample_index in range(CONFIG["samples_per_cell"]):
                gain = valid.get((prospect, "gain", order, sample_index))
                loss = valid.get((prospect, "loss", order, sample_index))
                if gain and loss:
                    units.append({
                        "prospect": prospect,
                        "order": order,
                        "sample_index": sample_index,
                        "gain_trace": gain["stripped_trace"],
                        "loss_trace": loss["stripped_trace"],
                    })
    return units


def route_prefix(tokenizer, route, prompt, trace):
    if route == "thinking":
        rendered = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True,
        )
        return rendered + "<think>\n" + trace.strip() + "\n</think>\n\n"
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    if not rendered.rstrip().endswith("</think>"):
        raise ValueError("Non-thinking template no longer ends with empty think block")
    return rendered + trace.strip() + "\n\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=24)
    args = parser.parse_args()
    spec = CONFIG["model"]
    decisions = {row["id"]: row for row in load_decisions()}
    units = load_units()
    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    label_ids = [
        tokenizer.encode(label, add_special_tokens=False)[0] for label in ["A", "B"]
    ]
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"],
        revision=spec["revision"],
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()
    pending = []
    for unit in units:
        decision = decisions[unit["prospect"]]
        gain_choice = shown_label(decision["gain_optimal"], unit["order"])
        for route in CONFIG["modes"]:
            for prompt_frame in CONFIG["frames"]:
                prompt = make_prompt(decision, prompt_frame, unit["order"])
                for trajectory_frame in CONFIG["frames"]:
                    pending.append({
                        "route": route,
                        "prospect": unit["prospect"],
                        "order": unit["order"],
                        "sample_index": unit["sample_index"],
                        "prompt_frame": prompt_frame,
                        "trajectory_frame": trajectory_frame,
                        "gain_choice": gain_choice,
                        "prefix": route_prefix(
                            tokenizer,
                            route,
                            prompt,
                            unit[f"{trajectory_frame}_trace"],
                        ),
                    })
    out = ROOT / CONFIG["result_dir"] / "control"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "raw.jsonl").open("w") as handle, torch.inference_mode():
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
                result = {key: value for key, value in row.items() if key != "prefix"}
                gain_index = 0 if row["gain_choice"] == "A" else 1
                result["p_gain_choice"] = float(probability[gain_index])
                handle.write(json.dumps(result) + "\n")
            handle.flush()


if __name__ == "__main__":
    main()
