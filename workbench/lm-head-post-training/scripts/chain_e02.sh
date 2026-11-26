#!/usr/bin/env bash
# E02 chain for one model on one GPU: rollouts -> replay geometry -> simulated head Adam.
# Usage: chain_e02.sh <gpu> <model_key>
set -uo pipefail
gpu=$1; mk=$2; D=$(dirname "$0")
"$D/run_vllm.sh" "$gpu" "e02r_$mk" e02_rollout.py --model "$mk" --n 8 --max_tokens 2048 || exit 1
"$D/run_node.sh" "$gpu" "e02g_$mk" e02_geometry.py --model "$mk" --rollouts "/tmp/xiang_lmhead/e02/rollouts_$mk.jsonl"
"$D/run_node.sh" "$gpu" "e02a_$mk" e02_headadam.py --model "$mk" --rollouts "/tmp/xiang_lmhead/e02/rollouts_$mk.jsonl"
