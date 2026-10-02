#!/bin/bash
# E04 runner over ssh host GPUs. Usage: HOST=fvcrc10 GPUS="1 2 3" bash scripts/run_e04.sh jobs.txt
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
GPUS=(${GPUS:-1}); mapfile -t JOBS < "$1"; mkdir -p ../results/e04/logs
shard() { local gi=$1; for ((j=gi; j<${#JOBS[@]}; j+=${#GPUS[@]})); do set -- ${JOBS[$j]}
  [ -f ../results/e04/$1__step$2.json ] && continue
  ssh -o BatchMode=yes $HOST "cd $PWD && CUDA_VISIBLE_DEVICES=${GPUS[$gi]} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e04_ctx_gating.py --seed $1 --step $2" 2>&1 | grep -E "@|Error" >> ../results/e04/logs/run.log; done; }
for ((g=0; g<${#GPUS[@]}; g++)); do shard $g & done; wait
