#!/bin/bash
# E19: E18 readout at late steps for the 410M population. Usage: bash run_e19.sh host:gpu
cd "$(dirname "$0")"
g=$1
for step in 133000 123000 138000; do for i in "" -seed1 -seed2 -seed3 -seed4 -seed5 -seed6 -seed7 -seed8 -seed9; do
  t=pythia-410m$i
  [ -f ../results/e18/${t}__step$step.json ] && continue
  ssh -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=${g##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $HOME/.venvs/mechpop/bin/python e18_trait.py --repo EleutherAI/$t --step $step" > ../results/e18/logs/${t}__step$step.log 2>&1
  echo "$t step$step exit=$?"
done; done
