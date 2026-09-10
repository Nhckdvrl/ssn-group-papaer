# L08 — Claim Ledger

Status: `hypothesis` / `supported` / `weakened` / `rejected` / `established-by-others`.
A claim is load-bearing only if [MAINLINE.md](MAINLINE.md) changes when it flips.

---

## P0 — Not ours to claim

**P0.1** Halving the final pre-unembedding representation, with the unembedding
reduced correspondingly, leaves MMLU accuracy near baseline and reduces GSM8K strict
exact-match to near zero for Llama 3.1 8B and Qwen 2.5 7B.
`established-by-others` — Takeshita et al., EMNLP 2025 Main, Table 3. Substrate only.

**P0.2** A pruned model can pass multiple-choice evaluation while failing open
generation on the same questions, and the answer is demoted rather than erased.
`established-by-others` — "The Benchmark Illusion", arXiv 2606.17609 (June 2026).
Cited as prior work **and** as independent replication of our protocol effect on a
different task family. We do not claim the multiple-choice-versus-generation
observation.

---

## C1 — The evidence base for capability-selective compression damage is confounded

**C1.1 — SQuAD-v2's apparent survival is a metric floor.** `supported`.
`best_exact` sweeps a no-answer threshold and cannot fall below the unanswerable
fraction of the split (5945/11873 = 50.0716%), which is exactly the 50.07 the parent
reports for all four truncated conditions. Our reproduction: `best_exact` 50.30 under
full, first and last alike (rel 1.000) while `HasAns_exact` falls 78.07 -> 25.76
(rel 0.33). Evidence: E01.

**C1.2 — The collapse tracks the readout protocol and the output length, not the
capability.** `supported`, four model families.
Same MMLU items, same model, same intervention: ranking retains 0.50-1.00 while the
identical knowledge read out by generation retains 0.000-0.243, in 8 of 8 conditions.
The protocol pair is difficulty-matched to within 0.002-0.005 in every model.
Evidence: E02, E10 model extension.

**C1.3 — Output length is a factor separate from protocol, and the larger of the two.**
`supported`, and now **causal within items**. Llama, first mask: rank 0.889 -> one
generated token 0.837 -> generated chain 0.030 (E02, pre-registered depth contrast).
E07 holds items, model, mask, content and protocol fixed and varies only the time
window over which the mask is applied: truncating the opening 16 generated steps and
then restoring the readout leaves 0.567, truncating everything after step 16 leaves
0.313, and truncating throughout leaves 0.109. Early damage is largely recoverable;
the collapse requires sustained exposure.

**C1.4 — The parent's representational conclusion about mask identity is also
protocol-bound.** `supported`, now with a random-mask control.
"Removing first or last does not have an impact, indicating the presence of inefficient
representation space usage by LLMs" reproduces exactly under ranking and fails under
generation. With three random half-masks added per cell, so that the comparison is at a
*fixed count* of surviving dimensions: the best and worst of five different half-masks
differ by **1.0-1.1x under ranking** and by **2.7-13.0x under generation**; the
random-mask coefficient of variation goes from 0.4-2.6% to 9.7-50.9%. The structured
halves are also not exchangeable with arbitrary ones — for Qwen's `mmlu_gen_cot` the
random masks band at 0.052-0.064 while `first` is 0.146 and `last` is 0.011.
Evidence: E02, E11.

---

## C2 — What the removed dimensions were doing: five accounts rejected

| id | account | decisive test, with its control | verdict |
|---|---|---|---|
| C2-R1 | a fixed vocabulary prior is installed | E03b, add back `b̄` vs a norm-matched random vector | `rejected` |
| C2-R2 | extreme-value competition over ~150k tokens | E04, survival vs candidate-set size | `rejected` — flat beyond K ~ 8 |
| C2-R3 | capture by repetition attractors | E05, `no_repeat_ngram_size=6` | `rejected` — degeneration 0.87 -> 0.006, accuracy 0.109 -> 0.089 |
| C2-R4 | per-step prediction is badly damaged | E04, top-1 agreement | `rejected` — 0.62-0.92 |
| C2-R5 | structural tokens selectively demoted | E09, class x margin | `rejected` — no cross-model replication |

**C2.1 — Survival is monotone in the full model's decision margin.** `supported`,
partial. `s(m)` rises from ~0.2 below m = 1 to ~1.0 above m = 12 in all four
model x mask conditions; as a parameter-free predictor its errors span -0.66 to +0.22.
Evidence: E06.

**C2.2 — A substantial part of the loss is failure to emit an answer, not failure to
compute one.** `supported`, partial. Supplying the answer marker turns a literal
**0.000** into **0.178** (Llama) and 0.106 into 0.204 (Qwen). Conditional on emitting
an answer, truncated models match or beat the full model's accuracy (0.868-1.000 vs
0.782-0.850) with 94.5-100% of calculator steps correct. About one third of the gap.
Evidence: E08, `scripts/analyze_arithmetic.py`.

**C2.3 — The damage is diffuse; there is no single mechanism.** `supported` as the
honest reading of C2-R1..R5 plus C2.1-C2.2. Recorded as a result, not a gap: it is why
the paper is not a mechanism paper.

---

## C3 — The positive contribution

**C3.1 — Controlling protocol and output length removes 29.5-111% of the apparent
capability-selective damage.** `supported`. Evidence: E10, paired bootstrap, 11
estimable conditions.

**C3.2 — What survives the controls separates interventions that damage computation
from interventions that damage only expression.** `supported`, and load-bearing.
Across 15 estimable conditions, five model families and three intervention families,
**not one crosses in the wrong direction**: of eight readout conditions, six are
significantly below 1 and none is above; of seven parameter conditions, five are
significantly above 1 and none is below. A deliberately mild prune, which has no
protocol inflation to remove, still shows genuine selectivity (1.34, CI [1.19, 1.50])
while a severe readout truncation shows the opposite sign (0.27), so severity is not the explanation. Evidence: E10.

**C3.3 — Redundancy estimated under ranking protocols does not license claims about a
model's computation.** `hypothesis`, the prescriptive form of C3.1 + C3.2. Needs the
corrected re-measurement stated as a recommendation.

---

## Retired

**R1 — "Reasoning requires a higher-dimensional per-step readout than knowledge."**
The candidate-stage mainline. Rejected: at matched protocol and length the sign is
negative for readout interventions in five of six estimable conditions.

**R2 — "The collapse is an attractor phenomenon."** Rejected by E05, which eliminated
degeneration entirely without recovering accuracy.
