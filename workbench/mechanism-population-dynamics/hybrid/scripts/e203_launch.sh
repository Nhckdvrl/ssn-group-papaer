#!/usr/bin/env bash
# E203: noconv in all layers for DeltaNet (24 layers) and Mamba (48 layers), after the E202 chains on GPUs 0/1 finish.
cd /tmp/xiang_e194
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
PY="/tmp/xiang_e199/env/bin/python -I /tmp/xiang_e194/e202_run.py"
I=/tmp/xiang_hyb/work_fla/items.json; M=/tmp/xiang_hyb/models; O=/tmp/xiang_hyb/out_fla
nohup bash -c "until grep -q E202_G0_DONE $O/g0.log; do sleep 20; done; CUDA_VISIBLE_DEVICES=0 $PY $M/fla_delta_net $I passages.json $O/DN_noconv_all --noconv_upto 23; echo E203_DN_DONE" > $O/e203_dn.log 2>&1 &
nohup bash -c "until grep -q E202_G1_DONE $O/g1.log; do sleep 20; done; CUDA_VISIBLE_DEVICES=1 $PY $M/fla_mamba $I passages.json $O/MB_noconv_all --noconv_upto 47; echo E203_MB_DONE" > $O/e203_mb.log 2>&1 &
