#!/bin/bash
# E59 worker: run_e59.sh <host:gpu> <worker> <nworkers>
cd "$(dirname "$0")"
g=$1; PY=$HOME/.venvs/mechpop/bin/python
ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY e59_roles.py --jobs ../results/e59_jobs.txt --worker $2 --nworkers $3 $4"
