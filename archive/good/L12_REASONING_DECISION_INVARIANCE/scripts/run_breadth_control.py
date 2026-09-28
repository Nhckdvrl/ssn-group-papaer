#!/usr/bin/env python3
"""Score the E10 prompt-by-trajectory factorial on independent decisions."""

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_control_reorganization import answer_prefix
from run_trajectory_takeover import make_prompt, shown_label


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())


def load_decisions():
    with (ROOT / CONFIG["output"]).open() as handle:
        rows = [json.loads(line) for line in handle]
    return {
        row["id"]: {
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
        }
        for row in rows
    }


def load_units():
    path = ROOT / CONFIG["result_dir"] / "think_sft/raw.jsonl"
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=["instruct_sft", "think_sft"], required=True)
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
        for prompt_frame in CONFIG["frames"]:
            prompt = make_prompt(decision, prompt_frame, unit["order"])
            for trajectory_frame in CONFIG["frames"]:
                pending.append({
                    "prospect": unit["prospect"],
                    "order": unit["order"],
                    "sample_index": unit["sample_index"],
                    "prompt_frame": prompt_frame,
                    "trajectory_frame": trajectory_frame,
                    "gain_choice": gain_choice,
                    "prefix": answer_prefix(
                        tokenizer,
                        args.branch,
                        prompt,
                        unit[f"{trajectory_frame}_trace"],
                    ),
                    "ev_gap_stratum": decision["ev_gap_stratum"],
                    "probability_gap_stratum": decision[
                        "probability_gap_stratum"
                    ],
                    "payoff_scale": decision["payoff_scale"],
                })

    out = ROOT / CONFIG["result_dir"] / "control"
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / f"{args.branch}.jsonl"
    with raw_path.open("w") as handle, torch.inference_mode():
        for start in range(0, len(pending), args.batch_size):
            batch_rows = pending[start:start + args.batch_size]
            encoded = tokenizer(
                [row["prefix"] for row in batch_rows],
                padding=True,
                return_tensors="pt",
                return_token_type_ids=False,
            ).to(args.device)
            logits = model(**encoded, use_cache=False).logits[:, -1, label_ids].float()
            probabilities = torch.softmax(logits, dim=1).cpu()
            for row, probability in zip(batch_rows, probabilities):
                gain_index = 0 if row["gain_choice"] == "A" else 1
                result = {key: value for key, value in row.items() if key != "prefix"}
                result.update({
                    "branch": args.branch,
                    "p_gain_choice": float(probability[gain_index]),
                })
                handle.write(json.dumps(result) + "\n")
            handle.flush()


if __name__ == "__main__":
    main()
