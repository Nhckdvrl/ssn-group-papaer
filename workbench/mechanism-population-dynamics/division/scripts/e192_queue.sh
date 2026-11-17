# E192 replication-arm queue (card section 追加臂, 11-18).  Run once per node with nohup; polls node-local files every 60 s,
# launches each job when (a) the DONE file of the arm currently on that GPU exists and (b) the GPU uses < 2 GB.
# Double launch is impossible: a job is claimed by `mkdir $B/queue/<job>` (atomic) and skipped if its arm dir already exists.
# usage: nohup bash e192_queue.sh fvcrc20|fvcrc21 > /tmp/xiang_e192/queue/queue_<node>.out 2>&1 &
B=/tmp/xiang_e192; S=$B/scripts; Q=$B/queue; mkdir -p $Q; L=$S/e192_launch.sh
INC="C_INCLUDE_PATH=$B/uv/python/cpython-3.12.16-linux-x86_64-gnu/include/python3.12"
log() { echo "$(date '+%F %T') $*" >> $Q/queue.log; }
P6="cd /tmp; for x in 'off1080 --ckpt $B/ckpt/iter_0001080' 'off1620 --ckpt $B/ckpt/iter_0001620' \
 'A1_c0540 --state $B/arms/A1/full_c0540.pt --start-ckpt $B/ckpt/iter_0001080' \
 'A2_c0540 --state $B/p6/states/A2_full_c0540.pt --start-ckpt $B/ckpt/iter_0001080' \
 'E_c0540 --state $B/p6/states/E_full_c0540.pt --start-ckpt $B/ckpt/iter_0000540'; do \
 eval env CUDA_VISIBLE_DEVICES=3 TORCHINDUCTOR_CACHE_DIR=$B/inductor_3 TRITON_CACHE_DIR=$B/triton_3 $INC \
 $B/env/bin/python -I $S/e192_p6.py --out $B/p6 --name \$x >> $B/p6/p6.log 2>&1; done"
case $1 in
  fvcrc20) JOBS=("p6_B2r|3|F/DONE_0540|B2r|$P6; bash $L B2r 3 1080 frozen 2 540"
                 "A5|0|A1/DONE_1080|A5|bash $L A5 0 1080 free 5 540"
                 "B5|1|B1/DONE_1080|B5|bash $L B5 1 1080 frozen 5 540"
                 "G2|2|C1/DONE_1080|G2|bash $L G2 2 1080 frozen 2 540 off") ;;
  fvcrc21) JOBS=("A3|0|A2/DONE_1080|A3|bash $L A3 0 1080 free 3 540"
                 "B3|1|B2/DONE_1080|B3|bash $L B3 1 1080 frozen 3 540"
                 "A4|2|C2/DONE_1080|A4|bash $L A4 2 1080 free 4 540"
                 "B4|3|G/DONE_0540|B4|bash $L B4 3 1080 frozen 4 540") ;;
  *) echo "usage: $0 fvcrc20|fvcrc21"; exit 1 ;;
esac
log "queue start on $(hostname): ${#JOBS[@]} jobs"
while :; do
  left=0
  for j in "${JOBS[@]}"; do
    IFS='|' read -r name gpu wait arm cmd <<< "$j"
    [ -d $Q/$name ] && continue
    left=$((left + 1))
    [ -f $B/arms/$wait ] || continue
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $gpu | tr -d ' ')
    [ "$used" -lt 2000 ] || continue
    if [ -e $B/arms/$arm ]; then log "SKIP $name: arm dir $B/arms/$arm already exists"; mkdir -p $Q/$name; continue; fi
    mkdir $Q/$name 2>/dev/null || continue
    mkdir -p $B/p6
    log "LAUNCH $name on gpu $gpu (waited for $wait): $cmd"
    nohup bash -c "$cmd" >> $Q/$name.log 2>&1 &
  done
  [ $left -eq 0 ] && { log "queue done on $(hostname)"; exit 0; }
  sleep 60
done
