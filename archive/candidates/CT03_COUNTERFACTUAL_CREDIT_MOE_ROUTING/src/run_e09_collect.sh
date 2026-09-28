#!/bin/bash
cd /home/xiang/ssn-group-papaer/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
CUDA_VISIBLE_DEVICES=0,1 $PY src/e09_collect.py --start 0   --n-problems 105 \
  --out results/e09_cache_a.pt > results/logs/e09_a.log 2>&1 &
A=$!
CUDA_VISIBLE_DEVICES=2,3 $PY src/e09_collect.py --start 105 --n-problems 105 \
  --out results/e09_cache_b.pt --head-out results/e09_head_b.pt > results/logs/e09_b.log 2>&1 &
B=$!
echo "launched a=$A (gpu0,1) b=$B (gpu2,3) on $(hostname)"
wait $A; ra=$?; wait $B; rb=$?
echo "E09_COLLECT_DONE a=$ra b=$rb"
