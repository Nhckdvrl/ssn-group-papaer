#!/usr/bin/env python3
"""Score the frozen CPC18 prompt-by-trajectory factorial for one regime."""

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from cpc18_common import CONFIG, ROOT, load_problems, make_prompt, shown_choice


def label_token_id(tokenizer, label):
    ids = tokenizer.encode(label, add_special_tokens=False)
    if len(ids) != 1:
        ids = tokenizer.encode(" " + label, add_special_tokens=False)
    if len(ids) != 1:
        raise ValueError(f"Cannot score {label!r} as one token: {ids}")
    return ids[0]


def make_prefix(tokenizer, spec, prompt, trace):
    kwargs = {}
    if "enable_thinking" in spec:
        kwargs["enable_thinking"] = spec["enable_thinking"]
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
        **kwargs,
    )
    if spec["requires_closed_think"]:
        if rendered.rstrip().endswith("<think>"):
            return rendered + trace.strip() + "\n</think>\n\n"
        return rendered + "<think>\n" + trace.strip() + "\n</think>\n\n"
    return rendered + trace.strip() + "\n\n"


def load_units(result_dir, donor_name):
    with (result_dir / "raw" / f"{donor_name}.jsonl").open() as handle:
        rows = [json.loads(line) for line in handle]
    valid = [
        row for row in rows
        if row["valid"] and row.get("stripped_trace")
    ]
    explicit = {
        (row["problem"], row["order"], row["sample_index"]): row
        for row in valid if row["presentation"] == "explicit"
    }
    units = []
    for row in valid:
        if row["presentation"] != "history":
            continue
        key = (row["problem"], row["order"], row["sample_index"])
        if key not in explicit:
            continue
        units.append({
            "problem": row["problem"],
            "order": row["order"],
            "history_id": row["history_id"],
            "sample_index": row["sample_index"],
            "explicit_trace": explicit[key]["stripped_trace"],
            "history_trace": row["stripped_trace"],
        })
    return units


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=24)
    parser.add_argument("--result-dir")
    args = parser.parse_args()
    spec = next(item for item in CONFIG["regimes"] if item["name"] == args.regime)
    donor = next(
        item for item in CONFIG["regimes"]
        if item["pair"] == spec["pair"] and item["role"] == "reasoning"
    )
    result_dir = Path(args.result_dir) if args.result_dir else ROOT / CONFIG["result_dir"]
    problems = {row["id"]: row for row in load_problems()}
    units = load_units(result_dir, donor["name"])
    if not units:
        raise ValueError(f"No matched stripped trajectories from {donor['name']}")

    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    label_ids = [label_token_id(tokenizer, label) for label in ["A", "B"]]
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
        problem = problems[unit["problem"]]
        history = next(
            value for value in problem["histories"]
            if value["id"] == unit["history_id"]
        )
        ev_shown = shown_choice(problem["ev_choice"], unit["order"])
        for prompt_presentation in ["explicit", "history"]:
            prompt = make_prompt(
                problem,
                prompt_presentation,
                unit["order"],
                history if prompt_presentation == "history" else None,
            )
            for trajectory_presentation in ["explicit", "history"]:
                pending.append({
                    **{key: unit[key] for key in [
                        "problem", "order", "history_id", "sample_index"
                    ]},
                    "regime": spec["name"],
                    "pair": spec["pair"],
                    "role": spec["role"],
                    "prompt_presentation": prompt_presentation,
                    "trajectory_presentation": trajectory_presentation,
                    "ev_shown": ev_shown,
                    "prefix": make_prefix(
                        tokenizer,
                        spec,
                        prompt,
                        unit[f"{trajectory_presentation}_trace"],
                    ),
                })

    control_dir = result_dir / "raw" / "control"
    control_dir.mkdir(parents=True, exist_ok=True)
    with (control_dir / f"{spec['name']}.jsonl").open("w") as handle, torch.inference_mode():
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
                result = {key: value for key, value in row.items() if key != "prefix"}
                result["p_ev_choice"] = float(
                    probability[0 if row["ev_shown"] == "A" else 1]
                )
                handle.write(json.dumps(result) + "\n")
            handle.flush()
    (result_dir / f"{spec['name']}.control.json").write_text(json.dumps({
        "regime": spec,
        "donor_regime": donor["name"],
        "n_trace_units": len(units),
        "n_scored_prefixes": len(pending),
        "label_token_ids": label_ids,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
