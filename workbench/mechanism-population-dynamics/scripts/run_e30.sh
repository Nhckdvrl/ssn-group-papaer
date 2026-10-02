#!/bin/bash
# E30 worker: jobs from e30_jobs.txt (repo rev), claims via mkdir.
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e30/logs ../results/e30/claims
while read repo rev; do
  t="$(basename $repo)__$rev"; [ -f ../results/e30/$t.json ] && continue
  mkdir ../results/e30/claims/$t 2>/dev/null || continue
  r=$rev; [ "$rev" = main ] && r=""
  ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_DATASETS_OFFLINE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 $PY e30_wild.py --repo $repo ${r:+--rev $r}" > ../results/e30/logs/$t.log 2>&1
  echo "$t exit=$?"
done < e30_jobs.txt
