#!/bin/bash
# E50 worker (claims via mkdir): run_e50.sh <host:gpu>
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e50/logs ../results/e50/claims
for s in default large-aux-2 large-aux-3; do for r in dolma1_7 dolma1_7-no-flan dolma1_7-no-code dolma1_7-no-math-code dolma1_7-no-reddit; do
  t=${r}__$s; [ -f ../results/e50/$t.json ] && continue
  mkdir ../results/e50/claims/$t 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY e50_switch_attribution.py --recipe $r --seed $s" > ../results/e50/logs/$t.log 2>&1
  echo "$t exit=$?"
done; done
