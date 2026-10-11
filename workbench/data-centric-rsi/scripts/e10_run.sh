#!/usr/bin/env bash
# Fixed E10 A100 evaluation and nested static training commands.
# Invoke from the repository root; never modify this file while a run uses it.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo 'usage: e10_run.sh {base|static120|train960|static960} GPU_INDEX' >&2
  exit 2
fi
mode="$1"
gpu_index="$2"
asset_root=/home/xiang/.cache/research/data-centric-rsi
run_root="$asset_root/runs/e10"
data_root="$asset_root/data"
mkdir -p "$run_root"
source workbench/data-centric-rsi/scripts/env.sh
export CUDA_VISIBLE_DEVICES="$gpu_index"
export VLLM_ENABLE_V1_MULTIPROCESSING=0

if [[ "$mode" == train960 ]]; then
  output="$run_root/train960_seed17"
  log="$run_root/train960_seed17.log"
  if [[ -e "$output" || -e "$log" ]]; then
    echo 'refusing to overwrite E10 training assets' >&2
    exit 2
  fi
  nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv,noheader > "$log"
  "$DATA_RSI_PYTHON" workbench/data-centric-rsi/scripts/e00_student.py train \
    --data "$data_root/static_960_e10.jsonl" --output "$output" --seed 17 >> "$log" 2>&1
  exit 0
fi

output="$run_root/${mode}_zero_format_dev1740.jsonl"
log="$run_root/${mode}_zero_format_dev1740.log"
if [[ -e "$output" || -e "$log" ]]; then
  echo "refusing to overwrite E10 evaluation assets: $mode" >&2
  exit 2
fi
case "$mode" in
  base) adapter= ;;
  static120) adapter="$asset_root/runs/e00/static_seed17_retry1/adapter" ;;
  static960) adapter="$run_root/train960_seed17/adapter" ;;
  *) echo "unknown E10 mode: $mode" >&2; exit 2 ;;
esac
if [[ -n "$adapter" && ! -d "$adapter" ]]; then
  echo "missing E10 adapter: $adapter" >&2
  exit 2
fi
nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv,noheader > "$log"
command=("$DATA_RSI_PYTHON" workbench/data-centric-rsi/scripts/e00_student.py evaluate
  --data "$data_root/dev.jsonl" --output "$output"
  --zero-shot --format-instruction --enforce-eager)
if [[ -n "$adapter" ]]; then
  command+=(--adapter "$adapter")
fi
"${command[@]}" >> "$log" 2>&1
