#!/usr/bin/env bash
# E221: 2x2 split of all-layer cuts + early all-mixer cut. Usage: e221_launch.sh fvcrc10 | fvcrc13
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
B=/tmp/xiang_e194; O=$B/out221; mkdir -p $O; cd $B
cp $S/e221_split.py $S/e217_levels.py $S/e209_run.py $S/e195_capture.py $S/e212_llamba.py .
grep -q "def classify" e221_split.py || { echo STALE; exit 1; }
P=passages.json; M=/tmp/xiang_hyb/models; PY=./env/bin/python
run() { g=$1; name=$2; shift 2; CUDA_VISIBLE_DEVICES=$g $PY -I e221_split.py "$@" > $O/$name.log 2>&1; echo "JOB_DONE $name" >> $O/done.log; }
case "$1" in
fvcrc10)
  run 0 QH $M/QH $P $O/QH.json --start none &
  run 1 QT $M/QT $P $O/QT.json --start none &
  run 2 FM $M/FM $P $O/FM.json --start eos & ;;
fvcrc13)
  run 0 H models/H $P $O/H.json --start eos &
  run 1 T models/T $P $O/T.json --start eos &
  run 2 GH $M/GH $P $O/GH.json --start none &
  (run 3 FH3 $M/FH3 $P $O/FH3.json --start bos; PY=/tmp/xiang_e201/env/bin/python run 3 Llamba $M/llamba1b $P $O/Llamba.json --start bos --llamba $M/llama32_1b_inst) & ;;
esac
wait
echo E221_DONE >> $O/done.log
