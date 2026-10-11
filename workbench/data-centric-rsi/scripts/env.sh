#!/usr/bin/env bash
# E00 local adaptation. Source before running scripts; pin the checkout below.
export DATAENVGYM_ROOT="${DATAENVGYM_ROOT:-/home/xiang/.cache/research/data-centric-rsi/DataEnvGym}"
export DATA_RSI_PYTHON="${DATA_RSI_PYTHON:-/home/xiang/.venvs/data-centric-rsi/bin/python}"
export PYTHONPATH="${DATAENVGYM_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
export HF_HUB_OFFLINE=1
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export OMP_NUM_THREADS=8
