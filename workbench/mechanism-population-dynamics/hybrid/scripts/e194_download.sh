#!/usr/bin/env bash
# E194 step 0: fetch the four checkpoints to node-local /tmp with curl (HF Xet stalls; see memory).
# Usage: e194_download.sh ROOT [KEY ...]   (run on the compute node; keys default to all four)
set -u
ROOT=${1:-/tmp/xiang_e194/models}
declare -A SPEC=(
  [H]="allenai/Olmo-Hybrid-7B stage1-step1414078"
  [H0]="allenai/Olmo-Hybrid-7B stage1-step0"
  [T]="allenai/Olmo-3-1025-7B stage1-step1413814"
  [T0]="allenai/Olmo-3-1025-7B stage1-step0"
)
KEYS=("${@:2}"); [ ${#KEYS[@]} -eq 0 ] && KEYS=(H H0 T T0)
for key in "${KEYS[@]}"; do
  read -r repo rev <<<"${SPEC[$key]}"
  dir="$ROOT/$key"; mkdir -p "$dir"
  files=$(curl -sL --max-time 60 "https://huggingface.co/api/models/$repo/tree/$rev" | python3 -I -c '
import json,sys
for f in json.load(sys.stdin):
    p=f["path"]
    if p.endswith((".json",".safetensors",".txt")) and "/" not in p: print(p, f.get("size",0))')
  echo "$key $repo@$rev" > "$dir/SOURCE"
  while read -r p size; do
    [ -z "$p" ] && continue
    if [ -f "$dir/$p" ] && [ "$(stat -c %s "$dir/$p")" = "$size" ]; then continue; fi
    for try in 1 2 3 4 5; do
      curl -sL --fail --retry 3 -C - --max-time 7200 -o "$dir/$p" "https://huggingface.co/$repo/resolve/$rev/$p" && break
      sleep 20
    done
    echo "$(date +%T) $key $p $(stat -c %s "$dir/$p" 2>/dev/null)/$size"
  done <<<"$files"
done
echo DONE
