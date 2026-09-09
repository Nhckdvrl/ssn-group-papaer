#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-/home/xiang/miniconda3/envs/verl-clean/bin/python}"
gpu_instruct="${GPU_INSTRUCT:-2}"
gpu_think="${GPU_THINK:-3}"

CUDA_VISIBLE_DEVICES="$gpu_instruct" "$python_bin" "$project_dir/scripts/run_boundary.py" --model-index 0 --device cuda:0 &
p0=$!
CUDA_VISIBLE_DEVICES="$gpu_think" "$python_bin" "$project_dir/scripts/run_boundary.py" --model-index 1 --device cuda:0 &
p1=$!
wait "$p0" "$p1"

"$python_bin" "$project_dir/scripts/summarize_boundary.py"
