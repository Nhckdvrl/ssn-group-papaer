#!/usr/bin/env bash
# E219: per-layer isolation map. Usage: e219_launch.sh fvcrc10 | fvcrc13   (4 GPUs each; daytime cap 8 cards)
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
B=/tmp/xiang_e194; O=$B/out219; mkdir -p $O; cd $B
cp $S/e219_map.py $S/e217_levels.py $S/e209_run.py $S/e195_capture.py $S/e212_llamba.py .
grep -q "def sdpa_wrap" e219_map.py || { echo STALE; exit 1; }
P=passages.json; M=/tmp/xiang_hyb/models; PY=./env/bin/python
run() { g=$1; name=$2; shift 2; CUDA_VISIBLE_DEVICES=$g $PY -I e219_map.py "$@" > $O/$name.log 2>&1; echo "JOB_DONE $name" >> $O/done.log; }
seq_layers() { seq -s, $1 $2; }
case "$1" in
fvcrc10)
  run 0 QH $M/QH $P $O/QH.json --start none &
  run 1 QT $M/QT $P $O/QT.json --start none &
  run 2 FM_a $M/FM $P $O/FM_a.json --start eos --only_layers $(seq_layers 0 31) &
  run 3 FM_b $M/FM $P $O/FM_b.json --start eos --only_layers $(seq_layers 32 63) & ;;
fvcrc13)
  run 0 H models/H $P $O/H.json --start eos &
  run 1 T models/T $P $O/T.json --start eos &
  (run 2 GH $M/GH $P $O/GH.json --start none; run 2 GT $M/GT $P $O/GT.json --start none) &
  (run 3 FH3 $M/FH3 $P $O/FH3.json --start bos; PY=/tmp/xiang_e201/env/bin/python run 3 Llamba $M/llamba1b $P $O/Llamba.json --start bos --llamba $M/llama32_1b_inst;
   run 3 L1B $M/llama32_1b_inst $P $O/L1B.json --start bos) & ;;
esac
wait
echo E219_DONE >> $O/done.log
