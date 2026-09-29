#!/bin/bash
# Download JSON trajectories (no audio) for all voice + selected text leaderboard submissions.
cd "$(dirname "$0")"
ROOT=/home/xiang/rt_ext/data
SUBS="livekit-cascaded_livekit_2026-05-19 gpt-live-1-diamond-alpha_openai_2026-09-09 pine-voice-preview-user-sim-v1-0_pineai_2026-08-17 grok-voice-think-fast-1-0_xai_2026-04-21 grok-voice-think-fast-2-0_xai_2026-08-06 gpt-realtime-2-minimal_openai_2026-07-01 gpt-realtime-2_openai_2026-06-29 gpt-realtime-1.5_sierra_2026-03-03 gpt-realtime-1-0_openai_2026-04-13 gemini-live-2.5-flash_sierra_2026-03-03 xai-realtime_sierra_2026-03-03 gemini-3-1-flash-live-preview-thinking-high_google_2026-04-02 gemini-3-1-flash-live-preview-thinking-minimal_google_2026-04-13 qwen3-5-omni-plus-realtime_qwen_2026-08-06 gpt-5-2_sierra_2026-02-26 gpt-5-2-none_sierra_2026-02-26 claude-opus-4-5_sierra_2026-02-26 qwen3.5-397b-a17b-think_sierra_2026-03-02 gemini-3-flash_sierra_2026-03-02 glm-5_sierra_2026-03-02 claude-sonnet-4-5_sierra_2026-02-26"
for s in $SUBS; do
  echo "== $s $(date)"
  python3 s3_fetch.py get submissions/$s/trajectories/ $ROOT json,txt
done
echo DONE
