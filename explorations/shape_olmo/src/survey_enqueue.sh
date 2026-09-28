#!/bin/bash
# Once survey downloads finish, queue probe_order (PROBE_N=60) on each downloaded hybrid.
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
until grep -q "Nemotron-Nano-9B-v2-Base" logs/dl_survey.log; do sleep 60; done
> logs/jobs_survey.txt
grep -v ERR logs/dl_survey.log | grep "^[a-z]" | while read repo path; do
  tag=SV_$(basename "$repo" | tr '.-' '__')
  printf '%s\tsource src/env.sh && PROBE_N=60 $PY src/probe_order.py %s/ %s\n' "$tag" "$path" "${tag#SV_}" >> logs/jobs_survey.txt
done
# Qwen3.5-4B (already cached) as a RoPE GDN hybrid reference
printf 'SV_Qwen3_5_4B\tsource src/env.sh && PROBE_N=60 $PY src/probe_order.py %s Qwen3_5_4B\n' "$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-4B/snapshots/*/ | head -1)" >> logs/jobs_survey.txt
exec src/chain_queue.sh logs/jobs_survey.txt "probe_order survey of public hybrids (NoPE vs RoPE)"
