#!/bin/bash
# E48b worker (dose-escalated cue swap; claims via mkdir; waits for >= 20 GB free; releases the claim on failure)
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
SFX=__p30t300M
mkdir -p ../results/e48/logs ../results/e48/claims
for pass in 1 2 3 4 5 6; do for s in default small-aux-2 small-aux-3; do for c in orig swap none; do
  t=60M__${s}__${c}$SFX; [ -f ../results/e48/$t.json ] && continue
  mkdir ../results/e48/claims/$t 2>/dev/null || continue
  until [ "$(ssh -n -o BatchMode=yes ${g%%:*} "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i ${g##*:}" 2>/dev/null)" -ge 20000 ] 2>/dev/null; do sleep 120; done
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=${g##*:} $PY e48_cueswap.py --train --size 60M --seed $s --cond $c --tokens 300000000 --p-flan 0.3 --evals-at 0,50000000,100000000,200000000,300000000" > ../results/e48/logs/$t.log 2>&1
  echo "$t exit=$?"
  [ -f ../results/e48/$t.json ] || rmdir ../results/e48/claims/$t
done; done; sleep 300; done
