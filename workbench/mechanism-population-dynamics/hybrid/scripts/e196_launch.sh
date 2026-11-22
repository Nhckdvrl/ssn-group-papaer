#!/usr/bin/env bash
# E196 on fvcrc10: H conditions on GPU 2 (none, noconv, nomem) and GPU 3 (none_mix, then T_noattn on T).
cd /tmp/xiang_e194
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
PY="/tmp/xiang_e194/env/bin/python -I"
run() { CUDA_VISIBLE_DEVICES=$1 $PY e196_causal.py /tmp/xiang_e194/models/$2 /tmp/xiang_e194/work/items.json /tmp/xiang_e194/passages.json /tmp/xiang_e194/out196/$3 $3; }
nohup bash -c "$(declare -f run); export PY='$PY'; run 2 H none; run 2 H noconv; run 2 H nomem; echo E196_GPU2_DONE" > /tmp/xiang_e194/run196_g2.log 2>&1 &
nohup bash -c "$(declare -f run); export PY='$PY'; run 3 H none_mix; run 3 T T_noattn; echo E196_GPU3_DONE" > /tmp/xiang_e194/run196_g3.log 2>&1 &
