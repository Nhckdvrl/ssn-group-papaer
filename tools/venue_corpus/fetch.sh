#!/usr/bin/env bash
# Download top-tier venue paper lists (titles, abstracts, decisions, review scores where public).
# Sources: papercopilot/paperlists (OpenReview-derived JSON) and acl-org/acl-anthology (XML).
# Policy (2026-09-30): top-tier only. EACL and all Findings volumes are excluded by build.py.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data/raw
PC_RAW=https://raw.githubusercontent.com/papercopilot/paperlists/main
PC_LFS=https://media.githubusercontent.com/media/papercopilot/paperlists/main
ACL_RAW=https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml

get() {  # get <url> <out>; tolerate missing files
  if curl -sS -m 600 -L --fail -o "$2.tmp" "$1"; then
    # papercopilot stores some large files in Git LFS: a tiny pointer on raw, the payload on media
    if head -c 40 "$2.tmp" | grep -q "git-lfs"; then rm -f "$2.tmp"; return 1; fi
    mv "$2.tmp" "$2"; echo "ok   $2 ($(wc -c < "$2") bytes)"
  else rm -f "$2.tmp"; echo "miss $1"; return 1; fi
}
for f in iclr/iclr2026 iclr/iclr2025 icml/icml2026 icml/icml2025 nips/nips2025 nips/nips2024 \
         cvpr/cvpr2026 cvpr/cvpr2025 iccv/iccv2025 naacl/naacl2025 acl/acl2025 emnlp/emnlp2024 nips/nips2026; do
  out=data/raw/$(basename $f).json
  get "$PC_RAW/$f.json" "$out" || get "$PC_LFS/$f.json" "$out" || true
done
for v in 2026.acl 2025.acl 2025.emnlp 2026.naacl 2025.naacl 2026.emnlp; do
  get "$ACL_RAW/$v.xml" "data/raw/$v.xml" || true
done
echo "done. next: python3 build.py"
