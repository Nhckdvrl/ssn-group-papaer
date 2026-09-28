#!/usr/bin/env bash
# L13 pilot: E01 (commitment profile) + E02 (timeline-induced actualization).
# Usage: scripts/run_pilot.sh <model_slug> <gpu_id>
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-/home/xiang/miniconda3/envs/verl-clean/bin/python}"
model="${1:?model slug}"
gpu="${2:-2}"
config="${CONFIG:-$project_dir/configs/pilot_v1.json}"

"$python_bin" "$project_dir/scripts/build_stimuli.py"
"$python_bin" "$project_dir/scripts/validate_stimuli.py"

CUDA_VISIBLE_DEVICES="$gpu" HF_HUB_OFFLINE=1 "$python_bin" \
  "$project_dir/scripts/run_commitment.py" --config "$config" --model "$model" --device cuda:0
