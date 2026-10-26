#!/bin/bash
# E35 add-on: maps of the three initializations themselves (step0; identical across recipes, so one recipe repo suffices)
cd "$(dirname "$0")"; g=$1; PY=$HOME/.venvs/mechpop/bin/python
for s in default large-aux-2 large-aux-3; do
  t=c4-1B__${s}__step0; [ -f ../results/e35/$t.json ] && continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_DATASETS_OFFLINE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 $PY e35_census.py --repo allenai/DataDecide-c4-1B --seed $s --step 0" > ../results/e35/logs/$t.log 2>&1
  echo "$t exit=$?"
done
