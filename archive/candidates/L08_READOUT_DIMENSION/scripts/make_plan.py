"""Emit the E01+E02 condition plan (factorial over protocol x depth x content)."""
import json, pathlib, sys

MODELS = {
    "llama31_8b_instruct": "NousResearch/Meta-Llama-3.1-8B-Instruct",
    "qwen25_7b_instruct": "Qwen/Qwen2.5-7B-Instruct",
}
# cell -> (n, batch size)   protocol/depth/content coordinates in src/tasks.py
CELLS = {
    "mmlu_rank":        (1000, 16),   # rank   / single / knowledge   <- parent "survivor"
    "mmlu_gen_letter":  (1000, 32),   # gen    / short  / knowledge
    "mmlu_gen_cot":     (400,  16),   # gen    / long   / knowledge   <- decisive cell
    "gsm8k_gen_cot":    (500,  16),   # gen    / long   / reasoning   <- parent "collapse"
    "gsm8k_gen_direct": (500,  32),   # gen    / short  / reasoning
    "squad_gen":        (1000, 16),   # gen    / short  / reading     <- parent "survivor"
}
MASKS = [("full", 0), ("first", 0), ("last", 0)]

jobs = []
for mkey, mpath in MODELS.items():
    for cell, (n, bs) in CELLS.items():
        for mask, seed in MASKS:
            jobs.append({
                "model": mpath, "cell": cell, "mask": mask, "mask_seed": seed,
                "n": n, "bs": bs,
                "out": f"results/e01/{mkey}/{cell}__{mask}{seed if mask=='random' else ''}.jsonl",
            })
print(json.dumps({"jobs": jobs}, indent=1))
