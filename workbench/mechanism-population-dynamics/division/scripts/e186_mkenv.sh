# E186: build a node-local Python env (uv, from the internet; no NFS reads) replicating the mechpop venv versions.
# Usage: ssh <node> bash -s < e186_mkenv.sh   -> /tmp/xiang_e186/env  (11-10, shared NFS stalled)
set -e
B=/tmp/xiang_e186
mkdir -p $B/uv
export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python XDG_CACHE_HOME=$B/uv/xdg XDG_DATA_HOME=$B/uv/xdgd XDG_CONFIG_HOME=$B/uv/xdgc UV_NO_CONFIG=1 PYTHONNOUSERSITE=1
cd $B/uv
t0=$(date +%s)
[ -x $B/uv/uv-x86_64-unknown-linux-gnu/uv ] || curl -sSL https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz | tar xz
UV=$B/uv/uv-x86_64-unknown-linux-gnu/uv
$UV --version
[ -x $B/env/bin/python ] || $UV venv $B/env --python 3.12
$UV pip install -q --python $B/env/bin/python torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
$UV pip install -q --python $B/env/bin/python transformers==4.57.6 numpy==1.26.4 scipy accelerate safetensors huggingface_hub
$B/env/bin/python -c "import torch, transformers, numpy, accelerate; print(torch.__version__, transformers.__version__, numpy.__version__, accelerate.__version__, torch.cuda.is_available())"
echo "env ready in $(( $(date +%s) - t0 )) s on $(hostname)"
