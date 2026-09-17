#!/bin/bash
# S03 / E02 — per-arm learning-rate selection.
#
# LR is chosen PER ARM by held-out cross-entropy on ordinary instruction data.
# It is never chosen by the E01 goal effect: that would be outcome shopping.
# Arms differ by four orders of magnitude in trainable-parameter count, so a
# single shared LR would handicap the constrained arms and manufacture the
# result we are testing for.
set -u
cd "$(dirname "$0")/.."
PY=/home/xiang/miniconda3/envs/dlm_clean/bin/python
export HF_HUB_OFFLINE=1
STEPS=200
mkdir -p results/logs/lrsweep

run () { # arm lr gpu
  CUDA_VISIBLE_DEVICES=$3 $PY src/e02_train.py --arm $1 --lr $2 --steps $STEPS \
      --tag lrsweep/$1_lr$2 > results/logs/lrsweep/$1_lr$2.log 2>&1
}

case "${1:-all}" in
  R)    run R 3e-2 0 & run R 1e-1 1 & run R 3e-1 2 & run R 1e0 3 & wait ;;
  Rmlp) run Rmlp 1e-3 0 & run Rmlp 3e-3 1 & run Rmlp 1e-2 2 & run Rmlp 3e-2 3 & wait ;;
  S)    run S 5e-6 0 & run S 1e-5 1 & run S 2e-5 2 & run S 5e-5 3 & wait ;;
  F)    run F 5e-6 0 & run F 1e-5 1 & run F 2e-5 2 & run F 5e-5 3 & wait ;;
esac
echo "sweep $1 done"
