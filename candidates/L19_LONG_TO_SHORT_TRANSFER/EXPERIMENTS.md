# L19 experiment ledger

| id | run | claim served | status |
|---|---|---|---|
| E01-a | `SHORT-SUPPORT` seed 1 | matched-supervision baseline | not started |
| E01-b | `LONG-FULL` seed 1 | treatment | not started |
| E01-c | `SHORT-SUPPORT` seed 2 | seed stability / kill condition 1 | not started |
| E01-d | `LONG-FULL` seed 2 | seed stability / kill condition 1 | not started |
| E01-pc1 | `ULTRACHAT-ONLY` 10k | mother positive control, short arm | not started |
| E01-pc2 | `CHATQA2` 10k + UltraChat 10k | mother positive control, long arm | not started |

Common to E01-a..d: `Llama-3-8B-ProLong-512k-Base`, 20,000 examples (10k NQ + the same
10k UltraChat), 1 epoch, 32 examples/optimizer step, lr 2e-5 cosine→2e-6, warmup 3%,
AdamW(0.9, 0.95), bf16, DeepSpeed ZeRO-2, completion-only loss.

Evaluation for every run: MMLU 0-shot / BBH 3-shot CoT / LAMBADA 0-shot / GSM8K 4-shot
CoT, per the parent's Appendix B. Primary statistic is the macro over the four.

## Log

- 2026-09-11 — parent paper read in full; no length-controlled experiment exists in it.
  Table 1 re-analysis recorded. NQ length audit on 3 shards: 18.4% of raw examples give
  clean pairs, 6.5% survive the frozen length window. Design frozen in `PILOT_CARD.md`.
