#!/usr/bin/env bash
set -euo pipefail

PYTHON=/home/xiang/miniconda3/envs/verl-clean/bin/python
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

CUDA_VISIBLE_DEVICES="${INSTRUCT_GPU:-0}" "$PYTHON" "$ROOT/scripts/run_breadth_behavior.py" --branch instruct_sft --device cuda:0 &
INSTRUCT_PID=$!
CUDA_VISIBLE_DEVICES="${THINK_GPU:-2}" "$PYTHON" "$ROOT/scripts/run_breadth_behavior_vllm.py" &
THINK_PID=$!

wait "$INSTRUCT_PID"
wait "$THINK_PID"
"$PYTHON" "$ROOT/scripts/summarize_breadth_behavior.py"
