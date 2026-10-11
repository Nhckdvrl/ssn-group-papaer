#!/bin/bash
# launch.sh GPU TASK SIZE SEED EPISODES STEPS [extra args]
G=$1; T=$2; S=$3; SEED=$4; EP=$5; ST=$6; shift 6
NAME=${T}_${S}_ep${EP}_s${SEED}_st${ST}$(echo "$@" | tr -d ' -')
OUT=${RUNROOT:-/tmp/latent-wm-runs/scaling}/$NAME
mkdir -p $OUT
CK=2000,5000,10000,20000,40000,60000,100000,150000
cd /home/xiang/ssn-group-papaer/workbench/latent-world-model-planning/scaling
LWM_DATA=${LWM_DATA:-/tmp/latent-wm-data/lowres} CUDA_VISIBLE_DEVICES=$G setsid nohup /home/xiang/.venvs/latent-wm/bin/python train.py --task $T --size $S --seed $SEED --episodes $EP --steps $ST --ckpts $CK --out $OUT "$@" > $OUT/train.log 2>&1 < /dev/null &
echo $NAME $!
