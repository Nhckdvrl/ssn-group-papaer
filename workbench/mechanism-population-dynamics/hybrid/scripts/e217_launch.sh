#!/usr/bin/env bash
# E217: four-level locality readouts. GPU 3 of each node. Usage: e217_launch.sh fvcrc10 | fvcrc13
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
B=/tmp/xiang_e194; O=$B/out217; mkdir -p $O; cd $B
cp $S/e217_levels.py $S/e209_run.py $S/e195_capture.py $S/e212_llamba.py .
grep -q "def piece_kind" e217_levels.py || { echo STALE; exit 1; }
P=passages.json; BL=/tmp/xiang_hyb/blimp; M=/tmp/xiang_hyb/models
run() { CUDA_VISIBLE_DEVICES=3 "$@" 2>&1 | grep -v -i "warn\|falling\|loading" | tail -n 3; }
case "$1" in
fvcrc10)
  for c in none conv mem; do run ./env/bin/python -I e217_levels.py $M/QH $P $BL $O/QH_$c.json $c --start none; done
  for c in none conv mem; do run ./env/bin/python -I e217_levels.py models/H $P $BL $O/H_$c.json $c --start eos; done
  for c in none attn; do run ./env/bin/python -I e217_levels.py models/T $P $BL $O/T_$c.json $c --start eos; done ;;
fvcrc13)
  for c in none convmean mem attn; do run ./env/bin/python -I e217_levels.py $M/FH3 $P $BL $O/FH3_$c.json $c --start bos; done
  for c in none conv mem; do run ./env/bin/python -I e217_levels.py $M/GH $P $BL $O/GH_$c.json $c --start none; done
  for c in none convmean mem; do run /tmp/xiang_e201/env/bin/python -I e217_levels.py $M/llamba1b $P $BL $O/Llamba_$c.json $c --start bos --llamba $M/llama32_1b_inst; done ;;
esac
echo E217_DONE
