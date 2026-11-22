#!/usr/bin/env bash
# E197 on fvcrc10: Qwen3.5-4B-Base (QH) on GPU 3 now; Qwen3-4B-Base (QT) on GPU 2 once E196 has freed it.
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e197_xling.py .
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/results/e197/pud_parallel.json .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
mkdir -p out197
CUDA_VISIBLE_DEVICES=3 nohup /tmp/xiang_e194/env/bin/python -I e197_xling.py /tmp/xiang_hyb/models/QH pud_parallel.json out197/QH.json --start none > out197/QH.log 2>&1 &
nohup bash -c 'while pgrep -f "e196_causal.py" >/dev/null; do sleep 15; done; CUDA_VISIBLE_DEVICES=2 /tmp/xiang_e194/env/bin/python -I e197_xling.py /tmp/xiang_hyb/models/QT pud_parallel.json out197/QT.json --start none' > out197/QT.log 2>&1 &
