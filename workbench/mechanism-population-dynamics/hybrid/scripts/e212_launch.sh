#!/usr/bin/env bash
# E212 on fvcrc13: build Llama-3 items, then GPU 2 = Llamba-1B (none, zero, mean, nomem), GPU 3 = teacher (none).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
until grep -q DL_DONE /tmp/xiang_hyb/dl_llamba1b.log && grep -q DL_DONE /tmp/xiang_hyb/dl_llama32.log; do sleep 30; done
grep -h MISMATCH /tmp/xiang_hyb/dl_llamba1b.log /tmp/xiang_hyb/dl_llama32.log && exit 1
cd /tmp/xiang_e194 && cp $S/e212_llamba.py $S/e195_capture.py $S/e194_items.py $S/e202_run.py $S/r1_summary.py .
PY=/tmp/xiang_e201/env/bin/python; T=/tmp/xiang_hyb/models/llama32_1b_inst; I=/tmp/xiang_hyb/work_llama3/items.json; P=/tmp/xiang_e194/passages.json; O=/tmp/xiang_hyb/out_e212
mkdir -p $O
[ -f $I ] || $PY -I e194_items.py $P $T /tmp/xiang_hyb/work_llama3 | tail -n 4
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
( for c in none zero mean nomem; do CUDA_VISIBLE_DEVICES=2 $PY -I e212_llamba.py /tmp/xiang_hyb/models/llamba1b $T $I $P $O/llamba_$c $c 2>&1 | filt; done; echo E212_LLAMBA_DONE ) > $O/llamba.log 2>&1 &
( CUDA_VISIBLE_DEVICES=3 $PY -I e202_run.py $T $I $P $O/teacher --no_fla 2>&1 | filt; echo E212_TEACHER_DONE ) > $O/teacher.log 2>&1 &
wait
echo E212_DONE >> $O/llamba.log
