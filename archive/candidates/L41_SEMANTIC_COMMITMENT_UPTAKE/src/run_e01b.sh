#!/usr/bin/env bash
# E01-B critical confirmation: 4 Latin-square assignments x 3 training-order seeds.
# Every hyper-parameter here MUST come from frozen/FREEZE.md. Nothing in this
# script may be edited after the first critical result is inspected.
set -euo pipefail
cd "$(dirname "$0")/.."
source frozen/FREEZE.env          # LR, N_DOCS, EPOCHS, BS, MICRO_BS, GEN_RATIO, SCHED
TORCHRUN=/home/xiang/miniconda3/envs/verl-clean/bin/torchrun
mkdir -p results/e01b results/logs
for L in 0 1 2 3; do
  for S in 0 1 2; do
    OUT=results/e01b/L${L}_s${S}.json
    [ -f "$OUT" ] && { echo "skip $OUT"; continue; }
    echo "=== Latin square L${L} seed ${S} ==="
    $TORCHRUN --nproc_per_node=4 --master_port=$((29700 + L*10 + S)) src/train_eval.py \
      --pools crit:256,pilot:64 --holdout_pool hold --n_holdout 64 \
      --assign frozen/assign/critical_L${L}.json \
      --n_docs "$N_DOCS" --epochs "$EPOCHS" --bs "$BS" --micro_bs "$MICRO_BS" \
      --lr "$LR" --sched "$SCHED" --generic_ratio "$GEN_RATIO" --seed "$S" \
      --before results/e01b/cache_before.json \
      --out "$OUT" > results/logs/e01b_L${L}_s${S}.log 2>&1
  done
done
echo "E01-B complete"
