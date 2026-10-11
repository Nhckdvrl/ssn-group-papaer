#!/bin/bash
# E29 worker (claims via mkdir): Flan pair x 3 seeds x 4 intermediate steps (downloads checkpoints).
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e29/logs ../results/e29/claims
for step in 7500 35000 2500 17500; do for r in dolma1_7-1B dolma1_7-no-flan-1B; do for s in default large-aux-2 large-aux-3; do
  t=${r}__${s}__$step; [ -f ../results/e29/$t.json ] && continue
  mkdir ../results/e29/claims/$t 2>/dev/null || continue
  ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_DATASETS_OFFLINE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 $PY e29_timecourse.py --repo allenai/DataDecide-$r --seed $s --step $step" > ../results/e29/logs/$t.log 2>&1
  echo "$t exit=$?"
done; done; done
