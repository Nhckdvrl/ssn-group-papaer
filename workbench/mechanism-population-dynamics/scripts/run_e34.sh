#!/bin/bash
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e34/logs ../results/e34/claims
for r in dolma1_7-1B dolma1_7-no-flan-1B c4-1B dclm-baseline-1B; do for s in default large-aux-2 large-aux-3; do
  t=${r}__$s; [ -f ../results/e34/$t.json ] && continue
  mkdir ../results/e34/claims/$t 2>/dev/null || continue
  ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e34_popqa.py --repo allenai/DataDecide-$r --seed $s" > ../results/e34/logs/$t.log 2>&1
  echo "$t exit=$?"
done; done
