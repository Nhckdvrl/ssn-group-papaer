#!/bin/bash
# E186 CPU analysis, node-local (same steps as scripts/e186_pipeline.sh). Usage: run_pipe_local.sh KEY [PROCS]
set -e
KEY=$1; NP=${2:-8}
B=/tmp/xiang_e186
mkdir -p $B/tok $B/atlas $B/bundle/results/e186 $B/logs
for n in phimoe mixtral dsv2lite; do [ -d $B/models/$n ] && ln -sfn $B/models/$n $B/tok/$n; done
for d in $B/models/olmoe0924_*; do [ -d $d ] && ln -sfn $d $B/tok/olmoe0924; break; done
export PYTHONNOUSERSITE=1 HF_HOME=$B/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export E186_SRC=$B/store E185_CACHE=$B/views E185_OUT=$B/atlas E185_RES=$B/bundle/results/e186
PY=$B/env/bin/python; C=$B/bundle/code
{
echo "[$(date +%T)] pipeline $KEY on $(hostname) procs $NP"
$PY $C/e186_views.py $KEY --src $B/store --views $B/views
$PY $C/e185_atlas.py --data d184 --model $KEY --procs $NP
$PY $C/e185_crossfit.py --data d184 --model $KEY --procs $NP
$PY $C/e185_tokens.py --data d184 --model $KEY
$PY $C/e185_residuals.py --part a --model $KEY
for p in ctx resa vs8 geom; do $PY $C/e186_extra.py --part $p --key $KEY; done
$PY $C/e185_atlas.py --data d180 --model $KEY --procs $NP
E185_FREQ_ONLY=1 $PY $C/e185_crossfit.py --data d180 --model $KEY --procs $NP
echo "[$(date +%T)] pipeline done $KEY"
} >> $B/logs/pipe_$KEY.log 2>&1
