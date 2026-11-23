#!/usr/bin/env bash
# E206: envs with older/newer fla to find one that reproduces the Mamba and HGRN2 checkpoints (NLL check only).
set -e
B=/tmp/xiang_e194
export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python UV_NO_CONFIG=1 PYTHONNOUSERSITE=1
for v in 0.1.2 0.2.2 0.6.0; do
  E=/tmp/xiang_e206_fla$v/env
  [ -x $E/bin/python ] || { mkdir -p /tmp/xiang_e206_fla$v; cp -a /tmp/xiang_e199/env $E; }
  $B/uv/uv-x86_64-unknown-linux-gnu/uv pip install -q --python $E/bin/python "flash-linear-attention==$v" 2>&1 | tail -n 2
  $E/bin/python -c "import fla, transformers; print('ENV', fla.__version__, transformers.__version__)"
done
echo E206_ENVS_DONE
