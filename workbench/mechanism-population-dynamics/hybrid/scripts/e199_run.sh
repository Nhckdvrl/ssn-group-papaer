#!/usr/bin/env bash
# E199 run for one Ring/Ling model on one GPU (env: transformers 4.57.6 + fla; remote code read beforehand).
# Usage: e199_run.sh MODEL_DIR OUT GPU
set -eu
M=$1; OUT=$2; GPU=$3
I=/tmp/xiang_hyb/work_RL/items.json
PY="/tmp/xiang_e199/env/bin/python -I"
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p $OUT
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e195_capture.py /tmp/xiang_e194/e199_capture.py
until grep -q DL_DONE /tmp/xiang_hyb/dl_$(basename $M).log; do sleep 30; done
$PY /tmp/xiang_e194/e199_capture.py nll $M $I $OUT --passages /tmp/xiang_e194/passages.json --trust
$PY /tmp/xiang_e194/e199_capture.py S $M $I $OUT --trust
echo "E199_DONE $OUT $(date +%T)"
