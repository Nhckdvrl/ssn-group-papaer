#!/usr/bin/env bash
# Like run_node.sh but with the vLLM env (~/.venvs/vllm023-cu128, vllm 0.23).
set -euo pipefail
gpu=$1; log=$2; shift 2
cd "$(dirname "$0")"
mkdir -p /tmp/xiang_lmhead/logs
export CUDA_VISIBLE_DEVICES=$gpu HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TOKENIZERS_PARALLELISM=false VLLM_CACHE_ROOT=/tmp/xiang_lmhead/vllm_cache
export PATH=~/.venvs/vllm023-cu128/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0
exec ~/.venvs/vllm023-cu128/bin/python -u "$@" > /tmp/xiang_lmhead/logs/$log.log 2>&1
