#!/bin/bash
# L34 E01 launcher.  usage: launch.sh trunk | launch.sh arms
# Slots: fvcrc13:0-3 and fvcrc15:0-3  = 8 cards (user cap 2026-09-14: at most 8).
set -u
SRC=/home/xiang/ssn-group-papaer/candidates/L34_PROSPECTIVE_ENCODING/src
LOGS=/home/xiang/ssn-group-papaer/candidates/L34_PROSPECTIVE_ENCODING/results/logs
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
TAG=${TAG:-l3b}
BASE=${BASE:-unsloth/Llama-3.2-3B}
mkdir -p "$LOGS"

if [ "$1" = "trunk" ]; then
  echo "$(date) TRUNK on fvcrc13:0 base=$BASE tag=$TAG" | tee -a "$LOGS/e01_launch.log"
  ssh -o BatchMode=yes fvcrc13 "cd $SRC && CUDA_VISIBLE_DEVICES=0 nohup $PY run.py trunk --base $BASE --tag $TAG > $LOGS/e01_${TAG}_trunk.stdout 2>&1 &" 
  exit 0
fi

SLOTS=(fvcrc15:0 fvcrc15:1 fvcrc15:2 fvcrc15:3 fvcrc12:0 fvcrc12:1 fvcrc13:0 fvcrc10:2)
JOBS=()
for arm in PIT_A PIT_B PIT_BAL NO_PIT; do for s in 0 1 2; do JOBS+=("$arm $s"); done; done

declare -A QUEUE
i=0
for j in "${JOBS[@]}"; do
  k=$(( i % ${#SLOTS[@]} ))
  QUEUE[$k]="${QUEUE[$k]:-}|$j"
  i=$((i+1))
done

for k in "${!QUEUE[@]}"; do
  slot=${SLOTS[$k]}; host=${slot%%:*}; gpu=${slot##*:}
  cmd=""
  IFS='|' read -ra items <<< "${QUEUE[$k]}"
  for it in "${items[@]}"; do
    [ -z "$it" ] && continue
    set -- $it; arm=$1; sd=$2
    cmd+="CUDA_VISIBLE_DEVICES=$gpu $PY run.py arm --arm $arm --seed $sd --tag $TAG >> $LOGS/e01_${TAG}_${arm}_s${sd}.stdout 2>&1; "
  done
  echo "$(date) SLOT $slot -> ${QUEUE[$k]}" | tee -a "$LOGS/e01_launch.log"
  ssh -o BatchMode=yes "$host" "cd $SRC && nohup bash -c '$cmd' > $LOGS/e01_slot_${host}_${gpu}.stdout 2>&1 &"
done
echo "$(date) all slots dispatched" | tee -a "$LOGS/e01_launch.log"
