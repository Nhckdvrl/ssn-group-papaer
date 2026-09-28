#!/bin/bash
# Usage: launch.sh <queue_dir> host:gpu [host:gpu ...]   (starts one worker per card)
Q=$1; shift
source /home/xiang/ssn-group-papaer/workbench/modern-guidance/scripts/env.sh
mkdir -p $Q/logs
for hg in "$@"; do
  h=${hg%%:*}; g=${hg##*:}
  ssh $h "cd $MG/scripts && source env.sh && CUDA_VISIBLE_DEVICES=$g nohup \$PY worker.py --queue $Q > $Q/logs/worker_${h}_${g}.log 2>&1 &" 
  echo "$(date -Iseconds) started worker $h gpu$g queue=$Q" | tee -a $Q/logs/launch.log
done
