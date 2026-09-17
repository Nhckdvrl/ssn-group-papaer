#!/bin/bash
# S03 / E02b — budget ladder on Arm R vs Arm F.
#
# This experiment distinguishes:
#   X  "readout adaptation suffices"  -- R and F rise together at every budget,
#      so the gap to the released SFT checkpoint is a data/compute effect and
#      the parameter locus is never the binding constraint;
# from
#   Y  "readout suffices only up to a budget" -- F pulls away from R once the
#      budget is large enough, so internal-state change IS load-bearing, but
#      only beyond some scale.
#
# Same corpus, order, format, geometry and LR as the main four-arm run; only
# the number of optimizer steps varies.
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SEED=${SEED:-0}

run () { # arm lr steps gpu extra...
  local arm=$1 lr=$2 st=$3 gpu=$4; shift 4
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
      --steps "$st" --seed $SEED --bs 4 --accum 4 --n-train 12000 --n-val 400 \
      "$@" --eval-after --tag "budget/${arm}_st${st}_s${SEED}" \
      > "results/logs/budget_${arm}_st${st}_s${SEED}.log" 2>&1
}

# 750 is already covered by the main run; add the rungs above and below.
run R 3e-3  250 0 &
run F 2e-5  250 1 --opt8bit &
run R 3e-3 2250 2 &
run F 2e-5 2250 3 --opt8bit &
wait
echo "budget ladder done"
