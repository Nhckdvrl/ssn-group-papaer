#!/bin/bash
# Batch census worker: run_census_batch.sh <jobfile> <host:gpu> <worker> <nworkers>
cd "$(dirname "$0")"
g=$2; PY=$HOME/.venvs/mechpop/bin/python
ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY census.py --jobs $1 --worker $3 --nworkers $4"
