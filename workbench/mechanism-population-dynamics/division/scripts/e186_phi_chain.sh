#!/bin/bash
# E186: on fvcrc11, wait for the Phi download, capture on 2 idle GPUs, then run the local CPU pipeline.
B=/tmp/xiang_e186
until [ -f $B/models/phimoe/_download.json ]; do sleep 30; done
echo "[$(date +%T)] phi download done" >> $B/logs/phi_chain.log
G=""
for g in 0 1 2 3; do
  read used util <<< $(nvidia-smi -i $g --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ',')
  if [ "$used" -lt 1000 ] && [ "$util" -le 5 ]; then G="$G${G:+,}$g"; fi
  [ $(echo $G | tr ',' ' ' | wc -w) -ge 2 ] && break
done
[ $(echo $G | tr ',' ' ' | wc -w) -ge 2 ] || { echo "[$(date +%T)] fewer than 2 idle GPUs: $G" >> $B/logs/phi_chain.log; exit 3; }
echo "[$(date +%T)] capture on $G" >> $B/logs/phi_chain.log
$B/bundle/run_local.sh phimoe $G
$B/bundle/run_pipe_local.sh phimoe 16
echo "[$(date +%T)] phi chain done" >> $B/logs/phi_chain.log
