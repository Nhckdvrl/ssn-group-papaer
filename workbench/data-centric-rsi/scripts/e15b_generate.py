"""E15b: sample candidate questions from an R-Zero questioner exactly as the official
question_generate.py does (same system/user prompt, temperature 1.0, top_p 0.95, max 4096 tokens,
eos stop), but with ONE chat template for every questioner (taken from --template_dir) so that the
initial model and the trained checkpoints see identical prompt strings.

Usage: python e15b_generate.py --model <dir> --template_dir <dir> --n 5000 --seed 0 --out <jsonl>
"""
import argparse
import json
import re
import time

import vllm
from transformers import AutoTokenizer

SYSTEM = (
    "You are an expert competition-math problem setter.\n"
    "FIRST, in your private scratch-pad, think step-by-step to design a brand-new, non-trivial problem. "
    "The problem could come from any field of mathematics, including but not limited to algebra, geometry, number theory, combinatorics, prealgebra, probability, statistics, and calculus. "
    "Aim for a difficulty such that fewer than 30 % of advanced high-school students could solve it. "
    "Avoid re-using textbook clichés or famous contest problems.\n"
    "THEN, without revealing any of your private thoughts, output **exactly** the following two blocks:\n\n"
    "<question>\n"
    "{The full problem statement on one or more lines}\n"
    "</question>\n\n"
    r"\boxed{final_answer}"
    "\n\n"
    "Do NOT output anything else—no explanations, no extra markup."
)
USER = "Generate one new, challenging reasoning question now. Remember to format the output exactly as instructed."


def extract_boxed(text):
    """Same logic as R-Zero question_generate.extract_boxed: all balanced \\boxed{...} contents."""
    results, i, prefix = [], 0, r"\boxed{"
    while True:
        start = text.find(prefix, i)
        if start == -1:
            break
        j, depth = start + len(prefix), 1
        while j < len(text) and depth > 0:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        results.append(text[start + len(prefix): j - 1])
        i = j
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--template_dir", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    ttok = AutoTokenizer.from_pretrained(a.template_dir)
    chat = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}]
    prompt = ttok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    mtok = AutoTokenizer.from_pretrained(a.model)
    llm = vllm.LLM(model=a.model, tokenizer=a.model, seed=a.seed, gpu_memory_utilization=0.85)
    sp = vllm.SamplingParams(max_tokens=4096, temperature=1.0, top_p=0.95, n=1,
                             stop_token_ids=[mtok.eos_token_id])  # no per-request seed: identical prompts would share one random stream
    t0 = time.time()
    outs = llm.generate([prompt] * a.n, sampling_params=sp)
    gen_s = time.time() - t0
    ntok = 0
    with open(a.out, "w") as f:
        for i, o in enumerate(outs):
            text = o.outputs[0].text
            ntok += len(o.outputs[0].token_ids)
            qs = re.findall(r"<question>(.*?)</question>", text, re.DOTALL)
            ans = extract_boxed(text)
            ok = bool(qs and ans)
            f.write(json.dumps({"tag": a.tag, "seed": a.seed, "idx": i, "parse_ok": ok,
                                "question": qs[-1].strip() if ok else "", "answer": ans[-1].strip() if ok else "",
                                "n_tokens": len(o.outputs[0].token_ids),
                                "finish": o.outputs[0].finish_reason, "raw": text}) + "\n")
    with open(a.out + ".meta.json", "w") as f:
        json.dump({"model": a.model, "template_dir": a.template_dir, "n": a.n, "seed": a.seed,
                   "prompt": prompt, "gen_seconds": gen_s, "gen_tokens": ntok,
                   "uniq_raw": len({o.outputs[0].text for o in outs})}, f, indent=1)
    print(f"done {a.n} in {gen_s:.0f}s, {ntok} tokens, {len({o.outputs[0].text for o in outs})} distinct outputs", flush=True)


if __name__ == "__main__":
    main()
