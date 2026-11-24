#!/usr/bin/env bash
# E218 B1: single-layer conv / memory switches (layer 0, 1 or 2), R1 by m. Usage: e218_launch.sh fvcrc10 | fvcrc13
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
B=/tmp/xiang_e194; O=$B/out218; mkdir -p $O; cd $B
cp $S/e196_causal.py $S/e198_causal.py $S/e205_run.py $S/e209_run.py $S/e195_capture.py $S/r1_summary.py .
grep -q E218_LAYERS e196_causal.py || { echo STALE; exit 1; }
PY=./env/bin/python; P=passages.json
filt() { grep -v -i "warn\|falling\|loading"; }
job() {  # gpu model cond layer
  g=$1; m=$2; c=$3; l=$4; o=$O/${m}_${c}_L$l
  case $m in
    H)   E218_LAYERS=$l CUDA_VISIBLE_DEVICES=$g $PY -I e196_causal.py models/H work/items.json $P $o no$c ;;
    QH)  CUDA_VISIBLE_DEVICES=$g $PY -I e198_causal.py /tmp/xiang_hyb/models/QH /tmp/xiang_hyb/work_qwen/items.json $P $o no$c $l --start none ;;
    GH)  CUDA_VISIBLE_DEVICES=$g $PY -I e198_causal.py /tmp/xiang_hyb/models/GH /tmp/xiang_hyb/work_granite/items.json $P $o no$c $l --start none ;;
    FH3) if [ $c = conv ]; then CUDA_VISIBLE_DEVICES=$g $PY -I e209_run.py /tmp/xiang_hyb/models/FH3 /tmp/xiang_hyb/work_fh3/items.json $P $o mean --layers $l-$l
         else E218_LAYERS=$l CUDA_VISIBLE_DEVICES=$g $PY -I e205_run.py /tmp/xiang_hyb/models/FH3 /tmp/xiang_hyb/work_fh3/items.json $P $o nomem; fi ;;
  esac 2>&1 | filt | tail -n 2
  echo "JOB_DONE ${m}_${c}_L$l"
}
queue() { g=$1; shift; for spec in "$@"; do job $g ${spec//:/ }; done; }
case "$1" in
fvcrc10)
  queue 0 QH:conv:0 QH:mem:0 H:conv:0 H:mem:0 > $O/q0.log 2>&1 &
  queue 1 QH:conv:1 QH:mem:1 H:conv:1 H:mem:1 > $O/q1.log 2>&1 &
  queue 2 QH:conv:2 QH:mem:2 H:conv:2 H:mem:2 > $O/q2.log 2>&1 & ;;
fvcrc13)
  queue 0 GH:conv:0 GH:mem:0 FH3:conv:0 FH3:mem:0 > $O/q0.log 2>&1 &
  queue 1 GH:conv:1 GH:mem:1 FH3:conv:1 FH3:mem:1 > $O/q1.log 2>&1 &
  queue 2 GH:conv:2 GH:mem:2 FH3:conv:2 FH3:mem:2 > $O/q2.log 2>&1 & ;;
esac
wait
echo E218_DONE >> $O/q0.log
