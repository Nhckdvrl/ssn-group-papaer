#!/usr/bin/env bash
# E198 Granite-H conditions on fvcrc13 GPUs 0-3 (layers 0-4 are Mamba-2, first attention at 5).
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e198_causal.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p out198
g=0
for c in none noconv nomem none_mix; do
  CUDA_VISIBLE_DEVICES=$g nohup /tmp/xiang_e194/env/bin/python -I e198_causal.py /tmp/xiang_hyb/models/GH /tmp/xiang_hyb/work_granite/items.json passages.json out198/GH_$c $c 0,1,2,3,4 --start none > out198/GH_$c.log 2>&1 &
  g=$((g+1))
done
