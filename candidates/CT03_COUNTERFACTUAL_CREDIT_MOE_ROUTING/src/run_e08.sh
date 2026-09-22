#!/bin/bash
# E08 full-route screening audit: 2 workers x 2 cards (4 of the 8-card budget),
# host $(hostname). Each worker is an independent shard of the locked train pool.
cd /home/xiang/ssn-group-papaer/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
N=${1:-40}
CUDA_VISIBLE_DEVICES=0,1 $PY src/e08_fullroute.py --start 0  --n-problems $N \
  --chunk-rows 288 --out results/e08_cache_a.pt > results/logs/e08_a.log 2>&1 &
A=$!
CUDA_VISIBLE_DEVICES=2,3 $PY src/e08_fullroute.py --start $N --n-problems $N \
  --chunk-rows 288 --out results/e08_cache_b.pt > results/logs/e08_b.log 2>&1 &
B=$!
echo "launched a=$A (gpu0,1 start 0) b=$B (gpu2,3 start $N) on $(hostname)"
wait $A; ra=$?
wait $B; rb=$?
echo "E08_DONE a=$ra b=$rb"
