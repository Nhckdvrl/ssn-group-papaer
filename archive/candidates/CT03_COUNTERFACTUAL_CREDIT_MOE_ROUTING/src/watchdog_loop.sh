#!/bin/bash
# Self-re-arming watchdog. Writes a status block every INTERVAL to
# results/logs/watchdog.log and EXITS (notifying the caller) only when something
# needs a human: terminal state, dead driver, stalled progress, or NaN.
# The previous version ran one cycle and relied on being manually re-armed,
# which is exactly how a 2h23m gap happened.
cd /home/xiang/ssn-group-papaer/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING
INT=${1:-3000}
LOG=results/logs/watchdog.log
prev=""
while true; do
  sleep "$INT"
  {
    echo "=== $(date -Is) ==="
    grep -E "^=== " results/logs/cpd_driver.log 2>/dev/null | tail -2
    pgrep -af "cpd_v1.py|cpd_freegen.py" | grep -v grep | sed 's/.*bin\/python/  worker:/' | cut -c1-70
    echo "  freegen batches: $(grep -cE '^  \[' results/logs/cpd_freegen.log 2>/dev/null || echo 0)"
    echo "  freegen rows: $(wc -l < results/cpd_freegen.jsonl 2>/dev/null || echo 0)"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | head -2 | sed 's/^/  gpu /'
  } >> $LOG 2>&1
  tail -12 $LOG

  if grep -qE "PIPELINE_COMPLETE|DRIVER_FAIL" results/logs/cpd_driver.log 2>/dev/null; then
    echo "WATCHDOG_EXIT: terminal"; grep -E "PIPELINE_COMPLETE|DRIVER_FAIL" results/logs/cpd_driver.log; exit 0
  fi
  if ! pgrep -f "run_cpd_v1.sh" >/dev/null; then
    echo "WATCHDOG_EXIT: driver dead with no terminal line"; tail -5 results/logs/cpd_driver.log; exit 1
  fi
  cur="$(grep -cE '^  \[' results/logs/cpd_freegen.log 2>/dev/null)-$(cat results/cpd_train_*.jsonl 2>/dev/null | wc -l)"
  if [ "$cur" = "$prev" ]; then
    echo "WATCHDOG_EXIT: no progress in ${INT}s (marker $cur)"; exit 1
  fi
  prev="$cur"
  if grep -qiE '"loss": *(nan|infinity)' results/cpd_train_*.jsonl 2>/dev/null; then
    echo "WATCHDOG_EXIT: NaN in training log"; exit 1
  fi
done
