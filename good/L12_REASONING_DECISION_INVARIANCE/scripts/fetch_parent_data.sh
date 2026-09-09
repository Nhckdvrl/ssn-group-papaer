#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_dir="$project_dir/data/upstream/mind-the-dh-gap"
repo_url="https://github.com/Yongyan-Zhang/mind-the-dh-gap.git"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

mkdir -p "$(dirname "$target_dir")"
git clone --quiet --filter=blob:none "$repo_url" "$tmp_dir/repo"
git -C "$tmp_dir/repo" checkout --quiet --detach origin/main
commit="$(git -C "$tmp_dir/repo" rev-parse HEAD)"
mkdir -p "$target_dir"
rsync -a --delete --exclude='.git/' "$tmp_dir/repo/" "$target_dir/"
{
  printf 'source=%s\n' "$repo_url"
  printf 'commit=%s\n' "$commit"
  printf 'fetched_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  (
    cd "$project_dir"
    find data/upstream/mind-the-dh-gap/data -type f -name '*.csv' -print0 | sort -z | xargs -0 sha256sum
  )
} > "$project_dir/data/upstream/PROVENANCE.txt"
