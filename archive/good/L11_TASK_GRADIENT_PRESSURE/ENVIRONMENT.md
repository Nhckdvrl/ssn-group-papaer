# L11 Reproduction Environment

- Host audit date: 2026-09-09
- GPUs: 4 x NVIDIA RTX PRO 6000 Blackwell Max-Q, 97,887 MiB each
- Python: `/home/xiang/miniconda3/envs/verl-clean/bin/python`
- Core packages at audit: PyTorch 2.8.0, Transformers 4.57.6, Datasets 4.8.5, Accelerate 1.13.0, TRL 0.24.0, NumPy 1.26.4, SciPy 1.17.1, pandas 3.0.3, scikit-learn 1.8.0
- Parent implementation: verl; the pilot reimplements the documented estimator in a small auditable script rather than claiming bitwise reproduction of unpublished training code.

Model and dataset revisions are written into each raw result at runtime.
Per-example gradient sketch tensors (`results/**/*.pt`) are regenerable local artifacts and are intentionally excluded from Git; compact raw JSONL and statistical summaries are tracked.

## Commands

```bash
L11_CUDA_VISIBLE_DEVICES=0 L11_SEED=17 scripts/run_pilot.sh
L11_CUDA_VISIBLE_DEVICES=0 L11_SEED=18 scripts/run_pilot.sh
L11_CUDA_VISIBLE_DEVICES=0 L11_SEED=19 scripts/run_pilot.sh
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/summarize_seeds.py
```

Run these commands from the L11 directory. The separate calibration command and selection record are in `scripts/calibrate_arithmetic.py` and `results/arithmetic_calibration_seed1702/`.
