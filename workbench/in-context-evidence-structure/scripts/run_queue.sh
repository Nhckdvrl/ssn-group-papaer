#!/bin/bash
# run_queue.sh HOST GPU DATA_NAME "model1 model2 ..." [SHARD NSHARD BS]
# runs models sequentially on one GPU (remote, detached)
HOST=$1; GPU=$2; DN=$3; MODELS=$4; SHARD=${5:-0}; NSHARD=${6:-1}; BS=${7:-32}
D=/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure
mkdir -p $D/results/$DN $D/logs
CMD="cd $D/scripts; "
for M in $MODELS; do
  N=$(basename $M); MD=models--$(echo $M | sed "s#/#--#g")
  OUT=$D/results/$DN/$N.s$SHARD.jsonl; LOG=$D/logs/run_${DN}_$N.s$SHARD.log
  CMD+="if [ -d /tmp/xiang_hf/hub/$MD/snapshots ] && [ ! -f /tmp/xiang_hf/hub/$MD.staging ]; then HC=/tmp/xiang_hf/hub; else HC=\$HOME/.cache/huggingface/hub; fi; "
  CMD+="CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 HF_HUB_CACHE=\$HC /home/xiang/miniconda3/envs/verl-clean/bin/python run_lm.py --model $M --inp $D/data/$DN/rows.jsonl --out $OUT --shard $SHARD --nshard $NSHARD --bs $BS > $LOG 2>&1; "
done
ssh -n -o ConnectTimeout=10 $HOST "nohup bash -c '$CMD' > /dev/null 2>&1 &"
echo "queued on $HOST:$GPU [$MODELS] shard $SHARD/$NSHARD"
