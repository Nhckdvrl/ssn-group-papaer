# L43 E01 Preregistration — Natural Recruitment of IOI Backup Circuits

**Status:** `AUTHORIZED — E01 ONLY`  
**Parent:** `SELECTION.md`  
**Date locked:** 2026-09-15

## E01 question

> **Do the published GPT-2-small IOI backup name-mover heads become selectively load-bearing when the intact model faces answer-preserving prompt stress, without ablating the primary name movers?**

E01 is an instrument / existence test. It is **not** intended to establish a general law from GPT-2-small.

---

# 1. Fixed model and published circuit sets

Model:

- `gpt2` / GPT-2 small, frozen.

Primary name-mover seed set `P`:

- `(9,9)`
- `(10,0)`
- `(9,6)`

Published backup name-mover set `B`:

- `(10,10)`
- `(10,6)`
- `(10,2)`
- `(10,1)`
- `(11,2)`
- `(9,7)`
- `(9,0)`
- `(11,9)`

These sets come from the canonical IOI circuit / CoAx evaluation. **Do not alter them after looking at stress results.**

Use the released CoAx implementation and its exact head-ablation primitive wherever possible:

https://github.com/GongZhiren/Conditional-Co-Ablation

---

# 2. Prompt construction

Use three **paired** conditions built from the same sampled names / place / object tuple.

## BASE

Canonical IOI format.

Example:

`When Mary and John went to the store, John gave a drink to`

Correct completion: ` Mary`.

## DOUBLE

Published DoubleIO stress from Nainani et al. 2024: add one extra occurrence of the indirect-object name while preserving the final correct answer.

Example shape:

`When Mary and John went to the store, Mary was happy. John gave a drink to`

Correct completion remains ` Mary`.

## TRIPLE

Published TripleIO stress: add a second extra occurrence of the indirect-object name while preserving the final answer.

Example shape:

`When Mary and John went to the store, Mary was happy. Mary sat on a bench. John gave a drink to`

Correct completion remains ` Mary`.

Use the exact published template family / generation logic from *Adaptive Circuit Behavior and Generalization in Mechanistic Interpretability* where available. Do not invent harder stress prompts after seeing E01.

All three versions for an item must use the same names, place and object.

---

# 3. Data split

Generate with one sealed seed before any stress analysis:

- `CALIBRATION`: 256 paired triplets;
- `CONFIRMATION`: 512 paired triplets.

The confirmation triplets must remain untouched until:

1. CoAx replication passes on calibration;
2. matched negative-control heads have been frozen from BASE calibration only;
3. all analysis code and signs are verified.

No prompt filtering based on head behavior is allowed.

For the primary confirmation analysis, retain an item only if the intact model assigns the correct IO token a higher logit than the competing subject token in **BASE, DOUBLE and TRIPLE**. Report retention rate separately for each condition and the all-three intersection.

This retention rule is fixed because E01 asks how a mechanism supports a behavior the model still performs; failures belong to a later analysis, not this estimand.

If fewer than 250 of 512 items survive the all-three correctness intersection, mark `HOLD — STRESS SUPPORT TOO WEAK` rather than weakening the stress post hoc.

---

# 4. E00-style replication gate before the new test

On CALIBRATION BASE only:

1. reproduce CoAx backup recovery conditioned on `P`;
2. compute ROC-AUC using the published `B` labels.

Gate:

> **CoAx backup ROC-AUC >= 0.80**

(the paper reports about 0.91).

Also reproduce the qualitative wake-up signature:

> the published backup set has greater causal/output effect after `P` is ablated than on the intact BASE model.

If the AUC gate fails, stop E01 as `HOLD — PARENT INSTRUMENT REPLICATION FAILURE`.

Do not search for a different primary seed or redefine the backup labels.

---

# 5. Frozen matched negative controls

We need to rule out the trivial explanation:

> `stress just makes every late head more important`.

Construct one matched control set `C` of eight heads using **CALIBRATION BASE only**.

Eligible control heads:

- same layers represented in `B` (layers 9–11);
- not in any published primary or backup name-mover set;
- not a known negative-name-mover head;
- no stress-condition statistics may be used.

For each backup head, choose a unique eligible head minimizing absolute difference in **BASE single-head ablation damage**. Solve the one-to-one minimum-cost matching deterministically; ties broken lexicographically by `(layer, head)`.

Freeze `C` before opening any DOUBLE / TRIPLE mechanistic result.

Also report a sensitivity analysis over 100 fixed-seed layer-matched random control sets, but this is secondary. The single matched `C` is the preregistered control.

---

# 6. Quantities

For each item `i`, condition `s`, and head set `H`, define

`LD_intact(i,s) = logit(IO) - logit(S)`

and

`Damage_H(i,s) = LD_intact(i,s) - LD_ablate(H)(i,s)`.

Positive damage means removing `H` hurts the correct IO preference.

Primary backup-set damage:

`D_B(s) = mean_i Damage_B(i,s)`.

Matched-control damage:

`D_C(s) = mean_i Damage_C(i,s)`.

For each stress condition:

`I_s = [D_B(s) - D_B(BASE)] - [D_C(s) - D_C(BASE)]`.

Primary combined estimand:

`I = 0.5 * [I_DOUBLE + I_TRIPLE]`.

Interpretation:

> `I > 0` means the published backup set becomes more causally necessary under natural input stress than a BASE-importance-matched set of ordinary late heads.

All uncertainty is computed by paired bootstrap over retained item triplets (`10,000` bootstrap resamples, sealed RNG seed `43001`).

---

# 7. Mandatory intact-run evidence

Backup-only ablation is causal but still an intervention. Therefore E01 must also show what happens **before any ablation**.

For every published backup and control head, report on intact BASE / DOUBLE / TRIPLE:

- direct IO-vs-S logit contribution;
- attention mass to the correct IO token and competing S token at END;
- CoAx paper's available wake-up / output-grounded diagnostic adapted only where it is defined on the intact run.

The central intact-run check is:

> Does stress increase the backup set's correct-answer contribution relative to BASE and relative to the matched controls?

A causal-ablation result with no intact-run signature must be labeled `INTERVENTION-ONLY`, not `natural recruitment`.

---

# 8. Frozen decision rules

## 8.1 Positive natural-recruitment gate

E01 passes as `POSITIVE NATURAL RECRUITMENT` only if all hold:

1. primary combined interaction `I >= +0.20` logits;
2. paired-bootstrap 95% CI for `I` excludes 0;
3. `I_DOUBLE` and `I_TRIPLE` have the same non-negative sign;
4. the backup set's raw intact-model ablation damage increases from BASE to at least one stress condition by `>= +0.20` logits;
5. intact-run backup contribution shows the same qualitative recruitment direction rather than remaining completely flat.

If 1–4 pass but 5 fails, classify `INTERVENTION-ONLY / CONSTRUCT WARNING`, not positive natural recruitment.

## 8.2 Well-resolved near-null gate

Because a null is scientifically meaningful, do not force a positive result.

Classify `PRECISE NATURAL-NONRECRUITMENT` if:

1. the 95% CI for `I` lies entirely within `[-0.15, +0.15]` logits;
2. neither stress condition has `I_s >= +0.20` with a CI excluding 0;
3. intact-run backup contribution does not materially increase relative to controls.

This does **not** by itself justify a Main claim. It authorizes an E02 designed to test whether the near-null generalizes beyond IOI before concluding that self-repair is an intervention artifact.

## 8.3 Ambiguous / heterogeneous result

Anything else:

> `HOLD — E01 DOES NOT CLEANLY SEPARATE NATURAL RECRUITMENT FROM INTERVENTION RESPONSE`.

Do not rescue by:

- choosing different IOI templates;
- redefining backups;
- picking the stress condition with the best effect;
- model shopping;
- swapping to SAE features;
- adding more prompt perturbations after inspection.

---

# 9. Mandatory decomposition / anti-story controls

Always report:

- intact accuracy and mean `LD` for BASE / DOUBLE / TRIPLE;
- `D_P(s)`, `D_B(s)`, `D_C(s)`;
- primary+backup co-ablation damage `D_{P∪B}(s)` as a secondary quantity;
- per-backup-head effects, not only the eight-head aggregate;
- LayerNorm-rescaling contribution if it can be measured with the published Rushing–Nanda decomposition;
- results with the exact released CoAx ablation operation;
- one secondary ablation baseline (e.g. resample/mean where implementation permits) only as a robustness check, never as a replacement primary after seeing results.

The paper must not label an effect as `learned redundancy` if it is fully explained by LayerNorm rescaling.

---

# 10. What happens after E01

No full paper is authorized regardless of the E01 sign.

If E01 is decisively positive or precisely null, return to Selection and design E02 around an **independent behavior**.

Preferred E02 surface:

- induction / copying, because CoAx already demonstrates scalable backup discovery across multiple released model families;
- stress dimensions fixed before inspection, such as repeat distance, intervening distractor structure, and context length;
- at least two model families.

Only after cross-behavior evidence should Circuit Condensation be considered as an orthogonal intervention on redundancy itself.

---

# 11. Cost

This pilot is deliberately cheap:

- one frozen GPT-2-small;
- 768 paired prompt triplets total;
- `O(#heads)` CoAx discovery on calibration;
- a small set of frozen head-set ablations on confirmation;
- no training.

Expected wall-clock is comfortably below a GPU-day and likely far below it.

The reason for authorization is therefore not only scientific quality but unusually favorable **information gained per unit compute**.