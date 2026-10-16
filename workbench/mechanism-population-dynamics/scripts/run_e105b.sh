#!/bin/bash
# E105b chain: unlearn (matched, gentle) then relearn 1000 steps on Pile. Usage: bash run_e105b.sh <host:gpu> <subset> <seed>
set -u
cd "$(dirname "$0")"
G=$1; S=$2; SD=$3; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python; T=${S}_s$SD; O=/home/xiang/mechpop_cache/ckpt/e105/U2_$T
ssh -n -o BatchMode=yes $H "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e105_unlearn.py --subset $S --seed $SD --lr 5e-6 --margin 0 --target 0.5 --eval_every 5 --max_steps 2000 --tag U2_$T --out $O && E93_OUT=e105 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $O --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm C --tag R2_$T" > ../results/e105/logs/U2_$T.log 2>&1
