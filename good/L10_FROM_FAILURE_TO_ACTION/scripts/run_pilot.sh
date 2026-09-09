#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-/home/xiang/miniconda3/envs/verl-clean/bin/python}"
gpu="${GPU:-0}"

if [[ ! -f "$project_dir/data/upstream/implicitmembench/dataset/classical_conditioning/conditioned_api_aversion.json" ]]; then
  "$project_dir/scripts/fetch_parent_data.sh"
fi

CUDA_VISIBLE_DEVICES="$gpu" "$python_bin" "$project_dir/scripts/run_pilot.py" --device cuda:0
"$python_bin" "$project_dir/scripts/summarize_pilot.py"
