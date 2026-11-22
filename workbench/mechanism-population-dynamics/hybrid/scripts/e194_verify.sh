#!/usr/bin/env bash
# Verify downloaded safetensors against the HF LFS sha256 (oid). Usage: e194_verify.sh ROOT
ROOT=${1:-/tmp/xiang_e194/models}
declare -A SPEC=([H]="allenai/Olmo-Hybrid-7B stage1-step1414078" [H0]="allenai/Olmo-Hybrid-7B stage1-step0" [T]="allenai/Olmo-3-1025-7B stage1-step1413814" [T0]="allenai/Olmo-3-1025-7B stage1-step0")
for key in H H0 T T0; do
  read -r repo rev <<<"${SPEC[$key]}"
  curl -sL --max-time 60 "https://huggingface.co/api/models/$repo/tree/$rev" | python3 -I -c '
import json,sys
for f in json.load(sys.stdin):
    if f["path"].endswith(".safetensors"): print(f["path"], f["lfs"]["oid"])' | while read -r p oid; do
    got=$(sha256sum "$ROOT/$key/$p" | cut -d" " -f1)
    [ "$got" = "$oid" ] && echo "OK $key $p" || echo "MISMATCH $key $p $got $oid"
  done
done
