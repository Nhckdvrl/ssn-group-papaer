#!/bin/bash
# One queue runner: for each line of logs/jobs.txt ("TAG<TAB>command"), wait for an idle card
# (memory < 1 GB, util < 5%) on the allowed hosts, launch there, then pause 120 s before the next job.
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
while IFS=$'\t' read -r TAG CMD; do
  [ -z "$TAG" ] && continue
  while true; do
    n=0; for hh in fvcrc10 fvcrc12 fvcrc13 fvcrc15 fvcrc20; do c=$(timeout 10 ssh -n -o ConnectTimeout=5 $hh "pgrep -fc \"src/score(_any)?[.]py\"" 2>/dev/null | head -1); n=$((n + ${c:-0})); done
    if [ "$n" -ge 8 ]; then sleep 60; continue; fi
    for h in fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21; do
      g=$(timeout 10 ssh -n -o ConnectTimeout=5 $h "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits" 2>/dev/null \
          | awk -F', ' '$2<1000 && $3<5 {print $1; exit}')
      if [ -n "$g" ]; then
        echo "$(TZ=Asia/Tokyo date '+%F %H:%M') JST — $TAG launched on $h GPU$g" >> logs/P0_LAUNCH.md
        ssh -n $h "cd $PWD && CUDA_VISIBLE_DEVICES=$g nohup bash -c '$CMD' > logs/score_$TAG.log 2>&1 &" 2>/dev/null
        sleep 120; continue 3
      fi
    done
    sleep 60
  done
done < "${1:-logs/jobs.txt}"
