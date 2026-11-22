#!/usr/bin/env bash
# E198 Qwen3.5-4B-Base conditions on fvcrc21 GPUs 0-3 (layers 0-2 are GDN, first full attention at 3).
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e198_causal.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p out198
g=0
for c in none noconv nomem none_mix; do
  CUDA_VISIBLE_DEVICES=$g nohup /tmp/xiang_e194/env/bin/python -I e198_causal.py /tmp/xiang_hyb/models/QH /tmp/xiang_hyb/work_qwen/items.json passages.json out198/QH_$c $c 0,1,2 --start none > out198/QH_$c.log 2>&1 &
  g=$((g+1))
done
