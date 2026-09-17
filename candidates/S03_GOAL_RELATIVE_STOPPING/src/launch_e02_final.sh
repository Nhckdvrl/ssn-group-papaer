#!/bin/bash
# S03 / E02 — the four arms at their selected learning rates.
#
# Everything except the parameter freedom is shared: base checkpoint, corpus,
# example order, format, sequence length, step count, and batch size.
set -u
cd "$(dirname "$0")/.."
PY=/home/xiang/s03_venv/bin/python
export HF_HUB_OFFLINE=1
STEPS=${STEPS:-800}
SEED=${SEED:-0}

: "${LR_R:?}" "${LR_RMLP:?}" "${LR_S:?}" "${LR_F:?}"

run () { # arm lr gpu extra...
  local arm=$1 lr=$2 gpu=$3; shift 3
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
      --steps $STEPS --seed $SEED "$@" --tag "final/${arm}_s${SEED}" \
      > "results/logs/final_${arm}_s${SEED}.log" 2>&1
}

run R    "$LR_R"    0 &
run Rmlp "$LR_RMLP" 1 &
run S    "$LR_S"    2 --opt8bit &
run F    "$LR_F"    3 --opt8bit &
wait
echo "final arms done"
