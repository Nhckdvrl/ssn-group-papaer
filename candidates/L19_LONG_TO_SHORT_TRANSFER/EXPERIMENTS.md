# L19 experiment ledger

| id | run | claim served | status |
|---|---|---|---|
| E01-a | `SHORT-SUPPORT` seed 1 | matched-supervision baseline | not started |
| E01-b | `LONG-FULL` seed 1 | treatment | not started |
| E01-c | `SHORT-SUPPORT` seed 2 | seed stability / kill condition 1 | not started |
| E01-d | `LONG-FULL` seed 2 | seed stability / kill condition 1 | not started |
| E01-pc1 | `UC-UC`: UltraChat block A + UltraChat block B | mother positive control, short arm | not started |
| E01-pc2 | `UC-CHATQA2`: UltraChat block A + ChatQA2 | mother positive control, long arm | not started |

The positive control is structurally identical to the main contrast: the same 10k
UltraChat block A is held fixed and the *second* 10k block is swapped between a short
dataset (more UltraChat) and a long dataset (ChatQA2). Same example count, same
optimizer steps. It is the parent's dataset swap embedded in our pilot regime, so its
gap and the matched-supervision gap are measured with the same noise.

Common to E01-a..d: `Llama-3-8B-ProLong-512k-Base`, 20,000 examples (10k NQ + the same
10k UltraChat), 1 epoch, 32 examples/optimizer step, lr 2e-5 cosine→2e-6, warmup 3%,
AdamW(0.9, 0.95), bf16, DeepSpeed ZeRO-2, completion-only loss.

Evaluation for every run: MMLU 0-shot / BBH 3-shot CoT / LAMBADA 0-shot / GSM8K 4-shot
CoT, per the parent's Appendix B. Primary statistic is the macro over the four.

## Log

- 2026-09-11 — power section added to the pilot card before any run.
- 2026-09-11 — parent paper read in full; no length-controlled experiment exists in it.
  Table 1 re-analysis recorded. NQ length audit on 3 shards: 18.4% of raw examples give
  clean pairs, 6.5% survive the frozen length window. Design frozen in `PILOT_CARD.md`.
