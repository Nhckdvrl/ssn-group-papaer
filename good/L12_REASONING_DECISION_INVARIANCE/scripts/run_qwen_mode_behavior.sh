#!/usr/bin/env bash
set -euo pipefail

PYTHON=/home/xiang/miniconda3/envs/verl-clean/bin/python
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

CUDA_VISIBLE_DEVICES="${GPU:-3}" "$PYTHON" "$ROOT/scripts/run_qwen_mode_behavior.py"
"$PYTHON" "$ROOT/scripts/summarize_qwen_mode_behavior.py"
