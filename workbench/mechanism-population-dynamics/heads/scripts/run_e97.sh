#!/bin/bash
# E97 slot worker: wait until the GPU is free, then claim jobs from results/e97/queue.txt (claim = atomic mkdir).
# Job lines:  lesion TAG HEAD   |   post TAG   (post waits until the lesion run TAG has saved its final weights)
# Usage: bash run_e97.sh <host:gpu>
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
G=$1; H=${G%%:*}; D=${G##*:}
OUT=../results/e97; mkdir -p $OUT/claims $OUT/logs
BASE=/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000
SAVE=/home/xiang/mechpop_cache/ckpt/e97
free() { [ "$(ssh -n -o BatchMode=yes $H "nvidia-smi -i $D --query-gpu=memory.used --format=csv,noheader,nounits" 2>/dev/null)" -lt 1000 ] 2>/dev/null; }
until free; do sleep 60; done
while read -r kind tag head; do
  [ -z "$kind" ] && continue
  mkdir "$OUT/claims/${kind}_$tag" 2>/dev/null || continue
  if [ "$kind" = lesion ]; then
    ssh -n -o BatchMode=yes $H "cd $PWD && E93_OUT=e97 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $BASE --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm H --head $head --tag $tag --save_final $SAVE/$tag" > $OUT/logs/$tag.log 2>&1
  else
    until [ -s $SAVE/$tag/config.json ]; do sleep 60; done
    ssh -n -o BatchMode=yes $H "cd $PWD && E89_LOCAL=$SAVE/$tag LABOR_OUT=e97 CUDA_VISIBLE_DEVICES=$D $PY e89_labor.py --family hf --repo EleutherAI/post-$tag --rev step1000 --chunk 16" > $OUT/logs/post_$tag.log 2>&1
  fi
  echo "$(date +%H:%M) [$G] $kind $tag exit=$?"
done < $OUT/queue.txt
