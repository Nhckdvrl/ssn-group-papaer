"""E15b field labels for generated questions: Qwen3-14B (non-thinking, greedy, 8 tokens) assigns one of the eight
fields listed in R-Zero's own questioner prompt, or "other". Applied to a fixed random sample of parse_ok questions
per generation file, before any filtering, so the field distribution describes what each questioner produces.
The label is a model judgement, not ground truth.

Usage: python e15b_fields.py --model <Qwen3-14B dir> --gen <gen_*.jsonl ...> --per_file 500 --out <jsonl>
"""
import argparse
import json
import random

import vllm
from transformers import AutoTokenizer

FIELDS = ["algebra", "geometry", "number theory", "combinatorics", "prealgebra", "probability", "statistics", "calculus"]
FIELD_PROMPT = ("Classify the following math problem into exactly one of these fields: " + ", ".join(FIELDS) +
                ". If it fits none, answer other. Reply with the field name only.\n\nProblem:\n{q}")

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True); ap.add_argument("--gen", nargs="+", required=True)
ap.add_argument("--per_file", type=int, default=500); ap.add_argument("--out", required=True)
a = ap.parse_args()
pick = []
for p in a.gen:
    rows = [json.loads(l) for l in open(p)]
    rows = [r for r in rows if r["parse_ok"]]
    random.Random(f"fields|{p}").shuffle(rows)
    pick += rows[: a.per_file]
tok = AutoTokenizer.from_pretrained(a.model)
llm = vllm.LLM(model=a.model, tokenizer=a.model, gpu_memory_utilization=0.9, max_model_len=8192)
prompts = [tok.apply_chat_template([{"role": "user", "content": FIELD_PROMPT.format(q=r["question"][:6000])}],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in pick]
outs = llm.generate(prompts, vllm.SamplingParams(n=1, temperature=0.0, max_tokens=8))
with open(a.out, "w") as f:
    for r, o in zip(pick, outs):
        lab = o.outputs[0].text.strip().lower().rstrip(".")
        f.write(json.dumps({"tag": r["tag"], "seed": r["seed"], "idx": r["idx"],
                            "field": lab if lab in FIELDS else "other", "raw_label": lab}) + "\n")
print("done", len(pick), flush=True)
