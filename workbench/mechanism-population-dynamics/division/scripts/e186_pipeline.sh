#!/bin/bash
# E186 CPU analysis for one captured model: views -> E185 pipeline (env-redirected) -> E186 extra readouts.
# Usage: e186_pipeline.sh KEY [PROCS]     log: results/e186/_logs/pipe_<KEY>.log
set -e
KEY=$1; NP=${2:-12}
cd "$(dirname "$0")"
PY=~/.venvs/mechpop/bin/python
# stores and views live on the capture node's local disk (NFS is starved while downloads run); outputs are small
export E186_SRC=${E186_SRC:-/tmp/xiang_e186/store} E186_VIEWS=${E186_VIEWS:-/tmp/xiang_e186/views}
export E185_CACHE=$E186_VIEWS E185_OUT=$HOME/mechpop_cache/atlas_e186 E185_RES=$(cd ../results/e186 && pwd)
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 HF_HUB_OFFLINE=1
mkdir -p $E185_OUT
echo "[$(date +%T)] $KEY on $(hostname) procs $NP"
$PY e186_views.py $KEY --src $E186_SRC --views $E186_VIEWS
$PY e185_atlas.py --data d184 --model $KEY --procs $NP
$PY e185_crossfit.py --data d184 --model $KEY --procs $NP
$PY e185_tokens.py --data d184 --model $KEY
$PY e185_residuals.py --part a --model $KEY
for p in ctx resa vs8 geom; do $PY e186_extra.py --part $p --key $KEY; done
$PY e185_atlas.py --data d180 --model $KEY --procs $NP
E185_FREQ_ONLY=1 $PY e185_crossfit.py --data d180 --model $KEY --procs $NP
echo "[$(date +%T)] pipeline done $KEY"
