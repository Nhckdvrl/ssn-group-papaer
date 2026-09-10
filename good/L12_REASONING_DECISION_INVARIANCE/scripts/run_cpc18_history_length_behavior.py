#!/usr/bin/env python3
"""Run the frozen E18 supporting 20/100 history-length diagnosis."""

import argparse
import hashlib
import json

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from cpc18_common import parse_terminal_choice, split_trace, strip_terminal_conclusion, underlying_choice
from cpc18_history_length_common import CONFIG, ROOT, load_problems, make_prompt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", required=True)
    args = parser.parse_args()
    spec = next(item for item in CONFIG["regimes"] if item["name"] == args.regime)
    problems = load_problems()
    conditions = []
    for problem in problems:
        for order in CONFIG["orders"]:
            conditions.append((problem, "explicit", order, None))
            for history in problem["histories"]:
                conditions.append((problem, "history", order, history))
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"], local_files_only=True)
    prompts = []
    for problem, presentation, order, history in conditions:
        kwargs = {"enable_thinking": spec["enable_thinking"]} if "enable_thinking" in spec else {}
        prompts.append(tokenizer.apply_chat_template(
            [{"role": "user", "content": make_prompt(problem, presentation, order, history)}],
            tokenize=False, add_generation_prompt=True, **kwargs,
        ))
    engine = LLM(model=spec["id"], revision=spec["revision"], dtype="bfloat16", tensor_parallel_size=1, max_model_len=6144, gpu_memory_utilization=0.78, trust_remote_code=True)
    requests = engine.generate(prompts, SamplingParams(
        n=CONFIG["samples_per_cell"], temperature=CONFIG["temperature"], top_p=CONFIG["top_p"],
        max_tokens=spec["max_tokens"], seed=CONFIG["seed"] + CONFIG["regimes"].index(spec),
    ))
    output = ROOT / CONFIG["result_dir"]
    (output / "raw").mkdir(parents=True, exist_ok=True)
    with (output / "raw" / f"{args.regime}.jsonl").open("w") as handle:
        for condition, prompt, request in zip(conditions, prompts, requests):
            problem, presentation, order, history = condition
            for sample_index, completion in enumerate(request.outputs):
                shown, rule = parse_terminal_choice(completion.text, require_closed_think=spec["requires_closed_think"])
                trace = split_trace(completion.text) if spec["requires_closed_think"] else None
                stripped, removed = strip_terminal_conclusion(trace)
                handle.write(json.dumps({
                    "regime": args.regime, "pair": spec["pair"], "role": spec["role"],
                    "problem": problem["id"], "presentation": presentation,
                    "history_id": history["id"] if history else None,
                    "history_length": history["length"] if history else None,
                    "history_replicate": history["replicate"] if history else None,
                    "history_empirical_choice": history["empirical_choice"] if history else None,
                    "order": order, "sample_index": sample_index,
                    "shown_choice": shown, "underlying_choice": underlying_choice(shown, order),
                    "ev_choice": problem["ev_choice"], "valid": shown is not None,
                    "choice_parser": rule, "trace": trace, "stripped_trace": stripped,
                    "removed_terminal_segments": removed, "finish_reason": completion.finish_reason,
                    "continuation": completion.text, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                }) + "\n")
    (output / f"{args.regime}.model.json").write_text(json.dumps({**spec, "backend": "vllm", "sampling_seed": CONFIG["seed"] + CONFIG["regimes"].index(spec), "n_problems": len(problems)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
