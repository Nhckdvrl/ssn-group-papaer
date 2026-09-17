#!/bin/bash
# S03 / E02 — per-arm learning-rate selection.
#
# LR is chosen PER ARM by held-out cross-entropy on ordinary instruction data.
# It is never chosen by the E01 goal effect: that would be outcome shopping.
# Arms differ by six orders of magnitude in trainable-parameter count, so a
# single shared LR would handicap the constrained arms and manufacture exactly
# the result we are testing for.
set -u
cd "$(dirname "$0")/.."
PY=/home/xiang/s03_venv/bin/python
export HF_HUB_OFFLINE=1
STEPS=${STEPS:-150}
mkdir -p results/logs/lrsweep

run () { # arm lr gpu extra...
  local arm=$1 lr=$2 gpu=$3; shift 3
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
      --steps $STEPS --n-train 4000 --n-val 200 "$@" \
      --tag "lrsweep/${arm}_lr${lr}" > "results/logs/lrsweep/${arm}_lr${lr}.log" 2>&1
}

case "${1:-}" in
  R)    run R 1e-3 0 & run R 1e-2 1 & run R 3e-2 2 & run R 1e-1 3 & wait ;;
  Rmlp) run Rmlp 1e-4 0 & run Rmlp 3e-4 1 & run Rmlp 1e-3 2 & run Rmlp 3e-3 3 & wait ;;
  S)    run S 5e-6 0 --opt8bit & run S 1e-5 1 --opt8bit & \
        run S 2e-5 2 --opt8bit & run S 5e-5 3 --opt8bit & wait ;;
  F)    run F 5e-6 0 --opt8bit & run F 1e-5 1 --opt8bit & \
        run F 2e-5 2 --opt8bit & run F 5e-5 3 --opt8bit & wait ;;
  *) echo "usage: $0 {R|Rmlp|S|F}"; exit 1 ;;
esac
echo "sweep ${1} done"
