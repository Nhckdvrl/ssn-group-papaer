#!/bin/bash
# E92 queue worker (capability atlas): claims the next checkpoint in results/e92/jobs.txt (claim = atomic mkdir).
# Final checkpoints already in the shared HF cache (410M / 160M mains from E89) are loaded from there; everything else is
# fetched with curl over HTTP into the host's /tmp (huggingface_hub's Xet transfer stalls on this network, 2026-10-15),
# loaded from that directory and deleted after the run.
# Usage: bash run_e92.sh <host:gpu>
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
G=$1; H=${G%%:*}; D=${G##*:}
OUT=../results/e92; mkdir -p $OUT/claims $OUT/logs
CACHE=$HOME/mechpop_cache/hf
while read -r fam repo rev; do
  [ -z "$fam" ] && continue
  t="$(basename $repo)__${rev}"
  [ -f "$OUT/$t.json" ] && continue
  mkdir "$OUT/claims/$t" 2>/dev/null || continue
  if [ "$rev" = main ] && [[ $repo == *-410m* || $repo == *-160m* ]] && [ -d "$CACHE/models--${repo/\//--}" ]; then
    ssh -n -o BatchMode=yes "$H" "cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e92_atlas.py --repo $repo --rev main" > "$OUT/logs/$t.log" 2>&1
  else
    C=/tmp/xiang_e92/$t; U=https://huggingface.co/$repo/resolve/$rev
    ssh -n -o BatchMode=yes "$H" "mkdir -p $C && curl -sfL --retry 5 -o $C/config.json $U/config.json && (curl -sfL --retry 5 -o $C/pytorch_model.bin $U/pytorch_model.bin || curl -sfL --retry 5 -o $C/model.safetensors $U/model.safetensors) && cd $PWD && CUDA_VISIBLE_DEVICES=$D $PY e92_atlas.py --repo $repo --rev $rev --local $C; rc=\$?; rm -rf $C; exit \$rc" > "$OUT/logs/$t.log" 2>&1
  fi
  rc=$?; echo "$(date +%H:%M) [$G] $t exit=$rc"
  [ $rc -ne 0 ] && rmdir "$OUT/claims/$t" 2>/dev/null && mv "$OUT/logs/$t.log" "$OUT/logs/$t.fail.log"
done < $OUT/${JOBS:-jobs.txt}
