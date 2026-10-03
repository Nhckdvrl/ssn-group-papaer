#!/bin/bash
# E48 worker (claims via mkdir; waits until the GPU has >= 20 GB free before each run): run_e48.sh <host:gpu>
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e48/logs ../results/e48/claims
for pass in 1 2 3 4 5 6; do for size in 90M 60M; do for s in default small-aux-2 small-aux-3; do for c in orig swap none; do
  t=${size}__${s}__$c; [ -f ../results/e48/$t.json ] && continue
  mkdir ../results/e48/claims/$t 2>/dev/null || continue
  until [ "$(ssh -n -o BatchMode=yes ${g%%:*} "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i ${g##*:}" 2>/dev/null)" -ge 20000 ] 2>/dev/null; do sleep 120; done
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=${g##*:} $PY e48_cueswap.py --train --size $size --seed $s --cond $c" > ../results/e48/logs/$t.log 2>&1
  rc=$?; echo "$t exit=$rc"
  [ -f ../results/e48/$t.json ] || rmdir ../results/e48/claims/$t  # failed (e.g. OOM): release the claim so it is retried
done; done; done; done
