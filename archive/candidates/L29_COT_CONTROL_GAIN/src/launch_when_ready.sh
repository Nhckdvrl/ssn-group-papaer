#!/usr/bin/env bash
set -euo pipefail
step=$1
card=$2
phase=${3:-natural}
root=/home/xiang/ssn-group-papaer/candidates/L29_COT_CONTROL_GAIN
model_root=${L29_MODEL_ROOT:-/tmp/xiang-l29/checkpoints}
started=$SECONDS
while [[ ! -f "$model_root/$step/L29_DOWNLOAD_COMPLETE" ]]; do
  if (( SECONDS - started > 3600 )); then echo 'Download readiness timeout; no GPU allocated'; exit 75; fi
  sleep 5
done
free=$(nvidia-smi -i "$card" --query-gpu=memory.free --format=csv,noheader,nounits)
util=$(nvidia-smi -i "$card" --query-gpu=utilization.gpu --format=csv,noheader,nounits)
if (( free < 75000 || util > 0 )); then echo "GPU $card no longer idle: ${free} MiB free, ${util}% utilization. Not starting."; exit 75; fi
export CUDA_VISIBLE_DEVICES=$card
export L29_MODEL_ROOT=$model_root
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1
export OMP_NUM_THREADS=4
exec timeout 1200 /home/xiang/interesting/.venv-a100/bin/python -u "$root/src/run_audit.py" --step "$step" --phase "$phase" --batch-size 8
