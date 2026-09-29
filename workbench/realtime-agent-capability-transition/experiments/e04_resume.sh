#!/bin/bash
# resume one E04 run: e04_resume.sh <domain> <style> <agent_port> [concurrency]
cd /home/xiang/rt_ext/tau2-bench
AG="{\"api_base\":\"http://localhost:$3/v1\",\"api_key\":\"x\",\"temperature\":0.0}"
US='{"api_base":"http://localhost:8101/v1","api_key":"x","temperature":0.0,"extra_body":{"chat_template_kwargs":{"enable_thinking":false}}}'
USER_STYLE=$2 exec .venv/bin/python /home/xiang/ssn-group-papaer/workbench/realtime-agent-capability-transition/experiments/e04_run.py run \
  --domain $1 --agent-llm hosted_vllm/Qwen/Qwen3-32B --agent-llm-args "$AG" --user-llm hosted_vllm/Qwen/Qwen3-30B-A3B \
  --user-llm-args "$US" --num-tasks 50 --num-trials 1 --save-to /home/xiang/rt_ext/runs/e04_$1_$2 --max-concurrency ${4:-8} --auto-resume
