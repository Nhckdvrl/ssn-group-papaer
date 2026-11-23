#!/usr/bin/env bash
# E205 on fvcrc13 GPU 3: build Falcon-H1 items, then the five conditions in sequence.
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e205_run.py /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e195_capture.py /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e194_items.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
until grep -q DL_DONE /tmp/xiang_hyb/dl_FH3.log; do sleep 20; done
grep -h MISMATCH /tmp/xiang_hyb/dl_FH3.log && exit 1
./env/bin/python -I e194_items.py passages.json /tmp/xiang_hyb/models/FH3 /tmp/xiang_hyb/work_fh3 | tail -n 3
for c in none noconv nomem noattn noconv_noattn; do
  CUDA_VISIBLE_DEVICES=3 ./env/bin/python -I e205_run.py /tmp/xiang_hyb/models/FH3 /tmp/xiang_hyb/work_fh3/items.json passages.json /tmp/xiang_hyb/out_fh3/$c $c 2>&1 | grep -v "Warn\|warn\|falling\|Loading"
done
echo E205_DONE
