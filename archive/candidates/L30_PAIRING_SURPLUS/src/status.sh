#!/bin/bash
# One-shot health check for the L30 E01 pilot.
# Prints enough to tell "progressing normally" from "something died".
cd "$(dirname "$0")/.." || exit 1
echo "=== $(date -Is) ==="

echo "-- processes --"
echo "train.py:  $(pgrep -fc 'train.py --arm') running"
echo "launcher:  $(pgrep -fc 'launch_e01.sh') | chain: $(pgrep -fc 'chain.sh')"

echo "-- local GPUs --"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader

echo "-- training progress (step / 2424) --"
for f in results/logs/*_s*.log; do
  case "$f" in *interim*|*eval*) continue;; esac
  n=$(basename "$f" .log)
  last=$(grep -o "'step': [0-9]*" "$f" | tail -1 | grep -o '[0-9]*')
  loss=$(grep -o "'loss': [0-9.]*" "$f" | tail -1 | cut -d' ' -f2 | cut -c1-6)
  age=$(( ($(date +%s) - $(stat -c %Y "$f")) ))
  flag=""
  [ "$age" -gt 600 ] && flag="  <-- STALE ${age}s"
  [ -f "results/runs/$n/DONE" ] && flag="  DONE"
  printf "  %-12s step %-5s loss %-6s (log %ss ago)%s\n" "$n" "${last:-?}" "${loss:-?}" "$age" "$flag"
done

echo "-- completed runs --"
ls results/runs/*/DONE 2>/dev/null | sed 's|results/runs/||;s|/DONE||' | tr '\n' ' '; echo

echo "-- errors in training logs --"
grep -l -i "Traceback\|CUDA out of memory\|RuntimeError" results/logs/*_s*.log 2>/dev/null \
  | grep -v -E "interim|eval" | sed 's|results/logs/||' | tr '\n' ' '; echo

echo "-- evaluations done --"
ls -d results/evals/*/ 2>/dev/null | wc -l | tr -d '\n'; echo " of 36"
tail -2 results/logs/chain.log 2>/dev/null
