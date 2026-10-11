"""Readout factorial for the base-checkpoint model families."""
import json
MODELS = {"olmo3_7b_base": "allenai/Olmo-3-1025-7B",
          "mistral_7b_v03": "mistralai/Mistral-7B-v0.3"}
CELLS = {"mmlu_rank": (1000, 8), "mmlu_gen_letter": (1000, 32),
         "mmlu_gen_cot": (400, 16), "gsm8k_gen_cot": (500, 16),
         "gsm8k_gen_direct": (500, 32), "squad_gen": (1000, 16)}
print(json.dumps({"jobs": [
    {"model": mp, "cell": c, "mask": mk, "mask_seed": 0, "n": n, "bs": bs,
     "out": f"results/e01/{k}/{c}__{mk}.jsonl"}
    for k, mp in MODELS.items() for c, (n, bs) in CELLS.items()
    for mk in ("full", "first", "last")]}, indent=1))
