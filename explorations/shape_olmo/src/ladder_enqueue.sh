#!/bin/bash
# Wait for the 4 ladder checkpoints, then restart the queue with ladder jobs first, followed by
# the not-yet-launched jobs from logs/jobs_remaining.txt.
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
until [ "$(grep -c '^allenai' logs/dl_ladder.log)" -ge 4 ]; do sleep 60; done
snap(){ grep "^$1 $2 " logs/dl_ladder.log | awk '{print $3}'; }
D=pg19,wikipedia,python
T2=$(snap allenai/Olmo-3-1025-7B stage2-step47684); H2=$(snap allenai/Olmo-Hybrid-7B stage2-ingredient1+2-step23842)
T3=$(snap allenai/Olmo-3-1025-7B stage3-step1000);  H3=$(snap allenai/Olmo-Hybrid-7B stage3-step1000)
{
printf 'T7s2\tHF_HUB_OFFLINE=1 /home/xiang/miniconda3/envs/verl-clean/bin/python src/score.py %s/ T7s2 %s\n' "$T2" "$D"
printf 'H7s2\tsource src/env.sh && $PY src/score.py %s/ H7s2 %s\n' "$H2" "$D"
printf 'T7s3e\tHF_HUB_OFFLINE=1 /home/xiang/miniconda3/envs/verl-clean/bin/python src/score.py %s/ T7s3e %s\n' "$T3" "$D"
printf 'H7s3e\tsource src/env.sh && $PY src/score.py %s/ H7s3e %s\n' "$H3" "$D"
launched=$(grep -o '— [A-Za-z0-9_]* launched' logs/P0_LAUNCH.md | awk '{print $2}')
awk -F'\t' -v L="$launched" 'BEGIN{n=split(L,a,"\n"); for(i=1;i<=n;i++) s[a[i]]=1} !($1 in s)' logs/jobs_remaining.txt
} > logs/jobs_ladder_first.txt
pkill -f "src/queue2[.]sh"
sleep 2
echo "$(TZ=Asia/Tokyo date '+%F %H:%M') JST — ladder checkpoints local; queue restarted with ladder first: $(cut -f1 logs/jobs_ladder_first.txt | tr '\n' ' ')" >> logs/P0_LAUNCH.md
setsid nohup src/queue2.sh logs/jobs_ladder_first.txt > logs/queue.log 2>&1 < /dev/null &
