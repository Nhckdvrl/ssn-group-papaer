#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin=/home/xiang/miniconda3/envs/verl-clean/bin/python

CUDA_VISIBLE_DEVICES=0 "$python_bin" "$project_dir/scripts/run_model.py" --model-index 0 --device cuda:0 &
p0=$!
CUDA_VISIBLE_DEVICES=2 "$python_bin" "$project_dir/scripts/run_model.py" --model-index 1 --device cuda:0 &
p1=$!
CUDA_VISIBLE_DEVICES=3 "$python_bin" "$project_dir/scripts/run_model.py" --model-index 2 --device cuda:0 &
p2=$!
wait "$p0" "$p1" "$p2"
"$python_bin" "$project_dir/scripts/summarize_behavior.py"
"$python_bin" "$project_dir/scripts/probe_frames.py"
