"""E15c: sample AZR code_i / code_o proposals (program + input) from a model conditioned on reference programs
drawn from a materials file, using AZR's own prompt builder (data_construction/prompts.py) and instruction
template (answer_conditional), wrapped in the model's chat template as AZR's verl dataset does.
Six references per proposal (AZR io_n=6), composite functions off (as in the released scripts).

Usage: python e15c_propose.py --model <dir> --materials <jsonl> --task code_o --n 4096 --temp 1.0 --seed 0 --out <jsonl>
"""
import argparse
import importlib.util
import json
import random
import time

import vllm
from transformers import AutoTokenizer

AZR = "/home/xiang/.cache/research/data-centric-rsi/AZR/absolute_zero_reasoner"
INSTR = ("A conversation between User and Assistant. The user asks a question, and the Assistant solves it. The assistant "
         "first thinks about the reasoning process in the mind and then provides the user with the answer. The reasoning "
         "process and answer are enclosed within <think> </think> and <answer> </answer> tags, respectively, i.e., <think> "
         "reasoning process here </think> <answer> answer here </answer>. User: {}\nAssistant: <think>")
BANNED = ["logging", "random", "multiprocessing", "pebble", "subprocess", "threading", "datetime", "time", "hashlib",
          "hmac", "bcrypt", "os.sys", "os.path", "sys.exit", "os.environ", "calendar", "datetime"]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--materials", required=True)
    ap.add_argument("--task", choices=["code_i", "code_o"], required=True)
    ap.add_argument("--n", type=int, required=True); ap.add_argument("--temp", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    prompts_mod = load("azr_prompts", f"{AZR}/data_construction/prompts.py")
    mats = [json.loads(l) for l in open(a.materials)]
    rng = random.Random(f"{a.seed}|{a.task}|{a.materials}")
    tok = AutoTokenizer.from_pretrained(a.model)
    prompts, refs = [], []
    for _ in range(a.n):
        idx = rng.sample(range(len(mats)), k=min(6, len(mats)))
        chosen = [mats[i] for i in idx]
        body = prompts_mod.get_code_problem_generator_prompt(problem_type=a.task, reference_snippets=chosen,
                                                             banned_keywords=BANNED, banned_assertion_keywords=[],
                                                             composite_functions=[], remove_after_return=False,
                                                             num_inputs=10, remove_input_from_snippet=False)
        prompts.append(tok.apply_chat_template([{"role": "user", "content": INSTR.format(body)}],
                                               add_generation_prompt=True, tokenize=False))
        refs.append(idx)
    llm = vllm.LLM(model=a.model, tokenizer=a.model, seed=a.seed, gpu_memory_utilization=0.85, max_model_len=16384)
    sp = vllm.SamplingParams(temperature=a.temp, top_p=1.0, max_tokens=8096)  # engine-level seed only
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    gen_s = time.time() - t0
    with open(a.out, "w") as f:
        for i, (o, r) in enumerate(zip(outs, refs)):
            f.write(json.dumps({"tag": a.tag, "task": a.task, "temp": a.temp, "seed": a.seed, "idx": i, "refs": r,
                                "text": o.outputs[0].text, "n_tokens": len(o.outputs[0].token_ids),
                                "finish": o.outputs[0].finish_reason}) + "\n")
    json.dump({"model": a.model, "materials": a.materials, "task": a.task, "n": a.n, "temp": a.temp, "seed": a.seed,
               "gen_seconds": gen_s}, open(a.out + ".meta.json", "w"), indent=1)
    print(f"done {a.n} in {gen_s:.0f}s", flush=True)


if __name__ == "__main__":
    main()
