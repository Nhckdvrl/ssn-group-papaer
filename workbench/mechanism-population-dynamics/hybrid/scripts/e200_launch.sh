#!/usr/bin/env bash
# E200 on fvcrc10: Qwen3.5-4B-Base, PUD cross-lingual retrieval under none / noconv / nomem in layers 0-2.
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e197_xling.py e200_xling.py
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p out200
for spec in "none 0" "noconv 1" "nomem 3"; do
  set -- $spec
  CUDA_VISIBLE_DEVICES=$2 nohup /tmp/xiang_e194/env/bin/python -I e200_xling.py /tmp/xiang_hyb/models/QH pud_parallel.json out200/QH_$1.json --start none --cond $1 --layers 0,1,2 > out200/QH_$1.log 2>&1 &
done
