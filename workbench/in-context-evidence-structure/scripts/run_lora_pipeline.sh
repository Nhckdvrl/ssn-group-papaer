#!/bin/bash
# run_lora_pipeline.sh HOST GPU ARM SEED N_EPISODES TAG
# trains a LoRA arm on HOST:GPU, then scores confirm_v1 + conf_condarith with the merged model (host-local /tmp)
HOST=$1; GPU=$2; ARM=$3; SEED=$4; NEP=$5; TAG=$6
D=/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure
P=/home/xiang/miniconda3/envs/verl-clean/bin/python
M=/tmp/xiang_lora/${TAG}
CMD="cd $D/scripts; while nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | grep -q .; do sleep 30; done; export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 HF_HUB_CACHE=/tmp/xiang_hf/hub LEXICON=$D/data/lexicon_candidates.json; "
CMD+="$P lora_train.py --arm $ARM --seed $SEED --n_episodes $NEP --out $M > $D/logs/lora_${TAG}.log 2>&1; "
for DS in confirm_v1 conf_condarith; do
  mkdir -p $D/results/$DS
  CMD+="$P run_lm.py --model $M --inp $D/data/$DS/rows.jsonl --out $D/results/$DS/${TAG}.s0.jsonl --bs 32 > $D/logs/run_${DS}_${TAG}.s0.log 2>&1; "
done
ssh -n -o ConnectTimeout=10 $HOST "nohup bash -c '$CMD' > /dev/null 2>&1 &" 2>&1 | grep -v Warn
echo "queued LoRA $TAG ($ARM seed $SEED, $NEP episodes) on $HOST:$GPU"
