#!/bin/bash
# S03 / E02 — run the E01 instrument on every trained arm.
set -u
cd "$(dirname "$0")/.."
PY=/home/xiang/s03_venv/bin/python
export HF_HUB_OFFLINE=1
SEED=${SEED:-0}
i=0
for arm in R Rmlp S F; do
  d="results/e02/final/${arm}_s${SEED}"
  [ -d "$d" ] || { echo "missing $d"; continue; }
  CUDA_VISIBLE_DEVICES=$i $PY src/e02_eval.py --outdir "$d" \
      > "results/logs/eval_${arm}_s${SEED}.log" 2>&1 &
  i=$((i+1))
done
wait
echo "arm evals done"
