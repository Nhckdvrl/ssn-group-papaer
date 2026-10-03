#!/bin/bash
# E37 worker (claims): E35 census at early checkpoints, 3 recipes x 3 inits x steps {2500, 10000}
cd "$(dirname "$0")"; g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e35/logs ../results/e35/claims_e37
for step in 2500 10000; do for r in dolma1_7-1B c4-1B dclm-baseline-1B; do for s in default large-aux-2 large-aux-3; do
  t=${r}__${s}__step$step; [ -f ../results/e35/$t.json ] && continue
  mkdir ../results/e35/claims_e37/$t 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_DATASETS_OFFLINE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 $PY e35_census.py --repo allenai/DataDecide-$r --seed $s --step $step" > ../results/e35/logs/$t.log 2>&1
  echo "$t exit=$?"
done; done; done
