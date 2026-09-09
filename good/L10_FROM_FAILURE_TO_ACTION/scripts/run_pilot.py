#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())
MANIFEST = json.loads((ROOT / "data/audit_manifest.json").read_text())
SOURCE = ROOT / "data/upstream/implicitmembench" / MANIFEST["source_file"]


def source_messages(instance):
    role_map = {"User": "user", "Assistant": "assistant", "System": CONFIG["environment_role"]}
    messages = []
    for part in ["learning_phase", "interference_phase"]:
        for msg in instance[part]:
            messages.append({"role": role_map[msg["role"]], "content": msg["content"]})
    return messages


def action_prompt(test_text, note=None):
    prefix = "" if note is None else f"Memory note from the prior episode: {note}\n\n"
    return prefix + f"Current request: {test_text}\nTake the next action now. Respond with the tool name you would use first; do not explain."


def branch_query(kind, bad, good, test_text):
    if kind == "M":
        return f"In the earlier interactions, did {bad} repeatedly succeed or fail on the demanding requests? Answer only SUCCESS or FAILURE."
    if kind == "C":
        return f"Which tool was repeatedly associated with the errors, {bad} or {good}? Answer only the tool name."
    if kind == "P":
        return f"For a similar demanding request, which tool should be used first, {bad} or {good}? Answer only the tool name."
    if kind == "A0":
        return action_prompt(test_text)
    notes = {
        "A1": f"{bad} failed in the earlier attempts.",
        "A2": f"The earlier failures were caused by using {bad}.",
        "A3": f"Do not use {bad} for this request.",
        "A4": f"Use {good} instead for this request.",
    }
    return action_prompt(test_text, notes[kind])


def clean_exact(text):
    return text.strip().strip("'\"*.").strip()


def parse_result(kind, text, bad, good):
    cleaned = clean_exact(text)
    if kind == "M":
        parsed = cleaned.upper() if cleaned.upper() in {"SUCCESS", "FAILURE"} else None
        expected = "FAILURE"
    else:
        parsed = next((tool for tool in [bad, good] if cleaned.lower() == tool.lower()), None)
        expected = bad if kind == "C" else good
    correct = parsed is not None and parsed.lower() == expected.lower()
    return parsed, expected, bool(correct)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    if not SOURCE.exists():
        raise FileNotFoundError(f"missing {SOURCE}; run scripts/fetch_parent_data.sh first")

    dataset = json.loads(SOURCE.read_text())
    by_id = {x["task_id"]: x for x in dataset["instances"]}
    spec = CONFIG["model"]
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", low_cpu_mem_usage=True,
    ).to(args.device).eval()

    out_dir = ROOT / CONFIG["result_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"
    kinds = ["M", "C", "P", "A0", "A1", "A2", "A3", "A4"]

    with raw_path.open("w") as handle, torch.inference_mode():
        for item in MANIFEST["items"]:
            instance = by_id[item["task_id"]]
            bad, good = item["bad_action"], item["good_action"]
            history = source_messages(instance)
            for kind in kinds:
                query = branch_query(kind, bad, good, instance["test_probe"]["content"])
                messages = history + [{"role": "user", "content": query}]
                rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                encoded = tokenizer(rendered, return_tensors="pt", return_token_type_ids=False).to(args.device)
                output = model.generate(
                    **encoded,
                    do_sample=CONFIG["decoding"]["do_sample"],
                    max_new_tokens=CONFIG["decoding"]["max_new_tokens"],
                    pad_token_id=tokenizer.pad_token_id,
                )
                continuation = tokenizer.decode(output[0, encoded["input_ids"].shape[1]:], skip_special_tokens=True)
                parsed, expected, correct = parse_result(kind, continuation, bad, good)
                record = {
                    "task_id": item["task_id"], "condition": kind,
                    "bad_action": bad, "good_action": good,
                    "parsed": parsed, "expected": expected, "correct": correct,
                    "strict_valid": parsed is not None,
                    "bad_repeat": bool(kind.startswith("A") and parsed == bad),
                    "continuation": continuation,
                    "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                    "model": spec["id"], "revision": spec["revision"],
                    "upstream_commit": MANIFEST["upstream_commit"],
                }
                handle.write(json.dumps(record) + "\n")
                handle.flush()
    (out_dir / "run_config.json").write_text(json.dumps(CONFIG, indent=2) + "\n")
    print(raw_path)


if __name__ == "__main__":
    main()
