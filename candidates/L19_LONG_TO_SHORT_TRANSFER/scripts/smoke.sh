#!/usr/bin/env bash
# Throughput / memory smoke: 200 examples per arm, no science read from it.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs results/smoke
for cond in SHORT-SUPPORT LONG-FULL; do
  .venv/bin/torchrun --nproc_per_node=${GPUS:-4} --master_port=29519 \
    scripts/train_sft.py --condition $cond --seed 1 --out results/smoke/$cond \
    --n_nq 100 --n_uc 100 2>&1 | tee logs/smoke_$cond.log
done
