#!/bin/bash
# L36 E00 Gate C.3 — substrate-blind capability screen: greedy only, newstest2018 (a different
# year from the frozen newstest2019 substrate), first 300 segments, no beam sweep.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
mkdir -p results/e00/screen results/logs
MODELS=("meta-llama/Llama-3.1-8B-Instruct:llama31-8b:0" \
        "Qwen/Qwen2.5-7B-Instruct:qwen25-7b:1" \
        "Qwen/Qwen2.5-14B-Instruct:qwen25-14b:2" \
        "google/gemma-3-12b-it:gemma3-12b:3")
for spec in "${MODELS[@]}"; do
  IFS=':' read -r MODEL TAG GPU <<< "$spec"
  out="results/e00/screen/${TAG}_newstest2018_greedy.jsonl"
  [ -s "$out" ] && { echo "[skip] $out"; continue; }
  echo "[gpu$GPU] screening $MODEL"
  CUDA_VISIBLE_DEVICES="$GPU" $PY src/run_llm_mt.py --model "$MODEL" \
    --src data/newstest2018.en --out "$out" --beam 1 --semantics RAW \
    --max-new-tokens 256 --limit 300 > "results/logs/e00_gateC_${TAG}.log" 2>&1 &
done
wait
echo "GATE C SCREEN DONE"
