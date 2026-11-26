#!/usr/bin/env bash
# Run a script from this directory on a compute node: run_node.sh <gpu> <logname> <script.py> [args...]
# Logs go to node-local /tmp/xiang_lmhead/logs; Python env = ~/.venvs/ices-tf457 (torch 2.8 / transformers 4.57.6).
set -euo pipefail
gpu=$1; log=$2; shift 2
cd "$(dirname "$0")"
mkdir -p /tmp/xiang_lmhead/logs
export CUDA_VISIBLE_DEVICES=$gpu HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
exec ~/.venvs/ices-tf457/bin/python -u "$@" > /tmp/xiang_lmhead/logs/$log.log 2>&1
