#!/bin/bash
# E38 worker (claims): E35 census on the clean 300M crossed subset (7 recipes x 2 inits)
cd "$(dirname "$0")"; g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e38/logs ../results/e38/claims
python3 -c "import json;[print(x['recipe'],s,x[s]['final_step']) for x in json.load(open('/home/xiang/mechpop_cache/datadecide/e38_300m_subset.json')) for s in ('default','small-aux-2')]" > /tmp/e38_jobs_$$.txt
while read r s st; do
  t=${r}-300M__${s}; [ -f ../results/e38/$t.json ] && continue
  mkdir ../results/e38/claims/$t 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_DATASETS_OFFLINE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 E35_OUT=e38 $PY e35_census.py --repo allenai/DataDecide-${r}-300M --seed $s --step $st" > ../results/e38/logs/$t.log 2>&1
  echo "$t exit=$?"
done < /tmp/e38_jobs_$$.txt
