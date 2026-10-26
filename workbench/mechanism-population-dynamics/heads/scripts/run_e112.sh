#!/bin/bash
# E112 slot worker: wait until the GPU is free, claim jobs (atomic mkdir), unlearn (qk + attention-footprint penalty) then relearn 1000 steps.
set -u
cd "$(dirname "$0")"
G=$1; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python; OUT=../results/e112; C=/home/xiang/mechpop_cache/ckpt/e112
free() { [ "$(ssh -n -o BatchMode=yes $H "nvidia-smi -i $D --query-gpu=memory.used --format=csv,noheader,nounits" 2>/dev/null)" -lt 1000 ] 2>/dev/null; }
while read -r tag seed reg; do
  [ -z "$tag" ] && continue
  until free; do sleep 60; done
  mkdir "$OUT/claims/$tag" 2>/dev/null || continue
  ssh -n -o BatchMode=yes $H "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e105_unlearn.py --subset qk --seed $seed --lr 5e-6 --margin 0 --target 0.5 --eval_every 5 --max_steps 2000 --retain_bs 8 --attn_reg $reg --tag E112_$tag --out $C/U_$tag && E93_OUT=e112 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $C/U_$tag --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm C --tag R_$tag" > $OUT/logs/$tag.log 2>&1
  echo "$(date +%H:%M) [$G] $tag done" >> $OUT/workers.log
done < $OUT/queue.txt
