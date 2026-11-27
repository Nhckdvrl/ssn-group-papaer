"""E15b: score candidate questions with a FIXED solver exactly as R-Zero's question_evaluate/evaluate.py
(system "Please reason step by step...", temperature 1.0, top_p 1.0, top_k 40, max 4096 tokens, n samples,
answers clustered with mathruler.grade_answer, majority share = score; questions containing "证明" / "box"
or a majority answer containing "text" are dropped, as in the official code).

Input: one or more jsonl files from e15b_generate.py; a fixed random subsample of parse_ok rows per file.
Usage: python e15b_admit.py --solver <dir> --inputs a.jsonl b.jsonl --per_file 2000 --n 9 --out <jsonl>
"""
import argparse
import json
import random
import signal
import time

import vllm
from transformers import AutoTokenizer
from mathruler.grader import extract_boxed_content, grade_answer

SYSTEM = "Please reason step by step, and put your final answer within \\boxed{}."


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


def grade_t(x, y, secs=10):
    """grade_answer with a wall-clock timeout (the official code uses a 10 s stopit timeout)."""
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(secs)
    try:
        return grade_answer(x, y)
    except _Timeout:
        return False
    finally:
        signal.alarm(0)


def cluster(results, grade):
    counts = {}
    for r in results:
        hit = False
        for e in counts:
            if r == e or ("no " in r.lower() and "no " in e.lower()):
                counts[e] += 1; hit = True; break
            try:
                if grade(r, e) or grade(e, r):
                    counts[e] += 1; hit = True; break
            except Exception:
                continue
        if not hit:
            counts[r] = 1
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", required=True)
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--per_file", type=int, default=2000)
    ap.add_argument("--n", type=int, default=9)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows = []
    for path in a.inputs:
        cand = [json.loads(l) for l in open(path)]
        cand = [r for r in cand if r["parse_ok"]]
        random.Random(f"{path}|{a.seed}").shuffle(cand)
        for r in cand[: a.per_file]:
            r["src"] = path
            rows.append(r)
    tok = AutoTokenizer.from_pretrained(a.solver)
    prompts = [tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": r["question"]}],
                                       tokenize=False, add_generation_prompt=True) for r in rows]
    llm = vllm.LLM(model=a.solver, tokenizer=a.solver, seed=a.seed, gpu_memory_utilization=0.85)
    sp = vllm.SamplingParams(max_tokens=4096, temperature=1.0, top_p=1.0, top_k=40, n=a.n,
                             stop_token_ids=[tok.eos_token_id], seed=a.seed)
    t0 = time.time()
    outs = llm.generate(prompts, sampling_params=sp)
    gen_s = time.time() - t0
    ntok = 0
    with open(a.out, "w") as f:
        for r, o in zip(rows, outs):
            ntok += sum(len(c.token_ids) for c in o.outputs)
            res = [extract_boxed_content(c.text) for c in o.outputs]
            res = [x for x in res if x and x != "None"]
            counts = cluster(res, grade_t) if res else {}
            maj = max(counts, key=counts.get) if counts else ""
            score = counts[maj] / len(res) if counts else None
            dropped = ("证明" in r["question"] or "box" in r["question"].lower() or "text" in maj.lower()) if counts else True
            agree_setter = bool(maj) and bool(r["answer"]) and (grade_t(maj, r["answer"]) or grade_t(r["answer"], maj))
            f.write(json.dumps({"src": r["src"], "tag": r["tag"], "seed": r["seed"], "idx": r["idx"],
                                "question": r["question"], "setter_answer": r["answer"], "majority": maj,
                                "score": score, "n_boxed": len(res), "dropped": dropped,
                                "agree_setter": agree_setter, "answers": res,
                                "resp_tokens": [len(c.token_ids) for c in o.outputs]}) + "\n")
    with open(a.out + ".meta.json", "w") as f:
        json.dump({"solver": a.solver, "inputs": a.inputs, "per_file": a.per_file, "n": a.n,
                   "seed": a.seed, "gen_seconds": gen_s, "gen_tokens": ntok}, f, indent=1)
    print(f"done {len(rows)} questions x {a.n} in {gen_s:.0f}s", flush=True)


if __name__ == "__main__":
    main()
