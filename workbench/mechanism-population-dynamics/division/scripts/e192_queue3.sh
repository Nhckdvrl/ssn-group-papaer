# E192 round-3 queue (card "B2r 的结果与第三轮", 11-18).  Same mechanism as e192_queue.sh: node-local polling every 60 s,
# atomic `mkdir $B/queue/r3_<job>` claim, skip if the arm dir exists, launch when the occupying arm's DONE exists and the GPU
# uses < 2 GB.  Arm dirs: P6GS03, DL1only, CL1_1, CD_1, DL1free (fvcrc20); CL1_2, CD_2, D2, E2 (fvcrc21).
# usage: nohup bash e192_queue3.sh fvcrc20|fvcrc21 > /tmp/xiang_e192/queue/queue3_<node>.out 2>&1 &
B=/tmp/xiang_e192; S=$B/scripts; Q=$B/queue; mkdir -p $Q; L=$S/e192_launch.sh
log() { echo "$(date '+%F %T') [r3] $*" >> $Q/queue.log; }
D28="2,3,4,5,6,7,8"
case $1 in
  fvcrc20) JOBS=("r3_P6_DL1only|3|B2r/DONE_0540|P6GS03|bash $S/e192_p6run.sh"
                 "r3_CL1_1|0|A5/DONE_0540|CL1_1|XARGS='--reset-layers 1' bash $L CL1_1 0 1080 free 1 540 on 201"
                 "r3_CD_1|1|B5/DONE_0540|CD_1|XARGS='--reset-layers $D28' bash $L CD_1 1 1080 free 1 540 on 301"
                 "r3_DL1free|2|G2/DONE_0540|DL1free|XARGS='--freeze-layers $D28' bash $L DL1free 2 540 free 1 540") ;;
  fvcrc21) JOBS=("r3_CL1_2|0|A3/DONE_0540|CL1_2|XARGS='--reset-layers 1' bash $L CL1_2 0 1080 free 2 540 on 202"
                 "r3_CD_2|1|B3/DONE_0540|CD_2|XARGS='--reset-layers $D28' bash $L CD_2 1 1080 free 2 540 on 302"
                 "r3_D2|2|A4/DONE_0540|D2|bash $L D2 2 540 frozen 2 540"
                 "r3_E2|3|B4/DONE_0540|E2|bash $L E2 3 540 free 2 540") ;;
  *) echo "usage: $0 fvcrc20|fvcrc21"; exit 1 ;;
esac
log "queue3 start on $(hostname): ${#JOBS[@]} jobs"
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
    log "LAUNCH $name on gpu $gpu (waited for $wait): $cmd"
    nohup bash -c "$cmd" >> $Q/$name.log 2>&1 &
  done
  [ $left -eq 0 ] && { log "queue3 done on $(hostname)"; exit 0; }
  sleep 60
done
