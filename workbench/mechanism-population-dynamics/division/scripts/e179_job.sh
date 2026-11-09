#!/bin/bash
# E179 job: capture then geometry for one model on one GPU. Usage: e179_job.sh MODEL GPU [extra capture args]
set -e
M=$1; G=$2; shift 2
cd "$(dirname "$0")/.."
PY=~/.venvs/mechpop/bin/python
OUT=/home/xiang/mechpop_cache/e179/$M
echo "[$(date +%T)] start $M on $(hostname):$G"
CUDA_VISIBLE_DEVICES=$G $PY scripts/e179_capture.py --model $M --out $OUT "$@"
echo "[$(date +%T)] capture done; geometry"
CUDA_VISIBLE_DEVICES=$G $PY scripts/e179_geometry.py $OUT
echo "[$(date +%T)] job done $M"
