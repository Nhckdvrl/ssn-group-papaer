#!/bin/bash
# Evaluate L30 E01 adapters on a remote A100 node.
#
# ALL evaluation runs on A100 hardware while training stays on the local
# Blackwell cards. Mixing hardware across arms is not acceptable here: greedy
# decoding can flip a token on a tiny numerical difference, and the contrast we
# need to resolve is only a few percentage points. Keeping every arm on one
# device class removes that as a source of between-arm difference.
#
# usage: eval_remote.sh <out_subdir> <epoch_list> [arm:seed ...]
set -u
ROOT=/home/xiang/ssn-group-papaer/candidates/L30_PAIRING_SURPLUS
PY=/home/xiang/miniconda3/envs/openslime/bin/python
export PYTHONPATH=/home/xiang/.cache/l30/pylibs:$ROOT/src
export NLTK_DATA=/home/xiang/.cache/l30/nltk_data
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1

OUTDIR=$1; shift
EPOCHS=$1; shift
JOBS=("$@")
mkdir -p "$ROOT/results/$OUTDIR" "$ROOT/results/logs"

NGPU=$(nvidia-smi --query-gpu=index --format=csv,noheader | wc -l)
i=0
for job in "${JOBS[@]}"; do
  arm=${job%%:*}; seed=${job##*:}
  for ep in $EPOCHS; do
    dev=$(( i % NGPU )); i=$((i+1))
    ad=$ROOT/results/runs/${arm}_s${seed}/adapter_ep${ep}.pt
    out=$ROOT/results/$OUTDIR/${arm}_s${seed}_ep${ep}
    [ -f "$ad" ] || { echo "missing $ad"; continue; }
    [ -f "$out/summary.json" ] && { echo "skip ${arm}_s${seed}_ep${ep}"; continue; }
    (
      echo "[$(hostname) gpu$dev] ${arm}_s${seed}_ep${ep} start $(date -Is)"
      CUDA_VISIBLE_DEVICES=$dev $PY -u "$ROOT/src/evaluate.py" --adapter "$ad" \
        --out "$out" --batch-size 48 \
        > "$ROOT/results/logs/${OUTDIR}_${arm}_s${seed}_ep${ep}.log" 2>&1 \
        && echo "[$(hostname) gpu$dev] ${arm}_s${seed}_ep${ep} ok" \
        || echo "[$(hostname) gpu$dev] ${arm}_s${seed}_ep${ep} FAILED"
    ) &
    if [ $(( i % NGPU )) -eq 0 ]; then wait; fi
  done
done
wait
echo "REMOTE EVAL DONE $(hostname) $(date -Is)"
