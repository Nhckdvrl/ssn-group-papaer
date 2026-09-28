# L43 E01R Preregistration — Counterfactual Alternatives vs Endogenous Route Selection

**Status:** `AUTHORIZED — E01R ONLY`  
**Parent:** `SELECTION.md`  
**Date reconstructed:** 2026-09-15

## E01R question

> **Across intact IOI inputs, do attention heads that are stronger counterfactual substitutes for the primary name-mover route become more engaged / causally load-bearing when that primary route is naturally less engaged?**

Short form:

> **Does CoAx counterfactual substitutability predict endogenous substitution?**

This supersedes the earlier stress-trigger E01. DoubleIO / TripleIO are retained only as part of a fixed published input-variation family; E01R does not require either variant to produce a positive backup effect.

---

# 1. Fixed model and primary route

Model:

- `gpt2` / GPT-2 small, frozen.

Published primary name-mover set `P`:

- `(9,9)`
- `(10,0)`
- `(9,6)`

Do not redefine `P` from E01R confirmation results.

Published backup labels are used **only** for the CoAx replication gate, not as the primary scientific estimand:

- `(10,10)`
- `(10,6)`
- `(10,2)`
- `(10,1)`
- `(11,2)`
- `(9,7)`
- `(9,0)`
- `(11,9)`

Use the released CoAx implementation / ablation primitive wherever possible:

https://github.com/GongZhiren/Conditional-Co-Ablation

---

# 2. Split and firewall

Use two disjoint data stages.

## CALIBRATION

Use canonical published IOI prompts only.

Purpose:

1. reproduce CoAx backup recovery;
2. compute a frozen **counterfactual substitutability score** `C_h` for every non-primary attention head;
3. freeze the top-k CoAx set and matched controls before any endogenous-route analysis.

Use 256 prompts with a sealed RNG seed.

## CONFIRMATION

Use 512 semantic bundles. Each bundle fixes names / place / object and is rendered in a predeclared set of published answer-preserving IOI formats.

Confirmation must remain untouched until calibration and analysis code are locked.

No prompt family may be added or removed after seeing any CoAx-to-endogenous result.

---

# 3. Fixed intact-input variation family

For each semantic bundle, render the following six conditions using published template-generation logic:

1. Base IOI — BABA order;
2. Base IOI — ABBA order;
3. DoubleIO — BABA order;
4. DoubleIO — ABBA order;
5. TripleIO — BABA order;
6. TripleIO — ABBA order.

Use the template banks released / specified by Wang et al. and Nainani et al. where available. Preserve the correct IO answer across the bundle.

The purpose of these variants is **not** to call DoubleIO or TripleIO a special stressor. They provide pre-existing within-semantic input variation over which the intact primary route is known to vary.

Do not invent additional distractors, longer prompts, or adversarial templates after inspection.

Retention rule:

- primary analysis keeps a semantic bundle only if GPT-2 assigns the correct IO token a higher logit than the competing S token in at least 4 of the 6 variants;
- per-variant correctness is reported;
- analyses involving a specific variant use only correct intact predictions for that variant.

If fewer than 250 bundles remain, mark `HOLD — INTACT SUPPORT TOO WEAK`.

---

# 4. Calibration: freeze the counterfactual quantity

For every non-primary attention head `h`, compute the released CoAx conditional compensation score on CALIBRATION:

`C_h = E(delta z_h | P ablated) - E(delta z_h | intact)`

using the paper's output-grounded Fisher-centered geometry.

`C_h` is the preregistered measure of **counterfactual substitutability**.

### Replication gate

Using the eight documented backup labels only for validation:

> backup ROC-AUC from `C_h` must be `>= 0.80`.

The paper reports about `0.91`.

If this fails: `HOLD — COAX REPLICATION FAILURE`.

### Freeze top-k set

After replication, freeze:

`B = top 8 non-primary heads by C_h`.

This is the primary counterfactual-alternative set. The published labeled backups are secondary only.

### Freeze matched-control set

Construct an 8-head control set `M` without using any CONFIRMATION statistic.

For each `B` head, choose a unique non-primary, non-B head matched on:

- layer;
- CALIBRATION intact direct IO-vs-S logit contribution magnitude;
- CALIBRATION single-head ablation damage magnitude.

Use deterministic minimum-cost matching; ties broken lexicographically.

Freeze `B` and `M` before opening confirmation mechanistic results.

---

# 5. Measure primary-route engagement without damaging the model

The original E01 used prompt categories as the independent variable. E01R instead measures how strongly the primary route is engaged on each intact input.

For intact confirmation input `x`, define two predeclared primary-route engagement measures.

## Primary engagement measure

`A_P(x)` = mean attention mass from the three primary name-mover heads, at the final prediction position, to the correct IO token.

This is chosen because the documented function of these heads is to read / move the IO identity and because it is measured on an untouched forward pass.

## Secondary engagement measure

`L_P(x)` = summed direct-logit contribution of the primary heads to the `IO - S` logit direction on the intact run.

No result is called robust unless the qualitative direction agrees under both `A_P` and `L_P`.

Do **not** define primary engagement using the damage from ablating `P`, because self-repair can itself mask that damage and make the conditioning variable circular.

---

# 6. Endogenous substitution quantities

We need to know whether a head becomes more involved **when the primary route is naturally less engaged**, without first ablating `P`.

For every non-primary attention head `h` and intact confirmation input `x`, record:

- `DLA_h(x)`: direct contribution to the `IO - S` logit direction;
- `ATTN_h(x)`: attention mass from END to IO;
- `Damage_h(x)`: single-head ablation damage to `IO - S` logit difference.

The first two are intact-state measurements. `Damage_h` is a causal necessity check performed in a separate run from the intact input; it is never used to define primary engagement.

## 6.1 Head-level endogenous substitution score

Within each semantic bundle `j`, center `A_P` and `DLA_h` across the six variants.

For each head, estimate the pooled within-bundle slope:

`E_h = slope( DLA_h(x) ~ -A_P(x) + LD_intact(x) )`

with semantic-bundle fixed effects.

Positive `E_h` means the head writes more toward the correct answer on intact inputs where the primary route is less engaged.

Repeat as secondary analyses using:

- `L_P` instead of `A_P`;
- `Damage_h` instead of `DLA_h`.

The primary head-level scientific estimand is:

`rho = Spearman_h(C_h, E_h)`

across all non-primary attention heads.

This asks whether **counterfactual substitutability under internal damage predicts endogenous route recruitment across intact inputs**.

Bootstrap uncertainty by semantic bundle (10,000 resamples; sealed seed `43002`).

---

# 7. Group-level causal confirmation

A head-level DLA relation alone could arise from logit-budget redistribution. Therefore the scientific claim requires a group-level causal check.

Within each retained semantic bundle, rank its six variants by intact `A_P` only.

Define:

- `LOW-P`: the two variants with lowest primary engagement;
- `HIGH-P`: the two variants with highest primary engagement.

This grouping never uses backup statistics.

For head set `H`, define:

`Damage_H(x) = LD_intact(x) - LD_ablate(H)(x)`.

Compute:

`G_B = mean Damage_B(LOW-P) - mean Damage_B(HIGH-P)`

`G_M = mean Damage_M(LOW-P) - mean Damage_M(HIGH-P)`

and the preregistered difference-in-differences:

`G = G_B - G_M`.

Positive `G` means the counterfactual-alternative set becomes selectively more causally load-bearing when the intact primary route is naturally weak, beyond matched late-head changes.

Also report the same statistic with published backup labels in place of `B` as a secondary analysis.

---

# 8. Anti-tautology / anti-story controls

Always report:

1. intact `LD` across all six variants;
2. distribution and within-bundle range of `A_P` and `L_P`;
3. `C_h` vs `E_h` scatter for **all** non-primary heads, not just named backups;
4. layer-stratified correlations;
5. `B` and `M` direct contributions and ablation damages separately;
6. whether `B` recruitment is still present after controlling for intact logit margin;
7. the same causal group test using `L_P` to define LOW/HIGH primary engagement;
8. results under the released CoAx ablation value and one predeclared secondary ablation baseline;
9. LayerNorm-rescaling diagnostics where applicable.

A positive `rho` without positive selective causal evidence `G` is **not** sufficient for the claim `endogenous substitution`.

A positive group effect driven entirely by one prompt type is reported as heterogeneity, not a general relation.

---

# 9. Resolution-first decision rules

This pilot is intentionally **not** a positive-effect gate. Any well-resolved relation is scientifically informative.

## Instrument-support gate

Before interpreting `rho`, confirmation must contain real intact primary-route variation.

Require both:

- median within-bundle max-minus-min `A_P >= 0.10` attention mass;
- at least 75% of retained bundles contain two variants differing in `A_P` by `>= 0.08`.

If not: `HOLD — INSUFFICIENT ENDOGENOUS PRIMARY VARIATION`.

Do not create harder prompts to rescue the pilot.

## Outcome A — counterfactual-to-endogenous transfer

Classify `POSITIVE TRANSFER` if:

1. `rho > 0` and its 95% bootstrap CI excludes 0;
2. `G > 0` and its 95% bootstrap CI excludes 0;
3. qualitative direction agrees when primary engagement is defined by `L_P`;
4. the relationship is not confined to one single prompt family.

This supports the claim that intervention-discovered alternatives predict natural route allocation.

## Outcome B — precise dissociation

Classify `PRECISE DISSOCIATION` if:

1. the 95% CI for `rho` lies entirely inside `[-0.10, +0.10]`;
2. the 95% CI for `G` lies entirely inside `[-0.15, +0.15]` logits;
3. the same near-null holds under `L_P`.

This supports the claim that counterfactual alternatives do not predict endogenous route selection in the strongest labeled self-repair system.

## Outcome C — systematic mismatch

Classify `NEGATIVE / DIFFERENT-ROUTE MAPPING` if:

- `rho < 0` with CI excluding 0, or
- a non-CoAx head set shows reproducible endogenous recruitment while `B` does not,

provided the result survives matched controls.

This is scientifically interesting: internal damage exposes a different computational repertoire from natural input adaptation.

## Outcome D — unresolved

All other cases:

`HOLD — RELATION NOT RESOLVED`.

Do not rescue by selecting a favorite prompt family, changing k, redefining P, adding new variants, or model shopping.

---

# 10. Why this is exploration, not a phenomenon bet

The experiment does not require:

- DoubleIO to wake backups;
- TripleIO to wake backups;
- the eight published backups to be special on any one condition;
- a reversal or anomaly.

It estimates a predeclared relation over **all non-primary heads and within-bundle intact variation**, then causally validates the highest-counterfactual-substitutability set.

Positive, zero, and negative mappings each answer a different scientific hypothesis. The bad outcome is lack of resolution, not lack of a desired phenomenon.

---

# 11. After E01R

No Mainline promotion is automatic.

If E01R yields any well-resolved Outcome A/B/C, return to Selection and design an independent test.

Preferred E02:

- induction / copying, because CoAx already recovers alternative components across multiple model families;
- use predeclared intact variation such as repeat distance, distractor density, and context length;
- test at least two model families;
- retain the same central estimand: `counterfactual substitutability -> endogenous route selection`.

A second possible expansion uses OASR / alternative faithful circuits from *All Circuits Lead to Rome* to test whether low-overlap sufficient circuits are differentially load-bearing across natural inputs or are merely counterfactual equivalent realizations.

That expansion is **not authorized before E01R**.

---

# 12. Cost

E01R remains very cheap:

- one frozen GPT-2-small;
- 256 calibration prompts;
- 512 semantic bundles × 6 intact variants;
- CoAx calibration over attention heads;
- intact activation logging + a bounded set of single/head-set ablations;
- no training.

Expected compute remains comfortably below one GPU-day.
