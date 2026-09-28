# L13 Reproduction Environment

- Host audit date: 2026-09-11
- Python: `/home/xiang/miniconda3/envs/verl-clean/bin/python` (existing shared env; no
  new environment was created, no package was installed or upgraded)
- PyTorch 2.8.0+cu128, Transformers 4.57.6, NumPy 1.26.4
- Local GPUs: 4 × NVIDIA RTX PRO 6000 Blackwell Max-Q, 97,887 MiB each. The pilot uses
  only free local cards (GPUs 2 and 3 at audit time); GPUs 0 and 1 carried foreign
  compute and were not touched.
- Remote hosts `fvcrc10/11/12/13/15` are available if the pilot ever needs more than the
  local cards; by standing instruction, never occupy more than 8 GPUs at once and only
  cards with no foreign process.
- Models are read from the existing Hugging Face cache with `HF_HUB_OFFLINE=1`. Nothing
  was downloaded. `NousResearch/Meta-Llama-3.1-8B-Instruct` is used because the
  `meta-llama` snapshot in the local cache is metadata-only.

## Commands

Run from this directory:

```bash
scripts/build_stimuli.py            # deterministic stimulus construction
scripts/validate_stimuli.py         # structural invariants of DATA_AND_GOLD.md
scripts/run_pilot.sh qwen3_8b 2
scripts/run_pilot.sh llama31_8b_instruct 3
scripts/run_pilot.sh olmo3_7b_instruct_dpo 2
scripts/run_pilot.sh gemma3_12b_it 3
scripts/run_pilot.sh qwen3_32b 2
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/summarize_commitment.py
```

Each model run scores 200 items × 6 option permutations × 3 task orders (3,600 scored
prompts) plus 400 greedy context generations and 200 likelihood prompts. An 8B model
takes a few minutes on one card.

## Artifacts

`results/<tag>/<model_slug>/` holds `strict.jsonl` (per-item, per-permutation label
distributions), `likelihood.jsonl`, `context_turns.jsonl` (the model's own timeline and
paraphrase turns) and `manifest.json` (model id, dtype, seed, library versions,
wall-clock). `results/<tag>/summary.json` and `summary.md` are produced by the
summariser. Smoke-test outputs under `results/smoke/` are ignored by Git.
