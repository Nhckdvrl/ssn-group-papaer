#!/bin/bash
# S03 / E04 — supervision-source decomposition, matched in everything but the
# supervision.  One cosine schedule per run; mid-run E01 evals come from that
# SAME schedule, so any dynamics are a real trajectory.
set -u
cd "$(dirname "$0")/.."
PY="/home/xiang/s03_venv/bin/python -u"
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SEED=${SEED:-0}
LR=${LR:-2e-5}
STEPS=${STEPS:-2250}

# mask:pairing
JOBS=(
  "full:correct"        # positive control — ordinary SFT on the real stage data
  "terminal:correct"    # only where responses end
  "content:correct"     # only what to keep saying; never told where to stop
  "full:shuffled"       # response distribution without its goal
  "terminal:shuffled"   # endpoints without the goal that determines them
)

i=0
for j in "${JOBS[@]}"; do
  mask=${j%%:*}; pair=${j##*:}
  tag="${mask}_${pair}_s${SEED}"
  [ -f "results/e04/${tag}/e01.jsonl" ] && { echo "skip $tag"; continue; }
  gpu=$((i % 4)); i=$((i+1))
  echo "[gpu$gpu] $tag"
  CUDA_VISIBLE_DEVICES=$gpu $PY src/e04_supervision.py \
      --mask "$mask" --pairing "$pair" --lr "$LR" --steps "$STEPS" \
      --seed "$SEED" --tag "$tag" \
      > "results/logs/e04_${tag}.log" 2>&1 &
  if [ $((i % 4)) -eq 0 ]; then wait; fi
done
wait
echo "e04 grid done (seed $SEED)"
