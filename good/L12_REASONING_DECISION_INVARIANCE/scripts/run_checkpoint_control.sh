#!/usr/bin/env bash
set -euo pipefail

PYTHON=/home/xiang/miniconda3/envs/verl-clean/bin/python
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export HF_HUB_ENABLE_HF_TRANSFER=1

CUDA_VISIBLE_DEVICES="${INSTRUCT_GPU:-0}" "$PYTHON" "$ROOT/scripts/run_checkpoint_control.py" --branch instruct_dpo --device cuda:0 &
INSTRUCT_PID=$!
CUDA_VISIBLE_DEVICES="${THINK_GPU:-2}" "$PYTHON" "$ROOT/scripts/run_checkpoint_control.py" --branch think_dpo --device cuda:0 &
THINK_PID=$!

wait "$INSTRUCT_PID"
wait "$THINK_PID"
"$PYTHON" "$ROOT/scripts/summarize_checkpoint_control.py"
