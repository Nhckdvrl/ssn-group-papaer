#!/bin/bash
# E89 queue worker: claims the next model in results/e89/${JOBS:-models.txt} (claim = atomic mkdir) and runs it on one GPU.
# Usage: bash run_e89.sh <host:gpu>
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
G=$1; H=${G%%:*}; D=${G##*:}
OUT=../results/e89; mkdir -p $OUT/claims $OUT/logs
while read -r fam repo rev; do
  [ -z "$fam" ] && continue
  t="${fam}__$(basename $repo)__${rev}"
  [ -f "$OUT/$t.json" ] && continue
  mkdir "$OUT/claims/$t" 2>/dev/null || continue
  ssh -n -o BatchMode=yes "$H" "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e89_labor.py --family $fam --repo $repo --rev $rev --chunk 16" > "$OUT/logs/$t.log" 2>&1
  rc=$?; echo "$(date +%H:%M) [$G] $t exit=$rc"
  [ $rc -ne 0 ] && rmdir "$OUT/claims/$t" 2>/dev/null && mv "$OUT/logs/$t.log" "$OUT/logs/$t.fail.log"
done < $OUT/${JOBS:-models.txt}
