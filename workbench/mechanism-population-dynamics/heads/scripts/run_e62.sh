#!/bin/bash
# E62 retry worker (copy of run_e46r.sh with --bs): several passes over a job file; waits for >= 16 GB free GPU memory; releases the claim on failure.
# Usage: run_e46r.sh <host:gpu> <jobfile>
cd "$(dirname "$0")"
g=$1; jobs=$2; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e46/logs ../results/e46/claims
for pass in 1 2 3 4 5 6 7 8; do
while read -r args; do
  [ -z "$args" ] && continue
  name=$($PY -c "import sys, argparse; sys.argv=['x']+'''$args'''.split(); import e46_train as e; p=argparse.ArgumentParser(); [p.add_argument(a, **k) for a,k in [('--size',{'default':'S'}),('--init',{'type':int}),('--corpus',{}),('--order',{'type':int}),('--eps',{'type':float,'default':0.0}),('--branch',{'type':int,'default':None}),('--to-corpus',{'default':None}),('--to-order',{'type':int,'default':None}),('--rerun',{'type':int,'default':0}),('--save-branch-states',{'action':'store_true'}),('--steps',{'type':int,'default':10000}),('--init-std',{'type':float,'default':0.02}),('--lr',{'type':float,'default':1e-3}),('--bs',{'type':int,'default':64})]]; print(e.run_name(p.parse_args()))" 2>/dev/null)
  [ -z "$name" ] && continue
  [ -f ../results/e46/$name.json ] && continue
  if [[ "$args" == *--branch* ]]; then
    k=$(echo "$args" | sed 's/.*--branch \([0-9]*\).*/\1/'); par=$(echo "$name" | sed 's/_b[0-9].*//')
    [ -f /home/xiang/mechpop_cache/e46_runs/$par/state$k.pt ] || continue   # parent not there yet: try next pass
  fi
  mkdir ../results/e46/claims/$name 2>/dev/null || continue
  until [ "$(ssh -n -o BatchMode=yes ${g%%:*} "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i ${g##*:}" 2>/dev/null)" -ge 16000 ] 2>/dev/null; do sleep 120; done
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=${g##*:} $PY e46_train.py $args" > ../results/e46/logs/$name.log 2>&1
  echo "$name exit=$?"
  [ -f ../results/e46/$name.json ] || rmdir ../results/e46/claims/$name
done < "$jobs"
sleep 300
done
