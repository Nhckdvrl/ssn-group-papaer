#!/usr/bin/env bash
# Fetch one HF repo revision (json/txt/safetensors/model files at top level) with curl, then verify LFS sha256.
# Usage: dl_hf.sh REPO REV DIR
set -u
repo=$1; rev=$2; dir=$3; mkdir -p "$dir"
curl -sL --max-time 60 "https://huggingface.co/api/models/$repo/tree/$rev" | python3 -I -c '
import json,sys
for f in json.load(sys.stdin):
    p=f["path"]
    if "/" not in p and p.endswith((".json",".safetensors",".txt",".model",".py",".tiktoken")):
        print(p, f.get("size",0), (f.get("lfs") or {}).get("oid","-"))' > "$dir/.files"
echo "$repo@$rev" > "$dir/SOURCE"
while read -r p size oid; do
  if [ -f "$dir/$p" ] && [ "$(stat -c %s "$dir/$p")" = "$size" ]; then continue; fi
  for try in 1 2 3 4 5; do curl -sL --fail --retry 3 -C - --max-time 7200 -o "$dir/$p" "https://huggingface.co/$repo/resolve/$rev/$p" && break; sleep 20; done
  if [ "$oid" != "-" ]; then got=$(sha256sum "$dir/$p" | cut -d" " -f1); [ "$got" = "$oid" ] && s=OK || s=MISMATCH; else s=nolfs; fi
  echo "$(date +%T) $repo $p $s"
done < "$dir/.files"
echo "DL_DONE $repo"
