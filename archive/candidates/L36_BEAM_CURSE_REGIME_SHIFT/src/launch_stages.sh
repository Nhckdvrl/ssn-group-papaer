#!/bin/bash
# Stage-wise lineage probe. Usage: launch_stages.sh <lineage>
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
LINEAGE=${1:-olmo3}
mkdir -p results/stages results/logs

if [ "$LINEAGE" = "olmo3" ]; then
  SPECS=(
    "allenai/Olmo-3-1025-7B|olmo3-base|base|fewshot|0"
    "allenai/Olmo-3-7B-Instruct-SFT|olmo3-sft|sft|fewshot|1"
    "allenai/Olmo-3-7B-Instruct-DPO|olmo3-dpo|dpo|fewshot|2"
    "allenai/Olmo-3-7B-Instruct-SFT|olmo3-sft|sft|chat|3"
  )
  SPECS2=(
    "allenai/Olmo-3-7B-Instruct-DPO|olmo3-dpo|dpo|chat|0"
    "allenai/Olmo-3-7B-Instruct|olmo3-rlvr|rlvr|fewshot|1"
    "allenai/Olmo-3-7B-Instruct|olmo3-rlvr|rlvr|chat|2"
    "allenai/Olmo-3-1025-7B|olmo3-base|base|chat|3"
  )
else
  SPECS=(
    "NousResearch/Meta-Llama-3.1-8B|tulu3-base|base|fewshot|0"
    "allenai/Llama-3.1-Tulu-3-8B-SFT|tulu3-sft|sft|fewshot|1"
    "allenai/Llama-3.1-Tulu-3-8B-DPO|tulu3-dpo|dpo|fewshot|2"
    "allenai/Llama-3.1-Tulu-3-8B|tulu3-rlvr|rlvr|fewshot|3"
  )
  SPECS2=(
    "allenai/Llama-3.1-Tulu-3-8B-SFT|tulu3-sft|sft|chat|0"
    "allenai/Llama-3.1-Tulu-3-8B-DPO|tulu3-dpo|dpo|chat|1"
    "allenai/Llama-3.1-Tulu-3-8B|tulu3-rlvr|rlvr|chat|2"
    "NousResearch/Meta-Llama-3.1-8B|tulu3-base|base|chat|3"
  )
fi

run_wave () {
  local -n arr=$1
  for spec in "${arr[@]}"; do
    IFS='|' read -r MODEL TAG STAGE IFACE GPU <<< "$spec"
    out="results/stages/${TAG}_${IFACE}.json"
    [ -s "$out" ] && { echo "[skip] $out"; continue; }
    echo "[gpu$GPU] $TAG / $IFACE"
    CUDA_VISIBLE_DEVICES=$GPU $PY src/stage_probe.py --model "$MODEL" --tag "$TAG" \
      --stage "$STAGE" --interface "$IFACE" --n-margin 400 --n-beam 200 --beams 1,16,64 \
      > "results/logs/stage_${TAG}_${IFACE}.log" 2>&1 &
  done
  wait
}

run_wave SPECS
run_wave SPECS2
echo "STAGE SWEEP DONE ($LINEAGE)"
