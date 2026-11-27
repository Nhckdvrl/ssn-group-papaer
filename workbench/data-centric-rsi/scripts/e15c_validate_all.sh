#!/usr/bin/env bash
# E15c: validate every finished proposal file (prop_*.jsonl with its .meta.json) that has no validated output yet,
# against the materials file it was generated from (seed or late, read from the file name). CPU only.
# Usage: bash e15c_validate_all.sh [workers=8]
set -u
w=${1:-8}
S=$(cd "$(dirname "$0")" && pwd); D=/tmp/xiang_e15/data; O=/tmp/xiang_e15/azr
export PYTHONPATH=/tmp/xiang_e15/vendor
for meta in $O/prop_*.jsonl.meta.json; do
  f=${meta%.meta.json}; base=$(basename $f); out=$O/val_$base
  [ -s $out ] && continue
  case $base in *_seed_*) mat=$D/seed_materials.jsonl ;; *_late_*) mat=$D/late_materials.jsonl ;; *) continue ;; esac
  (cd $S && ~/.venvs/vllm023-cu128/bin/python -u e15c_validate.py --props $f --materials $mat --out $out.tmp --workers $w) \
    && mv $out.tmp $out && echo "validated $base"
done
echo VALIDATE_PASS_DONE
