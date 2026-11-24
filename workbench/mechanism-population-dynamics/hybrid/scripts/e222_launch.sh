#!/usr/bin/env bash
# E222: sink-preserving early cut + mid-conv re-entry factorial. Usage: e222_launch.sh fvcrc10 | fvcrc13
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
B=/tmp/xiang_e194; O=$B/out222; mkdir -p $O; cd $B
cp $S/e222_sink.py $S/e217_levels.py $S/e209_run.py $S/e195_capture.py $S/e212_llamba.py .
grep -q "s_sink" e222_sink.py || { echo STALE; exit 1; }
P=passages.json; M=/tmp/xiang_hyb/models; PY=./env/bin/python
run() { g=$1; name=$2; shift 2; CUDA_VISIBLE_DEVICES=$g $PY -I e222_sink.py "$@" > $O/$name.log 2>&1; echo "JOB_DONE $name" >> $O/done.log; }
case "$1" in
fvcrc10)
  run 0 QH $M/QH $P $O/QH.json --start none &
  run 1 QT $M/QT $P $O/QT.json --start none &
  run 2 FM $M/FM $P $O/FM.json --start eos &
  run 3 GT $M/GT $P $O/GT.json --start none & ;;
fvcrc13)
  run 0 H models/H $P $O/H.json --start eos &
  run 1 T models/T $P $O/T.json --start eos &
  run 2 GH $M/GH $P $O/GH.json --start none &
  (run 3 FH3 $M/FH3 $P $O/FH3.json --start bos; PY=/tmp/xiang_e201/env/bin/python run 3 Llamba $M/llamba1b $P $O/Llamba.json --start bos --llamba $M/llama32_1b_inst;
   run 3 L1B $M/llama32_1b_inst $P $O/L1B.json --start bos) & ;;
esac
wait
echo E222_DONE >> $O/done.log
