#!/bin/bash
# Out-of-sample test of the rank-onset law (results/stages/RANK_ONSET_PREDICTION.md):
# Olmo-3 base under the few-shot interface has median stop-rank 532, so b* = 266.
# Predicted: clean at beam 64 and 128, collapsing by beam 512.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
mkdir -p results/stages results/logs
run () {
  local BEAMS=$1 GPU=$2 TAG=$3
  local out="results/stages/${TAG}_fewshot_onset_b${BEAMS}.json"
  [ -s "$out" ] && { echo "[skip] $out"; return; }
  CUDA_VISIBLE_DEVICES=$GPU $PY src/stage_probe.py --model allenai/Olmo-3-1025-7B \
    --tag "${TAG}_onset_b${BEAMS}" --stage base --interface fewshot \
    --n-margin 8 --n-beam 200 --beams "$BEAMS" --beam-budget 256 \
    > "results/logs/onset_${TAG}_b${BEAMS}.log" 2>&1
  echo "[gpu$GPU] done onset beam $BEAMS"
}
run 128 "${1:-0}" olmo3-base &
run 256 "${2:-1}" olmo3-base &
wait
run 512 "${1:-0}" olmo3-base
echo "ONSET SWEEP DONE"
