#!/usr/bin/env bash
set -euo pipefail

PYTHON=/home/xiang/miniconda3/envs/verl-clean/bin/python
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

CUDA_VISIBLE_DEVICES="${GPU:-3}" "$PYTHON" "$ROOT/scripts/run_breadth_state_substitution.py" --device cuda:0
"$PYTHON" "$ROOT/scripts/summarize_breadth_state.py"
