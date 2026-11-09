#!/bin/bash
# E184 job: capture the three models one after another on one GPU. Usage: e184_job.sh GPU [model ...]
set -e
G=$1; shift
MODELS=${@:-"olmoe gptoss qwen3"}
cd "$(dirname "$0")/.."
PY=~/.venvs/mechpop/bin/python
for M in $MODELS; do
  echo "[$(date +%T)] start $M on $(hostname):$G"
  CUDA_VISIBLE_DEVICES=$G $PY scripts/e184_capture.py --model $M --out /home/xiang/mechpop_cache/e184/$M > results/e184/_logs/$M.log 2>&1
  echo "[$(date +%T)] done $M"
done
