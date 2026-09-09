#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CUDA_VISIBLE_DEVICES="${L11_CUDA_VISIBLE_DEVICES:-0}" HF_DATASETS_OFFLINE=1 \
  /home/xiang/miniconda3/envs/verl-clean/bin/python "$project_dir/scripts/run_pilot.py"
