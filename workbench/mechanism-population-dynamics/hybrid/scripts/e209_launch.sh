#!/usr/bin/env bash
# E209 launcher. Usage: e209_launch.sh fvcrc13 | fvcrc10
# fvcrc13: GPU 2 = Falcon-H1 (none, zero, mean, mean_noattn); GPU 3 = Qwen3.5-0.8B (none, zero, mean).
# fvcrc10: GPUs 0-2 = fla-hub Mamba-1.3B (none, mean 0-5, mean_all), transformers' native Mamba class.
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
O=/tmp/xiang_hyb/out_e209; mkdir -p $O
cd /tmp/xiang_e194 && cp $S/e209_run.py $S/e195_capture.py $S/r1_summary.py .
P=/tmp/xiang_e194/passages.json
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
case "$1" in
fvcrc13)
  ( for c in none zero mean mean_noattn; do
      CUDA_VISIBLE_DEVICES=2 ./env/bin/python -I e209_run.py /tmp/xiang_hyb/models/FH3 /tmp/xiang_hyb/work_fh3/items.json $P $O/fh3_$c $c --layers 0-2 2>&1 | filt
    done; echo E209_FH3_DONE ) > $O/fh3.log 2>&1 &
  ( for c in none zero mean; do
      CUDA_VISIBLE_DEVICES=3 /tmp/xiang_e201/env/bin/python -I e209_run.py /tmp/xiang_hyb/models/Q08 /tmp/xiang_hyb/work_qwen/items.json $P $O/q08_$c $c --layers 0-2 --no_start --fla 2>&1 | filt
    done; echo E209_Q08_DONE ) > $O/q08.log 2>&1 &
  wait ;;
fvcrc10)
  M=/tmp/xiang_hyb/models/fla_mamba; I=/tmp/xiang_hyb/work_fla/items.json
  CUDA_VISIBLE_DEVICES=0 ./env/bin/python -I e209_run.py $M $I $P $O/mb_none none --layers 0-5 > $O/mb_none.log 2>&1 &
  CUDA_VISIBLE_DEVICES=1 ./env/bin/python -I e209_run.py $M $I $P $O/mb_mean mean --layers 0-5 > $O/mb_mean.log 2>&1 &
  CUDA_VISIBLE_DEVICES=2 ./env/bin/python -I e209_run.py $M $I $P $O/mb_mean_all mean --layers 0-47 > $O/mb_mean_all.log 2>&1 &
  wait; echo E209_MB_DONE >> $O/mb_none.log ;;
esac
