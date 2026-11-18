# E192 round 3 (p6 test, card "B2r 的结果与第三轮"): continue from S (iter 1080) for 108 iters on the OFFICIAL training data
# (DCLM global-shard_03/local-shard_1, pool_GS03.u16; free router, seed 1), save/eval/dump at c0/c54/c108 on our held-out
# streams, keep full weights at c54/c108, then evaluate them (and nothing else) on the gs10 + gs05 streams with e192_p6.py.
# Then launch DL1only on the same GPU.  Run by e192_queue3.sh on fvcrc20 GPU 3.
B=/tmp/xiang_e192; S=$B/scripts; L=$S/e192_launch.sh; G=3
[ -f $B/dclm/pool_GS03.u16 ] || { echo "pool_GS03 missing"; exit 1; }
XARGS="--pools GS03 --full-every 54" bash $L P6GS03 $G 1080 free 1 108
until [ -f $B/arms/P6GS03/DONE_0108 ]; do sleep 60; done
sleep 30
for c in 0054 0108; do
  CUDA_VISIBLE_DEVICES=$G TORCHINDUCTOR_CACHE_DIR=$B/inductor_$G TRITON_CACHE_DIR=$B/triton_$G \
  C_INCLUDE_PATH=$B/uv/python/cpython-3.12.16-linux-x86_64-gnu/include/python3.12 \
  $B/env/bin/python -I $S/e192_p6.py --out $B/p6 --name P6GS03_c$c --state $B/arms/P6GS03/full_c$c.pt --start-ckpt $B/ckpt/iter_0001080
done
echo "p6 evals done $(date)"
XARGS="--freeze-layers 1" bash $L DL1only $G 540 free 1 540
