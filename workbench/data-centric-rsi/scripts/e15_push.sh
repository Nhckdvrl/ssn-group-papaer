#!/usr/bin/env bash
# E15: wait until a model's download log says DONE (sha256-verified), copy it over the LAN to the GPU node,
# then mark it ready there.  Usage: bash e15_push.sh <log name> <model dir name> <dest host|local>
set -u
log=$1; model=$2; dest=$3
until grep -q '^DONE' /tmp/xiang_e15/logs/$log 2>/dev/null; do sleep 30; done
if [ "$dest" = local ]; then
  touch /tmp/xiang_e15/models/$model/.ready
else
  rsync -a /tmp/xiang_e15/models/$model $dest:/tmp/xiang_e15/models/ && ssh -o BatchMode=yes $dest "touch /tmp/xiang_e15/models/$model/.ready"
fi
echo "PUSHED $model -> $dest $(date +%T)" >> /tmp/xiang_e15/logs/push.log
