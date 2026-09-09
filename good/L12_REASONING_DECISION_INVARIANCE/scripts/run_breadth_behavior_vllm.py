#!/usr/bin/env python3
"""High-throughput E10 Think-SFT sampling with the same audited raw schema."""

import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from run_model import parse_choice
from run_trajectory_takeover import make_prompt, split_trace, strip_terminal_conclusion


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())


def load_decisions():
    rows = []
    with (ROOT / CONFIG["output"]).open() as handle:
        for line in handle:
            row = json.loads(line)
            rows.append({
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
            })
    return rows


def main():
    spec = next(
        item for item in CONFIG["models"] if item["branch"] == "think_sft"
    )
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    decisions = load_decisions()
    conditions = [
        (decision, frame, order)
        for decision in decisions
        for frame in CONFIG["frames"]
        for order in CONFIG["orders"]
    ]
    rendered_prompts = []
    for decision, frame, order in conditions:
        prompt = make_prompt(decision, frame, order)
        rendered_prompts.append(tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        ))

    engine = LLM(
        model=spec["id"],
        revision=spec["revision"],
        dtype="bfloat16",
        tensor_parallel_size=1,
        max_model_len=1536,
        gpu_memory_utilization=0.75,
        trust_remote_code=True,
    )
    sampling = SamplingParams(
        n=CONFIG["samples_per_cell"],
        temperature=CONFIG["temperature"],
        top_p=CONFIG["top_p"],
        max_tokens=spec["max_new_tokens"],
        seed=CONFIG["seed"],
    )
    outputs = engine.generate(rendered_prompts, sampling)
    out = ROOT / CONFIG["result_dir"] / "think_sft"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "raw.jsonl").open("w") as handle:
        for (decision, frame, order), rendered, request in zip(
            conditions, rendered_prompts, outputs
        ):
            for sample_index, completion in enumerate(request.outputs):
                text = completion.text
                shown = parse_choice(text, require_closed_think=True)
                underlying = shown
                if shown is not None and order == "ba":
                    underlying = "B" if shown == "A" else "A"
                trace = split_trace(text)
                stripped, removed = (
                    strip_terminal_conclusion(trace)
                    if trace is not None else (None, [])
                )
                handle.write(json.dumps({
                    "model": spec["id"],
                    "revision": spec["revision"],
                    "branch": "think_sft",
                    "prospect": decision["id"],
                    "frame": frame,
                    "order": order,
                    "sample_index": sample_index,
                    "seed": CONFIG["seed"],
                    "shown_choice": shown,
                    "underlying_choice": underlying,
                    "gold_underlying": decision[f"{frame}_optimal"],
                    "valid": shown is not None,
                    "trace": trace,
                    "stripped_trace": stripped,
                    "removed_terminal_segments": removed,
                    "continuation": text,
                    "prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                    "ev_gap_stratum": decision["ev_gap_stratum"],
                    "probability_gap_stratum": decision["probability_gap_stratum"],
                    "payoff_scale": decision["payoff_scale"],
                }) + "\n")
    (out / "model.json").write_text(json.dumps({
        **spec,
        "backend": "vllm",
        "sampling_seed": CONFIG["seed"],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
