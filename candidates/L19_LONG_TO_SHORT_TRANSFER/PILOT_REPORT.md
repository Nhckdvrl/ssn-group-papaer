# L19 — E01 pilot report and re-selection (2026-09-12)

**Gate decision: outcome D. The treatment arms were never trained and are not authorized.**

## What the positive control returned

`Llama-3-8B-ProLong-512k-Base`, N=2,000, lr 5e-6, identical UltraChat block A, second
block swapped.

| run | MMLU | BBH | LAMBADA | GSM8K | macro |
|---|---|---|---|---|---|
| untrained base | 62.90 | 56.11 | 76.69 | 62.09 | **64.45** |
| `PC-UC-UC` (short arm) | 62.38 | 65.00 | 76.29 | 53.53 | **64.30** |
| `PC-UC-CHATQA2` (long arm) | 62.85 | **26.78** | 77.20 | 43.37 | **52.55** |
| parent, UltraChat-SFT | 61.50 | 61.00 | 64.44 | 54.69 | 60.41 |
| parent, ChatQA2-SFT | 62.80 | 63.79 | 70.11 | 68.75 | 66.36 |

Gap **-11.75** against the parent's +5.96.

**The training stack is correct.** The short arm sits at 64.30 against the untrained
base's 64.45 — essentially no damage — and BBH improves 56.11 -> 65.00. The failure is
confined to the ChatQA2 arm, and it is structured: the two **generative CoT** tasks
collapse (BBH 26.78, GSM8K 43.37) while the two non-generative ones are untouched
(MMLU 62.85, LAMBADA 77.20, both slightly above base). ChatQA2 teaches
"read a long document, write prose"; 2,000 examples is enough to disrupt chain-of-thought
style and nowhere near enough to rebuild it, and the arm's gradient norm runs ~26 against
the short arm's ~2.4 so it is clipped on essentially every step.

## Why this ends the route rather than advancing the ladder

On the two benchmarks that did not collapse, we reproduce **26%** of the parent's
dataset-swap effect: MMLU +0.47 against their +1.30, LAMBADA +0.91 against their +5.67.

Against the evaluation noise floor (binomial SE at our n, *before* counting seed-to-seed
training variance):

| benchmark | n | eval SE | detectable at 2 seeds |
|---|---|---|---|
| MMLU | 14,042 | 0.42 pp | ~1.18 pp |
| LAMBADA | 5,153 | 0.70 pp | ~1.95 pp |

**Our swap effect is already below its own noise floor**, and the matched-supervision
effect is a subset of the swap effect, so it is smaller still. Running
`SHORT-SUPPORT` / `LONG-FULL` would produce numbers that cannot be distinguished from
noise, and that was computable before spending the 5.7 GPU-hours.

Escalating to N=5,000 — the preregistered next rung — is declined. It is 6.3 GPU-hours
for 5% of the parent's token budget; the ChatQA2 arm would very likely still collapse and
the resolution would still be a fraction of what is needed. The ladder was specified
before these quantities were known.

## The honest diagnosis

The manipulation is sound and intact. What is not affordable here is the **dependent
variable**: short-benchmark accuracy responds to SFT-data character only at token budgets
near the parent's 1B, and at our budget the response is below measurement noise. The
full study this question requires is out of reach on this hardware whatever the pilot
returns — which is the condition under which the workflow says to stop rather than to
narrow the claim until it fits.

## What survives, and is not lost

1. **The parent re-analysis** (`MOTHER_REANALYSIS.md`), which cost no compute and stands
   independently: the published effect (+2.68 macro) is smaller than the spread between
   the parent's own two short-context datasets (+4.07), and 7 of 9 benchmarks reverse
   between the best short and worst long dataset.
2. **An empirical addition to that critique**: their two-dataset comparison also carries a
   gradient-scale asymmetry (grad norm ~26 vs ~2.4 under identical settings), so part of
   what they attribute to context length is attributable to how differently the two
   datasets' targets drive the optimizer.
3. **10,000 frozen matched NQ pairs** — human gold question, answer, supporting paragraph
   and source page; 98.4x median length contrast; targets identical token for token;
   verified to render byte-identical loss tokens under both Llama-3 and Qwen chat
   formats. A reusable instrument for any "what does length do" question.
4. **A working 8B SFT + evaluation stack**, with three real faults found and fixed
   (8x gradient from `model_accepts_loss_kwargs`, missing checkpoint tokenizer, lr/batch
   mismatch) and one alternative explanation empirically excluded (evaluation format).

## Recorded errors in our own preregistration

- kill condition 3 was mis-specified and was formally withdrawn before any treatment run;
- the "damage valley needs 1B tokens" reading was wrong — it was an lr/batch mismatch —
  so the 94 GPU-h/run and 400+ h/programme figures derived from it are void;
- the successful-result test was run but did not compare the expected effect size against
  the evaluation noise floor. **That single comparison would have stopped this route
  before any GPU time was spent.** It is the durable lesson from L19.
