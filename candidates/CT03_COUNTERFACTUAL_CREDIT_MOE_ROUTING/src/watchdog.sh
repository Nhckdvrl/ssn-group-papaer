#!/bin/bash
# One 50-minute cycle: sleep, then report enough to tell "healthy" from "stuck"
# or "silently broken". Exits so the caller is notified; re-arm for the next.
cd /home/xiang/ssn-group-papaer/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING
sleep "${1:-3000}"
echo "=== WATCHDOG $(date -Is) ==="
if grep -qE "PIPELINE_COMPLETE|DRIVER_FAIL" results/logs/cpd_driver.log 2>/dev/null; then
  echo "TERMINAL:"; grep -E "PIPELINE_COMPLETE|DRIVER_FAIL" results/logs/cpd_driver.log; exit 0
fi
pgrep -f "run_cpd_v1.sh" >/dev/null && echo "driver: alive" || echo "driver: DEAD (no terminal line!)"
pgrep -af "cpd_v1.py|cpd_freegen.py" | grep -v grep | sed 's/.*bin\/python/  worker:/' | cut -c1-80
echo "stage: $(grep -cE '^=== ' results/logs/cpd_driver.log 2>/dev/null) markers"
grep -E "^=== (LADDER DONE|SMOKE PASSED|TRAINED|FREEGEN)" results/logs/cpd_driver.log 2>/dev/null | tail -3
for A in cpd shuffled router_ce; do
  F=results/cpd_train_$A.jsonl
  [ -f "$F" ] && echo "  $A: $(wc -l < $F) steps, last=$(tail -1 $F | python3 -c 'import json,sys;r=json.load(sys.stdin);print(f"loss={r[\"loss\"]:.4f} drift={[round(x,4) for x in r[\"drift\"]]}")' 2>/dev/null)"
done
for F in results/cpd_train_*.jsonl; do
  [ -f "$F" ] && grep -qiE "nan|infinity" "$F" && echo "  !! NaN/Inf in $F"
done
grep -ciE "traceback|error|out of memory" results/logs/cpd_*.log 2>/dev/null | grep -v ":0$" | sed 's/^/  err /'
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | head -2 | sed 's/^/  gpu /'
