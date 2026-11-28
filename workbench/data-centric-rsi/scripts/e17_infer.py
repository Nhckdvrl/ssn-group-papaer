"""E17-0 generation for one model (vLLM, engine-level seed only).

--phase solve     : n samples per problem of the full `class Solution` (reason first, final ```python block)
--phase tests     : n samples per problem of 8 test cases written from the problem statement only
                    (keyword-argument inputs as in the examples + expected output, final ```json list)
--phase condtests : 1 sample per (problem, program) for programs listed in --cond (jsonl {id, code}): the same test
                    request, but the model is first shown that program as "the solution you wrote" (positive
                    control for candidate-conditioned test writing; arXiv 2607.05139)
Usage: python e17_infer.py --model <dir> --problems problems.jsonl --phase solve --n 8 --out solve_<tag>.jsonl
"""
import argparse
import json
import time

import vllm
from transformers import AutoTokenizer

SOLVE = ("Solve the following programming problem in Python 3.\n\n{desc}\n\nStarter code:\n```python\n{starter}```\n\n"
         "First reason step by step about the algorithm and edge cases. Then give your complete solution (the full "
         "`class Solution` with the given method signature) in a single ```python code block at the end.")
TESTS = ("Here is a programming problem.\n\n{desc}\n\nStarter code:\n```python\n{starter}```\n\n"
         "{cond}Write 8 test cases for this problem that would expose incorrect solutions: include edge cases and tricky "
         "cases, keep every input valid under the problem's constraints, and keep inputs small enough to check by hand. "
         "For each test give the input in the same format as the examples (keyword arguments, e.g. `nums = [1,2,3], "
         "k = 2`) and the exact expected output, worked out by careful reasoning. First reason step by step. Then end "
         "your answer with a single ```json block containing a list "
         '[{{"input": "...", "output": "..."}}, ...] where each output is a Python literal (strings quoted).')
COND = "You wrote the following solution to this problem:\n```python\n{code}\n```\n\nNow, for the same problem, "


def build(probs, phase, n, cond):
    out = []
    for p in probs:
        if phase == "solve":
            out += [dict(task="solve", pid=p["id"], sample=s, prompt=SOLVE.format(desc=p["desc"], starter=p["starter"]))
                    for s in range(n)]
        elif phase == "tests":
            out += [dict(task="tests", pid=p["id"], sample=s,
                         prompt=TESTS.format(desc=p["desc"], starter=p["starter"], cond="")) for s in range(n)]
        else:
            for c in cond.get(p["id"], []):
                out.append(dict(task="condtests", pid=p["id"], sample=0, cond_prog=c["prog"],
                                prompt=TESTS.format(desc=p["desc"], starter=p["starter"],
                                                    cond=COND.format(code=c["code"]))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--problems", required=True)
    ap.add_argument("--phase", choices=["solve", "tests", "condtests"], required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--cond", default=None); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--max_tokens", type=int, default=16384)
    ap.add_argument("--temperature", type=float, default=0.8)
    a = ap.parse_args()
    probs = [json.loads(l) for l in open(a.problems)]
    if a.limit:
        probs = probs[:a.limit]
    cond = {}
    if a.cond:
        for l in open(a.cond):
            r = json.loads(l); cond.setdefault(r["id"], []).append(r)
    its = build(probs, a.phase, a.n, cond)
    tok = AutoTokenizer.from_pretrained(a.model)
    prompts = [tok.apply_chat_template([{"role": "user", "content": it["prompt"]}], tokenize=False,
                                       add_generation_prompt=True) for it in its]
    llm = vllm.LLM(model=a.model, tokenizer=a.model, seed=a.seed, gpu_memory_utilization=0.88, max_model_len=24576)
    sp = vllm.SamplingParams(temperature=a.temperature, top_p=0.95, max_tokens=a.max_tokens)  # engine-level seed only
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    gen_s = time.time() - t0
    with open(a.out, "w") as f:
        for it, o in zip(its, outs):
            it = {k: v for k, v in it.items() if k != "prompt"}
            it.update(text=o.outputs[0].text, n_tokens=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason)
            f.write(json.dumps(it) + "\n")
    json.dump({"model": a.model, "phase": a.phase, "n": len(its), "gen_seconds": gen_s,
               "tokens": sum(len(o.outputs[0].token_ids) for o in outs),
               "distinct_outputs": len({o.outputs[0].text for o in outs})}, open(a.out + ".meta.json", "w"), indent=1)
    print(f"done {len(its)} in {gen_s:.0f}s", flush=True)


if __name__ == "__main__":
    main()
