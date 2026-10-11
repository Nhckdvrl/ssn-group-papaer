#!/usr/bin/env bash
# Frozen E08 full-dev action evaluation. Invoke from the repository root.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo 'usage: e08_eval.sh RUN GPU_INDEX' >&2
  exit 2
fi
run="$1"
gpu_index="$2"
asset_root=/home/xiang/.cache/research/data-centric-rsi
output_dir="$asset_root/runs/e08"

case "$run" in
  base|base_repeat1) adapter= ;;
  static_seed17) adapter="$asset_root/runs/e00/static_seed17_retry1/adapter" ;;
  static_seed29|static_seed43) adapter="$asset_root/runs/e00/$run/adapter" ;;
  retrieval_seed17|retrieval_seed29|retrieval_seed43) adapter="$asset_root/runs/e04/$run/adapter" ;;
  matched_seed17) adapter="$asset_root/runs/e05/$run/adapter" ;;
  *) echo "unknown E08 run: $run" >&2; exit 2 ;;
esac

mkdir -p "$output_dir"
output="$output_dir/${run}_zero_format_dev1740.jsonl"
log="$output_dir/${run}_zero_format_dev1740.log"
if [[ -e "$output" || -e "$log" ]]; then
  echo "refusing to overwrite E08 assets: $run" >&2
  exit 2
fi

source workbench/data-centric-rsi/scripts/env.sh
export VLLM_ENABLE_V1_MULTIPROCESSING=0
export CUDA_VISIBLE_DEVICES="$gpu_index"

nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv,noheader > "$log"
command=("$DATA_RSI_PYTHON" workbench/data-centric-rsi/scripts/e00_student.py evaluate
  --data "$asset_root/data/dev.jsonl" --output "$output"
  --zero-shot --format-instruction --enforce-eager)
if [[ -n "$adapter" ]]; then
  command+=(--adapter "$adapter")
fi
"${command[@]}" >> "$log" 2>&1
