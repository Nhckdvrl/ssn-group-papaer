#!/bin/bash
# Wait for local training to finish, then evaluate every adapter on the remote
# A100 nodes (all arms on one hardware class), then summarise.
# Epoch 3 is the pre-registered primary, so it is evaluated first.
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
PY=/home/xiang/miniconda3/envs/openslime/bin/python
while ! grep -q "ALL TRAINING DONE" results/logs/launcher.log 2>/dev/null; do sleep 120; done
echo "training done, starting remote evals $(date -Is)"

ALL=""
for arm in P S D_mask D_rt; do for s in 0 1 2; do ALL="$ALL $arm:$s"; done; done

for ep in 3 2 1; do
  # split the 12 runs across two nodes
  A=$(echo $ALL | cut -d' ' -f1-6); B=$(echo $ALL | cut -d' ' -f7-12)
  ssh -o BatchMode=yes fvcrc13 "bash $ROOT/src/eval_remote.sh evals $ep $A" &
  ssh -o BatchMode=yes fvcrc15 "bash $ROOT/src/eval_remote.sh evals $ep $B" &
  wait
  echo "epoch $ep evals done $(date -Is)"
  $PY src/summarize.py --epoch $ep --out results/E01_summary_ep$ep.json \
    > results/E01_summary_ep$ep.txt 2>&1
done
echo "CHAIN COMPLETE $(date -Is)"
