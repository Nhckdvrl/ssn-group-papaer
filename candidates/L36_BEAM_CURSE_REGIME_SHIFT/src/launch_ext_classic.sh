#!/bin/bash
# L36 E00-EXT (exploratory) — extend the classic grid into ACL-2022 Figure 2's catastrophic range
# (beams 128/256/512), RAW only: the NORM arm is already flat across 1..64, and the question here is
# whether the *reversed* uncertainty conditioning of the RAW curse ever turns over.
# usage: launch_ext_classic.sh <gpu_a> <gpu_b>
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; cd "$HERE"
V="$HERE/vendor"; export PYTHONPATH="$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
mkdir -p results/ext/gen results/logs
run () {
  local BEAM=$1 GPU=$2
  local out="results/ext/gen/fsmt_b${BEAM}_RAW.jsonl"
  [ -s "$out" ] && { echo "[skip] $out"; return; }
  echo "[gpu$GPU] fsmt beam=$BEAM RAW"
  CUDA_VISIBLE_DEVICES=$GPU $PY src/run_beam_sweep.py --model facebook/wmt19-en-de \
    --src data/newstest2019.en --out "$out" --beam "$BEAM" --semantics RAW \
    --max-new-tokens 256 --beam-budget 512 > "results/logs/ext_fsmt_b${BEAM}_RAW.log" 2>&1
  echo "[gpu$GPU] done beam=$BEAM"
}
run 256 "${1:-0}" &
run 512 "${2:-0}" &
wait
echo "CLASSIC EXT DONE"
