#!/usr/bin/env bash
# E216 worker: for each "REPO_KEY:STEP" in a queue file line range, download, run conditions on GPU $1, delete weights.
# Usage: e216_worker.sh GPU JOB [JOB ...]   JOB = H:1000 | T:3000 ...
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
B=/tmp/xiang_e194; O=$B/out216; mkdir -p $O $B/ckpt216
cd $B && cp $S/e196_causal.py $S/r1_summary.py . 2>/dev/null
g=$1; shift
for job in "$@"; do
  k=${job%%:*}; st=${job##*:}
  if [ $k = H ]; then repo=allenai/Olmo-Hybrid-7B; conds="none noconv nomem"; else repo=allenai/Olmo-3-1025-7B; conds="none T_noattn"; fi
  d=$B/ckpt216/${k}_$st
  bash $S/dl_hf.sh $repo stage1-step$st $d > $O/dl_${k}_$st.log 2>&1
  if grep -q MISMATCH $O/dl_${k}_$st.log || ! grep -q DL_DONE $O/dl_${k}_$st.log; then echo "DL_FAIL $job"; continue; fi
  for c in $conds; do
    CUDA_VISIBLE_DEVICES=$g ./env/bin/python -I e196_causal.py $d work/items.json passages.json $O/${k}_${st}_$c $c 2>&1 | grep -v -i "warn\|loading" | tail -n 2
  done
  rm -rf $d
  echo "JOB_DONE $job"
done
