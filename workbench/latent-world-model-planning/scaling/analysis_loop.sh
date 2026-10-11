#!/bin/bash
# periodic diagnostics + bank metrics over all finished checkpoints (one GPU)
cd /home/xiang/ssn-group-papaer/workbench/latent-world-model-planning/scaling
export CKS=0020000,0060000
while true; do
  for T in tworoom pusht reacher; do
    RUNS=$(ls -d /tmp/latent-wm-runs/scaling/${T}_* /home/xiang/.cache/latent-wm-results/scaling/${T}_* 2>/dev/null | while read d; do [ -f $d/config.json ] && echo $d; done)
    /home/xiang/.venvs/latent-wm/bin/python bank_metrics.py --runs $RUNS 2>&1 | grep -v -i warn
    /home/xiang/.venvs/latent-wm/bin/python analyze_ckpt.py --runs $RUNS 2>&1 | grep -v -i warn
  done
  for T in tworoom pusht; do /home/xiang/.venvs/latent-wm/bin/python kernel_ell.py --task $T 2>&1 | grep -v -i warn; done
  sleep 900
done
