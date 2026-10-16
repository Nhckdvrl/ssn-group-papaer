#!/bin/bash
# E102 slot worker: optionally wait until a wall-clock hour, wait for the GPU to be free, then claim jobs from
# results/e102/queue.txt (claim = atomic mkdir). Each job: lesion run (3000 steps, saves final weights) + E89 map.
# Usage: bash run_e102.sh <host:gpu> [start_hour]
set -u
cd "$(dirname "$0")"
G=$1; START=${2:-}; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python
B=/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000; S=/home/xiang/mechpop_cache/ckpt/e102; OUT=../results/e102
if [ -n "$START" ]; then until [ "$(date +%H)" -ge "$START" ]; do sleep 120; done; fi
free() { [ "$(ssh -n -o BatchMode=yes $H "nvidia-smi -i $D --query-gpu=memory.used --format=csv,noheader,nounits" 2>/dev/null)" -lt 1000 ] 2>/dev/null; }
until free; do sleep 60; done
while read -r tag head extra; do
  [ -z "$tag" ] && continue
  mkdir "$OUT/claims/$tag" 2>/dev/null || continue
  ssh -n -o BatchMode=yes $H "cd $PWD && E93_OUT=e102 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $B --fp32 --bs 128 --lr 2e-5 --steps 3000 --arm H --head $head $extra --tag $tag --save_final $S/$tag && E89_LOCAL=$S/$tag LABOR_OUT=e102 CUDA_VISIBLE_DEVICES=$D $PY e89_labor.py --family hf --repo EleutherAI/post-$tag --rev x --chunk 16" > $OUT/logs/$tag.log 2>&1
  echo "$(date +%H:%M) [$G] $tag exit=$?" >> $OUT/workers.log
done < $OUT/queue.txt
