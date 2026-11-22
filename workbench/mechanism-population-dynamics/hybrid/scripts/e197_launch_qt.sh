#!/usr/bin/env bash
# E197: Qwen3-4B-Base (QT) on fvcrc10 GPU 2.
cd /tmp/xiang_e194
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
CUDA_VISIBLE_DEVICES=2 nohup /tmp/xiang_e194/env/bin/python -I e197_xling.py /tmp/xiang_hyb/models/QT pud_parallel.json out197/QT.json --start none > out197/QT.log 2>&1 &
