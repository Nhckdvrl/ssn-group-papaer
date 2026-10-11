# CT08 E00 launch (2026-09-27 11:59)
vLLM (verl-clean, vllm 0.11): fvcrc10 g0 rlm-qwen3-8b :8100 | g1 qwen3-8b :8101 (arm B root) | g2,g3 qwen3-8b :8102,:8103 (sub-calls)
fvcrc12 g1 qwen3-8b :8111 (sub-calls) | g0 qwen3-8b-yarn x4 :8110 (arm C flat)
Clients on fvcrc10 CPU: A 24 workers, B 24 workers, C 16 workers. 400 instances each (data/e00_instances.jsonl).
- 12:50 arm A done; arm B restarted with 48 workers (resume; in-flight B instances re-run)
- 13:18 C done; yarn server replaced by qwen3-8b :8112 (fvcrc12 g0); arm B restarted with roots load-balanced over :8101,:8112,:8111 (identical model)
- 13:20 first B restart pointed at a dead :8112 (server start self-killed by pkill pattern); stopped, 22 connection-error records removed, :8112 started, B restarted
- 14:07 stopped clients; unfinished instances recorded as timeout (score 0): same rule for A and B
