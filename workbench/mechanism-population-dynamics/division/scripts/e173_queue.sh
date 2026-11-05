#!/usr/bin/env bash
# E173 optional queue (start only with the main session's / user's OK): every INTERVAL seconds, look for idle GPUs
# (memory.used <= 1000 MiB and no compute process) on the allowed hosts and launch the next pending run in priority
# order (e) FRZ -> (a) LB0 -> (c) G16 -> (d) G256 -> (b) LB01, seed 0 and 1 of a recipe back to back.
# Never touches busy GPUs; caps E173 runs alive at MAXRUN. A run counts as started once its log file exists.
# Usage: e173_queue.sh [MAXRUN=8] [INTERVAL=600]
set -uo pipefail
MAXRUN=${1:-8}; INTERVAL=${2:-600}
HOSTS="fvcrc10 fvcrc11 fvcrc15"   # never fvcrc12/13/20/21
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
L=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/results/e173/_logs
R=/home/xiang/mechpop_cache/e173_runs
ORDER="FRZ:0 FRZ:1 LB0:0 LB0:1 G16:0 G16:1 G256:0 G256:1 LB01:0 LB01:1"
while true; do
  pending=(); for x in $ORDER; do [ -f $L/${x%%:*}_I${x##*:}.log ] || pending+=($x); done
  [ ${#pending[@]} -eq 0 ] && { echo "$(date '+%F %T') all launched"; exit 0; }
  alive=0; for h in $HOSTS; do n=$(ssh -o BatchMode=yes -o ConnectTimeout=10 $h "pgrep -fc 'e173_job.sh'" 2>/dev/null || echo 0); alive=$((alive + n)); done
  for h in $HOSTS; do
    [ ${#pending[@]} -eq 0 ] && break
    idle=$(ssh -o BatchMode=yes -o ConnectTimeout=10 $h 'busy=$(nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader | sort -u); nvidia-smi --query-gpu=index,uuid,memory.used --format=csv,noheader,nounits | while IFS=", " read i u m; do echo "$busy" | grep -q "$u" || [ "$m" -gt 1000 ] || echo $i; done' 2>/dev/null)
    for g in $idle; do
      [ ${#pending[@]} -eq 0 ] || [ $alive -ge $MAXRUN ] && break
      x=${pending[0]}
      if $S/e173_launch.sh $h $g ${x%%:*} ${x##*:}; then pending=("${pending[@]:1}"); alive=$((alive + 1)); sleep 60; fi
    done
  done
  sleep $INTERVAL
done
