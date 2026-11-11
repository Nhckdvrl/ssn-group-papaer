#!/bin/bash
# E186 node-local runner (NFS stalled 11-10 00:00): local Python env (/tmp/xiang_e186/env, uv-built replica of the
# mechpop venv: torch 2.8.0+cu128, transformers 4.57.6, numpy 1.26.4), local code/data bundle, local logs.
# Usage: run_local.sh KEY GPUS [extra capture args]
KEY=$1; G=$2; shift 2
B=/tmp/xiang_e186
mkdir -p $B/logs $B/store
for g in ${G//,/ }; do
  read used util <<< $(nvidia-smi -i $g --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ',')
  if [ "$used" -gt 1000 ] || [ "$util" -gt 5 ]; then echo "[$(date +%T)] GPU $g busy ($used MiB, $util %) -- not starting $KEY" >> $B/logs/$KEY.log; exit 3; fi
done
export PYTHONNOUSERSITE=1 HF_HOME=$B/hf HF_HUB_OFFLINE=1 XDG_CACHE_HOME=$B/uv/xdg E186_DATA=$B/bundle/data TRITON_CACHE_DIR=$B/triton
echo "[$(date +%T)] start $KEY on $(hostname):$G (local env)" >> $B/logs/$KEY.log
CUDA_VISIBLE_DEVICES=$G $B/env/bin/python $B/bundle/code/e186_capture.py --model-path $B/models/$KEY --key $KEY \
  --out $B/store/$KEY "$@" >> $B/logs/$KEY.log 2>&1
echo "[$(date +%T)] capture exit $? $KEY" >> $B/logs/$KEY.log
