#!/bin/bash
# E87 queue worker: claims the next training job (atomic mkdir) and runs it on one GPU. Usage: run_e84.sh host:gpu
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
G=$1; H=${G%%:*}; D=${G##*:}
OUT=../results/e87
while read -r tag args; do
  [ -z "$tag" ] && continue
  [ -f "$OUT/logs/$tag.done" ] && continue
  mkdir "$OUT/claims/$tag" 2>/dev/null || continue
  ssh -n -o BatchMode=yes "$H" "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e46_train.py $args" > "$OUT/logs/$tag.log" 2>&1
  rc=$?; echo "$(date +%H:%M) [$G] $tag exit=$rc"
  if [ $rc -eq 0 ]; then touch "$OUT/logs/$tag.done"; else rmdir "$OUT/claims/$tag"; mv "$OUT/logs/$tag.log" "$OUT/logs/$tag.fail.log"; fi
done < $OUT/jobs.txt
