# L15 Reproduction Environment

- Host audit date: 2026-09-11
- Python: `/home/xiang/miniconda3/envs/verl-clean/bin/python` (existing shared env; no
  environment was created and no package was installed or upgraded)
- PyTorch 2.8.0+cu128, vLLM 0.11.0, Transformers 4.57.6, NumPy 1.26.4
- Local GPUs: 4 × NVIDIA RTX PRO 6000 Blackwell, 97,887 MiB each. At audit time all four
  were free of foreign compute; the pilot uses two of them (one per model). By standing
  instruction, never occupy more than 8 GPUs and only cards with no foreign process.
- Models are read from the existing Hugging Face cache with `HF_HUB_OFFLINE=1`. Nothing
  was downloaded.
- Decoding is greedy (`temperature=0`, `top_p=1`, `seed=0`).

## Commands

Run from this directory:

```bash
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
$PY scripts/build_stimuli.py
$PY scripts/validate_stimuli.py
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 $PY scripts/run_probes.py --model qwen3_32b --tag pilot_v1
CUDA_VISIBLE_DEVICES=1 HF_HUB_OFFLINE=1 $PY scripts/run_probes.py --model mistral_small_24b --tag pilot_v1
$PY scripts/summarize.py --tag pilot_v1 --model qwen3_32b
$PY scripts/summarize.py --tag pilot_v1 --model mistral_small_24b
```

## Artifacts

`results/<tag>/<model_slug>/` holds `raw.jsonl` (one row per prompt cell with the full
generation), `scored.jsonl` (parsed answer, validity, error), `summary.json`,
`summary.md` and `manifest.json` (model id, decoding, library versions, wall clock).
`results/smoke/` is a runner check only and carries no claim.
