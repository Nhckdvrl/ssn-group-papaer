#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
until [ -f results/runs/P_s2/DONE ] && [ -f results/runs/S_s1/DONE ] \
   && [ -f results/runs/D_mask_s0/DONE ] && [ -f results/runs/D_rt_s2/DONE ]; do sleep 60; done
echo "round3 training done $(date -Is)"
ssh -o BatchMode=yes fvcrc13 "bash $ROOT/src/eval_remote.sh evals 3 P:2 S:1 D_mask:0 D_rt:2" &
ssh -o BatchMode=yes fvcrc15 "bash $ROOT/src/eval_remote.sh evals 1 P:2 S:1 D_mask:0" &
wait
echo "ROUND3 EVAL DONE $(date -Is)"
