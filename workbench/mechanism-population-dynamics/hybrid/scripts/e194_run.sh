#!/usr/bin/env bash
# E194 run for one checkpoint on one GPU (node-local). Usage: e194_run.sh KEY GPU [LIMIT]
set -eu
KEY=$1; GPU=$2; LIM=${3:-0}
B=/tmp/xiang_e194; PY="$B/env/bin/python -I"
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
OUT=$B/out/$KEY; [ "$LIM" != 0 ] && OUT=$B/out_test/$KEY
mkdir -p $OUT
cp -n $B/tok/tokenizer*.json $B/tok/special_tokens_map.json $B/models/$KEY/ 2>/dev/null || true
$PY $B/e194_capture.py nll $B/models/$KEY $B/passages.json $OUT
$PY $B/e194_capture.py S $B/models/$KEY $B/work/items.json $OUT --limit $LIM
$PY $B/e194_capture.py N $B/models/$KEY $B/work/items.json $OUT --limit $LIM
case $KEY in H|T) $PY $B/e194_patch.py $B/models/$KEY $B/tok $B/work/items.json $OUT --limit $LIM ;; esac
echo "E194_DONE $KEY $(date +%T)"
