#!/bin/bash
# L36 E00 Gate B — classic positive control beam sweep.
# Local host only (fvcrc21, 4x RTX PRO 6000); 4 concurrent cells, well inside the 8-card cap.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
V="$HERE/vendor"
export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
mkdir -p results/e00/gen results/logs

JOBS=()
for MODEL_TAG in "facebook/wmt19-en-de:fsmt" "Helsinki-NLP/opus-mt-en-de:marian"; do
  MODEL="${MODEL_TAG%%:*}"; TAG="${MODEL_TAG##*:}"
  for BEAM in 1 4 8 16 32 64; do
    for SEM in RAW NORM; do
      # beam 1 is greedy: the length penalty cannot apply, so it is run once and reused
      if [ "$BEAM" = "1" ] && [ "$SEM" = "NORM" ]; then continue; fi
      JOBS+=("$MODEL|$TAG|$BEAM|$SEM")
    done
  done
done

run_job () {
  local job="$1" gpu="$2"
  IFS='|' read -r MODEL TAG BEAM SEM <<< "$job"
  local out="results/e00/gen/${TAG}_b${BEAM}_${SEM}.jsonl"
  local log="results/logs/e00_gateB_${TAG}_b${BEAM}_${SEM}.log"
  if [ -s "$out" ]; then echo "[skip] $out"; return; fi
  echo "[gpu$gpu] $TAG beam=$BEAM $SEM -> $out"
  CUDA_VISIBLE_DEVICES="$gpu" $PY src/run_beam_sweep.py \
    --model "$MODEL" --src data/newstest2019.en --out "$out" \
    --beam "$BEAM" --semantics "$SEM" --max-new-tokens 256 --beam-budget 256 \
    > "$log" 2>&1
  echo "[gpu$gpu] done $TAG beam=$BEAM $SEM rc=$?"
}

NGPU=4
i=0
for job in "${JOBS[@]}"; do
  gpu=$(( i % NGPU ))
  run_job "$job" "$gpu" &
  i=$(( i + 1 ))
  if (( i % NGPU == 0 )); then wait; fi
done
wait
echo "ALL GATE B CELLS DONE"
