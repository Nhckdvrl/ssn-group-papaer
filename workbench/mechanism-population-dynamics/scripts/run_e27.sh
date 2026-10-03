#!/bin/bash
# E27 worker: E26 factorial on the default seed of every DataDecide recipe (weights cached by E20).
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
for f in ../results/e20/*__default.json; do
  t=$(basename $f .json); [ -f ../results/e26/$t.json ] && continue
  mkdir ../results/e26/claim_$t 2>/dev/null || continue
  ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e26_factorial.py --repo allenai/DataDecide-${t%__*} --seed default" > ../results/e26/logs/$t.log 2>&1
  echo "$t exit=$?"
done
