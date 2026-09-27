# usage: serve.sh MODEL_PATH NAME PORT GPU [extra vllm args...]
M=$1; N=$2; P=$3; G=$4; shift 4
export HF_HUB_OFFLINE=1
CUDA_VISIBLE_DEVICES=$G exec /home/xiang/miniconda3/envs/verl-clean/bin/python -m vllm.entrypoints.openai.api_server \
  --model $M --served-model-name $N --port $P --host 0.0.0.0 --gpu-memory-utilization 0.88 \
  --max-num-seqs 64 --enable-prefix-caching "$@"
