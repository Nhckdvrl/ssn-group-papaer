#!/bin/bash
# CT03 E01 launch. One card; the harness is single-GPU by construction
# (the exact side needs a deterministic replay of one model's upper stack).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
mkdir -p results/logs

{
  echo "host=$(hostname) card=$CUDA_VISIBLE_DEVICES date=$(date -Is)"
  nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader
} > results/logs/e01_assignment.log

$PY src/e01_validity.py 2>&1 | tee results/logs/e01_validity.log
$PY src/e01_credit.py "$@" 2>&1 | tee results/logs/e01_credit.log
$PY src/e01_report.py --exact dL_seq --out results/e01_report.json 2>&1 | tee results/logs/e01_report.log
$PY src/e01_report.py --exact dL_tok --out results/e01_report_tok.json 2>&1 | tee -a results/logs/e01_report.log
