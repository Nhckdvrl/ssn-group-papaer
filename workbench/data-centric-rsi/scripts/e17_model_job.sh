#!/usr/bin/env bash
# E17-0: for one model on one node/GPU, wait until its weights are fully downloaded (no fetch process for the repo and
# an index or single safetensors present), then run solve (8/problem) and tests (4/problem).
# Usage: bash e17_model_job.sh <gpu> <tag> <repo> [<local dir name>]
set -uo pipefail
gpu=$1; tag=$2; repo=$3; dir=/tmp/xiang_e17/models/${4:-${repo//\//__}}
SC=$(cd "$(dirname "$0")" && pwd)
while pgrep -u "$USER" -f "e15_fetch.py /tmp/xiang_e17/models $repo" >/dev/null || ! ls "$dir"/*.safetensors >/dev/null 2>&1; do sleep 60; done
mkdir -p /tmp/xiang_e17/gen
bash "$SC/e17_run.sh" "$gpu" "solve_$tag" "$SC/e17_infer.py" --model "$dir" --problems /tmp/xiang_e17/problems.jsonl \
  --phase solve --n 16 --out "/tmp/xiang_e17/gen/solve_$tag.jsonl" || exit 1
bash "$SC/e17_run.sh" "$gpu" "tests_$tag" "$SC/e17_infer.py" --model "$dir" --problems /tmp/xiang_e17/problems.jsonl \
  --phase tests --n 4 --out "/tmp/xiang_e17/gen/tests_$tag.jsonl" || exit 1
echo done > "/tmp/xiang_e17/gen/DONE_$tag"
