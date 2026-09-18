#!/bin/bash
# S03 — per-family, per-arm LR selection for the replication families.
# OLMo's selected LRs are not assumed to transfer: a different tokenizer,
# vocabulary size and turn-end token change the loss landscape.  Chosen on
# held-out CE over ordinary instruction data only, never on the goal effect.
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FAM=$1
STEPS=${STEPS:-120}
mkdir -p results/logs/lrsweep
run () { # arm lr gpu extra
  local arm=$1 lr=$2 gpu=$3; shift 3
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
      --family "$FAM" --steps $STEPS --bs 4 --accum 4 --n-train 12000 --n-val 400 \
      "$@" --tag "lrsweep/${FAM}_${arm}_lr${lr}" \
      > "results/logs/lrsweep/${FAM}_${arm}_lr${lr}.log" 2>&1
}
run R 1e-3 0 & run R 3e-3 1 & run R 1e-2 2 & wait
run F 1e-5 0 --opt8bit & run F 2e-5 1 --opt8bit & run F 5e-5 2 --opt8bit & wait
echo "lr sweep $FAM done"
