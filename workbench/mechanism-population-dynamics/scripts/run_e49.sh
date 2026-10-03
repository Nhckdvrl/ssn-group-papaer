#!/bin/bash
# E49 worker (claims via mkdir): run_e49.sh <host:gpu>
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e49/logs ../results/e49/claims
while read -r fam repo rev name; do
  [ -f ../results/e49/$name.json ] && continue
  mkdir ../results/e49/claims/$name 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY e49_nqswap.py --family $fam --repo $repo --rev $rev --name $name" > ../results/e49/logs/$name.log 2>&1
  echo "$name exit=$?"
done < ../results/e49_jobs.txt
