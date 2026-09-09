# L12 Reproduction Environment

- Host audit date: 2026-09-09
- GPUs: 4 x NVIDIA RTX PRO 6000 Blackwell Max-Q, 97,887 MiB each
- Python: `/home/xiang/miniconda3/envs/verl-clean/bin/python`
- Core packages: PyTorch 2.8.0, Transformers 4.57.6, Datasets 4.8.5, vLLM 0.11.0, NumPy 1.26.4, SciPy 1.17.1, pandas 3.0.3, scikit-learn 1.8.0

Checkpoint revisions and prompt hashes are embedded in raw outputs. The common-base relationship is taken from the official OLMo 3 model cards, not the contradictory sentence in the ACL paper appendix.
Prompt-activation arrays (`results/**/*.npz`) are regenerable local artifacts and are intentionally excluded from Git; probe summaries and compact raw generations are tracked.

## Commands

Run from the L12 directory:

```bash
scripts/run_parent_audit.sh
scripts/run_behavior.sh
CUDA_VISIBLE_DEVICES=2 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/score_reasoning_prefix.py --device cuda:0
CUDA_VISIBLE_DEVICES=2 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/score_calculation_intervention.py --device cuda:0
```

`run_behavior.sh` needs three free GPUs. The archived invalid runs are documented in `results/pilot_seed29/INVALID_RUNS.md` and are not reproduced by the formal pipeline.
