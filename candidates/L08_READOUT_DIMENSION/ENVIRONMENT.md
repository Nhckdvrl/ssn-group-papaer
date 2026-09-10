# L08 — Reproduction Environment

- Host: `fvcrc21`, audited 2026-09-10.
- GPUs: 4 x NVIDIA RTX PRO 6000 Blackwell Max-Q, 97,887 MiB each, all idle at project start.
- Python: `/home/xiang/miniconda3/envs/verl-clean/bin/python` (the existing shared
  environment; no new environment was created, no package was installed or upgraded).
- Core packages: PyTorch 2.8.0+cu128, Transformers 4.57.6, Datasets 4.8.5,
  NumPy 1.26.4, scikit-learn 1.8.0.
- Precision: bf16 for the 7B/8B evaluation runs; fp32 for the intervention
  correctness audit (E00), where numerical identity is the point.
- Decoding: greedy everywhere; token budgets are fixed per cell and identical across
  masks, so no condition gets more test-time compute than another.

## Models

Reused from the local Hugging Face cache; no weights are committed.

| key | checkpoint | note |
|---|---|---|
| `llama31_8b_instruct` | `NousResearch/Meta-Llama-3.1-8B-Instruct` | the `meta-llama/` cache entry contains only LICENSE/README, so the mirror is used |
| `qwen25_7b_instruct` | `Qwen/Qwen2.5-7B-Instruct` | |
| `llama31_8b` (E01b) | `meta-llama/Llama-3.1-8B` | base, matches the parent; downloading |
| `qwen25_7b` (E01b) | `Qwen/Qwen2.5-7B` | base, matches the parent; downloading |

## Data

All from the local cache, offline (`HF_DATASETS_OFFLINE=1`, `HF_HUB_OFFLINE=1`):

| dataset | split used | size |
|---|---|---|
| `cais/mmlu` (`all`) | `test`, 5-shot prompts from `dev` | 14,042 |
| `openai/gsm8k` (`main`) | `test`, 5-shot prompts from `train` | 1,319 |
| `rajpurkar/squad_v2` | `validation` | 11,873 (5,945 unanswerable) |

Item subsets are drawn by a fixed shuffle with `data_seed=1234` and are identical
across models and masks, so every condition sees exactly the same items.

## Commands

Run from this directory. `PY=/home/xiang/miniconda3/envs/verl-clean/bin/python`

### Audits (run these first; every later claim is an intervention claim)
```bash
$PY scripts/validate_intervention.py       # readout hook == W_U[:,S] h[S], reversible
CUDA_VISIBLE_DEVICES=0 $PY scripts/validate_rank_scoring.py   # batched rank scorer
$PY scripts/validate_bias_hook.py          # logit-bias identities (E03b machinery)
$PY scripts/validate_interventions.py      # prune/quant bite and restore exactly
```

### E01 + E02 — the factorial, readout truncation
```bash
$PY scripts/make_plan.py           > configs/plan_e01.json
$PY scripts/make_plan_rank.py      > configs/plan_rank.json
$PY scripts/make_plan_families.py  > configs/plan_families.json    # extra model families
$PY scripts/make_plan_families2.py > configs/plan_families2.json
$PY scripts/launch.py --plan configs/plan_e01.json --gpus 0,1,2,3
$PY scripts/summarize.py                   # per-condition table
$PY scripts/analyze_e02.py                 # pre-registered contrasts, paired bootstrap
```

### E03-E09 — the mechanism hunt
```bash
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e03a_perturbation.py --model <ckpt> --mask first \
    --n-prompts 96 --max-pos 24 --out results/e03/perturbation_<tag>.json \
    --bias-out results/e03/bias_<tag>.pt
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e03b_bias.py  --model <ckpt> --tag <tag> --mask first
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e04_candidate_set.py --model <ckpt> --mask first \
    --out results/e04/<tag>.json
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e05_decoding.py --model <ckpt> --tag <tag> --also-full
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e06_margin_law.py --model <ckpt> --mask first \
    --out results/e06/<tag>.json
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e08_emission.py --model <ckpt> --tag <tag> --mask first
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e09_token_class.py --model <ckpt> --mask first \
    --out results/e09/<tag>.json
$PY scripts/summarize_e03b.py
$PY scripts/summarize_e05.py
$PY scripts/summarize_e08.py
$PY scripts/analyze_degeneration.py
$PY scripts/analyze_arithmetic.py
```

### E10 — the same factorial under other compression families
```bash
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e10_families.py --model <ckpt> --tag <tag> \
    --family prune --level 0.4
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_e10_families.py --model <ckpt> --tag <tag> \
    --family quant --level 4
$PY scripts/analyze_e10.py
$PY scripts/analyze_selectivity.py         # uncontrolled vs controlled, with CIs
```

### The paper's tables
```bash
$PY scripts/make_paper_tables.py
```

`scripts/launch.py` shards a plan by model and loads each checkpoint once per GPU
worker; it skips outputs that already exist, so it is safe to re-run. Raw per-item
outputs go to `results/<experiment>/<model>/<cell>__<condition>.jsonl` with a header
line recording model, cell, mask mode, kept-dimension count, a hash of the exact
boolean mask, item count and data seed.

## Artifact policy

Raw generation files under `results/e01/` are compact JSONL (per-item text plus gold)
and are tracked, since every reported number must be recomputable from them. Model
weights, HF caches and `results/_logs/`, `results/_shards/` scratch are not committed.
