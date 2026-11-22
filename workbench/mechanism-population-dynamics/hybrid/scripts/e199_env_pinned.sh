#!/usr/bin/env bash
# E199 env pinned to the Ring-linear model card: transformers 4.56.1 + flash-linear-attention 0.3.2 (torch 2.8 cu128).
set -e
rm -rf /tmp/xiang_e199b/env; mkdir -p /tmp/xiang_e199b
cp -a /tmp/xiang_e194/env /tmp/xiang_e199b/env
B=/tmp/xiang_e194
export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python UV_NO_CONFIG=1 PYTHONNOUSERSITE=1
$B/uv/uv-x86_64-unknown-linux-gnu/uv pip install -q --python /tmp/xiang_e199b/env/bin/python "transformers==4.56.1" "flash-linear-attention==0.3.2"
/tmp/xiang_e199b/env/bin/python -c "import torch, transformers, fla; print('ENV_OK', torch.__version__, transformers.__version__, fla.__version__)"
