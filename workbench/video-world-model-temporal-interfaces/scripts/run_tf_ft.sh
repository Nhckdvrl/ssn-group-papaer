#!/bin/bash
# Teacher-forcing AR fine-tuning of the released minWM Wan21 Action2V stage-1 (AR TF) model on a chosen LMDB.
# Usage: run_tf_ft.sh <gpu_list e.g. 0,1> <lmdb_dir> <out_dir> <max_steps> [port]
source /home/xiang/ssn-group-papaer/workbench/video-world-model-temporal-interfaces/scripts/env.sh
export PYTHONPATH=$WB/vendor/minWM:$PYTHONPATH
cd $WB/vendor/minWM
export CUDA_VISIBLE_DEVICES=$1
NP=$(echo $1 | tr ',' '\n' | wc -l)
TF=./ckpts/Wan21/Action2V/stage1_ar_tf/model.pt
$PY -m torch.distributed.run --nproc_per_node=$NP --master_port=${5:-29521} tools/train_mwm.py \
  --config-file ${CONFIG:-configs/wan21/action2v/train/stage1_ar_tf.py} --output-dir $3 \
  training.sp_size=1 training.max_steps=$4 training.ckpt_interval=${CKPT:-250} training.log_interval=10 \
  training.activation_checkpointing=${AC:-True} recipe.optimizer.lr=${LR:-2e-6} checkpoint.pretrained=$TF data.dataset.data_path=$2
