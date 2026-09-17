#!/bin/bash
# S03 / E02c — pin down the "beyond the stop readout" component.
#
# Two things are being separated here:
#   S      = everything EXCEPT the stop row may move (non-stop output rows too)
#   Sbody  = STRICT state-only: the ENTIRE output head is frozen, only the
#            transformer body and input embeddings may move
#
# If Sbody shows the same growing-with-budget residual that F does, then the
# residual is genuinely internal-computation change and not any readout change.
# If only S (which may move non-stop rows) shows it, the residual lives in the
# rest of the output head instead, which is a different claim.
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SEED=${SEED:-0}

run () { # arm lr steps gpu
  local arm=$1 lr=$2 st=$3 gpu=$4
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
      --steps "$st" --seed $SEED --bs 4 --accum 4 --n-train 12000 --n-val 400 \
      --opt8bit --eval-after --tag "budget/${arm}_st${st}_s${SEED}" \
      > "results/logs/budget_${arm}_st${st}_s${SEED}.log" 2>&1
}

# S already has its 750 rung from the main four-arm run; add 250 and 2250.
run S     2e-5  250 0 &
run S     2e-5 2250 1 &
run Sbody 2e-5  250 2 &
run Sbody 2e-5 2250 3 &
wait
# Sbody still needs its middle rung to match the ladder.
run Sbody 2e-5 750 0
echo "state ladder done"
