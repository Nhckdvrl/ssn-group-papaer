#!/usr/bin/env python3
"""Generate E20 behavior over orthogonal form and evidence conditions."""

import argparse
import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from cpc18_form_evidence_common import (
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
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    args = parser.parse_args()
    spec = next(item for item in CONFIG["regimes"] if item["name"] == args.regime)
    problems = load_problems(args.limit)[args.shard_index::args.num_shards]
    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    conditions = []
    for problem in problems:
        for evidence in problem["evidence"]:
            for form in ("raw", "summary"):
                for order in CONFIG["orders"]:
                    conditions.append((problem, evidence, form, order))
    rendered = []
    for problem, evidence, form, order in conditions:
        kwargs = {}
        if "enable_thinking" in spec:
            kwargs["enable_thinking"] = spec["enable_thinking"]
        rendered.append(tokenizer.apply_chat_template(
            [{"role": "user", "content": make_prompt(problem, evidence, form, order)}],
            tokenize=False,
            add_generation_prompt=True,
            **kwargs,
        ))
    engine = LLM(
        model=spec["id"], revision=spec["revision"], dtype="bfloat16",
        tensor_parallel_size=1, max_model_len=5120,
        gpu_memory_utilization=0.78, trust_remote_code=True,
    )
    sampling = SamplingParams(
        n=CONFIG["samples_per_cell"], temperature=CONFIG["temperature"],
        top_p=CONFIG["top_p"], max_tokens=spec["max_tokens"],
        seed=CONFIG["seed"] + CONFIG["regimes"].index(spec),
    )
    requests = engine.generate(rendered, sampling)
    output = ROOT / CONFIG["result_dir"]
    raw_dir = output / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.num_shards == 1 else f".shard{args.shard_index}of{args.num_shards}"
    with (raw_dir / f"{args.regime}{suffix}.jsonl").open("w") as handle:
        for condition, prompt, request in zip(conditions, rendered, requests):
            problem, evidence, form, order = condition
            for sample_index, completion in enumerate(request.outputs):
                text = completion.text
                shown, rule = parse_terminal_choice(
                    text, require_closed_think=spec["requires_closed_think"]
                )
                trace = split_trace(text) if spec["requires_closed_think"] else None
                stripped, removed = strip_terminal_conclusion(trace)
                handle.write(json.dumps({
                    "regime": args.regime,
                    "pair": spec["pair"],
                    "role": spec["role"],
                    "problem": problem["id"],
                    "source_split": problem["source_split"],
                    "evidence_choice": evidence["evidence_choice"],
                    "evidence_history_id": evidence["history_id"],
                    "form": form,
                    "order": order,
                    "sample_index": sample_index,
                    "shown_choice": shown,
                    "underlying_choice": underlying_choice(shown, order),
                    "valid": shown is not None,
                    "choice_parser": rule,
                    "trace": trace,
                    "stripped_trace": stripped,
                    "removed_terminal_segments": removed,
                    "finish_reason": completion.finish_reason,
                    "continuation": text,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "normalized_empirical_gap": evidence["normalized_empirical_gap"],
                }) + "\n")
    (output / f"{args.regime}{suffix}.model.json").write_text(json.dumps({
        **spec,
        "backend": "vllm",
        "sampling_seed": CONFIG["seed"] + CONFIG["regimes"].index(spec),
        "n_problems": len(problems),
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
