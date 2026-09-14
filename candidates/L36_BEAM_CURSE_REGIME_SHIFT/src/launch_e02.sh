#!/bin/bash
# L36 E02 — one training condition per GPU, exactly as preregistered.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
mkdir -p results/e02 results/logs
run () {
  local COND=$1 GPU=$2
  [ -s "results/e02/${COND}.jsonl" ] && { echo "[skip] $COND"; return; }
  echo "[gpu$GPU] $COND $(date +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=$GPU $PY src/e02_train.py --condition "$COND" \
    --epochs 3 --batch 8 --accum 1 --lr 1e-5 --eval-every 50 --eval-n 200 \
    --behaviour-at 200,600,final --beams 1,16,64 --beam-n 200 \
    > "results/logs/e02_${COND}.log" 2>&1
  echo "[gpu$GPU] done $COND rc=$? $(date +%H:%M:%S)"
}
run A_ONLY 0 &
run B_ONLY 1 &
run MIXED 2 &
run A_ONLY_NOEOSLOSS 3 &
wait
echo "E02 ALL CONDITIONS DONE"
