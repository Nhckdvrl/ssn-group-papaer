#!/bin/bash
# L36 E00-EXT (exploratory, beyond the pre-registered gate) — modern arm beam sweep on the frozen
# newstest2019 substrate with the Gate-C-frozen checkpoint. Runs both scoring semantics.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
MODEL=google/gemma-3-12b-it
TAG=gemma3-12b
mkdir -p results/ext/gen results/ext/shards results/logs

# cheap cells first: one GPU each, large batches
run_small () {
  local BEAM=$1 SEM=$2 GPU=$3
  local out="results/ext/gen/${TAG}_b${BEAM}_${SEM}.jsonl"
  [ -s "$out" ] && { echo "[skip] $out"; return; }
  CUDA_VISIBLE_DEVICES=$GPU $PY src/run_llm_mt.py --model "$MODEL" --src data/newstest2019.en \
    --out "$out" --beam "$BEAM" --semantics "$SEM" --max-new-tokens 256 --beam-budget 256 \
    > "results/logs/ext_${TAG}_b${BEAM}_${SEM}.log" 2>&1
  echo "[gpu$GPU] done beam=$BEAM $SEM"
}

run_sharded () {
  local BEAM=$1 SEM=$2
  local out="results/ext/gen/${TAG}_b${BEAM}_${SEM}.jsonl"
  [ -s "$out" ] && { echo "[skip] $out"; return; }
  local parts=()
  for G in 0 1 2 3; do
    local part="results/ext/shards/${TAG}_b${BEAM}_${SEM}_s${G}.jsonl"
    parts+=("$part")
    if [ ! -s "$part" ]; then
      CUDA_VISIBLE_DEVICES=$G $PY src/run_llm_mt.py --model "$MODEL" --src data/newstest2019.en \
        --out "$part" --beam "$BEAM" --semantics "$SEM" --max-new-tokens 256 --beam-budget 256 \
        --shard $G --nshards 4 > "results/logs/ext_${TAG}_b${BEAM}_${SEM}_s${G}.log" 2>&1 &
    fi
  done
  wait
  $PY src/merge_shards.py "$out" "${parts[@]}"
}

run_small 1 RAW 0 &
run_small 4 RAW 2 &
run_small 4 NORM 3 &
wait
run_small 16 RAW 0 &
run_small 16 NORM 2 &
wait
run_sharded 64 RAW
run_sharded 64 NORM
echo "MODERN EXT DONE"
