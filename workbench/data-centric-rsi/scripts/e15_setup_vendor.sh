#!/usr/bin/env bash
# E15: vendor the pure-Python graders R-Zero uses (mathruler + pylatexenc) into a node-local dir,
# without installing into any shared env (compute policy). Pinned by sha256.
# Usage: bash e15_setup_vendor.sh [dest=/tmp/xiang_e15/vendor]
set -euo pipefail
dest=${1:-/tmp/xiang_e15/vendor}
mkdir -p "$dest/whl"
fetch() {  # url sha256 name
  local f="$dest/whl/$3"
  [ -s "$f" ] || curl -sL --retry 5 --speed-limit 10000 --speed-time 60 -o "$f" "$1"
  echo "$2  $f" | sha256sum -c - >/dev/null
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$f" "$dest"
}
fetch https://files.pythonhosted.org/packages/54/a5/91d16d65b66251c2423bfedb9219c2e803f11d91af9bfba75f05ddc33bfb/mathruler-0.1.0-py3-none-any.whl \
      e8ce0d9e07e892bf971fbff5e6eee330f6a66fd022666c99828a0000c788079f mathruler-0.1.0-py3-none-any.whl
fetch https://files.pythonhosted.org/packages/e7/06/3d67bd912ef337aa4856b466121d03f304aa1bb4d804f9298b6227cd227e/pylatexenc-2.11-py2.py3-none-any.whl \
      e78e7391d6c104f1ed150e21cfaa58016cdb50aa54406a2eecb793649ffdfdd0 pylatexenc-2.11-py2.py3-none-any.whl
echo "vendor ready: export PYTHONPATH=$dest:\$PYTHONPATH"
