#!/usr/bin/env bash
# Download public checkpoints to node-local disk with plain curl (HF Xet client stalls on these hosts).
# Files are fetched in parallel (one curl per file, resumable with -C -).
# Usage: PAR=12 fetch_models.sh <dest_root> <repo_id>[@revision] ...
# Writes <dest_root>/<org>__<name>/ with all repo files + REVISION (resolved commit sha).
set -euo pipefail
dest=$1; shift
PAR=${PAR:-12}
jobs=$(mktemp)
for spec in "$@"; do
  repo=${spec%@*}; rev=main; [[ $spec == *@* ]] && rev=${spec#*@}
  out=$dest/${repo/\//__}; mkdir -p "$out"
  meta=$(curl -sf "https://huggingface.co/api/models/$repo/revision/$rev")
  sha=$(python3 -c 'import json,sys;print(json.loads(sys.stdin.read(),strict=False)["sha"])' <<<"$meta")
  echo "$sha" > "$out/REVISION"
  python3 -c 'import json,sys;[print(s["rfilename"]) for s in json.loads(sys.stdin.read(),strict=False)["siblings"]]' <<<"$meta" |
    grep -v -E '\.md$|^\.gitattributes$' | while read -r f; do echo "$repo $sha $out $f"; done >> "$jobs"
done
fetch_one() {
  set -- $1
  mkdir -p "$3/$(dirname "$4")"
  local auth=(); [[ -f ~/.cache/huggingface/token ]] && auth=(-H "Authorization: Bearer $(cat ~/.cache/huggingface/token)")
  local size; size=$(curl -sfIL --max-time 30 --retry 3 "${auth[@]}" "https://huggingface.co/$1/resolve/$2/$4" | grep -i '^content-length' | tail -1 | tr -dc 0-9)
  for attempt in $(seq 1 40); do
    [[ -n $size && -f "$3/$4" && $(stat -c %s "$3/$4") -ge $size ]] && { echo "ok $1 $4"; return; }
    # abort transfers slower than 50 kB/s for 60 s, then resume from the partial file
    curl -sL "${auth[@]}" --connect-timeout 20 --speed-limit 50000 --speed-time 60 -C - -o "$3/$4" "https://huggingface.co/$1/resolve/$2/$4"
    [[ -z $size ]] && { echo "ok? $1 $4 (no size)"; return; }
    sleep 3
  done
  echo "FAIL $1 $4"
}
export -f fetch_one
xargs -d '\n' -P "$PAR" -I{} bash -c 'fetch_one "$@"' _ {} < "$jobs"
rm -f "$jobs"
echo ALLDONE
