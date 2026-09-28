#!/bin/bash
# L30 E01: 4 arms x 3 training seeds = 12 runs over 4 GPUs.
#
# Arms are interleaved across devices so that no arm is confounded with a
# particular card. Each GPU runs its three jobs sequentially.
set -u
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
PY=/home/xiang/miniconda3/envs/openslime/bin/python
export PYTHONPATH=/home/xiang/.cache/l30/pylibs
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=4
mkdir -p results/logs results/runs

GPU0="P:0 S:0 D_mask:0"
GPU1="D_rt:0 P:1 S:1"
GPU2="D_mask:1 D_rt:1 P:2"
GPU3="S:2 D_mask:2 D_rt:2"

run_series() {
  local dev=$1; shift
  for job in "$@"; do
    local arm=${job%%:*} seed=${job##*:}
    local out=$ROOT/results/runs/${arm}_s${seed}
    if [ -f "$out/DONE" ]; then echo "skip $arm s$seed (done)"; continue; fi
    echo "[gpu$dev] start $arm seed $seed at $(date -Is)"
    CUDA_VISIBLE_DEVICES=$dev $PY -u "$ROOT/src/train.py" \
      --arm "$arm" --seed "$seed" --epochs 3 --micro-batch 8 \
      > "$ROOT/results/logs/${arm}_s${seed}.log" 2>&1
    echo "[gpu$dev] end   $arm seed $seed rc=$? at $(date -Is)"
  done
}

run_series 0 $GPU0 &
run_series 1 $GPU1 &
run_series 2 $GPU2 &
run_series 3 $GPU3 &
wait
echo "ALL TRAINING DONE $(date -Is)"
