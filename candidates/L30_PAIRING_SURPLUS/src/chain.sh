#!/bin/bash
# Wait for training to finish, then evaluate everything, then summarize.
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
while ! grep -q "ALL TRAINING DONE" results/logs/launcher.log 2>/dev/null; do sleep 120; done
echo "training done, starting evals $(date -Is)"
bash src/eval_all.sh
/home/xiang/miniconda3/envs/openslime/bin/python src/summarize.py --epoch 3 \
  --out results/E01_summary_ep3.json > results/E01_summary_ep3.txt 2>&1
echo "CHAIN COMPLETE $(date -Is)"
