#!/usr/bin/env bash
# E204 setup on fvcrc13: Qwen3.5-0.8B-Base, Qwen-tokenized FineWeb-Edu (220M tokens), Qwen items.
set -e
bash /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/dl_hf.sh Qwen/Qwen3.5-0.8B-Base main /tmp/xiang_hyb/models/Q08 > /tmp/xiang_hyb/dl_Q08.log 2>&1
grep -h "MISMATCH" /tmp/xiang_hyb/dl_Q08.log || true
cd /tmp/xiang_e201 && cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e201_prep.py .
/tmp/xiang_e201/env/bin/python -I e201_prep.py data/000_00000.parquet /tmp/xiang_hyb/models/Q08 data/tokens_qwen.npy 220000000 | tail -n 2
mkdir -p /tmp/xiang_hyb/work_qwen && scp -q -o BatchMode=yes fvcrc10:/tmp/xiang_hyb/work_qwen/items.json /tmp/xiang_hyb/work_qwen/
echo E204_SETUP_DONE
