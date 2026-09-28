#!/bin/bash
# Fast go/no-go read: evaluate the first epoch-1 adapter of each arm as soon as
# it exists, concurrently with ongoing training. One seed per arm (they differ),
# so this answers "is there a resolvable P-vs-S gap at all", not the estimand.
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
PY=/home/xiang/miniconda3/envs/openslime/bin/python
export PYTHONPATH=/home/xiang/.cache/l30/pylibs:$ROOT/src
export NLTK_DATA=/home/xiang/.cache/l30/nltk_data
export TOKENIZERS_PARALLELISM=false
mkdir -p results/evals_interim results/logs

# arm:seed:gpu -- matches the four jobs currently training
JOBS=("P:0:0" "D_rt:0:1" "D_mask:1:2" "S:2:3")
for job in "${JOBS[@]}"; do
(
  arm=${job%%:*}; rest=${job#*:}; seed=${rest%%:*}; dev=${rest##*:}
  ad=$ROOT/results/runs/${arm}_s${seed}/adapter_ep1.pt
  while [ ! -f "$ad" ]; do sleep 60; done
  sleep 20   # let the checkpoint finish writing
  out=$ROOT/results/evals_interim/${arm}_s${seed}_ep1
  echo "[interim] eval ${arm}_s${seed} ep1 on gpu$dev at $(date -Is)"
  CUDA_VISIBLE_DEVICES=$dev $PY -u "$ROOT/src/evaluate.py" --adapter "$ad" --out "$out" \
    --batch-size 16 > "$ROOT/results/logs/interim_${arm}_s${seed}.log" 2>&1 \
    || echo "[interim] FAILED $job"
) &
done
wait
echo "INTERIM DONE $(date -Is)"
for d in results/evals_interim/*/summary.json; do
  $PY -c "import json,sys;d=json.load(open('$d'));print(f\"{d.get('arm','?'):8s} s{d.get('seed','?')} ep{d.get('epoch','?')}  strict_prompt={100*d['strict_prompt_acc']:.2f}  strict_instr={100*d['strict_instruction_acc']:.2f}  loose_prompt={100*d['loose_prompt_acc']:.2f}  chars={d['mean_response_chars']:.0f}\")"
done
