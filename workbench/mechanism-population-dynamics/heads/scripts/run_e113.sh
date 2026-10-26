#!/bin/bash
# E113 chain on one GPU: add behaviour with subset, benign Pile training 1000 steps with checkpoints, evaluate retention.
set -u
cd "$(dirname "$0")"
G=$1; SD=$2; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python; C=/home/xiang/mechpop_cache/ckpt/e113; mkdir -p ../results/e113/logs
for S in qk ov mlp; do
  T=${S}_s$SD
  ssh -n -o BatchMode=yes $H "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e113_addition.py --subset $S --seed $SD --out $C/A_$T && E93_OUT=e113 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $C/A_$T --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm C --tag R_$T --save_final $C/R_$T --save_at 100,300 && CUDA_VISIBLE_DEVICES=$D $PY e113_addition.py --eval ../results/e113/retention_$T.json $C/A_$T $C/R_${T}_s100 $C/R_${T}_s300 $C/R_$T" > ../results/e113/logs/$T.log 2>&1
done
