#!/usr/bin/env python3
"""Score E20 evidence-prompt by evidence-trajectory factorials within form."""

import argparse
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from cpc18_form_evidence_common import CONFIG, ROOT, load_problems, make_prompt
from cpc18_common import shown_choice
from run_cpc18_control import label_token_id, make_prefix


def load_units(result_dir, donor_name):
    with (result_dir / "raw" / f"{donor_name}.jsonl").open() as handle:
        rows = [json.loads(line) for line in handle]
    eligible = [
        row for row in rows
        if row["valid"] and row.get("stripped_trace")
        and row.get("removed_terminal_segments")
        and row["underlying_choice"] == row["evidence_choice"]
    ]
    grouped = {}
    for row in eligible:
        key = (row["problem"], row["form"], row["order"], row["evidence_choice"])
        if key not in grouped or row["sample_index"] < grouped[key]["sample_index"]:
            grouped[key] = row
    units = []
    for problem in sorted({row["problem"] for row in eligible}):
        for form in ("raw", "summary"):
            for order in CONFIG["orders"]:
                a = grouped.get((problem, form, order, "A"))
                b = grouped.get((problem, form, order, "B"))
                if a and b:
                    units.append({
                        "problem": problem, "form": form, "order": order,
                        "a_sample_index": a["sample_index"],
                        "b_sample_index": b["sample_index"],
                        "a_trace": a["stripped_trace"], "b_trace": b["stripped_trace"],
                    })
    return units


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=24)
    args = parser.parse_args()
    spec = next(item for item in CONFIG["regimes"] if item["name"] == args.regime)
    donor = next(
        item for item in CONFIG["regimes"]
        if item["pair"] == spec["pair"] and item["role"] == "reasoning"
    )
    result_dir = ROOT / CONFIG["result_dir"]
    problems = {row["id"]: row for row in load_problems()}
    units = load_units(result_dir, donor["name"])
    if not units:
        raise ValueError(f"No strict opposite-evidence units for {donor['name']}")

    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    label_ids = [label_token_id(tokenizer, label) for label in ("A", "B")]
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True,
        torch_dtype=torch.bfloat16, attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()

    pending = []
    for unit in units:
        problem = problems[unit["problem"]]
        evidence = {row["evidence_choice"]: row for row in problem["evidence"]}
        a_shown = shown_choice("A", unit["order"])
        for prompt_evidence in ("A", "B"):
            prompt = make_prompt(
                problem, evidence[prompt_evidence], unit["form"], unit["order"]
            )
            for trajectory_evidence in ("A", "B"):
                pending.append({
                    "problem": unit["problem"], "form": unit["form"],
                    "order": unit["order"],
                    "a_sample_index": unit["a_sample_index"],
                    "b_sample_index": unit["b_sample_index"],
                    "regime": spec["name"], "pair": spec["pair"],
                    "role": spec["role"],
                    "prompt_evidence": prompt_evidence,
                    "trajectory_evidence": trajectory_evidence,
                    "a_shown": a_shown,
                    "prefix": make_prefix(
                        tokenizer, spec, prompt,
                        unit[f"{trajectory_evidence.lower()}_trace"],
                    ),
                })

    control_dir = result_dir / "raw" / "control"
    control_dir.mkdir(parents=True, exist_ok=True)
    with (control_dir / f"{spec['name']}.jsonl").open("w") as handle, torch.inference_mode():
        for start in range(0, len(pending), args.batch_size):
            rows = pending[start:start + args.batch_size]
            encoded = tokenizer(
                [row["prefix"] for row in rows], padding=True,
                return_tensors="pt", return_token_type_ids=False,
            ).to(args.device)
            logits = model(**encoded, use_cache=False, logits_to_keep=1).logits[:, -1, label_ids].float()
            probabilities = torch.softmax(logits, dim=1).cpu()
            for row, probability in zip(rows, probabilities):
                result = {key: value for key, value in row.items() if key != "prefix"}
                result["p_a_choice"] = float(probability[0 if row["a_shown"] == "A" else 1])
                handle.write(json.dumps(result) + "\n")
            handle.flush()
    (result_dir / f"{spec['name']}.control.json").write_text(json.dumps({
        "regime": spec, "donor_regime": donor["name"],
        "n_trace_units": len(units), "n_scored_prefixes": len(pending),
        "label_token_ids": label_ids,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
