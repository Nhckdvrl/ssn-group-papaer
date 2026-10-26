#!/bin/bash
# E105c chain: unlearn with a given retain weight, then relearn 1000 steps. Usage: bash run_e105c.sh <host:gpu> <subset> <seed> <retain_w>
set -u
cd "$(dirname "$0")"
G=$1; S=$2; SD=$3; RW=$4; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python; T=${S}_rw${RW}_s$SD; O=/home/xiang/mechpop_cache/ckpt/e105/U3_$T
ssh -n -o BatchMode=yes $H "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e105_unlearn.py --subset $S --seed $SD --lr 5e-6 --margin 0 --target 0.5 --eval_every 5 --max_steps 2000 --retain_w $RW --tag U3_$T --out $O && E93_OUT=e105 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $O --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm C --tag R3_$T" > ../results/e105/logs/U3_$T.log 2>&1
