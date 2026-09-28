#!/bin/bash
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
until [ "$(grep -c '^allenai' logs/dl_ladder_mid.log)" -ge 2 ]; do sleep 60; done
snap(){ grep "^$1 $2 " logs/dl_ladder_mid.log | awk '{print $3}'; }
D=pg19,wikipedia,python
{
printf 'T7s3m\tHF_HUB_OFFLINE=1 /home/xiang/miniconda3/envs/verl-clean/bin/python src/score.py %s/ T7s3m %s\n' "$(snap allenai/Olmo-3-1025-7B stage3-step6000)" "$D"
printf 'H7s3m\tsource src/env.sh && $PY src/score.py %s/ H7s3m %s\n' "$(snap allenai/Olmo-Hybrid-7B stage3-step12000)" "$D"
cat logs/jobs_redo.txt
} > logs/jobs_mid.txt
pgrep -f "src/queue2[.]sh" >/dev/null && { echo "queue busy, waiting"; while pgrep -f "src/queue2[.]sh" >/dev/null; do sleep 60; done; }
echo "$(TZ=Asia/Tokyo date '+%F %H:%M') JST — queue started: $(cut -f1 logs/jobs_mid.txt | tr '\n' ' ')" >> logs/P0_LAUNCH.md
exec src/queue2.sh logs/jobs_mid.txt
