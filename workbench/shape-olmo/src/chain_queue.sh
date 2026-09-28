#!/bin/bash
# usage: chain_queue.sh JOBFILE NOTE  -- start queue2 on JOBFILE once no queue2 is running
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
while pgrep -f "src/queue2[.]sh" >/dev/null; do sleep 60; done
echo "$(TZ=Asia/Tokyo date '+%F %H:%M') JST — queue: $2" >> logs/P0_LAUNCH.md
exec src/queue2.sh "$1"
