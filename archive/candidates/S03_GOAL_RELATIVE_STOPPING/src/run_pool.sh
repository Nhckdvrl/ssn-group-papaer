#!/bin/bash
# S03 — keep all four cards busy.
#
# The earlier fixed-wave schedule left two cards idle during every 2250-step
# wave (~4.7 GPU-hours wasted across three seeds).  This pulls jobs from a
# queue instead, so a card picks up the next job the moment it frees.
# Completed runs are skipped, so restarting costs nothing.
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
QUEUE=$1
NGPU=${NGPU:-4}

worker () {           # $1 = gpu id
  local gpu=$1 line
  while true; do
    line=$(flock "$QUEUE.lock" -c "head -1 '$QUEUE'; sed -i 1d '$QUEUE'")
    [ -z "$line" ] && break
    eval "set -- $line"
    local fam=$1 arm=$2 lr=$3 st=$4 sd=$5 extra=${6:-}
    local tag="repl/${fam}_${arm}_st${st}_s${sd}"
    if [ -f "results/e02/${tag}/e01.jsonl" ]; then
      echo "[gpu$gpu] skip $tag"; continue
    fi
    echo "[gpu$gpu] start $tag $(date +%H:%M)"
    CUDA_VISIBLE_DEVICES=$gpu $PY src/e02_train.py --arm "$arm" --lr "$lr" \
        --family "$fam" --steps "$st" --seed "$sd" --bs 4 --accum 4 \
        --n-train 12000 --n-val 400 $extra --eval-after --tag "$tag" \
        > "results/logs/${fam}_${arm}_st${st}_s${sd}.log" 2>&1
    echo "[gpu$gpu] done  $tag $(date +%H:%M)"
  done
}

touch "$QUEUE.lock"
for g in $(seq 0 $((NGPU-1))); do worker $g & done
wait
echo "pool drained: $QUEUE"
