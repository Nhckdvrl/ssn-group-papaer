#!/usr/bin/env bash
# E206 (Mamba part) on fvcrc10: fla-hub mamba-1.3B-100B with transformers' native Mamba class; none / conv off 0-5 / conv off all.
set -e
mkdir -p /tmp/xiang_hyb/models /tmp/xiang_hyb/work_fla /tmp/xiang_hyb/out_fla
[ -f /tmp/xiang_hyb/models/fla_mamba/model.safetensors ] || scp -q -o BatchMode=yes -r fvcrc13:/tmp/xiang_hyb/models/fla_mamba /tmp/xiang_hyb/models/
cp /tmp/xiang_hyb/models/fla_mamba/config.json /dev/null
scp -q -o BatchMode=yes fvcrc13:/tmp/xiang_hyb/models/fla_transformer/tokenizer.json fvcrc13:/tmp/xiang_hyb/models/fla_transformer/tokenizer_config.json fvcrc13:/tmp/xiang_hyb/models/fla_transformer/special_tokens_map.json /tmp/xiang_hyb/models/fla_mamba/ 2>/dev/null || true
scp -q -o BatchMode=yes fvcrc13:/tmp/xiang_hyb/work_fla/items.json /tmp/xiang_hyb/work_fla/
cd /tmp/xiang_e194
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e202_run.py /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e195_capture.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
PY="./env/bin/python -I e202_run.py /tmp/xiang_hyb/models/fla_mamba /tmp/xiang_hyb/work_fla/items.json passages.json"
CUDA_VISIBLE_DEVICES=0 $PY /tmp/xiang_hyb/out_fla/MB --no_fla > /tmp/xiang_hyb/out_fla/mb_none.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 $PY /tmp/xiang_hyb/out_fla/MB_noconv --noconv_upto 5 --no_fla > /tmp/xiang_hyb/out_fla/mb_noconv.log 2>&1 &
CUDA_VISIBLE_DEVICES=2 $PY /tmp/xiang_hyb/out_fla/MB_noconv_all --noconv_upto 47 --no_fla > /tmp/xiang_hyb/out_fla/mb_noconv_all.log 2>&1 &
wait
echo E206_MB_DONE
