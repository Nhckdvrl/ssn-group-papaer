# L19 — Causal Ingredients of Long→Short SFT Transfer

**Status: PILOT-AUTHORIZED — E01 ONLY.** E02 is not authorized and must not be started
before E01 reports.

## RQ

> Long-context SFT is reported to *improve* short-task performance. Is the active
> ingredient the fact that training samples are long, or what long datasets happen to
> teach?

## The example

One NQ question, one gold answer, one human-annotated Wikipedia paragraph that contains
everything needed to answer it. Train one model on `question + that paragraph`. Train
another on `question + the whole Wikipedia page`, same answer, same examples, same
gradient steps, loss on the same tokens. Then test both on GSM8K, BBH, MMLU and LAMBADA —
tasks with no long input at all.

If the second model is better, long-context exposure itself changes general capability.
If it is not, the published effect belongs to the datasets, not to length.

## Documents

| file | contents |
|---|---|
| [MOTHER_REANALYSIS.md](MOTHER_REANALYSIS.md) | what the parent's own Table 1 shows once dataset is the unit — the effect is smaller than its within-condition spread |
| [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) | ownership audit, verified against full texts |
| [DATA_AND_GOLD.md](DATA_AND_GOLD.md) | NQ pair contract and the frozen length cutoffs, with the audit that set them |
| [PILOT_CARD.md](PILOT_CARD.md) | E01 preregistration: design, primary outcome, the four outcome readings, kill conditions |
| [EXPERIMENTS.md](EXPERIMENTS.md) | run ledger |

## Fence

E01 alone compresses to "Zheng et al. with better controls" and is not a paper. It is a
gate. If it passes, the paper identity is re-selected from scratch before E02.
