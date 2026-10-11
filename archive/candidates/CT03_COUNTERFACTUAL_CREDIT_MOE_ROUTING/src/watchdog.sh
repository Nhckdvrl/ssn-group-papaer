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
  if [ -f "$F" ]; then
    /home/xiang/miniconda3/envs/verl-clean/bin/python - "$A" "$F" <<'PY'
import json, sys, numpy as np
arm, f = sys.argv[1], sys.argv[2]
R = [json.loads(l) for l in open(f)]
L = np.array([r["loss"] for r in R])
w = 25
print(f"  {arm}: {len(R)} steps  loss {L[:w].mean():.4f}->{L[-w:].mean():.4f}"
      f"  drift={[round(x,4) for x in R[-1]['drift']]}"
      f"  finite={bool(np.isfinite(L).all())}"
      f"  {R[-1]['elapsed']/60:.0f}min")
PY
  fi
done
for F in results/cpd_train_*.jsonl; do
  [ -f "$F" ] && grep -qiE "nan|infinity" "$F" && echo "  !! NaN/Inf in $F"
done
grep -ciE "traceback|error|out of memory" results/logs/cpd_*.log 2>/dev/null | grep -v ":0$" | sed 's/^/  err /'
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | head -2 | sed 's/^/  gpu /'
