#!/bin/bash
# C1: text parents of the speech/duplex models, served one at a time with vLLM 0.11 on one GPU; battery generations only
# (labels come later from battery_judge.py). usage: c1_text_parents.sh <gpu>
GPU=$1; EXP=/home/xiang/ssn-group-papaer/workbench/realtime-computation-boundaries/experiments
Q=/home/xiang/ssn-group-papaer/workbench/omni-recon/probes/battery.json; R=/home/xiang/rt_ext/runs/c1; L=/home/xiang/rt_ext/logs
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
snap() { ls -d ~/.cache/huggingface/hub/models--${1/\//--}/snapshots/*/ | head -1; }
for spec in "Qwen/Qwen3-8B|$(snap Qwen/Qwen3-8B)|--reasoning-parser qwen3" "Qwen/Qwen2-7B-Instruct|$(snap Qwen/Qwen2-7B-Instruct)|" \
            "Qwen/Qwen2.5-7B-Instruct|$(snap Qwen/Qwen2.5-7B-Instruct)|" "glm-4-9b-chat|/home/xiang/rt_ext/models/glm-4-9b-chat-hf|"; do
  IFS='|' read NAME PATHM EXTRA <<< "$spec"; TAG=$(basename $NAME)
  [ -s $R/text_$TAG.json ] && continue
  CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 $PY -m vllm.entrypoints.openai.api_server --model $PATHM --served-model-name $NAME \
    --port 8104 --max-model-len 8192 --gpu-memory-utilization 0.85 --trust-remote-code $EXTRA > $L/c1_vllm_$TAG.log 2>&1 &
  SP=$!
  until curl -s localhost:8104/v1/models >/dev/null; do sleep 5; kill -0 $SP 2>/dev/null || break; done
  (cd $EXP && LANGS=en NOJUDGE=1 $PY epistemic_eval.py --backend openai --url http://localhost:8104/v1 --model $NAME \
     --seeds 2 --queries $Q --out $R/text_$TAG.json > $L/c1_text_$TAG.log 2>&1)
  kill $SP; wait $SP 2>/dev/null
done
echo ALLDONE
