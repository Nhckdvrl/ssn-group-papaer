#!/bin/bash
# E01: 2 repos x 11 checkpoints, sharded over GPUs. Usage: GPUS="0 1 3 fvcrc10:1" bash scripts/run_e01.sh
# (host:idx entries run over ssh; /home is NFS-shared, checkpoints are pre-cached, so runs are HF-offline)
# Env: ~/.venvs/mechpop (verl-clean python 3.12, torch 2.8.0+cu128, transformers 4.57.6) + transformer_lens 2.16.1 (--no-deps).
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
GPUS=(${GPUS:-0})
LOGDIR=../results/e01/logs
mkdir -p "$LOGDIR"
JOBS=()
for repo in ${REPOS:-EleutherAI/pythia-70m-deduped EleutherAI/pythia-70m}; do
  for step in 143000 0 256 512 1000 2000 4000 8000 16000 32000 64000; do
    JOBS+=("$repo $step")
  done
done
run_shard() {
  local gi=$1 gpu=${GPUS[$1]}
  for ((j = gi; j < ${#JOBS[@]}; j += ${#GPUS[@]})); do
    set -- ${JOBS[$j]}
    tag="$(basename $1)__step$2"
    if [ -f "../results/e01/${tag}.json" ]; then continue; fi
    if [[ $gpu == *:* ]]; then
      ssh -o BatchMode=yes "${gpu%%:*}" "cd $PWD && CUDA_VISIBLE_DEVICES=${gpu##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY e01_induction.py --repo $1 --step $2" > "$LOGDIR/$tag.log" 2>&1
    else
      CUDA_VISIBLE_DEVICES=$gpu HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 "$PY" e01_induction.py --repo "$1" --step "$2" > "$LOGDIR/$tag.log" 2>&1
    fi
    echo "[gpu$gpu] $tag exit=$?"
  done
}
for ((g = 0; g < ${#GPUS[@]}; g++)); do run_shard $g & done
wait
