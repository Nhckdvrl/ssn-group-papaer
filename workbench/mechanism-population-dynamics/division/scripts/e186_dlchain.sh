#!/bin/bash
# E186: wait for the given PIDs (earlier downloads on this node), then download "repo revision key" triples in order.
# Usage: e186_dlchain.sh "PID PID" repo rev key [repo rev key ...]
W=$1; shift
for p in $W; do while kill -0 $p 2>/dev/null; do sleep 20; done; done
while [ $# -ge 3 ]; do
  /home/xiang/.venvs/mechpop/bin/python /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts/e186_download.py $1 $2 /tmp/xiang_e186/models/$3 --par 4 > /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/results/e186/_logs/dl_$3.log 2>&1
  shift 3
done
