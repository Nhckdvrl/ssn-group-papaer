#!/bin/bash
# Serve a local model with vLLM (fgvd env: vllm 0.23, cu130; works on fvcrc20 driver 580).
# usage: serve.sh <gpu_ids> <model_repo> <port> [tp]
GPU=$1; MODEL=$2; PORT=$3; TP=${4:-1}
SNAP=$(ls -d ~/.cache/huggingface/hub/models--${MODEL/\//--}/snapshots/*/ | head -1)
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 FLASHINFER_CUDA_ARCH_LIST="12.0f" PATH=$HOME/miniconda3/envs/fgvd/bin:$PATH
exec ~/miniconda3/envs/fgvd/bin/python -m vllm.entrypoints.openai.api_server \
  --model "$SNAP" --served-model-name "$MODEL" --port $PORT --tensor-parallel-size $TP \
  --max-model-len 65536 --gpu-memory-utilization 0.88 --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder --reasoning-parser qwen3 --language-model-only
