#!/bin/bash
# Launch queued mechanism-population workers on GPUs that become idle (no processes, <1 GB used, 0% util in two
# consecutive scans 5 min apart). Hosts per the human's instruction (2026-10-03): fvcrc10/11/12/13/15/20/21; fvcrc14 excluded.
# Never touches a GPU that has any process on it. Each GPU is used at most once (state file).
cd "$(dirname "$0")"
STATE=../results/gpu_scout_state.txt; touch $STATE
HOSTS="fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21"
declare -A seen
while true; do
  for h in $HOSTS; do
    out=$(timeout 25 ssh -n -o ConnectTimeout=8 -o BatchMode=yes $h "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits; echo APPS; nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader | sort | uniq -c; echo UUIDS; nvidia-smi --query-gpu=index,uuid --format=csv,noheader" 2>/dev/null) || continue
    while IFS=', ' read -r idx mem util; do
      [[ "$idx" =~ ^[0-9]+$ ]] || continue
      g="$h:$idx"
      grep -qx "$g" $STATE && continue
      uuid=$(echo "$out" | sed -n '/UUIDS/,$p' | grep "^$idx, " | awk -F', ' '{print $2}')
      napps=$(echo "$out" | sed -n '/APPS/,/UUIDS/p' | grep -c "$uuid")
      if [ "$mem" -lt 1000 ] && [ "$util" -eq 0 ] && [ "$napps" -eq 0 ]; then
        if [ "${seen[$g]}" = 1 ]; then
          echo "$g" >> $STATE
          echo "$(date +%H:%M) launching on idle $g"
          nohup ./run_e48.sh $g > ../results/scout_e48_${g/:/_}.out 2>&1 &
          nohup ./run_e46r.sh $g ../results/e46_jobs_stage1.txt > ../results/scout_e46s1_${g/:/_}.out 2>&1 &
          nohup ./run_e46r.sh $g ../results/e46c_jobs.txt > ../results/scout_e46c_${g/:/_}.out 2>&1 &
        else
          seen[$g]=1
        fi
      else
        seen[$g]=0
      fi
    done <<< "$(echo "$out" | sed '/APPS/,$d')"
  done
  sleep 300
done
