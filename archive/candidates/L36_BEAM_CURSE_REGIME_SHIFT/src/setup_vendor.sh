#!/bin/bash
# L36 vendored, NOT installed: the frozen `verl-clean` env lacks `sacremoses` (needed by the
# FSMT tokenizer) and `sacrebleu` (needed only to validate our own metric implementation), and the
# repo compute policy forbids installing packages. Both are unpacked into ./vendor and reached via
# PYTHONPATH, so site-packages is never touched. Pinned by sha256 in results/e00/vendor_manifest.json.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
V="$HERE/vendor"; mkdir -p "$V/stub" "$V/dl"

SACREMOSES_URL=https://files.pythonhosted.org/packages/a4/69/e71340bf92b312107e8e1e9d360d45c8b304151ff1e022b6d4c1343a073a/sacremoses-0.2.0.tar.gz
SACREBLEU_URL=https://github.com/mjpost/sacrebleu/archive/refs/tags/v2.4.3.tar.gz

[ -f "$V/dl/sacremoses.tar.gz" ] || curl -sL -o "$V/dl/sacremoses.tar.gz" "$SACREMOSES_URL"
[ -f "$V/dl/sacrebleu.tar.gz" ]  || curl -sL -o "$V/dl/sacrebleu.tar.gz"  "$SACREBLEU_URL"
tar xzf "$V/dl/sacremoses.tar.gz" -C "$V"
tar xzf "$V/dl/sacrebleu.tar.gz"  -C "$V"
echo '__version__ = "2.4.3"' > "$V/sacrebleu-2.4.3/sacrebleu/version.py"

# sacrebleu CLI-only deps we never exercise (no dataset downloads, no colored tables)
cat > "$V/stub/portalocker.py" <<'PY'
class Lock:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
def lock(*a, **k): pass
def unlock(*a, **k): pass
PY
cat > "$V/stub/colorama.py" <<'PY'
class _C:
    def __getattr__(self, k): return ""
Fore = Back = Style = _C()
def init(*a, **k): pass
PY
cat > "$V/stub/tabulate.py" <<'PY'
def tabulate(*a, **k): return ""
PY
mkdir -p "$V/stub/lxml"; : > "$V/stub/lxml/__init__.py"
cat > "$V/stub/lxml/etree.py" <<'PY'
def parse(*a, **k): raise NotImplementedError("stub: WMT XML datasets are not used")
PY

echo "PYTHONPATH=$V/sacremoses-0.2.0:$V/sacrebleu-2.4.3:$V/stub"
