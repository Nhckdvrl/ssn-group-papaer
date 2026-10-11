#!/bin/bash
# E66 worker: lines of the job file are "<run name>|<parent name or ->|<branch step or ->|<e46_train.py args>".
# Several passes; a branch waits for its parent's saved state. Claims prevent two workers taking one job.
# Usage: run_e66.sh <host:gpu> <jobfile>
cd "$(dirname "$0")"
g=$1; jobs=$2; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e46/logs ../results/e46/claims
for pass in $(seq 1 40); do
  left=0
  while IFS='|' read -r name par k args; do
    [ -z "$name" ] && continue
    [ -f ../results/e46/$name.json ] && continue
    left=1
    if [ "$par" != "-" ]; then
      [ -f /home/xiang/mechpop_cache/e46_runs/$par/state$k.pt ] || continue
    fi
    mkdir ../results/e46/claims/$name 2>/dev/null || continue
    ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=${g##*:} $PY e46_train.py $args" > ../results/e46/logs/$name.log 2>&1
    echo "$(date +%H:%M) $name exit=$?"
    [ -f ../results/e46/$name.json ] || rmdir ../results/e46/claims/$name
  done < "$jobs"
  [ $left = 0 ] && break
  sleep 120
done
