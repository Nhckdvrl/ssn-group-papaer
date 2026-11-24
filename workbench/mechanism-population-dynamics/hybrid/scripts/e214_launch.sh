#!/usr/bin/env bash
# E214 on fvcrc13: GPU 2 = none, mean, zero; GPU 3 = nomem, noattn, mean_noattn (Llama3.2-Mamba-3B-distill).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
until grep -q DL_DONE /tmp/xiang_hyb/dl_mil3b.log; do sleep 30; done
grep -h MISMATCH /tmp/xiang_hyb/dl_mil3b.log && exit 1
cd /tmp/xiang_e194 && cp $S/e214_mil.py $S/e213_m1.py $S/e195_capture.py .
PY=/tmp/xiang_e201/env/bin/python; M=/tmp/xiang_hyb/models/mil_3b; I=/tmp/xiang_hyb/work_llama3/items.json; P=/tmp/xiang_e194/passages.json; O=/tmp/xiang_hyb/out_e214
mkdir -p $O
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
( for c in none mean zero; do CUDA_VISIBLE_DEVICES=2 $PY -I e214_mil.py $M $I $P $O/mil_$c $c 2>&1 | filt; done ) > $O/a.log 2>&1 &
( for c in nomem noattn mean_noattn; do CUDA_VISIBLE_DEVICES=3 $PY -I e214_mil.py $M $I $P $O/mil_$c $c 2>&1 | filt; done ) > $O/b.log 2>&1 &
wait
echo E214_DONE >> $O/a.log
