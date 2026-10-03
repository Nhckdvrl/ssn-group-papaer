#!/bin/bash
# E26 worker: runs the factorial on the 12 registered models as soon as their weights are cached (E20 result exists).
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e26/logs
while true; do
  left=0
  for r in dolma1_7-1B dolma1_7-no-flan-1B c4-1B dclm-baseline-1B; do for s in default large-aux-2 large-aux-3; do
    t=${r}__$s; [ -f ../results/e26/$t.json ] && continue
    left=1; [ -f ../results/e20/$t.json ] || continue
    ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e26_factorial.py --repo allenai/DataDecide-$r --seed $s" > ../results/e26/logs/$t.log 2>&1
    echo "$t exit=$?"
  done; done
  [ $left -eq 0 ] && break
  sleep 120
done
