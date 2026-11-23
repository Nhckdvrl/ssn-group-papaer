#!/usr/bin/env bash
# E202 on fvcrc13: remaining fla-hub models (+ noconv for the conv models), sequential per GPU.
cd /tmp/xiang_e194
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
PY="/tmp/xiang_e199/env/bin/python -I /tmp/xiang_e194/e202_run.py"
I=/tmp/xiang_hyb/work_fla/items.json; M=/tmp/xiang_hyb/models; O=/tmp/xiang_hyb/out_fla
mkdir -p $O
nohup bash -c "CUDA_VISIBLE_DEVICES=0 $PY $M/fla_transformer $I passages.json $O/TF; CUDA_VISIBLE_DEVICES=0 $PY $M/fla_delta_net $I passages.json $O/DN; CUDA_VISIBLE_DEVICES=0 $PY $M/fla_delta_net $I passages.json $O/DN_noconv --noconv_upto 2; echo E202_G0_DONE" > $O/g0.log 2>&1 &
nohup bash -c "CUDA_VISIBLE_DEVICES=1 $PY $M/fla_mamba $I passages.json $O/MB; CUDA_VISIBLE_DEVICES=1 $PY $M/fla_mamba $I passages.json $O/MB_noconv --noconv_upto 5; echo E202_G1_DONE" > $O/g1.log 2>&1 &
nohup bash -c "CUDA_VISIBLE_DEVICES=2 $PY $M/fla_gla $I passages.json $O/GLA; CUDA_VISIBLE_DEVICES=2 $PY $M/fla_gsa $I passages.json $O/GSA; echo E202_G2_DONE" > $O/g2.log 2>&1 &
nohup bash -c "CUDA_VISIBLE_DEVICES=3 $PY $M/fla_hgrn $I passages.json $O/HGRN; CUDA_VISIBLE_DEVICES=3 $PY $M/fla_hgrn2 $I passages.json $O/HGRN2; CUDA_VISIBLE_DEVICES=3 $PY $M/fla_retnet $I passages.json $O/RET; echo E202_G3_DONE" > $O/g3.log 2>&1 &
