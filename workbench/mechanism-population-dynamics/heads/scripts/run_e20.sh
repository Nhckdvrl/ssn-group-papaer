#!/bin/bash
# E20 queue: workers claim (recipe, seed) via atomic mkdir; each job downloads + evaluates one DataDecide 1B model.
# Usage: GPUS="fvcrc12:0 fvcrc13:2" bash run_e20.sh
set -u
cd "$(dirname "$0")"
PY=$HOME/.venvs/mechpop/bin/python
OUT=../results/e20
mkdir -p "$OUT/logs" "$OUT/claims"
RECIPES=$(python3 -c "import json;print(' '.join(json.load(open('/home/xiang/mechpop_cache/datadecide_1b_final_steps.json'))))")
worker() {
  local g=$1
  for seed in default large-aux-2 large-aux-3; do for repo in $RECIPES; do
    tag="${repo#allenai/DataDecide-}__$seed"
    [ -f "$OUT/$tag.json" ] && continue
    mkdir "$OUT/claims/$tag" 2>/dev/null || continue
    ssh -o BatchMode=yes "${g%%:*}" "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_DATASETS_OFFLINE=1 $PY e20_recipe.py --repo $repo --seed $seed" > "$OUT/logs/$tag.log" 2>&1
    echo "[$g] $tag exit=$?"
  done; done
}
for g in ${GPUS}; do worker "$g" & sleep 20; done
wait
