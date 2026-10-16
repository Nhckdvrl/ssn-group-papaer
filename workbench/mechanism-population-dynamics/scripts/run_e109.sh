#!/bin/bash
# E109 chain: capital unlearning + targeted attack, then general relearning 1000 steps. Usage: run_e109.sh <host:gpu> <subset> <seed>
set -u
cd "$(dirname "$0")"
G=$1; S=$2; SD=$3; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python; T=${S}_s$SD; O=/home/xiang/mechpop_cache/ckpt/e109/U_$T
mkdir -p ../results/e109/logs
ssh -n -o BatchMode=yes $H "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e109_capital.py --subset $S --seed $SD --out $O && E93_OUT=e109 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $O --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm C --tag R_$T" > ../results/e109/logs/$T.log 2>&1
