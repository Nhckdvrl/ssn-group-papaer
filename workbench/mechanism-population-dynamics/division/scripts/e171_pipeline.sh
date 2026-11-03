#!/usr/bin/env bash
# E171: after I0D0R reaches its endpoint, run the remaining GPU captures (the analysis worker already does
# routing capture / R0 / R4-at-final / heads as checkpoints appear) and then the CPU comparisons.
# Usage: e171_pipeline.sh GPU
set -euo pipefail
G=${1:-2}
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
A=/home/xiang/mechpop_cache/e167_analysis
R=/home/xiang/mechpop_cache/e167_runs
PY=~/.venvs/mechpop/bin/python
FINAL=$R/I0D0R/ckpt_3999793152.pt
[ -f $FINAL ] || { echo "endpoint checkpoint missing: $FINAL"; exit 2; }
cd $S
echo "== token-level causal roles (E168 v3) at endpoint"
CUDA_VISIBLE_DEVICES=$G $PY -B token_roles.py capture $A/token_roles 2,3,6,7,8,9,10,11 128 $FINAL
echo "== hidden states at endpoint (E169/E170 analyses)"
CUDA_VISIBLE_DEVICES=$G $PY -B capture_hidden.py $A/hidden $FINAL
echo "== make sure routing / functional captures exist for every checkpoint (worker may still be busy)"
for ck in $R/I0D0R/ckpt_*.pt; do
  n=$(basename $ck .pt); t=${n#ckpt_}
  [ -f $A/routing/I0D0R__ckpt_$t.npz ] || CUDA_VISIBLE_DEVICES=$G $PY -B capture_routing.py $A/routing $ck
done
[ -f $A/functional/I0D0R__ckpt_3999793152.npz ] && $PY -c "import numpy as np,sys; z=np.load('$A/functional/I0D0R__ckpt_3999793152.npz'); sys.exit(0 if 'drop_fp' in z.files else 1)" \
  || E167_BATCH=16 CUDA_VISIBLE_DEVICES=$G $PY -B functional_probe.py $A/functional $FINAL
[ -f $A/heads_attn/I0D0R__ckpt_1600000000.npz ] || CUDA_VISIBLE_DEVICES=$G $PY -B heads_attn_fp.py $A/heads_attn $R/I0D0R/ckpt_1600000000.pt
echo "== CPU comparisons"
$PY -I e171_compare.py
echo "done"
