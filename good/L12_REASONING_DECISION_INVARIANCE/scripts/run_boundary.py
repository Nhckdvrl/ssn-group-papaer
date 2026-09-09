#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/boundary.json").read_text())


def option_text(p, frame, identity):
    sign = "Gain" if frame == "gain" else "Lose"
    amount = p[f"loss_{identity.lower()}"]
    probability = p[f"prob_{identity.lower()}"]
    if probability == 1.0:
        return f"{sign} {amount} with certainty."
    return f"{sign} {amount} with probability {probability:.2f}; otherwise 0."


def make_prompt(p, frame, order):
    identities = ["A", "B"] if order == "ab" else ["B", "A"]
    shown = [option_text(p, frame, identity) for identity in identities]
    return (
        "You will be provided with two options with different payoffs and uncertainties.\n"
        "Respond your choice with 'A' or 'B' only.\n\n"
        f"Option A: {shown[0]}\n"
        f"Option B: {shown[1]}"
    )


def expected_choice(p, frame):
    values = {"A": p["loss_a"] * p["prob_a"], "B": p["loss_b"] * p["prob_b"]}
    return max(values, key=values.get) if frame == "gain" else min(values, key=values.get)


def parse_choice(text, require_closed_think):
    if require_closed_think and "</think>" not in text:
        return None
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    match = re.search(r"(?<![A-Za-z])([AB])(?![A-Za-z])", text.strip(), flags=re.I)
    return match.group(1).upper() if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-index", type=int, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    spec = CONFIG["models"][args.model_index]

    # Pre-run identification assertion: every factual counterfactual must flip the EV target
    # in both gain and loss framings.
    for item in CONFIG["prospects"]:
        for frame in CONFIG["frames"]:
            base_target = expected_choice(item["base"], frame)
            cf_target = expected_choice(item["counterfactual"], frame)
            if base_target == cf_target:
                raise ValueError(f"{item['id']} {frame}: counterfactual does not flip target")

    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", low_cpu_mem_usage=True,
    ).to(args.device).eval()

    out_dir = ROOT / CONFIG["result_dir"] / spec["branch"]
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"

    conditions = []
    for item in CONFIG["prospects"]:
        for fact_variant in ["base", "counterfactual"]:
            p = item[fact_variant]
            for frame in CONFIG["frames"]:
                for order in CONFIG["orders"]:
                    conditions.append({
                        "prospect": item["id"], "fact_variant": fact_variant,
                        "changed_field": item["changed_field"], "frame": frame, "order": order,
                        "facts": p, "prompt": make_prompt(p, frame, order),
                        "expected_underlying": expected_choice(p, frame),
                    })

    with raw_path.open("w") as handle, torch.inference_mode():
        for condition_index, condition in enumerate(conditions):
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": condition["prompt"]}],
                tokenize=False, add_generation_prompt=True
            )
            batch = tokenizer(
                [rendered] * CONFIG["samples_per_cell"], padding=True,
                return_tensors="pt", return_token_type_ids=False
            ).to(args.device)
            seed = CONFIG["seed"] + condition_index
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            generated = model.generate(
                **batch, do_sample=True, temperature=CONFIG["temperature"], top_p=CONFIG["top_p"],
                max_new_tokens=spec["max_new_tokens"], pad_token_id=tokenizer.pad_token_id,
            )
            continuation = generated[:, batch["input_ids"].shape[1]:]
            texts = tokenizer.batch_decode(continuation, skip_special_tokens=True)
            for sample_index, text in enumerate(texts):
                shown = parse_choice(text, require_closed_think=(spec["branch"] == "think_sft"))
                underlying = None
                if shown is not None:
                    underlying = shown if condition["order"] == "ab" else ("B" if shown == "A" else "A")
                record = {
                    "model": spec["id"], "revision": spec["revision"], "branch": spec["branch"],
                    "prospect": condition["prospect"], "fact_variant": condition["fact_variant"],
                    "changed_field": condition["changed_field"], "frame": condition["frame"], "order": condition["order"],
                    "expected_underlying": condition["expected_underlying"],
                    "shown_choice": shown, "underlying_choice": underlying,
                    "ev_correct": bool(underlying == condition["expected_underlying"]) if underlying else False,
                    "strict_valid": underlying is not None,
                    "sample_index": sample_index, "continuation": text,
                    "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                    "seed": seed,
                }
                handle.write(json.dumps(record) + "\n")
            handle.flush()
    (out_dir / "model.json").write_text(json.dumps(spec, indent=2) + "\n")
    print(raw_path)


if __name__ == "__main__":
    main()
