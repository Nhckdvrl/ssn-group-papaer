#!/bin/bash
# S03 / E02c — pin down the "beyond the stop readout" component.
#
# The budget ladder so far compared R (stop readout only) against F (everything).
# F's advantage could come from either the non-stop output rows or the internal
# computation, so it does not by itself identify an internal-state component.
# Two arms separate them, at the same rungs as the R/F ladder:
#
#   S      everything except the stop row  (body AND non-stop output rows move)
#   Sbody  strict state-only: the ENTIRE output head is frozen, only the
#          transformer body and input embeddings move
#
# If Sbody shows the same growing residual as F, the component is genuinely
# internal computation and not output-row reshaping.
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SEED=${SEED:-0}

run () { # arm steps gpu
  local arm=$1 st=$2 gpu=$3
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr 2e-5 \
      --steps "$st" --seed $SEED --bs 4 --accum 4 --n-train 12000 --n-val 400 \
      --opt8bit --eval-after --tag "budget/${arm}_st${st}_s${SEED}" \
      > "results/logs/budget_${arm}_st${st}_s${SEED}.log" 2>&1
}

run S     250  0 & run S     2250 1 & run Sbody 250  2 & run Sbody 2250 3 & wait
run Sbody 750  0 &
wait
echo "state ladder done"
