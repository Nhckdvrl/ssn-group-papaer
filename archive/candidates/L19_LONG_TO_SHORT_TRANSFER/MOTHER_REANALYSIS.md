# Re-analysis of the mother result (Zheng et al., EMNLP 2025 Main, Table 1)

Source: `When Long Helps Short: How Context Length in Supervised Fine-tuning Affects
Behavior of Large Language Models`, ACL Anthology 2025.emnlp-main.522, Table 1 and
Appendix A Table 2. All numbers below are recomputed from their published table by
`scripts/reanalyze_mother.py`; nothing here is our own measurement.

## The design, as printed

| arm | datasets | n units |
|---|---|---|
| short-context SFT | UltraChat (avg 568 tok), Tulu-v2 (avg 1759 tok) | **2** |
| long-context SFT | LongAlpaca (9358), LongMIT (78716), ChatQA2 (9548) | **3** |

Training budget is unified (1B tokens, 4M-token batch, same ProLong-512k base), so the
headline is *not* a token-count artifact. But the independent scientific unit is the
**dataset**, and length is perfectly confounded with task, domain, supervision format and
data quality. There are five units in total.

## What the table actually shows

```
condition gap (macro, 9 benchmarks)   +2.68
within-SHORT spread (UltraChat->Tulu) +4.07   <-- larger than the effect
within-LONG  spread                   +0.50
```

Per benchmark (macro over datasets in each arm):

| benchmark | short | long | gap | within-SHORT spread |
|---|---|---|---|---|
| HumanEval | 41.16 | 49.19 | **+8.03** | **16.47** |
| GSM8K | 58.59 | 65.63 | **+7.03** | **7.81** |
| LAMBADA | 64.32 | 70.15 | **+5.83** | 0.24 |
| MBPP | 45.20 | 47.53 | +2.33 | **12.00** |
| MMLU | 61.44 | 62.52 | +1.09 | 0.13 |
| BBH | 61.25 | 62.29 | +1.04 | 0.50 |
| MATH | 16.85 | 17.66 | +0.81 | 0.86 |
| OBQA | 74.40 | 74.27 | -0.13 | 0.00 |
| PIQA | 75.78 | 73.89 | -1.90 | 1.09 |

Two things follow directly, without any new experiment.

**1. The three benchmarks that carry most of the headline are exactly the three where the
two short-context datasets disagree most.** HumanEval, GSM8K and MBPP have condition gaps
of +8.03/+7.03/+2.33 and within-arm spreads of 16.47/7.81/12.00. On all three, Tulu-v2
alone is at or above the long-context arm. The apparent length effect on these benchmarks
is indistinguishable from "UltraChat is a weaker instruction dataset than Tulu".

**2. On 7 of 9 benchmarks the best short-context dataset beats the worst long-context
dataset.** Only MMLU and LAMBADA are dominated by the long arm.

The residual that a dataset-quality story does *not* explain is small and specific:
roughly **+1 MMLU, +1 BBH, +5.8 LAMBADA, ~0 on OBQA/PIQA**. LAMBADA — predict the final
word given the immediately preceding passage — is the most *contextual-use* of the nine
benchmarks and the least diagnostic of general capability.

## Consequence for L19

This does not refute the mother paper; the aggregate number is what they report and it is
correct. It relocates the question. The published evidence is consistent with at least
three different worlds:

- **(W1)** exposure to long inputs during SFT genuinely improves general short-context
  capability;
- **(W2)** the long-SFT datasets are simply better instruction data than UltraChat, and
  length is a passenger;
- **(W3)** long inputs shift the model toward *using context* (LAMBADA, retrieval-style
  behaviour) with no general-capability gain, and the rest of the table is (W2).

A five-dataset design cannot separate these. E01 is built to separate them with sequence
length as the only manipulated variable.
