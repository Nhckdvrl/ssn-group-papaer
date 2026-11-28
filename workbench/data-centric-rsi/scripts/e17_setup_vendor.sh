#!/usr/bin/env bash
# E17: vendor sortedcontainers (imported by the LeetCodeDataset prefix) into a local dir, pinned by sha256; the
# sandboxed programs add this dir to sys.path (e17_common reads $E17_VENDOR). Nothing is installed into any env.
# Usage: bash e17_setup_vendor.sh <dest>
set -euo pipefail
dest=$1; mkdir -p "$dest/whl"
f="$dest/whl/sortedcontainers-2.4.0-py2.py3-none-any.whl"
[ -s "$f" ] || curl -sL --retry 5 --speed-limit 10000 --speed-time 60 -o "$f" \
  https://files.pythonhosted.org/packages/32/46/9cb0e58b2deb7f82b84065f37f3bffeb12413f947f9388e4cac22c4621ce/sortedcontainers-2.4.0-py2.py3-none-any.whl
echo "a163dcaede0f1c021485e957a39245190e74249897e2ae4b2aa38595db237ee0  $f" | sha256sum -c - >/dev/null
python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$f" "$dest"
echo "export E17_VENDOR=$dest"
