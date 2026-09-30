#!/bin/bash
# sequential pulls to stay under HF throttling
cd "$(dirname "$0")"
for r in "BayLing-Models/BayLing-Duplex BayLing-Duplex" "THUDM/glm-4-voice-9b glm-4-voice-9b" "xinrongzhang2022/MiniCPM-duplex MiniCPM-duplex" "openbmb/MiniCPM-2B-sft-bf16 MiniCPM-2B-sft-bf16" "THUDM/glm-4-9b-chat-hf glm-4-9b-chat-hf"; do
  set -- $r
  python3 hf_pull.py $1 /home/xiang/rt_ext/models/$2 16 > /home/xiang/rt_ext/logs/pull_$2.log 2>&1
done
echo ALLDONE
