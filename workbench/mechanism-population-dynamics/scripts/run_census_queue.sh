#!/bin/bash
# Generic census worker (claims via mkdir). Job file lines: <family> <repo> <rev> <out> <name>
# Usage: run_census_queue.sh <jobfile> <host:gpu>
cd "$(dirname "$0")"
jobs=$1; g=$2; PY=$HOME/.venvs/mechpop/bin/python
while read -r fam repo rev out name; do
  [ -z "$name" ] && continue
  mkdir -p ../results/$out/logs ../results/$out/claims
  [ -f ../results/$out/$name.json ] && continue
  mkdir ../results/$out/claims/$name 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY census.py --family $fam --repo $repo --rev $rev --out $out --name $name" > ../results/$out/logs/$name.log 2>&1
  echo "$name exit=$?"
done < "$jobs"
