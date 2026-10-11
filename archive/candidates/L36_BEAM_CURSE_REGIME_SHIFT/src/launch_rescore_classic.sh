#!/bin/bash
# Re-run the classic RAW cells with generate-time transition scores. The earlier cells' text is
# unaffected, but their `sum_logprob` came from a teacher-forced full forward, which disagrees with
# FSMT's incremental decoding path in transformers 4.57.6 by tens of nats.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
GPU=${1:-2}
mkdir -p results/ext/scored results/logs
for BEAM in 1 4 8 16 32 64; do
  out="results/ext/scored/fsmt_b${BEAM}_RAW.jsonl"
  [ -s "$out" ] && { echo "[skip] $out"; continue; }
  echo "[gpu$GPU] rescoring-run fsmt beam=$BEAM"
  CUDA_VISIBLE_DEVICES=$GPU $PY src/run_beam_sweep.py --model facebook/wmt19-en-de \
    --src data/newstest2019.en --out "$out" --beam "$BEAM" --semantics RAW \
    --max-new-tokens 256 --beam-budget 32 --score-mode generate \
    > "results/logs/ext_scored_fsmt_b${BEAM}.log" 2>&1
done
echo "RESCORE DONE"
