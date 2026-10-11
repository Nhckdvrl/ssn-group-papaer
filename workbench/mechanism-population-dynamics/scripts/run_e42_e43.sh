#!/bin/bash
# E42 (causal maps -> transfer) and E43 (dumps -> pairs / lmc) worker; claims via mkdir. Usage: run_e42_e43.sh <host:gpu> <stage>
# stage: maps | transfer | dump | pairs | lmc
cd "$(dirname "$0")"
g=$1; stage=$2; PY=$HOME/.venvs/mechpop/bin/python
ENV="PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 CUDA_VISIBLE_DEVICES=${g##*:}"
run() { ssh -n -o BatchMode=yes ${g%%:*} "cd $PWD && $ENV $PY $*"; }
mkdir -p ../results/e42/logs ../results/e42/claims ../results/e43/logs ../results/e43/claims
if [ "$stage" = pairs ] || [ "$stage" = lmc ]; then
  for i in 0 1 2 3 4 5; do
    mkdir ../results/e43/claims/$stage-$i 2>/dev/null || continue
    [ "$stage" = lmc ] && until [ "$(ssh -n -o BatchMode=yes ${g%%:*} "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i ${g##*:}" 2>/dev/null)" -ge 25000 ] 2>/dev/null; do sleep 120; done
    run e43_basis.py --$stage --part $i/6 > ../results/e43/logs/$stage-$i.log 2>&1; echo "$stage $i exit=$?"
  done; exit
fi
for s in default large-aux-2 large-aux-3; do for r in c4 falcon dclm-baseline fineweb-edu fineweb-pro dolma1_7; do
  t=${r}__$s
  case $stage in
    maps|transfer) d=../results/e42; f=$d/$stage/$t.json; cmd="e42_causal.py --$stage --recipe $r --seed $s";;
    dump) d=../results/e43; f=/home/xiang/mechpop_cache/e43/$t.pt; cmd="e43_basis.py --dump --recipe $r --seed $s";;
  esac
  [ -f $f ] && continue
  mkdir $d/claims/$stage-$t 2>/dev/null || continue
  run $cmd > $d/logs/$stage-$t.log 2>&1; echo "$stage $t exit=$?"
done; done
