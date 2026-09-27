#!/bin/bash
# usage: wait_launch.sh TAG "<remote command using $CUDA_VISIBLE_DEVICES>"  -- waits for an idle card
TAG=$1; CMD=$2
while true; do
  for h in fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21; do
    g=$(timeout 10 ssh $h "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits" 2>/dev/null \
        | awk -F', ' '$2<1000 && $3<5 {print $1; exit}')
    if [ -n "$g" ]; then
      echo "$(TZ=Asia/Tokyo date '+%F %H:%M') JST — $TAG launched on $h GPU$g" >> logs/P0_LAUNCH.md
      ssh $h "cd $PWD && CUDA_VISIBLE_DEVICES=$g nohup bash -c '$CMD' > logs/score_$TAG.log 2>&1 &" 2>/dev/null
      exit 0
    fi
  done
  sleep 60
done
