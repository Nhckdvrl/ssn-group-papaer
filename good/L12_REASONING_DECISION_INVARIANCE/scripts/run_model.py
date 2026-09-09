#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())


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


def parse_choice(text, require_closed_think=False, require_direct_answer=False):
    if require_closed_think and "</think>" not in text:
        return None
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    if require_direct_answer:
        match = re.fullmatch(r"\s*([AB])[.)]?\s*", text, flags=re.I)
        return match.group(1).upper() if match else None
    match = re.search(r"(?<![A-Za-z])([AB])(?![A-Za-z])", text.strip(), flags=re.I)
    return match.group(1).upper() if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-index", type=int, required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--force-no-think", action="store_true")
    args = parser.parse_args()
    spec = CONFIG["models"][args.model_index]
    run_name = spec["branch"] + ("_no_think" if args.force_no_think else "")
    out_dir = ROOT / "results/pilot_seed29" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", low_cpu_mem_usage=True,
    ).to(args.device).eval()

    conditions = []
    for prospect in CONFIG["prospects"]:
        for frame in CONFIG["frames"]:
            for order in CONFIG["orders"]:
                prompt = make_prompt(prospect, frame, order)
                conditions.append({"prospect": prospect["id"], "frame": frame, "order": order, "prompt": prompt})

    raw_path = out_dir / "raw.jsonl"
    activations = []
    activation_meta = []
    with raw_path.open("w") as raw_file, torch.inference_mode():
        for condition_index, condition in enumerate(conditions):
            prompt = condition["prompt"]
            if spec["protocol"] == "native_chat":
                rendered_prompt = tokenizer.apply_chat_template(
                    [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
                )
                if args.force_no_think:
                    if not rendered_prompt.rstrip().endswith("<think>"):
                        raise ValueError("force-no-think requires a template ending in <think>")
                    rendered_prompt = rendered_prompt.rstrip() + "</think>\n"
            else:
                rendered_prompt = prompt
            encoded = tokenizer(rendered_prompt, return_tensors="pt", return_token_type_ids=False).to(args.device)
            forward = model(**encoded, output_hidden_states=True, use_cache=False)
            label_ids = []
            for label in ["A", "B"]:
                ids = tokenizer.encode(label, add_special_tokens=False)
                if len(ids) != 1:
                    raise ValueError(f"label {label} is not one token for {spec['id']}: {ids}")
                label_ids.append(ids[0])
            logits = forward.logits[0, -1, label_ids].float()
            p_a = torch.softmax(logits, dim=0)[0].item()
            layer_states = torch.stack([state[0, -1].float().cpu() for state in forward.hidden_states]).numpy()
            activations.append(layer_states)
            activation_meta.append({k: condition[k] for k in ["prospect", "frame", "order"]})
            del forward

            batch = tokenizer([rendered_prompt] * CONFIG["samples_per_cell"], padding=True, return_tensors="pt", return_token_type_ids=False).to(args.device)
            condition_seed = CONFIG["seed"] + condition_index
            torch.manual_seed(condition_seed)
            torch.cuda.manual_seed_all(condition_seed)
            generated = model.generate(
                **batch, do_sample=True, temperature=CONFIG["temperature"], top_p=CONFIG["top_p"],
                max_new_tokens=(32 if args.force_no_think else spec["max_new_tokens"]),
                pad_token_id=tokenizer.pad_token_id,
            )
            continuation = generated[:, batch["input_ids"].shape[1]:]
            texts = tokenizer.batch_decode(continuation, skip_special_tokens=True)
            for sample_index, text in enumerate(texts):
                shown = parse_choice(
                    text,
                    require_closed_think=(spec["branch"] == "think_sft" and not args.force_no_think),
                    require_direct_answer=args.force_no_think,
                )
                underlying = None
                if shown is not None:
                    underlying = shown if condition["order"] == "ab" else ("B" if shown == "A" else "A")
                record = {
                    "model": spec["id"], "revision": spec["revision"], "branch": spec["branch"],
                    **{k: condition[k] for k in ["prospect", "frame", "order"]},
                    "sample_index": sample_index, "shown_choice": shown, "underlying_choice": underlying,
                    "continuation": text, "forced_p_shown_a": p_a,
                    "protocol": spec["protocol"], "force_no_think": args.force_no_think,
                    "prompt_sha256": hashlib.sha256(rendered_prompt.encode()).hexdigest(),
                }
                raw_file.write(json.dumps(record) + "\n")
            raw_file.flush()
    np.savez_compressed(
        out_dir / "prompt_activations.npz", activations=np.stack(activations),
        metadata=np.asarray([json.dumps(x) for x in activation_meta]),
    )
    (out_dir / "model.json").write_text(json.dumps(spec, indent=2) + "\n")


if __name__ == "__main__":
    main()
