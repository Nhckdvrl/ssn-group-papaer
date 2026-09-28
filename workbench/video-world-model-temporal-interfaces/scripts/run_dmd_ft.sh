#!/bin/bash
# DMD fine-tuning of the released minWM Wan21 Action2V DMD student with a chosen conditioning LMDB.
# Usage: run_dmd_ft.sh <gpu_list e.g. 0,1> <lmdb_dir> <out_dir> <max_steps> [port]
source /home/xiang/ssn-group-papaer/workbench/video-world-model-temporal-interfaces/scripts/env.sh
export PYTHONPATH=$WB/vendor/minWM:$PYTHONPATH
cd $WB/vendor/minWM
export CUDA_VISIBLE_DEVICES=$1
NP=$(echo $1 | tr ',' '\n' | wc -l)
DMD=./ckpts/Wan21/Action2V/stage3_ar_dmd/model.pt
$PY -m torch.distributed.run --nproc_per_node=$NP --master_port=${5:-29511} tools/train_mwm.py \
  --config-file configs/wan21/action2v/train/stage3_ar_dmd.py --output-dir $3 \
  training.sp_size=$NP training.max_steps=$4 training.ckpt_interval=100 training.log_interval=5 training.activation_checkpointing=${AC:-True} training.activation_offload=${AO:-False} \
  checkpoint.pretrained=$DMD checkpoint.auxiliary_pretrained.generator_ema=$DMD \
  data.dataset.data_path=$2
