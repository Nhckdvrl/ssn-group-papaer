"""E16 stage 0 (GPU): one model, four behaviours on the selected CodeContests problems, neutral prompts.

  solve      : write a Python 3 stdin/stdout program (4 samples per problem)
  judge      : is this program correct? (one correct reference, one human WA submission, one mutant; 2 samples)
  disc_ref   : given reference + buggy program, give one input on which they differ (2 samples per bug)
  disc_cand  : given a candidate (buggy or correct), give a failing input or say it is correct (2 samples)
Bug sources: human (WA-type submissions), mutant (AST mutants of a reference), own (this model's own WA programs,
passed in with --own <jsonl from e16_score.py --emit_own>; only the disc tasks are run in that pass).
The random seed is set at engine level only (per-request seeds made identical prompts share one stream in E15).

Usage: python e16_infer.py --model <dir> --problems problems_100.jsonl --out gen_<tag>.jsonl [--own own_<tag>.jsonl]
"""
import argparse
import json
import time

import vllm
from transformers import AutoTokenizer

SOLVE = ("Solve the following competitive programming problem in Python 3. Read from standard input and write to "
         "standard output. Give the complete final program in a single ```python code block at the end.\n\n"
         "Problem:\n{desc}")
JUDGE = ("Here is a competitive programming problem and a Python 3 program meant to solve it.\n\nProblem:\n{desc}\n\n"
         "Program:\n```python\n{code}\n```\n\nIs the program correct on every valid input (within the time limit)? "
         "Reason about it, then end your answer with exactly one line: VERDICT: CORRECT or VERDICT: INCORRECT.")
DISC_REF = ("Problem:\n{desc}\n\nA correct reference solution:\n```python\n{ref}\n```\n\nA buggy program:\n"
            "```python\n{code}\n```\n\nThe buggy program gives a wrong answer on some valid input. Write one valid "
            "input, following the problem's input format and constraints, on which the buggy program's output differs "
            "from the reference solution's output. Keep the input small. End your answer with the input inside a "
            "single ```input code block.")
DISC_CAND = ("Problem:\n{desc}\n\nA candidate program:\n```python\n{code}\n```\n\nThe candidate may or may not be "
             "correct. If you believe it is wrong, write one valid input, following the problem's input format and "
             "constraints, on which it gives a wrong answer, and end your answer with that input inside a single "
             "```input code block. If you believe it is correct on every valid input, end your answer with the line "
             "VERDICT: CORRECT instead.")


def items(probs, own):
    out = []
    for p in probs:
        d, pid, ref = p["description"], p["id"], p["refs"][0]
        if own is None:
            for s in range(4):
                out.append(dict(task="solve", pid=pid, inst="solve", source="-", sample=s, prompt=SOLVE.format(desc=d)))
            judge_set = [("ref", "correct", p["refs"][1])] + [("human", "bug", h["code"]) for h in p["human"][:1]] + \
                        [("mutant", "bug", m["code"]) for m in p["mutants"][:1]]
            for src, lab, code in judge_set:
                for s in range(2):
                    out.append(dict(task="judge", pid=pid, inst=f"{src}0", source=src, label=lab, sample=s,
                                    prompt=JUDGE.format(desc=d, code=code)))
            bugs = [("human", i, h["code"]) for i, h in enumerate(p["human"][:2])] + \
                   [("mutant", i, m["code"]) for i, m in enumerate(p["mutants"][:2])]
            cands = bugs + [("ref", 1, p["refs"][1])]
        else:
            bugs = [("own", i, c) for i, c in enumerate(own.get(pid, [])[:2])]
            cands = bugs
        for src, i, code in bugs:
            for s in range(2):
                out.append(dict(task="disc_ref", pid=pid, inst=f"{src}{i}", source=src, label="bug", sample=s,
                                code=code, prompt=DISC_REF.format(desc=d, ref=ref, code=code)))
        for src, i, code in cands:
            for s in range(2):
                out.append(dict(task="disc_cand", pid=pid, inst=f"{src}{i}", source=src,
                                label="correct" if src == "ref" else "bug", sample=s, code=code,
                                prompt=DISC_CAND.format(desc=d, code=code)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--problems", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--own", default=None)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--max_tokens", type=int, default=16384)
    a = ap.parse_args()
    probs = [json.loads(l) for l in open(a.problems)]
    own = None
    if a.own:
        own = {}
        for l in open(a.own):
            r = json.loads(l); own.setdefault(r["pid"], []).append(r["code"])
    its = items(probs, own)
    tok = AutoTokenizer.from_pretrained(a.model)
    prompts = [tok.apply_chat_template([{"role": "user", "content": it["prompt"]}], tokenize=False,
                                       add_generation_prompt=True) for it in its]
    llm = vllm.LLM(model=a.model, tokenizer=a.model, seed=a.seed, gpu_memory_utilization=0.88,
                   max_model_len=a.max_tokens + 8192)
    sp = vllm.SamplingParams(temperature=0.6, top_p=0.95, max_tokens=a.max_tokens)  # engine-level seed only
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    gen_s = time.time() - t0
    with open(a.out, "w") as f:
        for it, o in zip(its, outs):
            it = {k: v for k, v in it.items() if k != "prompt"}
            it.update(text=o.outputs[0].text, n_tokens=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason)
            f.write(json.dumps(it) + "\n")
    json.dump({"model": a.model, "problems": a.problems, "own": a.own, "n": len(its), "gen_seconds": gen_s,
               "distinct_outputs": len({o.outputs[0].text for o in outs})}, open(a.out + ".meta.json", "w"), indent=1)
    print(f"done {len(its)} in {gen_s:.0f}s", flush=True)


if __name__ == "__main__":
    main()
