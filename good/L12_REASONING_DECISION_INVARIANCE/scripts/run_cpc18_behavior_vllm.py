#!/usr/bin/env python3
"""Run E17 CPC18 explicit/history behavior with one vLLM process per regime."""

import argparse
import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from cpc18_common import (
    CONFIG,
    ROOT,
    load_problems,
    make_prompt,
    parse_terminal_choice,
    split_trace,
    strip_terminal_conclusion,
    underlying_choice,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--result-dir")
    args = parser.parse_args()
    spec = next(item for item in CONFIG["regimes"] if item["name"] == args.regime)
    problems = load_problems(args.limit)
    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )

    conditions = []
    for problem in problems:
        for order in CONFIG["orders"]:
            conditions.append((problem, "explicit", order, None))
            for history in problem["histories"]:
                conditions.append((problem, "history", order, history))
    prompts = []
    for problem, presentation, order, history in conditions:
        prompt = make_prompt(problem, presentation, order, history)
        kwargs = {}
        if "enable_thinking" in spec:
            kwargs["enable_thinking"] = spec["enable_thinking"]
        prompts.append(tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
            **kwargs,
        ))

    engine = LLM(
        model=spec["id"],
        revision=spec["revision"],
        dtype="bfloat16",
        tensor_parallel_size=1,
        max_model_len=5120,
        gpu_memory_utilization=0.78,
        trust_remote_code=True,
    )
    sampling = SamplingParams(
        n=CONFIG["samples_per_cell"],
        temperature=CONFIG["temperature"],
        top_p=CONFIG["top_p"],
        max_tokens=spec["max_tokens"],
        seed=CONFIG["seed"] + CONFIG["regimes"].index(spec),
    )
    requests = engine.generate(prompts, sampling)
    result_dir = Path(args.result_dir) if args.result_dir else ROOT / CONFIG["result_dir"]
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    with (raw_dir / f"{args.regime}.jsonl").open("w") as handle:
        for condition, rendered, request in zip(conditions, prompts, requests):
            problem, presentation, order, history = condition
            for sample_index, completion in enumerate(request.outputs):
                text = completion.text
                shown, parser_rule = parse_terminal_choice(
                    text, require_closed_think=spec["requires_closed_think"]
                )
                trace = split_trace(text) if spec["requires_closed_think"] else None
                stripped, removed = strip_terminal_conclusion(trace)
                handle.write(json.dumps({
                    "regime": args.regime,
                    "pair": spec["pair"],
                    "role": spec["role"],
                    "problem": problem["id"],
                    "game_id": problem["game_id"],
                    "presentation": presentation,
                    "history_id": history["id"] if history else None,
                    "order": order,
                    "sample_index": sample_index,
                    "shown_choice": shown,
                    "underlying_choice": underlying_choice(shown, order),
                    "ev_choice": problem["ev_choice"],
                    "valid": shown is not None,
                    "choice_parser": parser_rule,
                    "trace": trace,
                    "stripped_trace": stripped,
                    "removed_terminal_segments": removed,
                    "finish_reason": completion.finish_reason,
                    "continuation": text,
                    "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                    "support_dominance": problem["support_dominance"],
                    "outcome_complexity": problem["outcome_complexity"],
                    "relative_ev_gap": problem["relative_ev_gap"],
                }) + "\n")
    (result_dir / f"{args.regime}.model.json").write_text(json.dumps({
        **spec,
        "backend": "vllm",
        "sampling_seed": CONFIG["seed"] + CONFIG["regimes"].index(spec),
        "n_problems": len(problems),
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
