#!/bin/bash
# Export an E23 TF fine-tuning checkpoint and run the phase-resolved impulse probe (20-step sampler, as tfbase).
# Usage: eval_tf_ft.sh <run_dir> <step> <tag> <gpu> [prompts]
source /home/xiang/ssn-group-papaer/workbench/video-world-model-temporal-interfaces/scripts/env.sh
export PYTHONPATH=$WB/vendor/minWM:$PYTHONPATH
cd $WB/vendor/minWM
RUN=$1; STEP=$2; TAG=$3; GPU=$4; PR=${5:-1,2,3,4}
PT=$RUN/export_${STEP}_model.pt
until [ -f $PT ] || { [ -f $RUN/ckpts/checkpoint_$STEP/.metadata ] && [ -z "$(find $RUN/ckpts/checkpoint_$STEP -mmin -2)" ]; }; do sleep 60; done
[ -f $PT ] || CUDA_VISIBLE_DEVICES=$GPU $PY tools/export_checkpoint.py --checkpoint $RUN/ckpts/checkpoint_$STEP --output $PT --model-key model
S=$(for k in 3 4 5 6 7 8 9 10 11 12; do printf "impulse:3:$k,"; done)
CUDA_VISIBLE_DEVICES=$GPU $PY $WB/scripts/mwm_sysid.py --stage stage1_ar_tf --ckpt $PT --tag $TAG --ov 'inference.num_inference_steps=20' \
  --out $WB/results/raw/e23_eval --prompts $PR --seqs ${S%,}
