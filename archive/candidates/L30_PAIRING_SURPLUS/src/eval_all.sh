#!/bin/bash
# Evaluate every finished L30 E01 adapter on IFEval, plus the untuned base.
# Epoch 3 is the pre-registered primary; 1 and 2 are the trajectory.
set -u
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
PY=/home/xiang/miniconda3/envs/openslime/bin/python
export PYTHONPATH=/home/xiang/.cache/l30/pylibs:$ROOT/src
export NLTK_DATA=/home/xiang/.cache/l30/nltk_data
export TOKENIZERS_PARALLELISM=false
mkdir -p results/evals results/logs

EPOCHS=${EPOCHS:-"3 2 1"}
JOBS=()
for ep in $EPOCHS; do
  for arm in P S D_mask D_rt; do
    for seed in 0 1 2; do
      JOBS+=("$arm:$seed:$ep")
    done
  done
done

worker() {
  local dev=$1 start=$2 stride=$3 i=0
  for job in "${JOBS[@]}"; do
    if [ $(( i % stride )) -eq $start ]; then
      local arm=$(echo "$job" | cut -d: -f1)
      local seed=$(echo "$job" | cut -d: -f2)
      local ep=$(echo "$job" | cut -d: -f3)
      local ad=$ROOT/results/runs/${arm}_s${seed}/adapter_ep${ep}.pt
      local out=$ROOT/results/evals/${arm}_s${seed}_ep${ep}
      if [ ! -f "$ad" ]; then echo "[gpu$dev] missing $ad"; i=$((i+1)); continue; fi
      if [ -f "$out/summary.json" ]; then echo "[gpu$dev] skip ${arm}_s${seed}_ep${ep}"; i=$((i+1)); continue; fi
      echo "[gpu$dev] eval ${arm}_s${seed}_ep${ep} at $(date -Is)"
      CUDA_VISIBLE_DEVICES=$dev $PY -u "$ROOT/src/evaluate.py" --adapter "$ad" --out "$out" \
        > "$ROOT/results/logs/eval_${arm}_s${seed}_ep${ep}.log" 2>&1 || echo "[gpu$dev] FAILED $job"
    fi
    i=$((i+1))
  done
}

if [ ! -f "$ROOT/results/evals/base/summary.json" ]; then
  echo "evaluating untuned base"
  CUDA_VISIBLE_DEVICES=0 $PY -u "$ROOT/src/evaluate.py" --out "$ROOT/results/evals/base" \
    > "$ROOT/results/logs/eval_base.log" 2>&1
fi

for d in 0 1 2 3; do worker "$d" "$d" 4 & done
wait
echo "ALL EVALS DONE $(date -Is)"
