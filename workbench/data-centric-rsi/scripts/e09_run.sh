#!/usr/bin/env bash
# Frozen E09 Qwen3 teacher qualification. Invoke from the repository root.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo 'usage: e09_run.sh GPU_INDEX' >&2
  exit 2
fi
asset_root=/home/xiang/.cache/research/data-centric-rsi
out="$asset_root/runs/e09"
if [[ -e "$out" ]]; then
  echo "refusing to overwrite E09 assets: $out" >&2
  exit 2
fi
mkdir -p "$out"
source workbench/data-centric-rsi/scripts/env.sh
export CUDA_VISIBLE_DEVICES="$1"
export VLLM_ENABLE_V1_MULTIPROCESSING=0
git rev-parse HEAD > "$out/git_sha.txt"
nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv,noheader > "$out/gpu.txt"

"$DATA_RSI_PYTHON" workbench/data-centric-rsi/scripts/e09_generate.py \
  --pool "$asset_root/data/train_pool.jsonl" \
  --smoke "$asset_root/data/smoke.jsonl" \
  --feedback "$asset_root/runs/e00/base_zero_format_dev360.jsonl" \
  --dev "$asset_root/data/dev.jsonl" \
  --test-hashes "$asset_root/data/test_problem_hashes.txt" \
  --template-source "$asset_root/DataEnvGym/src/dataenvgym/gym/data_generation_agents/math/baselines/open_ended.py" \
  --start 0 --count 10 --max-tokens 3072 \
  --out "$out" \
  --manifest "$out/manifest.json" \
  > "$out/run.log" 2>&1
