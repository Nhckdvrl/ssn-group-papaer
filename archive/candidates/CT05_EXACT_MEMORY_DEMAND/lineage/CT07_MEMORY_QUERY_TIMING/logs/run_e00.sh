# usage: run_e00.sh SHARD GPU
source /home/xiang/ssn-group-papaer/candidates/CT07_MEMORY_QUERY_TIMING/src/env.sh
cd $CT07/src
CUDA_VISIBLE_DEVICES=$2 $PY e00.py $Q35_9B $CT07/results/e00/q35_9b.s$1.jsonl $1 6 $CT05/data/checkpoints.jsonl "$CT05/results/e01/q35_9b.s*.jsonl" > $CT07/logs/e00_s$1.log 2>&1
