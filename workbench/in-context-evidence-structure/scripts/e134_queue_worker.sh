#!/bin/bash
# Per-GPU worker for the rebuttal runs (E134-E136). usage: e134_queue_worker.sh JOBFILE GPU
# JOBFILE lines: "<job_id>|<model_dir>|<script and args...>"; a job runs once its model has .done (node-local copy).
JOBS=$1; GPU=$2
W=/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure
PY=/tmp/ices-env/.venvs/ices-tf457/bin/python
LOCKS=/tmp/ices_jobs; mkdir -p $LOCKS
export HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
while true; do
  pending=0; ran=0
  while IFS='|' read -r id model cmd; do
    [ -z "$id" ] && continue
    [ -e $LOCKS/$id.done ] && continue
    [ -d $LOCKS/$id.lock ] && continue
    pending=1
    [ -f $model/.done ] || continue
    mkdir $LOCKS/$id.lock 2>/dev/null || continue
    echo "$(date '+%F %T') gpu$GPU start $id" >> $LOCKS/worker.log
    (cd $W/scripts && CUDA_VISIBLE_DEVICES=$GPU $PY $cmd > $W/results/_logs_rebuttal/$id.log 2>&1)
    echo "$(date '+%F %T') gpu$GPU end $id rc=$?" >> $LOCKS/worker.log
    touch $LOCKS/$id.done; ran=1; break
  done < $JOBS
  [ $pending = 0 ] && break
  [ $ran = 0 ] && sleep 60
done
echo "$(date '+%F %T') gpu$GPU exit" >> $LOCKS/worker.log
