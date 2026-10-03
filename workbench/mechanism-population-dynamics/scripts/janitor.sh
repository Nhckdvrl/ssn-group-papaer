#!/bin/bash
# Release claims of runs that failed with CUDA OOM (no result json, log contains OutOfMemoryError, log idle > 3 min).
cd "$(dirname "$0")/../results"
while true; do
  for e in e46 e48; do
    for d in $e/claims/*; do
      [ -d "$d" ] || continue; t=$(basename $d); f=$e/logs/$t.log
      [ -f $e/$t.json ] && continue
      [ -f "$f" ] && grep -q OutOfMemoryError "$f" && [ $(( $(date +%s) - $(stat -c %Y "$f") )) -gt 180 ] && rmdir "$d" && echo "$(date +%H:%M) released $e/$t"
    done
  done
  sleep 300
done
