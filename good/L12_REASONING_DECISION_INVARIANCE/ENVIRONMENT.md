# L12 Reproduction Environment

- Host audit date: 2026-09-10
- GPUs: 4 x NVIDIA RTX PRO 6000 Blackwell Max-Q, 97,887 MiB each
- Python: `/home/xiang/miniconda3/envs/verl-clean/bin/python`
- Core packages: PyTorch 2.8.0, Transformers 4.57.6, Datasets 4.8.5, vLLM 0.11.0, NumPy 1.26.4, SciPy 1.17.1, pandas 3.0.3, scikit-learn 1.8.0
- CPC18 additions in the same environment: openpyxl 3.1.5 and statsmodels 0.15.0.
- CPC18 execution hosts: `fvcrc13` and `fvcrc15`, NVIDIA A100 80GB PCIe. Only GPUs showing no foreign compute process were used; `fvcrc13:1` was excluded because it had an existing non-L12 process.

Checkpoint revisions and prompt hashes are embedded in raw outputs. The common-base relationship is taken from the official OLMo 3 model cards, not the contradictory sentence in the ACL paper appendix.
Prompt-activation arrays (`results/**/*.npz`) are regenerable local artifacts and are intentionally excluded from Git; probe summaries and compact raw generations are tracked.
The full E10 Think-SFT trajectory file (`results/breadth_seed71/think_sft/raw.jsonl`, about 4 MB) is likewise retained locally and ignored. Its compact behavior/control summaries and all regeneration code/configs are tracked.
The full Qwen3 thinking-generation file (`results/qwen_mode_seed83/thinking.jsonl`, about 3.6 MB) is also regenerable and ignored. No checkpoint weights, caches, activation arrays, or other large binary artifacts are committed.
The full DeepSeek E14 reasoning-generation file (`results/llama_external_seed89/deepseek_r1.jsonl`, about 4.1 MB) is likewise local and ignored. The compact behavior/control summaries, control scores, and E15 state-substitution results remain traceable and tracked.
The CPC18 Zenodo raw CSV (47,488,058 bytes) and official workbook are cached under `/home/xiang/.cache/l12-cpc18`, verified against `configs/cpc18.json`, and never committed. E17 full continuations and factorial cell scores live under an ignored `results/cpc18_*/raw/` directory; the frozen PII-free corpus, parser audit, unit summaries, and model manifests are tracked.

## Commands

Run from the L12 directory:

```bash
scripts/run_parent_audit.sh
scripts/run_behavior.sh
scripts/run_breadth_behavior.sh
scripts/run_breadth_control.sh
scripts/run_breadth_state.sh
scripts/run_checkpoint_control.sh
scripts/run_qwen_mode_behavior.sh
scripts/run_qwen_mode_control.sh
scripts/run_llama_external.sh
CUDA_VISIBLE_DEVICES=2 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/run_deepseek_state_substitution.py --device cuda:0
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/summarize_deepseek_state.py
CUDA_VISIBLE_DEVICES=2 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/score_reasoning_prefix.py --device cuda:0
CUDA_VISIBLE_DEVICES=2 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/score_calculation_intervention.py --device cuda:0
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/audit_cpc18.py --problems /home/xiang/.cache/l12-cpc18/calibration_problems.xlsx --raw /home/xiang/.cache/l12-cpc18/calibration_verified.csv
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/run_cpc18_behavior_vllm.py --regime olmo_think_sft
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/reparse_cpc18_behavior.py
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/summarize_cpc18_behavior.py
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/run_cpc18_control.py --regime olmo_think_sft --device cuda:0
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/summarize_cpc18_control.py
```

`run_behavior.sh` needs three free GPUs. The archived invalid runs are documented in `results/pilot_seed29/INVALID_RUNS.md` and are not reproduced by the formal pipeline.

E10 Think-SFT, E13 Qwen, and E14 Llama-ecosystem behavior generation use vLLM for batched sampling; backends and exact revisions are recorded in model manifests. Hugging Face model caches and vLLM compilation caches are outside the repository. E12 and E15 use exact cached safetensors revisions listed in `AUDIT.md`.
