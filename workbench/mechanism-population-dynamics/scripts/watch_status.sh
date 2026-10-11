#!/bin/bash
# Status of the running experiments (E66 training runs, E67 audit, E68 baselines) and any sign of failure.
cd "$(dirname "$0")/../results"
echo "== $(date +%H:%M)"
done=0; run=0; wait=0
while IFS='|' read -r n par k args; do
  if [ -f e46/$n.json ]; then done=$((done+1));
  elif [ -d e46/claims/$n ]; then run=$((run+1)); s=$(grep "^$n " e46/logs/$n.log 2>/dev/null | tail -1 | awk '{print $2}'); echo "  E66 run $n @${s:-start}";
  else wait=$((wait+1)); fi
done < e66_jobs.txt
echo "E66 done $done running $run waiting $wait"
grep -l -E "Traceback|Error|exit=[1-9]" e46/logs/S_*w1000*.log e46/logs/S_*_ro.log e66_worker*.out 2>/dev/null | grep -v killed | sed 's/^/  E66 PROBLEM in /'
echo "E67 $(grep -c 'runs' e67_run.out) / 15 sizes; flagged: $(grep 'runs' e67_run.out | grep -v 'label: \[\]' | tr '\n' ' ')"
grep -E "Traceback|Error" e67_run.out | head -2 | sed 's/^/  E67 PROBLEM /'
echo "E68 $(ls e68/*.npz 2>/dev/null | wc -l) / 761 models; failures $(grep -h FAILED e68_worker_*.out | wc -l); workers alive $(ps -u $USER -o args | grep -c '[e]68_baselines.py --worker')"
grep -h FAILED e68_worker_*.out | tail -2 | sed 's/^/  /'
for h in fvcrc10 fvcrc20; do echo "$h $(ssh -n -o BatchMode=yes -o ConnectTimeout=8 $h 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | tr "\n" ";"' 2>/dev/null)"; done
