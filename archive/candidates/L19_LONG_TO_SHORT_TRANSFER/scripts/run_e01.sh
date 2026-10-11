#!/usr/bin/env bash
# E01 run driver.
#
# Order matters and is the point: the positive control runs FIRST, at the smallest
# budget, because kill condition D ("this regime has no identification power") is the
# one that ends the route and must be paid for before the treatment is.
#
#   stage 1  PC ladder      N=2000, escalate once to N=5000, hard stop there
#   stage 2  main contrast  only at the N the ladder licensed
#
# usage:  scripts/run_e01.sh pc 2000
#         scripts/run_e01.sh main 2000
set -euo pipefail
cd "$(dirname "$0")/.."
GPUS=${GPUS:-4}
mkdir -p logs results/sft

run () {  # run <condition> <seed> <n> <tag>
  local cond=$1 seed=$2 n=$3 tag=$4
  if [ -f "results/sft/$tag/run.json" ]; then echo "skip $tag (already done)"; return; fi
  echo "=== $tag : $cond seed=$seed n=$n  $(date +%H:%M) ==="
  .venv/bin/torchrun --nproc_per_node=$GPUS --master_port=${PORT:-29517} \
    scripts/train_sft.py --condition "$cond" --seed "$seed" --out "results/sft/$tag" \
    --n_nq "$n" --n_uc "$n" 2>&1 | tee -a "logs/$tag.log"
}

stage=${1:-pc}; N=${2:-2000}
case "$stage" in
  pc)
    run PC-UC-UC      1 "$N" "PC-UC-UC-n$N"
    run PC-UC-CHATQA2 1 "$N" "PC-UC-CHATQA2-n$N"
    echo "PC_STAGE_DONE n=$N — evaluate both before running stage 2"
    ;;
  main)
    run SHORT-SUPPORT 1 "$N" "SHORT-SUPPORT-n$N-s1"
    run LONG-FULL     1 "$N" "LONG-FULL-n$N-s1"
    run SHORT-SUPPORT 2 "$N" "SHORT-SUPPORT-n$N-s2"
    run LONG-FULL     2 "$N" "LONG-FULL-n$N-s2"
    echo "MAIN_STAGE_DONE n=$N"
    ;;
  *) echo "usage: $0 {pc|main} <N>"; exit 1;;
esac
