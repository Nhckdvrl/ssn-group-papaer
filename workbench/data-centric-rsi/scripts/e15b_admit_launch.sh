#!/usr/bin/env bash
# E15b admission: score the generated candidates with the two fixed solvers (Qwen3-4B-Base and solver_v5).
# 1,000 parse_ok candidates per 4,000-sample file (= 2,000 per trained questioner, 4 x 2,000 for the 4x base budget),
# 9 samples each (official R-Zero code).  Runs on the generation node (fvcrc21) once all 18 generation files exist
# and the generation queues have exited; on any other node it first pulls the files from fvcrc21.
# Usage: bash e15b_admit_launch.sh <group: base|trained> <gpu for base solver> <gpu for s5 solver>
set -u
grp=$1; gb=$2; gs=$3
S=$(dirname "$0"); M=/tmp/xiang_e15/models; G=/tmp/xiang_e15/gen; A=/tmp/xiang_e15/admit; mkdir -p $G $A
if [ "$grp" = base ]; then pat='gen_base_s*.jsonl'; else pat='gen_v*_s*.jsonl'; fi
if [ "$(hostname -s)" = fvcrc21 ]; then
  until [ "$(ls $G/gen_*.jsonl.meta.json 2>/dev/null | wc -l)" -ge 18 ] && ! pgrep -u "$USER" -f e15b_gen_queue >/dev/null; do sleep 120; done
else
  until [ "$(ssh -o BatchMode=yes fvcrc21 "ls /tmp/xiang_e15/gen/gen_*.jsonl.meta.json 2>/dev/null | wc -l")" -ge 18 ]; do sleep 120; done
  rsync -a --include="$pat" --include="${pat}.meta.json" --exclude='*' fvcrc21:/tmp/xiang_e15/gen/ $G/
fi
files=$(ls $G/$pat)
bash $S/e15_run.sh $gb admit_base_$grp e15b_admit.py --solver $M/Qwen__Qwen3-4B-Base --inputs $files --per_file 1000 --n 9 --out $A/admit_base_$grp.jsonl &
bash $S/e15_run.sh $gs admit_s5_$grp e15b_admit.py --solver $M/jinyuan222__qwen3_4b_fullrun_authorsettings_solver_v5 --inputs $files --per_file 1000 --n 9 --out $A/admit_s5_$grp.jsonl &
wait
echo "ADMIT_DONE $grp $(date +%T)"
