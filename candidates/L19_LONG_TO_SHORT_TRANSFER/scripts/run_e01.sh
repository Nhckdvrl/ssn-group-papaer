#!/usr/bin/env bash
# E01 run driver. Runs are sequential; all four GPUs serve one run at a time.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
GPUS=${GPUS:-4}
run () {  # run <condition> <seed> <tag>
  local cond=$1 seed=$2 tag=$3
  if [ -f "results/sft/$tag/run.json" ]; then echo "skip $tag (done)"; return; fi
  echo "=== $tag : $cond seed=$seed  $(date +%H:%M) ==="
  .venv/bin/torchrun --nproc_per_node=$GPUS --master_port=${PORT:-29517} \
    scripts/train_sft.py --condition "$cond" --seed "$seed" --out "results/sft/$tag" \
    2>&1 | tee -a "logs/$tag.log"
}
mkdir -p logs results/sft
run SHORT-SUPPORT  1 SHORT-SUPPORT-s1
run LONG-FULL      1 LONG-FULL-s1
run SHORT-SUPPORT  2 SHORT-SUPPORT-s2
run LONG-FULL      2 LONG-FULL-s2
run PC-UC-UC       1 PC-UC-UC-s1
run PC-UC-CHATQA2  1 PC-UC-CHATQA2-s1
echo "ALL_E01_TRAINING_DONE"
