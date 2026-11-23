#!/usr/bin/env bash
# E204: three continued-training variants on fvcrc13 GPUs 0-2; each reads its own checkpoints afterwards.
cd /tmp/xiang_e201
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
PY=/tmp/xiang_e201/env/bin/python
g=0
for v in ctrl id_train id_frozen; do
  nohup bash -c "CUDA_VISIBLE_DEVICES=$g $PY -I e204_train.py $v /tmp/xiang_hyb/models/Q08 data/tokens_qwen.npy e204/$v --tokens 1e8 > e204/$v.train.log 2>&1;
    for c in 10M 50M 100M; do CUDA_VISIBLE_DEVICES=$g $PY -I e204_readout.py e204/$v/ckpt_\$c /tmp/xiang_hyb/models/Q08 /tmp/xiang_hyb/work_qwen/items.json /tmp/xiang_e194/passages.json e204/$v/read_\$c >> e204/$v.read.log 2>&1; done;
    echo E204_DONE_$v >> e204/$v.read.log" > /dev/null 2>&1 &
  g=$((g+1))
done
