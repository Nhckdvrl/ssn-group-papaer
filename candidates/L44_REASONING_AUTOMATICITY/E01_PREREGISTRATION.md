# L44 E01 — Internalization vs Workspace Dependence

**Status:** `AUTHORIZED — E01 ONLY`  
**Date:** 2026-09-15

## 0. Purpose

E01 asks only one question:

> **As an explicit reasoning procedure is progressively internalized during training, how does its causal dependence on the model's shared J-space change?**

E01 is not authorized to become a generic `inspect implicit CoT activations` study. It is a relationship estimate between **internalization stage** and **causal workspace dependence**.

---

# 1. Two-stage gate

## Gate A — validate the instrument on the exact open model

Before training any internalization trajectory, the chosen model must reproduce a causal distinction of the same form as the global-workspace paper.

Preferred initial model: an open 7B–9B decoder supported by the released Jacobian-lens code, with Qwen-family models preferred for implementation compatibility.

Required positive controls:

1. **deliberative reasoning control:** direct-answer multi-step arithmetic / GSM8K should show substantial task damage under J-space ablation beyond a matched non-J perturbation;
2. **externalization control:** explicit-CoT solution of the same items should be less J-space-dependent than direct answering, matching the published qualitative dissociation;
3. **automatic/routine control:** at least one routine task such as text continuation / shallow classification should remain substantially more robust than the direct-reasoning condition;
4. **general-damage control:** the intervention may not simply destroy fluency or next-token prediction globally.

Use the paper's safeguards where applicable:

- ablate the most active J-lens directions over the identified workspace layer band;
- avoid directions corresponding to tokens the clean model is imminently trying to output;
- compare to layer/rank/norm-matched perturbations;
- report clean accuracy and general language-model damage separately.

### Gate-A kill

If the exact open model does not show a selective causal workspace effect after reasonable reproduction effort, **STOP L44**. Do not compensate by inventing a new workspace metric or switching to a descriptive J-lens readout paper.

A different open model may be tried only if there is prior independent evidence that the J-space phenomenon reproduces there.

---

# 2. Internalization trajectory

After Gate A passes, construct a controlled trajectory using a published internalization procedure.

Preferred first route:

> **stepwise CoT internalization** following Deng et al. (2024): begin from a model that solves a task with explicit intermediate steps, then progressively remove those steps during fine-tuning while preserving the same task / answer mapping.

The pilot task should satisfy:

- performance is high with explicit reasoning before internalization;
- the same examples / target function can be retained across stages;
- intermediate reasoning can be progressively removed in a deterministic curriculum;
- enough checkpoints exist to estimate a trajectory rather than compare only two endpoints;
- compute remains small enough that a failed E01 costs much less than a full paper.

A controlled arithmetic / algorithmic reasoning task is acceptable for E01. The full paper may not remain toy-only.

Freeze at minimum:

- base checkpoint before the internalization curriculum;
- task data and split;
- optimizer family and schedule except where the published internalization method requires stage resets;
- total stage definition;
- decoding / answer extraction;
- J-space fitting corpus and fitting recipe;
- evaluation items.

Save multiple checkpoints spanning:

> `explicit -> partially internalized -> strongly internalized -> direct`.

Do not define stages retrospectively from interesting J-space behavior.

---

# 3. Primary quantities

For checkpoint/stage `s`:

### Behavioral internalization

Record at least:

- task accuracy `A_s`;
- mean generated reasoning tokens / explicit reasoning steps `R_s`;
- inference passes/tokens required by the trained procedure where meaningful.

The trajectory is valid only if `R_s` changes materially while `A_s` stays sufficiently high to make causal damage interpretable.

### Causal workspace dependence

Let:

- `A_s(clean)` = task score at checkpoint `s`;
- `A_s(J)` = score with J-space ablation;
- `A_s(ctrl)` = score with a matched non-J perturbation.

Define the primary effect:

> **`W_s = [A_s(clean) - A_s(J)] - [A_s(clean) - A_s(ctrl)]`**
>
> equivalently `W_s = A_s(ctrl) - A_s(J)`.

`W_s` measures selective causal workspace dependence beyond generic intervention damage.

If accuracy saturates or is too discrete for stable estimation, preregister a continuous answer-margin/log-probability analogue before viewing the trajectory result. Do not choose the endpoint post hoc.

### Primary estimand

> **relationship between internalization stage `s` (or preregistered `R_s`) and `W_s`.**

The key object is a slope / monotonic trend or an explicitly tested non-monotonic trajectory, not one pairwise endpoint contrast.

Bootstrap / uncertainty should resample independent problem instances, not token positions.

---

# 4. Measurement invariance across checkpoints

The J-lens / workspace may itself shift during fine-tuning. Therefore E01 must not blindly reuse one fixed direction set and call reduced overlap `automaticity`.

Primary plan:

- fit or calibrate the J-lens separately for each checkpoint using the **same frozen generic corpus and same fitting recipe**;
- identify the workspace band by the same preregistered criterion;
- measure functional causal dependence `W_s`, not vector cosine similarity across checkpoints.

Secondary diagnostic:

- repeat with a fixed pre-internalization lens where technically valid, only to estimate sensitivity to the moving-instrument choice.

A result that exists only under one arbitrary lens-transport convention is not a pass.

---

# 5. Outcome map

## PASS-A — decreasing workspace dependence

`W_s` decreases as reasoning is internalized, with CIs resolving a meaningful trajectory.

Interpretation:

> internalization produces genuine mechanistic automaticity / specialized computation.

## PASS-B — increasing workspace dependence

`W_s` increases while explicit reasoning disappears.

Interpretation:

> the computation has become behaviorally direct but more reliant on silent workspace deliberation.

This is especially consequential because it falsifies the common behavioral equation `no CoT -> System 1 / automatic`.

## PASS-C — resolved non-monotonic trajectory

For example, workspace dependence rises during early internalization and falls only after further practice.

Interpretation:

> internalization may have distinct stages: externalized deliberation -> latent deliberation -> automatic compilation.

## PASS-D — precise invariance

`W_s` stays effectively constant across a large, successful change in `R_s` with a narrow interval excluding effects large enough to support the other mechanistic stories.

Interpretation:

> runtime/token internalization and workspace dependence are separable dimensions.

## FAIL-1 — instrument failure

Gate A fails.

## FAIL-2 — no real internalization

Reasoning length/steps do not materially change, or performance collapses so badly that ablation effects cannot be compared.

## FAIL-3 — unresolved

Intervals are too wide / task too saturated / intervention damage too high to resolve the relationship.

Do not promote on an unresolved pilot.

---

# 6. Forbidden rescues

If E01 fails, do **not** rescue L44 as:

- `what concepts are in J-space during implicit CoT`;
- `J-lens visualization of training`;
- `another latent-CoT method`;
- `a better System 1 benchmark`;
- `post-training changes J-space features`;
- `reasoning tokens become shorter with training`;
- `internalization hurts OOD` (already directly studied);
- `wider vs deeper models internalize differently` (already directly studied).

A failed causal workspace measurement kills the current route unless a new independent instrument becomes available.

---

# 7. After E01 only

No full expansion is authorized yet.

If E01 resolves the relationship, the next selection audit should decide whether the result has enough magnitude and independence to justify:

- a second task / training route;
- testing whether workspace independence predicts OOD/flexible-composition loss;
- a simple theory of when a procedure can be compiled out of the shared workspace.

Those are **not** automatic follow-ups and must not be started before E01 is reviewed.