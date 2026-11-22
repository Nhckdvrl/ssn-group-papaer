# E199: node-local env for the Ring/Ling remote code (written for transformers 4.56; needs flash-linear-attention).
# Usage: ssh <node> bash -s < e199_mkenv.sh   -> /tmp/xiang_e199/env
set -e
B=/tmp/xiang_e199
mkdir -p $B/uv
export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python XDG_CACHE_HOME=$B/uv/xdg XDG_DATA_HOME=$B/uv/xdgd XDG_CONFIG_HOME=$B/uv/xdgc UV_NO_CONFIG=1 PYTHONNOUSERSITE=1
cd $B/uv
[ -x $B/uv/uv-x86_64-unknown-linux-gnu/uv ] || curl -sSL https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz | tar xz
UV=$B/uv/uv-x86_64-unknown-linux-gnu/uv
[ -x $B/env/bin/python ] || $UV venv $B/env --python 3.12
$UV pip install -q --python $B/env/bin/python torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
$UV pip install -q --python $B/env/bin/python transformers==4.57.6 numpy scipy accelerate safetensors huggingface_hub flash-linear-attention==0.4.0
$B/env/bin/python -c "import torch, transformers, fla; print(torch.__version__, transformers.__version__, fla.__version__, torch.cuda.is_available())"
