#!/usr/bin/env bash
# E173 node-side job (started by e173_launch.sh on an idle GPU): train, then on the same GPU capture routing at
# every checkpoint and the route fingerprint / R0 at 8e8, then delete the one-off resume state.
# Usage (CUDA_VISIBLE_DEVICES already set): e173_job.sh RUN SEED [train_moe.py args...]
set -uo pipefail
RUN=$1 SEED=$2; shift 2
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
OUT=/home/xiang/mechpop_cache/e173_runs/$RUN
A=/home/xiang/mechpop_cache/e173_analysis
PY=/home/xiang/.venvs/mechpop/bin/python
cd $S
$PY -B train_moe.py --run $RUN --init-seed $SEED --data-seed 0 \
  --train-dir /tmp/xiang-e167/data/train --held-dir /tmp/xiang-e167/data/held \
  --out $OUT --resume /tmp/xiang-e173/resume/$RUN "$@"
rc=$?
echo "$(date '+%F %T') train rc=$rc"
if [ $rc -ne 0 ] && [ ! -f $OUT/DONE.json ] && [ ! -f /tmp/xiang-e173/resume/$RUN/latest.pt ] && \
   tail -50 /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/results/e173/_logs/$RUN.log | grep -q "OutOfMemoryError"; then
  echo "$(date '+%F %T') E173 DEVIATION: OOM at --micro 16; restarting from scratch with --micro 8 (aux-LB window 8x2048)"
  rm -f $OUT/ckpt_*.pt $OUT/train_log.jsonl
  $PY -B train_moe.py --run $RUN --init-seed $SEED --data-seed 0 \
    --train-dir /tmp/xiang-e167/data/train --held-dir /tmp/xiang-e167/data/held \
    --out $OUT --resume /tmp/xiang-e173/resume/$RUN "$@" --micro 8
  rc=$?
  echo "$(date '+%F %T') train (micro 8) rc=$rc"
fi
[ -f $OUT/DONE.json ] || { echo "no DONE.json; stopping before analysis"; exit $rc; }
rm -rf /tmp/xiang-e173/resume/$RUN
mkdir -p $A/routing $A/functional
echo "$(date '+%F %T') routing captures"
$PY -B capture_routing.py $A/routing $OUT/ckpt_*.pt
echo "$(date '+%F %T') route fingerprints + R0 at 8e8"
E167_BATCH=16 $PY -B functional_probe.py $A/functional --no-r4 $OUT/ckpt_800000000.pt
echo "$(date '+%F %T') job done"
