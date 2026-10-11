# E01 launch log
2026-09-27 ~06:20 JST
- Qwen3.5-9B shard 0/2 -> fvcrc10 GPU2 ; shard 1/2 -> fvcrc10 GPU3   (SUB=16)
- Qwen3-8B  shard 0/1 -> fvcrc12 GPU0                                (SUB=8)
Only these three cards were idle; fvcrc13/15 full, fvcrc20 memory held, fvcrc11/21 unreachable.
Env: openslime python + vendored transformers 5.12.1 (src/env.sh).
- restart with SINK=4 protection at 06:12 (same cards)
- Qwen3-8B resumed after OOM with per-row log-softmax at 06:44
- Qwen3.5-9B shard1 resumed after OOM at 06:54
- adaptive sub-batch (<=6GB logits) patch; shard1 restarted 06:54
