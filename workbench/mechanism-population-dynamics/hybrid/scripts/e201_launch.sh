#!/usr/bin/env bash
# E201 launch on one node. Usage: e201_launch.sh "ARCH:GPU ARCH:GPU ..."
cd /tmp/xiang_e201
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e201_train.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p runs
for spec in $1; do
  a=${spec%%:*}; g=${spec##*:}
  CUDA_VISIBLE_DEVICES=$g nohup /tmp/xiang_e201/env/bin/python -I e201_train.py $a data/tokens.npy runs/$a --tokens 5e8 > runs/$a.log 2>&1 &
done
