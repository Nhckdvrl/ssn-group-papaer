#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-/home/xiang/miniconda3/envs/verl-clean/bin/python}"

cd "$ROOT"
CUDA_VISIBLE_DEVICES="${LLAMA_GPU:-0}" "$PYTHON" scripts/run_llama_external_behavior.py --branch llama_instruct
CUDA_VISIBLE_DEVICES="${DEEPSEEK_GPU:-2}" "$PYTHON" scripts/run_llama_external_behavior.py --branch deepseek_r1
"$PYTHON" scripts/summarize_llama_external_behavior.py
CUDA_VISIBLE_DEVICES="${LLAMA_GPU:-0}" "$PYTHON" scripts/run_llama_external_control.py --branch llama_instruct
CUDA_VISIBLE_DEVICES="${DEEPSEEK_GPU:-2}" "$PYTHON" scripts/run_llama_external_control.py --branch deepseek_r1
"$PYTHON" scripts/summarize_llama_external_control.py
