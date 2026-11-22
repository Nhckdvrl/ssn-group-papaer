#!/usr/bin/env bash
# E195 run for one model on one GPU. Usage: e195_run.sh MODEL_DIR ITEMS OUT GPU "EXTRA_FLAGS"
set -eu
M=$1; I=$2; OUT=$3; GPU=$4; X=${5:-}
B=/tmp/xiang_e194; PY="$B/env/bin/python -I"
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p $OUT
$PY $B/e195_capture.py nll $M $I $OUT --passages $B/passages.json $X
$PY $B/e195_capture.py S $M $I $OUT $X
$PY $B/e195_capture.py N $M $I $OUT $X
echo "E195_DONE $OUT $(date +%T)"
