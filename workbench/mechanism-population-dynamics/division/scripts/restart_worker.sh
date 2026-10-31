#!/usr/bin/env bash
# Restart the E167 analysis worker for one run on this host/GPU: stop the old worker (not its running child),
# wait for that child to finish, then start the new worker. Usage: restart_worker.sh GPU RUN
G=$1 R=$2
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
W=/home/xiang/mechpop_cache/e167_analysis
OLD=$(pgrep -u xiang -f "analysis_worker.py --runs $R( |$)")
KIDS=""
for p in $OLD; do KIDS="$KIDS $(pgrep -P $p)"; kill $p; done
cd $S
nohup bash -c "for k in $KIDS; do while kill -0 \$k 2>/dev/null; do sleep 20; done; done; E167_BATCH=16 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=$G exec ~/.venvs/mechpop/bin/python -B analysis_worker.py --runs $R" >> $W/worker_$R.log 2>&1 &
echo "$R: stopped [$OLD], waiting on [$KIDS]"
