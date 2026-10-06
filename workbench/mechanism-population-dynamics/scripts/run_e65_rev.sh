#!/bin/bash
# E65 on another GPU: models in reverse order, skipping finished ones and ones claimed by another worker.
cd "$(dirname "$0")"; g=$1; PY=$HOME/.venvs/mechpop/bin/python
mkdir -p ../results/e65/claims
for m in $($PY -c "import e65_flan_layout as e; print(' '.join(f'{r}__{s}' for r, s in reversed(e.models())))"); do
  [ -f ../results/e65/$m.json ] && continue
  mkdir ../results/e65/claims/$m 2>/dev/null || continue
  ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:} $PY e65_flan_layout.py --recipe ${m%%__*} --seed ${m##*__}" 2>&1 | grep -v -i "warning\|cached"
done
