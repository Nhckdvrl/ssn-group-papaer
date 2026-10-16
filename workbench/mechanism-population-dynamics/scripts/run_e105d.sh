#!/bin/bash
# E105d: wait until the given E109 deep run on this card has finished, then run "all"-subset unlearning + relearning.
set -u
cd "$(dirname "$0")"
G=$1; WAIT=$2; JOB=$3; H=${G%%:*}; D=${G##*:}
PY=$HOME/.venvs/mechpop/bin/python
until grep -q '"step": 1000' ../results/e109/logs/$WAIT.log 2>/dev/null; do sleep 60; done; sleep 60
if [ "$JOB" = capital ]; then
  bash run_e109.sh $G all 1
else
  O=/home/xiang/mechpop_cache/ckpt/e105/U4_all_s$JOB
  ssh -n -o BatchMode=yes $H "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e105_unlearn.py --subset all --seed $JOB --lr 5e-6 --margin 0 --target 0.5 --eval_every 5 --max_steps 2000 --tag U4_all_s$JOB --out $O && E93_OUT=e105 CUDA_VISIBLE_DEVICES=$D $PY e93_lesion.py --local $O --fp32 --bs 128 --lr 2e-5 --steps 1000 --arm C --tag R4_all_s$JOB" > ../results/e105/logs/U4_all_s$JOB.log 2>&1
fi
