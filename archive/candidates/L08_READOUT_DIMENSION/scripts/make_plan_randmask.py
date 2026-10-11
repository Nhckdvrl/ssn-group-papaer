"""E11 — random half-masks, to control the mask-identity result at a fixed count."""
import json
M = {"llama31_8b_instruct": "NousResearch/Meta-Llama-3.1-8B-Instruct",
     "qwen25_7b_instruct": "Qwen/Qwen2.5-7B-Instruct"}
C = {"mmlu_rank": (1000, 8), "mmlu_gen_cot": (400, 16), "gsm8k_gen_cot": (500, 16)}
print(json.dumps({"jobs": [
    {"model": mp, "cell": c, "mask": "random", "mask_seed": s, "n": n, "bs": bs,
     "out": f"results/e01/{k}/{c}__random{s}.jsonl"}
    for k, mp in M.items() for c, (n, bs) in C.items() for s in (11, 22, 33)]}, indent=1))
