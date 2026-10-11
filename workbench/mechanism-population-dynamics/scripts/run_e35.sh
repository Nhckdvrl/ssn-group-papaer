#!/bin/bash
# E35 worker (claims via mkdir): census on all 75 DataDecide 1B final models (weights cached by E20).
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e35/logs ../results/e35/claims
for s in default large-aux-2 large-aux-3; do for f in ../results/e20/*__$s.json; do
  t=$(basename $f .json); [ -f ../results/e35/$t.json ] && continue
  mkdir ../results/e35/claims/$t 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e35_census.py --repo allenai/DataDecide-${t%__*} --seed $s" > ../results/e35/logs/$t.log 2>&1
  echo "$t exit=$?"
done; done
