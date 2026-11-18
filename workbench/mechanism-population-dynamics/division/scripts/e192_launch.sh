# E192 launcher: one arm per GPU, nohup, node-local dirs.  Re-running the same line resumes from resume.pt.
# usage (on the node): [XARGS="--reset-layers 1 ..."] bash e192_launch.sh <arm> <gpu> <start_iter> <router> <seed> <n_iter> [aux] [init_seed]
set -e
ARM=$1; GPU=$2; START=$3; ROUTER=$4; SEED=$5; NIT=$6; AUX=${7:-on}; INIT=${8:-}
B=/tmp/xiang_e192; O=$B/arms/$ARM; mkdir -p $O
CK=$B/ckpt/iter_$(printf %07d $START)
EXTRA=""; [ -n "$INIT" ] && EXTRA="--init-seed $INIT"
cd /tmp
CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false \
  TORCHINDUCTOR_CACHE_DIR=$B/inductor_$GPU TRITON_CACHE_DIR=$B/triton_$GPU C_INCLUDE_PATH=$B/uv/python/cpython-3.12.16-linux-x86_64-gnu/include/python3.12 \
  nohup $B/env/bin/python -I $B/scripts/e192_train.py --arm $ARM --start-ckpt $CK --router $ROUTER --seed $SEED \
  --n-iter $NIT --aux $AUX --out $O --mbs 16 $EXTRA $XARGS >> $O/stdout.log 2>&1 &
echo "$ARM pid $! gpu $GPU host $(hostname)"
