#!/bin/bash
# Export a fine-tuned minWM DMD checkpoint (generator EMA or raw) and run the E19 probe set on it.
# Usage: eval_ft.sh <run_dir> <step> <tag> <gpu> [model_key]
source /home/xiang/ssn-group-papaer/workbench/video-world-model-temporal-interfaces/scripts/env.sh
export PYTHONPATH=$WB/vendor/minWM:$PYTHONPATH
cd $WB/vendor/minWM
RUN=$1; STEP=$2; TAG=$3; GPU=$4; KEY=${5:-aux/generator_ema}
OUT=$WB/results/raw/e19_eval
PT=$RUN/export_${STEP}_$(echo $KEY | tr '/' '_').pt
[ -f $PT ] || CUDA_VISIBLE_DEVICES=$GPU $PY tools/export_checkpoint.py --checkpoint $RUN/ckpts/checkpoint_$STEP --output $PT --model-key $KEY
EXTRA="step:3:3,sine:3:8,sine:3:6"
CUDA_VISIBLE_DEVICES=$GPU $PY $WB/scripts/mwm_sysid.py --stage stage3_ar_dmd --ckpt $PT --tag $TAG --out $OUT --prompts 1,2,3,4,5 --seqs $(cat $OUT/imp_specs.txt),$EXTRA
CUDA_VISIBLE_DEVICES=$GPU $PY $WB/scripts/mwm_sysid.py --stage stage3_ar_dmd --ckpt $PT --tag $TAG --out $OUT --prompts 1,2 --seqs $(cat $OUT/nudge_specs.txt)
