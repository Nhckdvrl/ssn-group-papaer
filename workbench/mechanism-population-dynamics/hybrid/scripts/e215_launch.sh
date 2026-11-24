#!/usr/bin/env bash
# E215 on fvcrc13: build Qwen2.5 items; GPU 2 = Jet-Nemotron-2B (none, zero, mean, nomem); GPU 3 = teacher Qwen2.5-1.5B (none).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
until grep -q DL_DONE /tmp/xiang_hyb/dl_jet2b.log && grep -q DL_DONE /tmp/xiang_hyb/dl_qwen25.log; do sleep 30; done
grep -h MISMATCH /tmp/xiang_hyb/dl_jet2b.log /tmp/xiang_hyb/dl_qwen25.log && exit 1
cd /tmp/xiang_e194 && cp $S/e215_jet.py $S/e195_capture.py $S/e194_items.py $S/e202_run.py .
grep -q patched_naive e215_jet.py || { echo STALE_SCRIPT; exit 1; }
PY=/tmp/xiang_e199/env/bin/python; J=/tmp/xiang_hyb/models/jet2b; T=/tmp/xiang_hyb/models/qwen25_15b; I=/tmp/xiang_hyb/work_qwen25/items.json; P=/tmp/xiang_e194/passages.json; O=/tmp/xiang_hyb/out_e215
mkdir -p $O
[ -f $I ] || $PY -I e194_items.py $P $T /tmp/xiang_hyb/work_qwen25 | tail -n 4
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
( for c in none zero mean nomem; do CUDA_VISIBLE_DEVICES=2 $PY -I e215_jet.py $J $I $P $O/jet_$c $c 2>&1 | filt; done ) > $O/jet.log 2>&1 &
( CUDA_VISIBLE_DEVICES=3 $PY -I e202_run.py $T $I $P $O/teacher --no_fla 2>&1 | filt ) > $O/teacher.log 2>&1 &
wait
echo E215_DONE >> $O/jet.log
