#!/usr/bin/env bash
# E216: four workers on fvcrc13 GPUs 0-3.
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
O=/tmp/xiang_e194/out216; mkdir -p $O
nohup bash $S/e216_worker.sh 0 H:1000 H:30000 T:100000 > $O/worker_0.log 2>&1 < /dev/null &
nohup bash $S/e216_worker.sh 1 H:3000 H:100000 T:400000 > $O/worker_1.log 2>&1 < /dev/null &
nohup bash $S/e216_worker.sh 2 H:10000 H:400000 T:30000 > $O/worker_2.log 2>&1 < /dev/null &
nohup bash $S/e216_worker.sh 3 T:1000 T:3000 T:10000 > $O/worker_3.log 2>&1 < /dev/null &
