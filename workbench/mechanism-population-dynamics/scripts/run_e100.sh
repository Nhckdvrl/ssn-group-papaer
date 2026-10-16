#!/bin/bash
# E100: wait for a free GPU slot, then run one lesion/control arm on a given checkpoint and save weights.
# Usage: bash run_e100.sh <host:gpu> <tag> <step> <extra args>
set -u
cd "$(dirname "$0")"
G=$1; T=$2; S=$3; shift 3; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python
B=/home/xiang/mechpop_cache/ckpt/pythia-160m_step$S
O=/home/xiang/mechpop_cache/ckpt/e100
free() { [ "$(ssh -n -o BatchMode=yes $H "nvidia-smi -i $D --query-gpu=memory.used --format=csv,noheader,nounits" 2>/dev/null)" -lt 1000 ] 2>/dev/null; }
until free; do sleep 60; done
ssh -n -o BatchMode=yes $H "cd $PWD && E93_OUT=e100 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $B --fp32 --bs 128 --lr 2e-5 --steps 5000 --tag $T --save_final $O/$T --save_at 400,2500 $*" > ../results/e100/logs/$T.log 2>&1
