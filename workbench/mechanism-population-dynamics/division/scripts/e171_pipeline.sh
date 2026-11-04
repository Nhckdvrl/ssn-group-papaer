#!/usr/bin/env bash
# E171: after the exact rerun reaches its endpoint, run the GPU captures and then the CPU comparisons.
# 11-04: generalised to the relocated rerun (I4D0R vs I4D0, endpoint 3.2B). Order: cheap captures first so the
# routing ceiling is available minutes after training ends; R4 (drop fingerprints, ~1 h per model) last.
# Usage: e171_pipeline.sh GPU [RUN BASE END]
set -euo pipefail
G=${1:-0}; RUN=${2:-I4D0R}; BASE=${3:-I4D0}; END=${4:-3200000000}
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/division/scripts
A=/home/xiang/mechpop_cache/e167_analysis
R=/home/xiang/mechpop_cache/e167_runs
PY=~/.venvs/mechpop/bin/python
FINAL=$R/$RUN/ckpt_$END.pt
[ -f $FINAL ] || { echo "endpoint checkpoint missing: $FINAL"; exit 2; }
cd $S
export CUDA_VISIBLE_DEVICES=$G
echo "== routing captures for every $RUN checkpoint"
for ck in $R/$RUN/ckpt_*.pt; do
  n=$(basename $ck .pt); t=${n#ckpt_}
  [ -f $A/routing/${RUN}__ckpt_$t.npz ] || $PY -B capture_routing.py $A/routing $ck
done
echo "== quick routing comparison"
$PY -I e171_compare.py $RUN $BASE $END routing_only || true
echo "== token-level causal roles (E168 v3) at $END for the rerun pair and the reference runs"
$PY -B token_roles.py capture $A/token_roles 2,3,6,7,8,9,10,11 128 $FINAL $R/$BASE/ckpt_$END.pt $R/I0D0/ckpt_$END.pt $R/I0D1/ckpt_$END.pt $R/I1D0/ckpt_$END.pt
echo "== route fingerprints (no R4) at $END for $RUN"
[ -f $A/functional/${RUN}__ckpt_$END.npz ] || E167_BATCH=16 $PY -B functional_probe.py $A/functional --no-r4 $FINAL
echo "== heads attention fingerprints for $RUN (4e8, 8e8, 1.6e9)"
for t in 400000000 800000000 1600000000; do
  [ -f $A/heads_attn/${RUN}__ckpt_$t.npz ] || [ ! -f $R/$RUN/ckpt_$t.pt ] || $PY -B heads_attn_fp.py $A/heads_attn $R/$RUN/ckpt_$t.pt
done
echo "== hidden states at $END (E169/E170 style analyses)"
$PY -B capture_hidden.py $A/hidden $FINAL $R/$BASE/ckpt_$END.pt
echo "== CPU comparisons"
$PY -I e171_compare.py $RUN $BASE $END
echo "== R4 drop fingerprints at $END (rerun pair only; ~1 h each)"
for r in $RUN $BASE; do
  f=$A/functional/${r}__ckpt_$END.npz
  if ! $PY -c "import numpy as np,sys; z=np.load('$f'); sys.exit(0 if 'drop_fp' in z.files else 1)" 2>/dev/null; then
    mv -f $f $f.nor4 2>/dev/null || true
    E167_BATCH=16 $PY -B functional_probe.py $A/functional $R/$r/ckpt_$END.pt
  fi
done
$PY -I e171_compare.py $RUN $BASE $END
echo "done"
