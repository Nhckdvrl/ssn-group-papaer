#!/bin/bash
# E92 queue worker (capability atlas): like run_e89.sh, but each checkpoint is downloaded into a per-job cache on the
# host's local /tmp and deleted after the run (one-off intermediate checkpoints must not stay in the shared HF cache).
# Usage: bash run_e90.sh <host:gpu>
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
G=$1; H=${G%%:*}; D=${G##*:}
OUT=../results/e92; mkdir -p $OUT/claims $OUT/logs
while read -r fam repo rev; do
  [ -z "$fam" ] && continue
  t="$(basename $repo)__${rev}"
  [ -f "$OUT/$t.json" ] && continue
  mkdir "$OUT/claims/$t" 2>/dev/null || continue
  C=/tmp/xiang_e92/$t
  ssh -n -o BatchMode=yes "$H" "cd $PWD && E89_MODEL_CACHE=$C CUDA_VISIBLE_DEVICES=$D $PY e92_atlas.py --repo $repo --rev $rev; rc=\$?; rm -rf $C; exit \$rc" > "$OUT/logs/$t.log" 2>&1
  rc=$?; echo "$(date +%H:%M) [$G] $t exit=$rc"
  [ $rc -ne 0 ] && rmdir "$OUT/claims/$t" 2>/dev/null && mv "$OUT/logs/$t.log" "$OUT/logs/$t.fail.log"
done < $OUT/${JOBS:-jobs.txt}
