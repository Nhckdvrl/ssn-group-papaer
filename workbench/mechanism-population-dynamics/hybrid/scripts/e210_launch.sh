#!/usr/bin/env bash
# E210 on fvcrc11: build NeoX items, then GPU k = one size: RWKV-4 (none, noshift, nomem, noshift_nomem; fp32) + Pythia (none).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
until grep -q E210_SETUP_DONE /tmp/xiang_hyb/e210_setup.log; do sleep 30; done
grep -q MISMATCH /tmp/xiang_hyb/e210_setup.log && { echo MISMATCH; exit 1; }
cd /tmp/xiang_e194 && cp $S/e210_run.py $S/e195_capture.py $S/e194_items.py $S/r1_summary.py .
P=/tmp/xiang_e194/passages.json; I=/tmp/xiang_hyb/work_neox/items.json; O=/tmp/xiang_hyb/out_e210; mkdir -p $O
[ -f $I ] || ./env/bin/python -I e194_items.py $P /tmp/xiang_hyb/models/pythia_160m /tmp/xiang_hyb/work_neox | tail -n 3
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
run() {  # gpu rwkv_size pythia_size
  for c in none noshift nomem noshift_nomem; do
    CUDA_VISIBLE_DEVICES=$1 ./env/bin/python -I e210_run.py /tmp/xiang_hyb/models/rwkv4_$2 $I $P $O/rwkv4_$2_$c $c --fp32 2>&1 | filt
  done
  CUDA_VISIBLE_DEVICES=$1 ./env/bin/python -I e210_run.py /tmp/xiang_hyb/models/pythia_$3 $I $P $O/pythia_$3_none none 2>&1 | filt
}
run 0 169m 160m > $O/s1.log 2>&1 &
run 1 430m 410m > $O/s2.log 2>&1 &
run 2 1b5 1.4b > $O/s3.log 2>&1 &
run 3 3b 2.8b > $O/s4.log 2>&1 &
wait
echo E210_DONE
