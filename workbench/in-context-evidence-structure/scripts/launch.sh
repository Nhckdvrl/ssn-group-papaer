#!/bin/bash
# usage: launch.sh HOST GPU MODEL INP OUT [SHARD NSHARD BS]
HOST=$1; GPU=$2; MODEL=$3; INP=$4; OUT=$5; SHARD=${6:-0}; NSHARD=${7:-1}; BS=${8:-16}
D=/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure
LOG=$D/logs/run_$(basename $(dirname $OUT))_$(basename $OUT .jsonl).log
mkdir -p $(dirname $OUT) $D/logs
MD=models--$(echo $MODEL | sed "s#/#--#g")
ssh -n -o ConnectTimeout=10 $HOST "cd $D/scripts && if [ -d /tmp/xiang_hf/hub/$MD/snapshots ] && [ ! -f /tmp/xiang_hf/hub/$MD.staging ]; then export HF_HUB_CACHE=/tmp/xiang_hf/hub; fi; CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 nohup /home/xiang/miniconda3/envs/verl-clean/bin/python run_lm.py --model $MODEL --inp $INP --out $OUT --shard $SHARD --nshard $NSHARD --bs $BS > $LOG 2>&1 &"
echo "launched $HOST:$GPU $MODEL shard $SHARD/$NSHARD -> $OUT (log $LOG)"
