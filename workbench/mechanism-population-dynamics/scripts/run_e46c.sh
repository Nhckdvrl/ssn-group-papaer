#!/bin/bash
# E46c worker (copy of run_e46.sh with --init-std / --lr in the name parser): run_e46.sh <host:gpu> <jobfile>  (claims via mkdir on the run name; stage-2 jobs wait for parent states)
cd "$(dirname "$0")"
g=$1; jobs=$2; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e46/logs ../results/e46/claims
while read -r args; do
  [ -z "$args" ] && continue
  name=$($PY -c "import sys, argparse; sys.argv=['x']+'''$args'''.split(); import e46_train as e; p=argparse.ArgumentParser(); [p.add_argument(a, **k) for a,k in [('--size',{'default':'S'}),('--init',{'type':int}),('--corpus',{}),('--order',{'type':int}),('--eps',{'type':float,'default':0.0}),('--branch',{'type':int,'default':None}),('--to-corpus',{'default':None}),('--to-order',{'type':int,'default':None}),('--rerun',{'type':int,'default':0}),('--save-branch-states',{'action':'store_true'}),('--steps',{'type':int,'default':10000}),('--init-std',{'type':float,'default':0.02}),('--lr',{'type':float,'default':1e-3})]]; print(e.run_name(p.parse_args()))" 2>/dev/null)
  [ -f ../results/e46/$name.json ] && continue
  mkdir ../results/e46/claims/$name 2>/dev/null || continue
  if [[ "$args" == *--branch* ]]; then  # wait for the parent's state file
    k=$(echo "$args" | sed 's/.*--branch \([0-9]*\).*/\1/'); par=$(echo "$name" | sed 's/_b[0-9].*//')
    until [ -f /home/xiang/mechpop_cache/e46_runs/$par/state$k.pt ]; do sleep 60; done
  fi
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY e46_train.py $args" > ../results/e46/logs/$name.log 2>&1
  echo "$name exit=$?"
done < "$jobs"
