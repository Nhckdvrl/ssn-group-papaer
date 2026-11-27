"""E15b identity smoke test: greedy MATH500 accuracy on a fixed random subset, R-Zero evaluation prompt
(evaluation/generate.py: system "Please reason step by step...", temperature 0, max 4096 tokens).
Graded with mathruler.grade_answer (the official evaluation uses math_verify; this is only an identity check).

Usage: python e15b_smoke.py --model <dir> --csv math_500_test.csv --k 200 --out <json>
"""
import argparse
import csv
import json
import random

import vllm
from transformers import AutoTokenizer
from mathruler.grader import extract_boxed_content, grade_answer

SYSTEM = "Please reason step by step, and put your final answer within \\boxed{}."

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True); ap.add_argument("--csv", required=True)
ap.add_argument("--k", type=int, default=200); ap.add_argument("--out", required=True)
a = ap.parse_args()
rows = list(csv.DictReader(open(a.csv)))
random.Random(0).shuffle(rows)
rows = rows[: a.k]
tok = AutoTokenizer.from_pretrained(a.model)
prompts = [tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": r["Question"]}],
                                   tokenize=False, add_generation_prompt=True) for r in rows]
llm = vllm.LLM(model=a.model, tokenizer=a.model, gpu_memory_utilization=0.85)
outs = llm.generate(prompts, vllm.SamplingParams(max_tokens=4096, temperature=0.0, stop_token_ids=[tok.eos_token_id]))
correct, recs = 0, []
for r, o in zip(rows, outs):
    pred = extract_boxed_content(o.outputs[0].text) or ""
    ref = extract_boxed_content(r["Answer"]) or r["Answer"]  # the csv holds full solutions; take the boxed answer
    ok = bool(pred) and (grade_answer(pred, ref) or grade_answer(ref, pred))
    correct += ok
    recs.append({"answer": ref, "pred": pred, "ok": ok, "n_tokens": len(o.outputs[0].token_ids)})
json.dump({"model": a.model, "k": a.k, "acc": correct / len(rows), "records": recs}, open(a.out, "w"), indent=1)
print(f"{a.model}: {correct}/{len(rows)} = {correct / len(rows):.3f}", flush=True)
