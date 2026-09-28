#!/usr/bin/env python3
"""Run the E14 behavior gate in the Llama instruction/reasoning ecosystem."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from run_model import parse_choice
from run_qwen_mode_behavior import load_decisions
from run_trajectory_takeover import make_prompt, split_trace, strip_terminal_conclusion


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/llama_external_validation.json").read_text())


def parse_deepseek_final_choice(text):
    """Parse the terminal answer region, never the first option mention."""
    if "</think>" not in text:
        return None, "no_closed_think"
    answer = text.split("</think>", 1)[1].strip()
    patterns = [
        (r"^\s*(?:\\boxed\{)?\s*([AB])\s*\}?\s*[.!]?\s*$", "direct"),
        (r"\\boxed\{(?:\\text\{)?\s*([AB])\s*\}?\}", "boxed"),
        (r"(?i)(?:final\s+)?(?:answer|choice)\s*(?:is|would be|:)\s*"
         r"(?:option\s*)?[*\\({\s]*([AB])\b", "answer_field"),
        (r"(?i)(?:better|best|optimal|correct|preferred)\s+"
         r"(?:answer|choice|option)\s*(?:is|would be|:)\s*"
         r"[*\\({\s]*([AB])\b", "decision_field"),
        (r"(?i)(?:choose|select|pick|go with)\s+(?:option\s+)?"
         r"\**([AB])\b", "choice_verb"),
        (r"(?i)\boption\s+([AB])\b[^.\n]{0,100}"
         r"\b(?:better|best|optimal|correct|preferable|preferred)\b", "terminal_relation"),
        (r"(?im)(?:^|\n)\s*\*{0,2}([AB])\*{0,2}\s*[.!]?\s*$", "terminal_label"),
    ]
    matches = []
    for pattern, rule in patterns:
        found = list(re.finditer(pattern, answer))
        if found:
            matches.append((found[-1].start(), found[-1].group(1).upper(), rule))
    if not matches:
        return None, "no_terminal_answer"
    _, choice, rule = max(matches)
    return choice, rule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    args = parser.parse_args()
    spec = next(item for item in CONFIG["models"] if item["branch"] == args.branch)
    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    decisions = load_decisions()
    conditions = [
        (decision, frame, order)
        for decision in decisions
        for frame in CONFIG["frames"]
        for order in CONFIG["orders"]
    ]
    prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": make_prompt(decision, frame, order)}],
            tokenize=False,
            add_generation_prompt=True,
        )
        for decision, frame, order in conditions
    ]
    engine = LLM(
        model=spec["id"],
        revision=spec["revision"],
        dtype="bfloat16",
        tensor_parallel_size=1,
        max_model_len=1536,
        gpu_memory_utilization=0.75,
    )
    sampling = SamplingParams(
        n=CONFIG["samples_per_cell"],
        temperature=CONFIG["temperature"],
        top_p=CONFIG["top_p"],
        max_tokens=spec["max_tokens"],
        seed=CONFIG["seed"] + CONFIG["models"].index(spec),
    )
    requests = engine.generate(prompts, sampling)
    out = ROOT / CONFIG["result_dir"]
    out.mkdir(parents=True, exist_ok=True)
    with (out / f"{args.branch}.jsonl").open("w") as handle:
        for (decision, frame, order), rendered, request in zip(
            conditions, prompts, requests
        ):
            for sample_index, completion in enumerate(request.outputs):
                text = completion.text
                if spec["requires_closed_think"]:
                    shown, parser_rule = parse_deepseek_final_choice(text)
                else:
                    shown = parse_choice(text)
                    parser_rule = "direct_first_label" if shown is not None else "invalid"
                underlying = shown
                if shown is not None and order == "ba":
                    underlying = "B" if shown == "A" else "A"
                trace = split_trace(text) if spec["requires_closed_think"] else None
                stripped, removed = (
                    strip_terminal_conclusion(trace)
                    if trace is not None else (None, [])
                )
                handle.write(json.dumps({
                    "model": spec["id"],
                    "scientific_identity": spec.get("scientific_identity", spec["id"]),
                    "revision": spec["revision"],
                    "branch": args.branch,
                    "prospect": decision["id"],
                    "frame": frame,
                    "order": order,
                    "sample_index": sample_index,
                    "seed": CONFIG["seed"] + CONFIG["models"].index(spec),
                    "shown_choice": shown,
                    "underlying_choice": underlying,
                    "gold_underlying": decision[f"{frame}_optimal"],
                    "valid": shown is not None,
                    "choice_parser": parser_rule,
                    "trace": trace,
                    "stripped_trace": stripped,
                    "removed_terminal_segments": removed,
                    "finish_reason": completion.finish_reason,
                    "continuation": text,
                    "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                }) + "\n")
    (out / f"{args.branch}.model.json").write_text(json.dumps({
        **spec,
        "backend": "vllm",
        "sampling_seed": CONFIG["seed"] + CONFIG["models"].index(spec),
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
