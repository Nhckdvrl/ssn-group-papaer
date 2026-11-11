#!/bin/bash
# E186 node-side runner: refuse to start unless every requested GPU is idle, then capture to node-local disk.
# Usage: e186_run.sh KEY GPUS [extra capture args]      (model weights at /tmp/xiang_e186/models/KEY)
KEY=$1; G=$2; shift 2
cd "$(dirname "$0")/.."
for g in ${G//,/ }; do
  read used util <<< $(nvidia-smi -i $g --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ',')
  if [ "$used" -gt 1000 ] || [ "$util" -gt 5 ]; then echo "[$(date +%T)] GPU $g busy ($used MiB, $util %) -- not starting $KEY"; exit 3; fi
done
mkdir -p /tmp/xiang_e186/store
scripts/e186_job.sh $KEY $G /tmp/xiang_e186/models/$KEY /tmp/xiang_e186/store/$KEY "$@" > results/e186/_logs/$KEY.log 2>&1
echo "[$(date +%T)] capture exit $? $KEY"
