#!/bin/bash
# E24 worker: evaluates induction strength for every DataDecide model whose E20 result exists (weights cached).
# Usage: bash run_e24.sh host:gpu   (loops until all 75 done)
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e24/logs
while true; do
  left=0
  for f in ../results/e20/*__*.json; do
    t=$(basename $f .json); [ -f ../results/e24/$t.json ] && continue
    left=1; recipe=${t%__*}; seed=${t##*__}
    ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_HUB_OFFLINE=1 $PY e24_induction.py --repo allenai/DataDecide-$recipe --seed $seed" > ../results/e24/logs/$t.log 2>&1
    echo "$t exit=$?"
  done
  [ $(ls ../results/e24/*__*.json 2>/dev/null | wc -l) -ge 75 ] && break
  sleep 120
done
