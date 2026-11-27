#!/usr/bin/env bash
# E15b generation queue for one GPU: runs the listed jobs one after another.
# Job spec: <tag>:<model dir name>:<seed>; each job samples 4,000 candidates.
# Usage: bash e15b_gen_queue.sh <gpu> <job> [<job> ...]
set -u
gpu=$1; shift
M=/tmp/xiang_e15/models; O=/tmp/xiang_e15/gen; mkdir -p $O
TPL=$M/jinyuan222__qwen3_4b_fullrun_authorsettings_questioner_v1
for job in "$@"; do
  IFS=: read tag model seed <<< "$job"
  out=$O/gen_${tag}_s${seed}.jsonl
  [ -s "$out.meta.json" ] && { echo "skip $job"; continue; }
  bash "$(dirname "$0")/e15_run.sh" $gpu gen_${tag}_s${seed} e15b_generate.py --model $M/$model --template_dir $TPL \
       --n 4000 --seed $seed --tag $tag --out $out || echo "FAILED $job"
done
echo QUEUE_DONE
