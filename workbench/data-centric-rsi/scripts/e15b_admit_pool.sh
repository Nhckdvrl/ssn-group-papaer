#!/usr/bin/env bash
# E15b admission as a per-file job pool on the generation node (fvcrc21). One worker per GPU; a worker starts once
# that GPU's generation queue has finished (QUEUE_DONE in queue<gpu>.log), then repeatedly takes any (solver, file)
# job whose generation file is complete and which nobody has claimed (atomic mkdir lock), until all 36 jobs are done.
# Each job: 500 parse_ok candidates of one 4,000-sample file (the first 500 of a fixed shuffle), 9 samples each
# (official R-Zero settings); 500 rather than 1,000 to keep E15 within the approved GPU budget.
# Output: /tmp/xiang_e15/admit/admit_<solver>__<file stem>.jsonl  (solver = base | s5)
# Usage: bash e15b_admit_pool.sh <gpu>
set -u
gpu=$1
S=$(cd "$(dirname "$0")" && pwd); M=/tmp/xiang_e15/models; G=/tmp/xiang_e15/gen; A=/tmp/xiang_e15/admit; L=/tmp/xiang_e15/logs
mkdir -p $A
declare -A SOLVER=([base]=$M/Qwen__Qwen3-4B-Base [s5]=$M/jinyuan222__qwen3_4b_fullrun_authorsettings_solver_v5)
STEMS="gen_v1_s0 gen_v1_s1 gen_v2_s0 gen_v2_s1 gen_v3_s0 gen_v3_s1 gen_v4_s0 gen_v4_s1 gen_base_s0 gen_base_s4 gen_base_s1 gen_base_s5 gen_base_s2 gen_base_s6 gen_base_s3 gen_base_s7 gen_v5_s0 gen_v5_s1"
until grep -q QUEUE_DONE $L/queue$gpu.log 2>/dev/null; do sleep 60; done
while :; do
  left=0; ran=0
  for stem in $STEMS; do
    for sv in base s5; do
      out=$A/admit_${sv}__${stem}.jsonl
      [ -s $out.meta.json ] || [ -e $out.failed ] && continue
      left=1
      [ -s $G/$stem.jsonl.meta.json ] || continue
      mkdir $out.lock 2>/dev/null || continue
      echo "gpu$gpu start $sv $stem $(date +%T)"
      bash $S/e15_run.sh $gpu admit_${sv}__${stem} e15b_admit.py --solver ${SOLVER[$sv]} --inputs $G/$stem.jsonl \
           --per_file 500 --n 9 --out $out || { echo "FAILED $sv $stem"; touch $out.failed; }
      ran=1
    done
  done
  [ $left = 0 ] && break
  [ $ran = 0 ] && sleep 60
done
echo "POOL_DONE gpu$gpu $(date +%T)"
