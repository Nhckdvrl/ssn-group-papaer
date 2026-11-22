#!/usr/bin/env bash
# E201 setup on the training node: env (E194 env + fla 0.4.0 + pyarrow) and one FineWeb-Edu sample-10BT shard.
set -e
mkdir -p /tmp/xiang_e201/data
if [ ! -x /tmp/xiang_e201/env/bin/python ]; then
  cp -a /tmp/xiang_e194/env /tmp/xiang_e201/env
  B=/tmp/xiang_e194
  export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python UV_NO_CONFIG=1 PYTHONNOUSERSITE=1
  $B/uv/uv-x86_64-unknown-linux-gnu/uv pip install -q --python /tmp/xiang_e201/env/bin/python "flash-linear-attention==0.4.0" pyarrow
fi
/tmp/xiang_e201/env/bin/python -c "import fla, pyarrow, transformers; print('ENV_OK', fla.__version__, pyarrow.__version__, transformers.__version__)"
f=/tmp/xiang_e201/data/000_00000.parquet
[ -f $f ] && [ "$(stat -c %s $f)" -gt 2000000000 ] || curl -sL --fail --retry 3 -C - -o $f "https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/resolve/main/sample/10BT/000_00000.parquet"
ls -la /tmp/xiang_e201/data
echo SETUP_DONE
