#!/bin/bash
# S03 — core parameter-locus replication on a second/third model family.
#
# Only the load-bearing arms: Arm0 (lr=0 R, bit-identical to base by the
# zero-init construction) / R / Sbody / F.  Rmlp stays OLMo-only: it answers
# "is a linear readout too weak?", which needs answering once, not per family.
#
# The question this must replicate:
#   does R raise stop promotion while leaving continuation clearing at exactly
#   zero, and does Sbody produce BOTH promotion and clearing?
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FAM=$1; LR_R=$2; LR_S=$3
mkdir -p results/logs

job () { # arm lr steps seed gpu extra...
  local arm=$1 lr=$2 st=$3 sd=$4 gpu=$5; shift 5
  local tag="repl/${FAM}_${arm}_st${st}_s${sd}"
  [ -f "results/e02/${tag}/e01.jsonl" ] && { echo "skip $tag"; return; }
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
      --family "$FAM" --steps "$st" --seed "$sd" --bs 4 --accum 4 \
      --n-train 12000 --n-val 400 "$@" --eval-after --tag "$tag" \
      > "results/logs/${FAM}_${arm}_st${st}_s${sd}.log" 2>&1
}

# Arm 0 once: lr=0 leaves the zero-init readout at zero.
job R 0 1 0 0

# R is cheap (frozen forward, no grad through the transformer): all rungs/seeds.
for sd in 0 1 2; do
  job R "$LR_R" 250 $sd 0 & job R "$LR_R" 750 $sd 1 & job R "$LR_R" 2250 $sd 2 & wait
done

# Sbody and F are full-size; run them two at a time across the four cards.
for sd in 0 1 2; do
  job Sbody "$LR_S" 250  $sd 0 --opt8bit & job F "$LR_S" 250  $sd 1 --opt8bit &
  job Sbody "$LR_S" 750  $sd 2 --opt8bit & job F "$LR_S" 750  $sd 3 --opt8bit & wait
  job Sbody "$LR_S" 2250 $sd 0 --opt8bit & job F "$LR_S" 2250 $sd 1 --opt8bit & wait
done
echo "replication $FAM done"
