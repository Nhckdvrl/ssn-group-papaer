#!/bin/bash
# E77 queue worker: claims the next job in results/e77/jobs.txt (claim = atomic mkdir), runs it on one GPU.
# Usage: bash run_e77.sh <host:gpu>   (e.g. fvcrc11:2). Several workers share one job list.
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
G=$1; H=${G%%:*}; D=${G##*:}
OUT=../results/e77; mkdir -p $OUT/claims $OUT/logs
while read -r fam repo rev; do
  [ -z "$fam" ] && continue
  t="${fam}__$(basename $repo)__${rev}"
  [ -f "$OUT/runs/$t.json" ] && continue
  mkdir "$OUT/claims/$t" 2>/dev/null || continue
  ssh -n -o BatchMode=yes "$H" "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e77_atlas.py --family $fam --repo $repo --rev $rev" > "$OUT/logs/$t.log" 2>&1
  rc=$?; echo "$(date +%H:%M) [$G] $t exit=$rc"
  [ $rc -ne 0 ] && rmdir "$OUT/claims/$t" 2>/dev/null && mv "$OUT/logs/$t.log" "$OUT/logs/$t.fail.log"
done < $OUT/${JOBS:-jobs2.txt}
