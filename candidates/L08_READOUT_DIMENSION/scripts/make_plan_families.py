"""Readout factorial for the additional model families (breadth for C1)."""
import json
MODELS = {"olmo3_7b_instruct": "allenai/Olmo-3-7B-Instruct-DPO",
          "phi4_mini_instruct": "microsoft/Phi-4-mini-instruct"}
CELLS = {"mmlu_rank": (1000, 8), "mmlu_gen_letter": (1000, 32),
         "mmlu_gen_cot": (400, 16), "gsm8k_gen_cot": (500, 16),
         "gsm8k_gen_direct": (500, 32), "squad_gen": (1000, 16)}
jobs = [{"model": mp, "cell": c, "mask": mk, "mask_seed": 0, "n": n, "bs": bs,
         "out": f"results/e01/{k}/{c}__{mk}.jsonl"}
        for k, mp in MODELS.items() for c, (n, bs) in CELLS.items()
        for mk in ("full", "first", "last")]
print(json.dumps({"jobs": jobs}, indent=1))
