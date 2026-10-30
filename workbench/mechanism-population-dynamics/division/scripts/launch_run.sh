#!/usr/bin/env bash
# Launch one E167 training run on HOST:GPU, only if that GPU is idle right now.
# Usage: launch_run.sh HOST GPU RUN INIT_SEED DATA_SEED [extra train_moe.py args...]
set -euo pipefail
HOST=$1 GPU=$2 RUN=$3 INIT=$4 DATA=$5; shift 5
EXTRA="$*"
SRC=/home/xiang/mechpop_cache/e167_dolma_6b
OUT=/home/xiang/mechpop_cache/e167_runs/$RUN
SCRIPTS=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
ssh -o BatchMode=yes "$HOST" bash -s <<EOF
set -euo pipefail
used=\$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU)
apps=\$(nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader | grep -c "\$(nvidia-smi --query-gpu=uuid --format=csv,noheader -i $GPU)" || true)
if [ "\$used" -gt 1000 ] || [ "\$apps" -gt 0 ]; then echo "GPU $GPU on $HOST busy (\${used}MiB, \$apps apps); not launching $RUN"; exit 3; fi
mkdir -p /tmp/xiang-e167/data /tmp/xiang-e167/resume/$RUN $OUT
if ! cmp -s $SRC/manifest.json /tmp/xiang-e167/data/manifest.json; then
  flock /tmp/xiang-e167/data.lock bash -c "cmp -s $SRC/manifest.json /tmp/xiang-e167/data/manifest.json || (rm -rf /tmp/xiang-e167/data/train /tmp/xiang-e167/data/held && cp -r $SRC/train $SRC/held /tmp/xiang-e167/data/ && cp $SRC/manifest.json /tmp/xiang-e167/data/)"
fi
cd $SCRIPTS
CUDA_VISIBLE_DEVICES=$GPU nohup ~/.venvs/mechpop/bin/python -B train_moe.py --run $RUN --init-seed $INIT --data-seed $DATA \
  --train-dir /tmp/xiang-e167/data/train --held-dir /tmp/xiang-e167/data/held \
  --out $OUT --resume /tmp/xiang-e167/resume/$RUN $EXTRA >> $OUT/console.log 2>&1 &
echo "launched $RUN on $HOST:$GPU pid \$!"
EOF
