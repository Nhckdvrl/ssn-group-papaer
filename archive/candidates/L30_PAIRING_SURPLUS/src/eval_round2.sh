#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
until [ -f results/runs/P_s1/DONE ] && [ -f results/runs/S_s0/DONE ] \
   && [ -f results/runs/D_mask_s2/DONE ] && [ -f results/runs/D_rt_s1/DONE ]; do sleep 60; done
echo "round2 training done $(date -Is)"
ssh -o BatchMode=yes fvcrc13 "bash $ROOT/src/eval_remote.sh evals 3 P:1 S:0 D_mask:2 D_rt:1" &
ssh -o BatchMode=yes fvcrc15 "bash $ROOT/src/eval_remote.sh evals 1 P:1 S:0 D_mask:2" &
wait
echo "ROUND2 EVAL DONE $(date -Is)"
