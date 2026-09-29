#!/bin/bash
# E04: same agent (Qwen3-32B) and user LLM (Qwen3-30B-A3B), text half-duplex, perfect transcripts.
# Only change: user simulator guidelines = standard text vs tau-voice VOICE-call guidelines.
cd /home/xiang/rt_ext/tau2-bench
AG='{"api_base":"http://localhost:8102/v1","api_key":"x","temperature":0.0}'
US='{"api_base":"http://localhost:8101/v1","api_key":"x","temperature":0.0,"extra_body":{"chat_template_kwargs":{"enable_thinking":false}}}'
R=/home/xiang/ssn-group-papaer/workbench/realtime-agent-capability-transition/experiments/e04_run.py
for dom in airline; do
 for style in text voice; do
  USER_STYLE=$style .venv/bin/python $R run --domain $dom --agent-llm hosted_vllm/Qwen/Qwen3-32B --agent-llm-args "$AG" \
   --user-llm hosted_vllm/Qwen/Qwen3-30B-A3B --user-llm-args "$US" --num-tasks 50 --num-trials 1 \
   --save-to /home/xiang/rt_ext/runs/e04_${dom}_${style} --max-concurrency 8 > /home/xiang/rt_ext/logs/e04_${dom}_${style}.log 2>&1 &
 done
done
wait; echo E04 AIRLINE DONE
