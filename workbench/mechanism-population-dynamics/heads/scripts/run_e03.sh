#!/bin/bash
# E03 runner: JOBS file lines "<seed> <step>", sharded over local GPUs. Usage: GPUS="0 1 3" bash scripts/run_e03.sh jobs.txt
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
GPUS=(${GPUS:-0}); mapfile -t JOBS < "$1"; mkdir -p ../results/e03/logs
shard() { local gi=$1; for ((j=gi; j<${#JOBS[@]}; j+=${#GPUS[@]})); do set -- ${JOBS[$j]}
  [ -f ../results/e03/$1__step$2.json ] && continue
  CUDA_VISIBLE_DEVICES=${GPUS[$gi]} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e03_antagonist.py --seed $1 --step $2 2>&1 | grep -E "@|Error" >> ../results/e03/logs/run.log; done; }
for ((g=0; g<${#GPUS[@]}; g++)); do shard $g & done; wait
