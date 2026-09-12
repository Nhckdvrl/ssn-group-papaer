# L19 — Causal Ingredients of Long→Short SFT Transfer

**Status: ARCHIVED / NO-GO (K184), 2026-09-12 — shelved for cost, not for novelty.**
No authorization. The treatment arms were never trained. Do not reopen this route by
shrinking the claim to fit a smaller budget.

## The question

Long-context SFT is reported to *improve* short-task performance
(Zheng et al., *When Long Helps Short*, EMNLP 2025 Main). Is the active ingredient the
fact that training samples are long, or what long datasets happen to teach?

One NQ question, one gold answer, one human-annotated Wikipedia paragraph containing
everything needed to answer it. Train one model on `question + that paragraph`, another
on `question + the whole page` — same answers, same examples, same gradient steps, loss
on the same tokens. Then test both on GSM8K, BBH, MMLU, LAMBADA, which have no long
input at all.

## Why it was worth asking, and still is

Read in full, the parent's short/long contrast is **five different datasets**, and
**no experiment anywhere varies sequence length with data source held fixed**. Its
central causal variable is unidentified. A 2026-09-12 search found no published critique,
replication, or matched-length experiment. **The novelty gap is open.**

Re-analysis of the parent's own Table 1, at zero compute, is sharper still:

| | |
|---|---|
| published condition gap (macro, 9 benchmarks) | **+2.68** |
| spread between the parent's own two short datasets | **+4.07** |
| benchmarks where best-short beats worst-long | **7 of 9** |

The three benchmarks carrying most of the headline (HumanEval +8.03, GSM8K +7.03,
MBPP +2.33) are exactly the three where its two short datasets disagree most
(16.47 / 7.81 / 12.00).

## Why it stopped

The positive control — the parent's own dataset swap, rerun in our regime at N=2,000,
lr 5e-6 — returned a macro gap of **−11.75** against their +5.96.

| run | MMLU | BBH | LAMBADA | GSM8K | macro |
|---|---|---|---|---|---|
| untrained base | 62.90 | 56.11 | 76.69 | 62.09 | **64.45** |
| `PC-UC-UC` (short arm) | 62.38 | 65.00 | 76.29 | 53.53 | **64.30** |
| `PC-UC-CHATQA2` (long arm) | 62.85 | **26.78** | 77.20 | 43.37 | **52.55** |

The training stack is correct — the short arm matches the untrained base. The failure is
confined to the long arm and is structured: both generative CoT tasks collapse while both
non-generative ones are untouched.

The decisive quantity is **resolution, not sign**. On the two benchmarks that held we
reproduce **26%** of the parent's swap effect (+0.47 vs +1.30 MMLU; +0.91 vs +5.67
LAMBADA) — already below the binomial evaluation noise floor at our n (1.18 pp and
1.95 pp detectable at two seeds), before any training variance. The matched contrast is a
subset of that effect and therefore smaller still. And the *interesting* outcome was the
null, which needs the interval to exclude the parent's +2.68 — parent-scale budgets plus
enough seeds to estimate run-level variance: **~100–300 GPU-hours** here, to chase a
2.7 pp effect.

## The durable lesson

The successful-result test was run, but it never compared the **expected effect size
against the evaluation noise floor**. Two numbers, no compute — and it would have stopped
this route before any GPU time was spent. Recorded in `CURRENT_SEARCH.md` and the ledger.

Two further preregistration errors of ours are recorded rather than dropped: kill
condition 3 was mis-specified and withdrawn before any treatment run (it would have
condemned the parent's own published result), and the "damage valley needs 1B tokens"
reading was wrong — it was an lr/batch-size mismatch (parent: lr 2e-5 at a 4M-token
batch; ours: the same lr at ~37k tokens/step).

## Reusable assets

- **`data/nq_pairs.jsonl`** — 10,000 frozen matched pairs, sha256 `b0e71fdf…`. Human gold
  question, short answer, long-answer paragraph and full source page; median context
  **133 vs 13,084** Llama-3 tokens (**98.4×**); targets identical token for token;
  verified to render byte-identical loss tokens under both Llama-3 and Qwen chat formats.
  Rebuild with `scripts/build_pairs.py`.
- **`data/probe.jsonl`** — 600 held-out context-reliance items with counterfactual answers.
- **An 8B SFT + vLLM evaluation stack** on the parent's protocol: DeepSpeed ZeRO-2, a
  completion-only sparse loss that avoids materialising a 24k × 128k logit tensor, bf16
  local staging. Three real faults found and fixed; evaluation-format mismatch
  empirically excluded as an explanation.

Model checkpoints (90 GB) were deleted on archive; they are regenerable from code, data
and configs. All evaluation results are kept under `results/`.

## Documents

| file | contents |
|---|---|
| [PILOT_REPORT.md](PILOT_REPORT.md) | the gate decision and re-selection, in full |
| [MOTHER_REANALYSIS.md](MOTHER_REANALYSIS.md) | the parent's own Table 1, re-analysed |
| [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) | ownership audit against full texts |
| [DATA_AND_GOLD.md](DATA_AND_GOLD.md) | NQ pair contract and frozen cutoffs |
| [PILOT_CARD.md](PILOT_CARD.md) | the preregistration, with its corrections marked |
| [EXPERIMENTS.md](EXPERIMENTS.md) | run ledger and the full diagnostic trail |
