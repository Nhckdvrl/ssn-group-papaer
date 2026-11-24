#!/usr/bin/env bash
# E213 rerun on fvcrc13 GPU 2 (teacher already done): M1-3B none, zero, mean, nomem (DT_DOUBLE_BIAS = True, as the original code).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
cd /tmp/xiang_e194 && cp $S/e213_m1.py $S/e195_capture.py .
PY=/tmp/xiang_e201/env/bin/python; I=/tmp/xiang_hyb/work_llama3/items.json; P=/tmp/xiang_e194/passages.json; O=/tmp/xiang_hyb/out_e213
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
for c in none zero mean nomem; do CUDA_VISIBLE_DEVICES=2 $PY -I e213_m1.py /tmp/xiang_hyb/models/m1_3b $I $P $O/m1_$c $c 2>&1 | filt; done > $O/m1.log 2>&1
echo E213_DONE >> $O/m1.log
