#!/bin/bash
# stage HF cache dirs of given models onto a host-local disk: stage_model.sh HOST model_dir_name...
HOST=$1; shift
for M in "$@"; do
  ssh -n -o ConnectTimeout=10 $HOST "mkdir -p /tmp/xiang_hf/hub && touch /tmp/xiang_hf/hub/$M.staging && rsync -a --exclude '*.lock' ~/.cache/huggingface/hub/$M /tmp/xiang_hf/hub/ && rm -f /tmp/xiang_hf/hub/$M.staging && echo staged $M" 2>/dev/null
done
