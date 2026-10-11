#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_url="https://github.com/qinchonghanzuibang/ImplicitMemBench.git"
commit="927413bf3f5389bb47c94c2a0ba987e435b101b8"
target="$project_dir/data/upstream/implicitmembench"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git clone --quiet --filter=blob:none "$repo_url" "$tmp/repo"
git -C "$tmp/repo" checkout --quiet --detach "$commit"
mkdir -p "$target/dataset/classical_conditioning"
cp "$tmp/repo/dataset/LICENSE" "$target/LICENSE"
cp "$tmp/repo/dataset/classical_conditioning/conditioned_api_aversion.json" "$target/dataset/classical_conditioning/conditioned_api_aversion.json"
{
  printf 'source=%s\n' "$repo_url"
  printf 'commit=%s\n' "$commit"
  printf 'fetched_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  (
    cd "$project_dir"
    sha256sum data/upstream/implicitmembench/LICENSE data/upstream/implicitmembench/dataset/classical_conditioning/conditioned_api_aversion.json
  )
} > "$project_dir/data/upstream/PROVENANCE.txt"
cat "$project_dir/data/upstream/PROVENANCE.txt"
