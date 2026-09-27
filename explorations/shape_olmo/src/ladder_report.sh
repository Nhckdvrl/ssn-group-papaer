#!/bin/bash
# After the stage-ladder scores exist (3 diagnostic domains), write results/stage_ladder_diag3.txt.
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
ok(){ for d in pg19 wikipedia python; do [ -f scores/$1/$d.npy ] || return 1; done; }
until ok T7s2 && ok H7s2 && ok T7s3e && ok H7s3e; do sleep 180; done
P=/home/xiang/miniconda3/envs/verl-clean/bin/python
F='resource_tracker|Exception ignored|AttributeError|File "|Traceback'
{
echo "### gap change per transition (D = later gap - earlier gap; gap = T - H; == DiD I(x))"
for pr in "T7s1 H7s1 T7s2 H7s2" "T7s2 H7s2 T7s3e H7s3e" "T7s3e H7s3e T7 H7"; do $P src/tokprofile.py change $pr 2>&1 | grep -Ev "$F"; done
echo "### within-model change per transition (earlier - later; > 0 = model improved)"
for pr in "T7s1 T7s2" "H7s1 H7s2" "T7s2 T7s3e" "H7s2 H7s3e" "T7s3e T7" "H7s3e H7"; do $P src/tokprofile.py pair $pr 2>&1 | grep -Ev "$F"; done
} > results/stage_ladder_diag3.txt
