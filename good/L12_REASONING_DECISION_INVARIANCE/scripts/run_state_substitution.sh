#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-/home/xiang/miniconda3/envs/verl-clean/bin/python}"
gpu="${GPU:-3}"

CUDA_VISIBLE_DEVICES="$gpu" "$python_bin" "$project_dir/scripts/run_state_substitution.py" --device cuda:0
"$python_bin" "$project_dir/scripts/summarize_state_substitution.py"
