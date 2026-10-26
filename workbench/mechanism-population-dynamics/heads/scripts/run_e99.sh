#!/bin/bash
# E99: wait for a free GPU slot, then run one arm. Usage: bash run_e99.sh <host:gpu> <tag> <extra args>
set -u
cd "$(dirname "$0")"
G=$1; T=$2; shift 2; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python
B=/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000
free() { [ "$(ssh -n -o BatchMode=yes $H "nvidia-smi -i $D --query-gpu=memory.used --format=csv,noheader,nounits" 2>/dev/null)" -lt 1000 ] 2>/dev/null; }
until free; do sleep 60; done
ssh -n -o BatchMode=yes $H "cd $PWD && E93_OUT=e99 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $B --fp32 --bs 128 --lr 2e-5 --steps 3000 --arm H --head 3.2 --knockout 3.0,1.2,7.7 --tag $T $*" > ../results/e99/logs/$T.log 2>&1
