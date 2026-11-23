#!/usr/bin/env bash
# E213 on fvcrc13: GPU 2 = M1-3B (none, zero, mean, nomem), GPU 3 = teacher Llama-3.2-3B-Instruct (none).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
until grep -q DL_DONE /tmp/xiang_hyb/dl_m1.log && grep -q DL_DONE /tmp/xiang_hyb/dl_llama32_3b.log; do sleep 30; done
grep -h MISMATCH /tmp/xiang_hyb/dl_m1.log /tmp/xiang_hyb/dl_llama32_3b.log && exit 1
cd /tmp/xiang_e194 && cp $S/e213_m1.py $S/e195_capture.py $S/e202_run.py .
PY=/tmp/xiang_e201/env/bin/python; I=/tmp/xiang_hyb/work_llama3/items.json; P=/tmp/xiang_e194/passages.json; O=/tmp/xiang_hyb/out_e213
mkdir -p $O
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
( for c in none zero mean nomem; do CUDA_VISIBLE_DEVICES=2 $PY -I e213_m1.py /tmp/xiang_hyb/models/m1_3b $I $P $O/m1_$c $c 2>&1 | filt; done; echo E213_M1_DONE ) > $O/m1.log 2>&1 &
( CUDA_VISIBLE_DEVICES=3 $PY -I e202_run.py /tmp/xiang_hyb/models/llama32_3b_inst $I $P $O/teacher --no_fla 2>&1 | filt; echo E213_TEACHER_DONE ) > $O/teacher.log 2>&1 &
wait
echo E213_DONE >> $O/m1.log
