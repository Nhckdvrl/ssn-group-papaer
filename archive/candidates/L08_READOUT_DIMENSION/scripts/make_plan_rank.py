"""Re-plan only the ranking cells (they OOMed on the first pass; run_rank fixed)."""
import json
MODELS = {"llama31_8b_instruct": "NousResearch/Meta-Llama-3.1-8B-Instruct",
          "qwen25_7b_instruct": "Qwen/Qwen2.5-7B-Instruct"}
jobs = [{"model": mp, "cell": "mmlu_rank", "mask": mk, "mask_seed": 0,
         "n": 1000, "bs": 8,
         "out": f"results/e01/{mk_}/mmlu_rank__{mk}.jsonl"}
        for mk_, mp in MODELS.items() for mk in ("full", "first", "last")]
print(json.dumps({"jobs": jobs}, indent=1))
