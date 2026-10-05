#!/bin/bash
# run_queue2.sh HOST GPU "DATA:MODEL[:SHARD:NSHARD] ..." [BS]
# waits until the GPU is free, then runs items sequentially (remote, detached)
HOST=$1; GPU=$2; ITEMS=$3; BS=${4:-32}
D=/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure
CMD="cd $D/scripts; while nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | grep -q .; do sleep 30; done; "
for IT in $ITEMS; do
  IFS=: read DN M SH NS <<< "$IT"; SH=${SH:-0}; NS=${NS:-1}
  N=$(basename $M); MD=models--$(echo $M | sed "s#/#--#g")
  mkdir -p $D/results/$DN
  OUT=$D/results/$DN/$N.s$SH.jsonl; LOG=$D/logs/run_${DN}_$N.s$SH.log
  CMD+="if [ -d /tmp/xiang_hf/hub/$MD/snapshots ] && [ ! -f /tmp/xiang_hf/hub/$MD.staging ]; then HC=/tmp/xiang_hf/hub; else HC=\$HOME/.cache/huggingface/hub; fi; "
  if [[ $M == *Qwen3.5* ]] || [[ $M == *Nemotron-H* ]]; then PYB="PYTHONPATH=$D/scripts/vendor /home/xiang/miniconda3/envs/openslime/bin/python"; else PYB=/home/xiang/miniconda3/envs/verl-clean/bin/python; fi
  CMD+="CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 HF_HUB_CACHE=\$HC $PYB run_lm.py --model $M --inp $D/data/$DN/rows.jsonl --out $OUT --shard $SH --nshard $NS --bs $BS > $LOG 2>&1; "
done
ssh -n -o ConnectTimeout=10 $HOST "nohup bash -c '$CMD' > /dev/null 2>&1 &" 2>&1 | grep -v Warn
echo "queued on $HOST:$GPU [$ITEMS]"
