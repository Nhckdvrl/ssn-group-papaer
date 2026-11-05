#!/usr/bin/env bash
# E173: launch one recipe x init-seed run on HOST:GPU, only if that GPU is idle right now (same check as launch_run.sh).
# Usage: e173_launch.sh HOST GPU RECIPE SEED [extra train_moe.py args...]
#   RECIPE in FRZ | LB0 | LB0001 | G16 | G256 | LB01 | BASE   (see experiments/E173-recipe-contrast-axis.md)
#   BASE = the E167 baseline config unchanged (BASE_I0 = exact-config rerun of I0D0, added 11-06)
# The node-side job (e173_job.sh) trains, then captures routing / route fingerprints on the same GPU.
# Every run: data_seed 0, cosine schedule over 4e9 tokens stopped at step 3052 (= 8e8 tokens, same lr as the
# E167 baseline's 8e8 checkpoint), checkpoints 0/1e8/2e8/4e8/8e8.
set -euo pipefail
HOST=$1 GPU=$2 RECIPE=$3 SEED=$4; shift 4
case $RECIPE in
  FRZ)    R="--freeze-router" ;;
  LB0)    R="--lb 0" ;;
  LB0001) R="--lb 0.001" ;;
  G16)    R="--n-experts 16 --top-k 2 --expert-ffn 1536" ;;
  G256)   R="--n-experts 256 --top-k 32 --expert-ffn 96" ;;
  LB01)   R="--lb 0.1" ;;
  BASE)   R="" ;;
  *) echo "unknown recipe $RECIPE"; exit 2 ;;
esac
RUN=${RECIPE}_I${SEED}
EXTRA="$R --tokens 4e9 --max-steps 3052 --ckpt-tokens 0,1e8,2e8,4e8,8e8 $*"
SRC=/home/xiang/mechpop_cache/e167_dolma_6b
OUT=/home/xiang/mechpop_cache/e173_runs/$RUN
SCRIPTS=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
LOG=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/results/e173/_logs/$RUN.log
ssh -o BatchMode=yes "$HOST" bash -s <<EOS
set -euo pipefail
used=\$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU)
apps=\$(nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader | grep -c "\$(nvidia-smi --query-gpu=uuid --format=csv,noheader -i $GPU)" || true)
if [ "\$used" -gt 1000 ] || [ "\$apps" -gt 0 ]; then echo "GPU $GPU on $HOST busy (\${used}MiB, \$apps apps); not launching $RUN"; exit 3; fi
mkdir -p /tmp/xiang-e167/data /tmp/xiang-e173/resume/$RUN $OUT
if ! cmp -s $SRC/manifest.json /tmp/xiang-e167/data/manifest.json; then
  flock /tmp/xiang-e167/data.lock bash -c "cmp -s $SRC/manifest.json /tmp/xiang-e167/data/manifest.json || (rm -rf /tmp/xiang-e167/data/train /tmp/xiang-e167/data/held && cp -r $SRC/train $SRC/held /tmp/xiang-e167/data/ && cp $SRC/manifest.json /tmp/xiang-e167/data/)"
fi
cd $SCRIPTS
echo "\$(date '+%F %T') launch $RUN on \$(hostname):$GPU args: $EXTRA" >> $LOG
CUDA_VISIBLE_DEVICES=$GPU nohup bash $SCRIPTS/e173_job.sh $RUN $SEED $EXTRA >> $LOG 2>&1 &
echo "launched $RUN on $HOST:$GPU pid \$!"
EOS
