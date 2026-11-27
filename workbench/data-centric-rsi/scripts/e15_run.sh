#!/usr/bin/env bash
# E15 node runner: one python job on one GPU with the shared vLLM 0.23 venv, vendored graders, offline HF,
# node-local caches and logs.  Usage: bash e15_run.sh <gpu> <logname> <script.py> [args...]
set -euo pipefail
gpu=$1; log=$2; shift 2
mkdir -p /tmp/xiang_e15/logs /tmp/xiang_e15/vllm_cache
export CUDA_VISIBLE_DEVICES=$gpu HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export VLLM_CACHE_ROOT=/tmp/xiang_e15/vllm_cache VLLM_USE_FLASHINFER_SAMPLER=0
export PYTHONPATH=/tmp/xiang_e15/vendor${PYTHONPATH:+:$PYTHONPATH}
cd "$(dirname "$0")"
exec ~/.venvs/vllm023-cu128/bin/python -u "$@" > /tmp/xiang_e15/logs/$log.log 2>&1
