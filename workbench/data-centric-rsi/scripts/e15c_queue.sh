#!/usr/bin/env bash
# E15c proposal queue for one GPU on fvcrc10: runs the listed jobs one after another.
# Job spec: <tag>:<model dir name>:<materials: seed|late>:<task>:<temp>:<seed>[:<n>]; n defaults to 1,024 for the
# initial weights (tag init; most outputs run to the 8,096-token limit) and 4,096 for the final weights.
# "late" jobs wait until the late-materials file has been built (see e15c_late.sh).
# Usage: bash e15c_queue.sh <gpu> <job> [<job> ...]
set -u
gpu=$1; shift
M=/tmp/xiang_e15/models; D=/tmp/xiang_e15/data; O=/tmp/xiang_e15/azr; mkdir -p $O
for job in "$@"; do
  IFS=: read tag model mat task temp seed n <<< "$job"
  [ -n "$n" ] || { [ "$tag" = init ] && n=1024 || n=4096; }
  out=$O/prop_${tag}_${mat}_${task}_t${temp}_s${seed}.jsonl
  [ -s "$out.meta.json" ] && { echo "skip $job"; continue; }
  until [ -e $D/${mat}_materials.ready ]; do sleep 60; done
  bash "$(dirname "$0")/e15_run.sh" $gpu prop_${tag}_${mat}_${task}_t${temp}_s${seed} e15c_propose.py --model $M/$model \
       --materials $D/${mat}_materials.jsonl --task $task --n $n --temp $temp --seed $seed --tag $tag --out $out \
       || echo "FAILED $job"
done
echo QUEUE_DONE
