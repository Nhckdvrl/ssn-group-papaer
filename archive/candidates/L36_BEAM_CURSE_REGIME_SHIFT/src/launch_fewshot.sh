#!/bin/bash
# L36 E00-EXT — same checkpoint, different interface: few-shot plain-text prompt with the line
# break as the stop symbol, RAW beam search. Tests FEWSHOT_INTERFACE_PREDICTION.md.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
GPU=${1:-0}
MODEL=${2:-google/gemma-3-12b-it}
TAG=${3:-gemma3-12b}
mkdir -p results/ext/gen results/logs
$PY src/termination_geometry.py --model "$MODEL" --kind dec_only --tag "${TAG}-fewshot" \
    --limit 300 --prompt-style fewshot > "results/logs/ext_term_${TAG}_fewshot.log" 2>&1
for BEAM in 1 4 16 64; do
  out="results/ext/gen/${TAG}_fewshot_b${BEAM}_RAW.jsonl"
  [ -s "$out" ] && { echo "[skip] $out"; continue; }
  echo "[gpu$GPU] $TAG fewshot beam=$BEAM"
  $PY src/run_llm_mt.py --model "$MODEL" --src data/newstest2019.en --out "$out" \
    --beam "$BEAM" --semantics RAW --max-new-tokens 128 --beam-budget 256 --limit 400 \
    --prompt-style fewshot > "results/logs/ext_${TAG}_fewshot_b${BEAM}.log" 2>&1
done
echo "FEWSHOT SWEEP DONE"
