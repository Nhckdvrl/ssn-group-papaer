"""E16 stage 0, function-level (HumanEval+), one model.

--phase solve    : 4 samples per problem of the completed function
--phase evidence : judge (reference, one external bug, one mutant; 2 samples each) and the two evidence tasks
                   (disc_ref: reference + bug -> distinguishing call; disc_cand: candidate -> failing call or
                   \\boxed{CORRECT}); bug sources external (Qwen2.5-Coder-1.5B wrong programs), mutant, own (this
                   model's wrong programs); up to 2 bugs per source per problem, 2 samples each.
Panels come from e16f_score.py --emit_bugs. Engine-level seed only. Verdicts as \\boxed{...}; inputs as JSON.
Pilot change (2026-11-28): the evidence prompts ask for step-by-step reasoning first; instruct models had answered
in ~22 tokens without reasoning while R1-distilled models reasoned for 2-3k tokens (a test-time compute confound).
Usage: python e16f_infer.py --model <dir> --problems problems_f.jsonl --phase solve --out solve_<tag>.jsonl
       python e16f_infer.py --model <dir> --problems pilot.jsonl --phase evidence --external ext.jsonl
                            --own own_<tag>.jsonl --out ev_<tag>.jsonl
"""
import argparse
import json
import time

import vllm
from transformers import AutoTokenizer

SOLVE = ("Complete the following Python function. Give the complete function, including its signature and any "
         "imports it needs, in a single ```python code block at the end.\n\n```python\n{prompt}```")
JUDGE = ("Here is the specification of a Python function and an implementation of it.\n\nSpecification:\n```python\n"
         "{prompt}```\n\nImplementation:\n```python\n{code}\n```\n\nIs the implementation correct on every valid input? "
         "First reason step by step about its behaviour on different valid inputs, then give your final answer as "
         "\\boxed{{CORRECT}} or \\boxed{{INCORRECT}}.")
CALL = ('[{{"input": "{entry}(...)"}}] where the arguments are Python literals')
DISC_REF = ("Specification:\n```python\n{prompt}```\n\nA correct reference implementation:\n```python\n{ref}\n```\n\n"
            "A buggy implementation:\n```python\n{code}\n```\n\nThe buggy implementation returns a wrong result for some "
            "valid input. Give one valid input (allowed by the specification) on which the two implementations return "
            "different results. First reason step by step about where the two implementations behave differently and "
            "check your input against both. Do not write any new program. End your answer with the input as a single "
            "function call in JSON, in a ```json block: " + CALL + ".")
DISC_CAND = ("Specification:\n```python\n{prompt}```\n\nA candidate implementation:\n```python\n{code}\n```\n\nThe "
             "candidate may or may not be correct. First reason step by step about its behaviour on different valid "
             "inputs. If you believe it is wrong, give one valid input (allowed by the "
             "specification) on which it returns a wrong result, and end your answer with that input as a single "
             "function call in JSON, in a ```json block: " + CALL + ". If you believe it is correct on every valid "
             "input, end your answer with \\boxed{{CORRECT}} instead.")


def load_panel(path):
    out = {}
    if path:
        for l in open(path):
            r = json.loads(l); out.setdefault(r["pid"], []).append(r["code"])
    return out


def items(probs, phase, ext, own, n_solve=4):
    out = []
    for p in probs:
        pid, pr, ent = p["id"], p["prompt"], p["entry"]
        if phase == "solve":
            for s in range(n_solve):
                out.append(dict(task="solve", pid=pid, inst="solve", source="-", sample=s, prompt=SOLVE.format(prompt=pr)))
            continue
        bugs = [("external", i, c) for i, c in enumerate(ext.get(pid, [])[:2])] + \
               [("mutant", i, m["code"]) for i, m in enumerate(p["mutants"][:2])] + \
               [("own", i, c) for i, c in enumerate(own.get(pid, [])[:2])]
        judge_set = [("ref", 0, "correct", p["ref_plain"])] + [(s, i, "bug", c) for s, i, c in bugs if i == 0 and s != "own"]
        for src, i, lab, code in judge_set:
            for s in range(2):
                out.append(dict(task="judge", pid=pid, inst=f"{src}{i}", source=src, label=lab, sample=s,
                                prompt=JUDGE.format(prompt=pr, code=code)))
        for src, i, code in bugs:
            for s in range(2):
                out.append(dict(task="disc_ref", pid=pid, inst=f"{src}{i}", source=src, label="bug", sample=s, code=code,
                                prompt=DISC_REF.format(prompt=pr, ref=p["ref_plain"], code=code, entry=ent)))
        for src, i, code in bugs + [("ref", 0, p["ref_plain"])]:
            for s in range(2):
                out.append(dict(task="disc_cand", pid=pid, inst=f"{src}{i}", source=src,
                                label="correct" if src == "ref" else "bug", sample=s, code=code,
                                prompt=DISC_CAND.format(prompt=pr, code=code, entry=ent)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--problems", required=True)
    ap.add_argument("--phase", choices=["solve", "evidence"], required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--external", default=None); ap.add_argument("--own", default=None)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--max_tokens", type=int, default=24576)
    ap.add_argument("--n_solve", type=int, default=4); ap.add_argument("--temperature", type=float, default=0.6)
    a = ap.parse_args()
    probs = [json.loads(l) for l in open(a.problems)]
    its = items(probs, a.phase, load_panel(a.external), load_panel(a.own), a.n_solve)
    tok = AutoTokenizer.from_pretrained(a.model)
    prompts = [tok.apply_chat_template([{"role": "user", "content": it["prompt"]}], tokenize=False,
                                       add_generation_prompt=True) for it in its]
    llm = vllm.LLM(model=a.model, tokenizer=a.model, seed=a.seed, gpu_memory_utilization=0.88, max_model_len=32768)
    sp = vllm.SamplingParams(temperature=a.temperature, top_p=0.95, max_tokens=a.max_tokens)  # engine-level seed only
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    gen_s = time.time() - t0
    with open(a.out, "w") as f:
        for it, o in zip(its, outs):
            it = {k: v for k, v in it.items() if k != "prompt"}
            it.update(text=o.outputs[0].text, n_tokens=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason)
            f.write(json.dumps(it) + "\n")
    json.dump({"model": a.model, "problems": a.problems, "phase": a.phase, "n": len(its), "gen_seconds": gen_s,
               "distinct_outputs": len({o.outputs[0].text for o in outs})}, open(a.out + ".meta.json", "w"), indent=1)
    print(f"done {len(its)} in {gen_s:.0f}s", flush=True)


if __name__ == "__main__":
    main()
