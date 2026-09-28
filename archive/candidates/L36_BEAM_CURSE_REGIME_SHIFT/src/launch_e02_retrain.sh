#!/bin/bash
# Retrain the E02 conditions keeping the final weights, so the boundary-specificity audit can run.
# Identical recipe, seed and data to the reported E02 run; behavioural cells are skipped because
# the audit needs the weights, not another beam sweep.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
mkdir -p results/e02/weights results/logs
run () {
  local COND=$1 GPU=$2
  local dir="results/e02/weights/$COND"
  [ -s "$dir/config.json" ] && { echo "[skip] $COND"; return; }
  echo "[gpu$GPU] retrain $COND $(date +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=$GPU $PY src/e02_train.py --condition "$COND" \
    --epochs 3 --batch 8 --accum 1 --lr 1e-5 --eval-every 200 --eval-n 100 \
    --behaviour-at none --save-final "$dir" \
    --out "results/e02/retrain_${COND}.jsonl" > "results/logs/e02_retrain_${COND}.log" 2>&1
  echo "[gpu$GPU] done $COND rc=$? $(date +%H:%M:%S)"
}
run A_ONLY 0 &
run B_ONLY 1 &
run MIXED 2 &
wait
echo "RETRAIN DONE"
