#!/usr/bin/env bash
# E208 on fvcrc13 GPUs 0-1: identity conv, fp32 master weights, early-layer GDN lr 1e-3, 50M tokens; then readouts.
cd /tmp/xiang_e201
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e204_train.py /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e204_readout.py /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e195_capture.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
PY=/tmp/xiang_e201/env/bin/python
mkdir -p e208
g=0
for v in id_train id_frozen; do
  nohup bash -c "CUDA_VISIBLE_DEVICES=$g $PY -I e204_train.py $v /tmp/xiang_hyb/models/Q08 data/tokens_qwen.npy e208/$v --tokens 5e7 --fp32 --early_lr 1e-3 > e208/$v.train.log 2>&1;
    for c in 10M 50M; do CUDA_VISIBLE_DEVICES=$g $PY -I e204_readout.py e208/$v/ckpt_\$c /tmp/xiang_hyb/models/Q08 /tmp/xiang_hyb/work_qwen/items.json /tmp/xiang_e194/passages.json e208/$v/read_\$c >> e208/$v.read.log 2>&1; done;
    echo E208_DONE_$v >> e208/$v.read.log" > /dev/null 2>&1 &
  g=$((g+1))
done
