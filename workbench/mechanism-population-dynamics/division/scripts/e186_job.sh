#!/bin/bash
# E186 job: one capture. Usage: e186_job.sh KEY GPUS MODEL_PATH OUTDIR [extra capture args]
#   GPUS = comma list for CUDA_VISIBLE_DEVICES (2 cards for phimoe / mixtral). Log: results/e186/_logs/<KEY>.log
set -e
KEY=$1; G=$2; MP=$3; OUT=$4; shift 4
cd "$(dirname "$0")/.."
PY=~/.venvs/mechpop/bin/python
echo "[$(date +%T)] start $KEY on $(hostname):$G <- $MP -> $OUT"
CUDA_VISIBLE_DEVICES=$G HF_HUB_OFFLINE=1 $PY scripts/e186_capture.py --model-path $MP --key $KEY --out $OUT "$@"
# small files to NFS right away (report reads them); the raw arrays are copied later (NFS is slow while downloads run)
mkdir -p $HOME/mechpop_cache/e186/$KEY && cp $OUT/meta.json $OUT/diag.npz $HOME/mechpop_cache/e186/$KEY/
echo "[$(date +%T)] job done $KEY"
