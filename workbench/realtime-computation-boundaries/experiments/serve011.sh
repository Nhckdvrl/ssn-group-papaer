#!/bin/bash
# vLLM 0.11 from the existing verl-clean env (fgvd's vllm 0.23 needs a flashinfer JIT/nvcc on this host).
# usage: serve011.sh <gpu_ids> <model_repo> <port> [tp]
GPU=$1; MODEL=$2; PORT=$3; TP=${4:-1}
SNAP=$(ls -d ~/.cache/huggingface/hub/models--${MODEL/\//--}/snapshots/*/ | head -1)
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1
exec ~/miniconda3/envs/verl-clean/bin/python -m vllm.entrypoints.openai.api_server \
  --model "$SNAP" --served-model-name "$MODEL" --port $PORT --tensor-parallel-size $TP \
  --max-model-len 40960 --gpu-memory-utilization ${UTIL:-0.88} --enable-auto-tool-choice \
  --tool-call-parser hermes --reasoning-parser qwen3
