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
`established-by-others` — Wen et al., "The Benchmark Illusion", arXiv 2606.17609
(June 2026). Cited as prior work **and** as independent replication of our protocol
effect on a different task family. We do not claim the multiple-choice-versus-generation
observation.

**P0.3** Which layers look important under pruning depends on whether the evaluation
is likelihood-based or generation-based; likelihood evaluation makes middle and deep
layers look nearly irrelevant, generation does not. Layer importance is task-, metric-
and model-dependent. `established-by-others` — Song et al., "Demystifying the Roles of
LLM Layers in Retrieval, Knowledge, and Reasoning", ICASSP 2026, arXiv 2510.02091.
This is the same MMLU benchmark x the same intervention x different protocols. Venue
does not affect ownership. **`evaluation protocol matters` is therefore fully owned
and is claimed nowhere in this package.**

**P0.4** Compression across pruning/quantization/distillation exhibits a `knowledge
bias`: factual knowledge is largely retained while reasoning, multilingual and
instruction-following degrade disproportionately. `established-by-others` — UniComp,
EMNLP 2026 Main, arXiv 2602.09130. This is the **target**, not a competitor: its
knowledge set is multiple-choice throughout and its reasoning set free-form CoT
throughout, and it does not control output length anywhere. It also reports, and
cannot explain, that GPQA-Diamond is more robust than GSM8K and MATH-500, conjecturing
that this is "likely attributable to its multiple-choice format".

**P0.5** Pruning calibrated only on prompt activations suffers distribution shift on
the model's own generated chain, and recalibrating on on-policy CoT activations
mitigates it. `established-by-others` — Reasoning-Aware Compression, arXiv 2509.12464.
Owns the calibration-shift account of CoT degradation after pruning. We must not
present "damage accumulates along a self-generated chain" as new; what is ours is the
**dissociation** — that it does not accumulate when the answer stays prompt-recoverable.

---

## C1 — Identification prerequisite (not a novelty claim)

**Status of the whole section:** `supported`, and **prior-owned at the level of the
generic statement** (P0.2, P0.3). C1 is reported as the identification step that makes
C2 estimable. It is not presented as a contribution. Our version is cleaner than the
owners' — same item, same prompt, same intervention, only the readout rule varies —
and that cleanliness is what C2 needs, not what the paper sells.

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
window over which the mask is applied. Every partial exposure beats full exposure, and
restoring the readout part-way through recovers a large factor (Llama 0.109 -> 0.567,
Qwen 0.138 -> 0.748 at a switch of 16 steps), so the damage is not permanent. But the
second dose point shows the mechanism is **positional, not cumulative**: truncating 64
early steps leaves 0.155 while truncating ~336 late steps leaves 0.756. What matters is
whether the answer-bearing tokens were produced under truncation — which is the same
quantity C2.2 identifies.

**C1.4 — The parent's representational conclusion about mask identity is also
protocol-bound.** `supported`, now with a random-mask control.
"Removing first or last does not have an impact, indicating the presence of inefficient
representation space usage by LLMs" reproduces exactly under ranking and fails under
generation. With three random half-masks added per cell, so that the comparison is at a
*fixed count* of surviving dimensions: the best and worst of five different half-masks
differ by **1.0-1.1x under ranking** and by **2.7-13.0x under generation**; the
random-mask coefficient of variation goes from 0.4-2.6% to 11.6-99.8%. The structured
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

## C2' — The load-bearing claim (new 2026-09-14)

**C2'.1 — Retention decays with answer depth only when the answer is carried by the
model's own generated prefix.** `supported`, observational; the confirmatory version is
preregistered as E12.

Logistic fit of per-item retention on `log2(1 + L)`, `L` = the full model's answer
position, pre-treatment; retention defined among items the full model answers
correctly. 15 estimable conditions, 5 model families, readout truncation + magnitude
pruning + quantization:

| | count |
|---|---|
| prompt-recoverable (`mmlu_gen_cot`) slope significantly negative | **1 of 15** |
| trajectory-carried (`gsm8k_gen_cot`) slope significantly negative | **14 of 15** |
| difference significant in the predicted direction | 8 of 15 |
| difference significant in the **wrong** direction | **0 of 15** |

Same model, same intervention, same free-generation protocol, same long-chain regime.
Evidence: `scripts/analyze_depth.py`, `results/depth_audit.json`.

**C2'.2 — The within-item causal counterpart.** `supported`, inherited. E07 varies only
the time window over which the intervention is applied: 64 early truncated steps leave
0.155, ~336 late truncated steps leave 0.756. Its own conclusion — what matters is
whether the answer-bearing tokens were generated under the intervention — is this law
stated within item. E08 adds that supplying the answer marker turns 0.000 into 0.178
with 94.5-100% of calculator steps correct: the trajectory-carried content is computed
and fails to be delivered.

**C2'.3 — Provenance, not capability, is the variable.** `hypothesis`, and the object
of E12. In the inherited data provenance is perfectly confounded with dataset, so
domain, answer format and item difficulty are all live alternatives. E12 manipulates
provenance **within item** with depth randomised, in a 2x2 against capability.

**C2'.4 — The published capability ordering is a provenance ordering.** `hypothesis`.
The prescriptive consequence; requires C2'.3 and the matched re-estimation of §C3.

---

## C3 — The positive contribution

**C3.1 — Controlling protocol and nominal output length removes 29.5-229% of the
apparent capability-selective damage.** `supported` as a statement about the
uncontrolled-vs-controlled gap; the range is 29.5-229% over 17 estimable conditions
(an earlier draft of this ledger said 29.5-111% and `MAINLINE` said 29.5-152%; both
were partial reads of the same table and are corrected here). Evidence: E10, paired
bootstrap. **Note:** "output length" here means the nominal long-chain regime, not
answer depth — see C3.2 and the 2026-09-14 audit.

**C3.2 — The intervention-locus sign boundary.** `weakened`, **demoted from
load-bearing 2026-09-14**. See [`AUDIT_2026-09-14_DEPTH_CONFOUND.md`](AUDIT_2026-09-14_DEPTH_CONFOUND.md).

The E10 "controlled" contrast does not hold answer depth fixed: the two cells differ by
1.7-3.4x in how many decoding steps precede the answer, in the same direction in all
five models, and the bias runs toward the `< 1` readings that formed the readout half.
Re-estimated with depth matched, readout conditions significantly `< 1` fall from 7 of
10 to **2 of 8**, and the severity control `prune0p25` — the one condition that ruled
out "pruning simply hits harder" — goes from 1.34 [1.19, 1.50] to **1.24 [0.96, 1.47],
null**. The three surviving `> 1` conditions are two 40% prunes and one quantization,
so severity is no longer excluded.

What survives is the no-crossing statement alone: 0 of 15 conditions cross. That is a
descriptive observation, not a contribution, and it may **not** be used to rescue the
package if C2 fails.

**C3.2a — the conceptual correction.** The earlier wording `readout channel
(computation intact)` vs `parameters (computation damaged)` is **withdrawn**. E00
establishes reversibility and hidden-state identity for a *fixed* forward pass only;
over a free-running trajectory a changed emitted token at step `t` changes the prefix
and therefore `h_{t+1}`, so upstream computation does diverge. The operational terms
are `readout-locus` and `parameter-locus`, defined by what is modified. Expression-vs-
computation is an account to be tested, not a fact.

**C3.3 — Redundancy estimated under ranking protocols does not license claims about a
model's computation.** `hypothesis`. Retained, but it is a restatement of P0.2/P0.3 and
is **not claimable**. Superseded as the prescriptive claim by C2'.4.

---

## Retired

**R0 — "What survives the controls separates damage to computation from damage to
expression."** The 2026-09-13 reopening's load-bearing claim. Demoted 2026-09-14: not
identified by the E10 design once answer depth is matched. See C3.2.

**R1 — "Reasoning requires a higher-dimensional per-step readout than knowledge."**
The candidate-stage mainline. Rejected: at matched protocol and length the sign is
negative for readout interventions in five of six estimable conditions.

**R2 — "The collapse is an attractor phenomenon."** Rejected by E05, which eliminated
degeneration entirely without recovering accuracy.
