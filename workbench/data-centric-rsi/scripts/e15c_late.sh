#!/usr/bin/env bash
# E15c "late materials": the final AZR weights propose code_i and code_o programs from the initial seed (vLLM seed 100,
# a batch separate from the grid), the AZR-style validator keeps the valid ones, exact (snippet, input) duplicates
# are dropped, and the result becomes an AZR-format materials file.  Runs on one GPU, then on the CPU.
# Usage: bash e15c_late.sh <gpu>
set -u
gpu=$1
S=$(dirname "$0"); M=/tmp/xiang_e15/models; D=/tmp/xiang_e15/data; O=/tmp/xiang_e15/azr; mkdir -p $O
F=andrewzh__Absolute_Zero_Reasoner-Coder-7b
for task in code_i code_o; do
  out=$O/late_${task}.jsonl
  [ -s $out.meta.json ] || bash $S/e15_run.sh $gpu late_$task e15c_propose.py --model $M/$F --materials $D/seed_materials.jsonl \
      --task $task --n 4096 --temp 1.0 --seed 100 --tag late_src --out $out || { echo "FAILED late $task"; exit 1; }
done
cd $S
export PYTHONPATH=/tmp/xiang_e15/vendor
~/.venvs/vllm023-cu128/bin/python -u e15c_validate.py --props $O/late_code_i.jsonl $O/late_code_o.jsonl \
    --materials $D/seed_materials.jsonl --out $O/late_validated.jsonl --workers 12 > /tmp/xiang_e15/logs/late_validate.log 2>&1 \
    || { echo "FAILED late validate"; exit 1; }
~/.venvs/vllm023-cu128/bin/python -u e15c_validate.py --materials_only $O/late_validated.jsonl --to_materials $D/late_materials.jsonl \
    || { echo "FAILED late materials"; exit 1; }
touch $D/late_materials.ready
echo "LATE_DONE $(wc -l < $D/late_materials.jsonl) materials $(date +%T)"
