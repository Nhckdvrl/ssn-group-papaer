# L19 experiment ledger

| id | run | claim served | status |
|---|---|---|---|
| E01-a | `SHORT-SUPPORT` seed 1 | matched-supervision baseline | not started |
| E01-b | `LONG-FULL` seed 1 | treatment | not started |
| E01-c | `SHORT-SUPPORT` seed 2 | seed stability / kill condition 1 | not started |
| E01-d | `LONG-FULL` seed 2 | seed stability / kill condition 1 | not started |
| E01-base | untrained ProLong-512k-Base, evaluation only | anchor for outcome D | not started |
| E01-pc1 | `UC-UC`: UltraChat block A + UltraChat block B | mother positive control, short arm | not started |
| E01-e | NQ-only `SHORT-SUPPORT` seed 1 | dilution diagnostic, conditional on outcome B | not authorized |
| E01-f | NQ-only `LONG-FULL` seed 1 | dilution diagnostic, conditional on outcome B | not authorized |
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

## Measured throughput (smoke, 2026-09-12)

`LONG-FULL` smoke, 128 NQ + 128 UltraChat examples, 4x RTX PRO 6000 Blackwell Max-Q,
DeepSpeed ZeRO-2, bf16, gradient checkpointing, completion-only sparse loss, 24k cap:
**10.42 min of training for ~1.85M context tokens = 2,962 tok/s aggregate**, 69/96 GB
per GPU. Model staged in bf16 on local NVMe (loading from the NFS cache cost ~40 min
per run before this).

Projected training cost, from that number:

| N | stage 1 (PC) | stage 2 (main, 2 seeds) | total |
|---|---|---|---|
| 2,000 | 2.1 h | 5.7 h | **7.8 h** |
| 5,000 | 5.2 h | 14.3 h | 19.5 h |
| 10,000 | 10.5 h | 28.5 h | 39.0 h |

**N=2,000 is the first rung**, per the ladder in the pilot card. Worst case — the
positive control fails at both rungs — the route stops having spent ~7 h.

Also added, free: the untrained `Llama-3-8B-ProLong-512k-Base` is evaluated on the same
four benchmarks. Without it, outcome D cannot be distinguished from "SFT at this budget
moves nothing at all".

## Log

- 2026-09-12 — **run order corrected before any training.** The driver had the positive
  control last, which would have spent ~40 GPU-hours on the treatment before learning
  whether the regime has identification power at all. Reordered to a PC-first budget
  ladder (N=2,000, one escalation to 5,000, hard stop). Worst case is now a ~4-hour
  stop instead of a two-day one. N is set by the positive control only; treatment data
  is not consulted.
- 2026-09-12 — pair set built and frozen: 10,000 pairs, 9,132 distinct pages, median
  context 133 vs 13,084 tokens (98.4x), identical targets. sha256 b0e71fdf...

- 2026-09-11 — power section added to the pilot card before any run.
- 2026-09-11 — parent paper read in full; no length-controlled experiment exists in it.
  Table 1 re-analysis recorded. NQ length audit on 3 shards: 18.4% of raw examples give
  clean pairs, 6.5% survive the frozen length window. Design frozen in `PILOT_CARD.md`.
