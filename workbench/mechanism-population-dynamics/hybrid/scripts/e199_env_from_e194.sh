#!/usr/bin/env bash
# E199 env = copy of the working E194 env (torch 2.8 cu128) + transformers 4.57.6 + flash-linear-attention 0.4.0.
# Avoids re-downloading NVIDIA wheels (pypi.nvidia.com failed repeatedly on 11-23 while models were downloading).
set -e
for p in $(ps -eo pid,args | grep "[e]199_mkenv.sh" | awk '{print $1}'); do pkill -P $p || true; kill $p || true; done
rm -rf /tmp/xiang_e199/env
mkdir -p /tmp/xiang_e199
cp -a /tmp/xiang_e194/env /tmp/xiang_e199/env
B=/tmp/xiang_e194
export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python UV_NO_CONFIG=1 PYTHONNOUSERSITE=1
$B/uv/uv-x86_64-unknown-linux-gnu/uv pip install -q --python /tmp/xiang_e199/env/bin/python "transformers==4.57.6" "flash-linear-attention==0.4.0"
/tmp/xiang_e199/env/bin/python -c "import torch, transformers, fla; print('ENV_OK', torch.__version__, transformers.__version__, fla.__version__, torch.cuda.is_available())"
