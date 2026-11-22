#!/usr/bin/env bash
# E197 on fvcrc13: Granite pair and OLMo pair, one GPU each.
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e197_xling.py .
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/results/e197/pud_parallel.json .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p /tmp/xiang_e194/out197
for spec in "GH /tmp/xiang_hyb/models/GH 0 none" "GT /tmp/xiang_hyb/models/GT 1 none" "H /tmp/xiang_e194/models/H 2 100257" "T /tmp/xiang_e194/models/T 3 100257"; do
  set -- $spec
  [ -f /tmp/xiang_e194/models/$1/tokenizer.json ] || cp /tmp/xiang_e194/tok/* /tmp/xiang_e194/models/$1/ 2>/dev/null
  CUDA_VISIBLE_DEVICES=$3 nohup /tmp/xiang_e194/env/bin/python -I e197_xling.py $2 pud_parallel.json out197/$1.json --start $4 > out197/$1.log 2>&1 &
done
