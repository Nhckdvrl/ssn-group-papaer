"""E15b external check on admitted questions: a stronger model (Qwen3-14B, thinking mode, 4 samples) solves
each question; we record whether its own answers agree with each other and with the fixed solver's majority.
It also labels the field with the eight fields listed in R-Zero's own questioner prompt (non-thinking, greedy).
Neither readout is ground truth; both are reported with that caveat (card E15).

Questions come from the base-solver admission files: per questioner tag, a fixed random sample of admitted
questions (score in [0.3, 0.8], not dropped) and of hard-tail questions (score <= 0.3, not dropped). The solver_v5
majority for the same question (same per-file subsample) is joined in from --alt files when given.

Usage: python e15b_validity.py --model <Qwen3-14B dir> --admit admit_base_*.jsonl [--alt admit_s5_*.jsonl]
       --per_tag 300 --tail_per_tag 150 --shard 0 --nshards 4 --out <jsonl>
"""
import argparse
import json
import random
import signal

import vllm
from transformers import AutoTokenizer
from mathruler.grader import extract_boxed_content, grade_answer

FIELDS = ["algebra", "geometry", "number theory", "combinatorics", "prealgebra", "probability", "statistics", "calculus"]
SOLVE_SYS = "Please reason step by step, and put your final answer within \\boxed{}."
FIELD_PROMPT = ("Classify the following math problem into exactly one of these fields: " + ", ".join(FIELDS) +
                ". If it fits none, answer other. Reply with the field name only.\n\nProblem:\n{q}")


class _T(Exception):
    pass


def _alarm(s, f):
    raise _T()


def same(x, y):
    signal.signal(signal.SIGALRM, _alarm); signal.alarm(10)
    try:
        return bool(x) and bool(y) and (x == y or grade_answer(x, y) or grade_answer(y, x))
    except _T:
        return False
    finally:
        signal.alarm(0)


ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True); ap.add_argument("--admit", nargs="+", required=True)
ap.add_argument("--alt", nargs="*", default=[])
ap.add_argument("--per_tag", type=int, default=300); ap.add_argument("--tail_per_tag", type=int, default=150)
ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
ap.add_argument("--out", required=True)
a = ap.parse_args()
rows = [json.loads(l) for p in a.admit for l in open(p)]
alt = {(r["tag"], r["seed"], r["idx"]): r for p in a.alt for l in open(p) for r in [json.loads(l)]}
ok = [r for r in rows if r["score"] is not None and not r["dropped"]]
pick = []
for kind, cond, k in [("admitted", lambda x: 0.3 <= x <= 0.8, a.per_tag), ("tail", lambda x: x <= 0.3, a.tail_per_tag)]:
    by = {}
    for r in ok:
        if cond(r["score"]):
            by.setdefault(r["tag"], []).append(r)
    for tag, rr in sorted(by.items()):
        rr.sort(key=lambda r: (r["seed"], r["idx"])); random.Random(f"{kind}|{tag}").shuffle(rr)
        pick += [dict(r, kind=kind) for r in rr[:k]]
pick = pick[a.shard::a.nshards]
tok = AutoTokenizer.from_pretrained(a.model)
llm = vllm.LLM(model=a.model, tokenizer=a.model, gpu_memory_utilization=0.9, max_model_len=16384)
solve_p = [tok.apply_chat_template([{"role": "system", "content": SOLVE_SYS}, {"role": "user", "content": r["question"]}],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=True) for r in pick]
field_p = [tok.apply_chat_template([{"role": "user", "content": FIELD_PROMPT.format(q=r["question"])}],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in pick]
so = llm.generate(solve_p, vllm.SamplingParams(n=4, temperature=0.6, top_p=0.95, top_k=20, max_tokens=12288))
fo = llm.generate(field_p, vllm.SamplingParams(n=1, temperature=0.0, max_tokens=8))
with open(a.out, "w") as f:
    for r, s, fl in zip(pick, so, fo):
        ans = [extract_boxed_content(c.text.split("</think>")[-1]) or "" for c in s.outputs]
        agree_ext = sum(same(x, ans[0]) for x in ans) / len(ans)
        agree_major = sum(same(x, r["majority"]) for x in ans) / len(ans)
        ar = alt.get((r["tag"], r["seed"], r["idx"]))
        agree_alt = None if ar is None or not ar["majority"] else sum(same(x, ar["majority"]) for x in ans) / len(ans)
        field = fl.outputs[0].text.strip().lower()
        f.write(json.dumps({"tag": r["tag"], "seed": r["seed"], "idx": r["idx"], "kind": r["kind"],
                            "question": r["question"], "solver_score": r["score"], "setter_answer": r["setter_answer"],
                            "solver_majority": r["majority"], "ext_answers": ans, "ext_self_agree": agree_ext,
                            "ext_agree_solver_majority": agree_major,
                            "alt_score": None if ar is None else ar["score"],
                            "alt_majority": None if ar is None else ar["majority"], "ext_agree_alt_majority": agree_alt,
                            "ext_agree_setter": sum(same(x, r["setter_answer"]) for x in ans) / len(ans),
                            "field": field if field in FIELDS else "other",
                            "ext_truncated": sum(c.finish_reason == "length" for c in s.outputs)}) + "\n")
print("done", len(pick), flush=True)
