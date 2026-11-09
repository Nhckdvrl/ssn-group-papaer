#!/bin/bash
# E182 job: capture for one model on one GPU. Usage: e182_job.sh MODEL GPU OUTDIR [extra capture args]
set -e
M=$1; G=$2; OUT=$3; shift 3
cd "$(dirname "$0")/.."
PY=~/.venvs/mechpop/bin/python
echo "[$(date +%T)] start $M on $(hostname):$G -> $OUT"
CUDA_VISIBLE_DEVICES=$G $PY scripts/e182_capture.py --model $M --out $OUT "$@"
echo "[$(date +%T)] job done $M"
