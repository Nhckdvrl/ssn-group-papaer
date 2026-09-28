#!/bin/bash
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
out=logs/jobs_survey.txt; : > $out
grep -v ERR logs/dl_survey.log | grep -E '^[a-zA-Z-]+/[^ ]+ /' | while read -r repo path; do
  tag=$(basename "$repo" | tr '.-' '__')
  printf 'SV_%s\tsource src/env.sh && PROBE_N=60 $PY src/probe_order.py %s/ %s\n' "$tag" "$path" "$tag" >> $out
done
q=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-4B/snapshots/*/ | head -1)
printf 'SV_Qwen3_5_4B\tsource src/env.sh && PROBE_N=60 $PY src/probe_order.py %s Qwen3_5_4B\n' "$q" >> $out
cut -f1 $out
