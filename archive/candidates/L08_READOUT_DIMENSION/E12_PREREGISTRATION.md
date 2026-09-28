# L08 — E12 preregistration: is compression damage trajectory-mediated?

**Rewritten 2026-09-14** after an identification review rejected the first draft
(`E12_SUPERSEDED_2026-09-14_capability_x_provenance.md`, the `capability × provenance`
2x2). **No treatment compute is authorized by this file.** Stage 1 must pass before
Stage 3 is authorized; the gate is in §8.

Linked claim: `C2` in [`MAINLINE.md`](MAINLINE.md).
Motivating audit: [`AUDIT_2026-09-14_DEPTH_CONFOUND.md`](AUDIT_2026-09-14_DEPTH_CONFOUND.md).

---

## 1. Why the first draft was rejected

The first draft made `answer provenance` the treatment via two constructed arms:
GSM8K with the solution supplied (arm B), MMLU with a derived intermediate required
(arm D). Neither isolates provenance.

- **Arm B changes the computation.** A becomes "solve"; B becomes "read and verify a
  supplied solution". If B is more robust, the correct reading is that we removed most
  of the work, not that provenance matters.
- **Arm D changes it symmetrically.** It adds sequential computation to a knowledge
  task. A perfect crossover `A < B, D < C` is then equally well explained by
  "conditions requiring more sequential computation are more fragile".
- **Arm D's corruption ablation does not fix this.** It shows D depends on the derived
  state. It does not show D and C are computationally equivalent up to state
  provenance. Those are different questions.

The binary itself was also loose. `prompt-recoverable` was doing work it cannot
support: MMLU's candidate strings are in the prompt but *which one is correct* is not,
and GSM8K's problem statement is in the prompt throughout, so the model could in
principle re-derive rather than depend on its own chain. `answer string is in the
prompt` is not `task-critical state is externally recoverable`.

## 2. The scientific object, restated

Let `T` be the compression treatment, `Z_t` the tokens the model has emitted, `Y` the
final answer. Compression reaches the answer by two paths:

```
  direct        T -> Y
  mediated      T -> Z(T) -> Y
```

The second path is the object:

> **trajectory-mediated compression damage** — the share of compression-induced failure
> that arrives not because the current step's computation is damaged, but because the
> context the current step conditions on was itself produced under the same treatment.

The governing variable is **trajectory dependence** (equivalently, external
re-groundability): whether the information needed for a correct decision at step `t`
can be recovered from a context that is not treatment-dependent. This replaces
`prompt-recoverable vs trajectory-carried`, which was a proxy for it and is retained
only as the observational correlate that motivated the question.

Central claim in its testable form:

> **Compression errors compound with dependence on treatment-generated context, not
> with output length or with semantic capability per se.**

## 3. The instrument: prefix clamping

Same item, same model, same compression, same reference trajectory content, same answer
depth. Only one thing changes: whether the context the model conditions on was produced
under the treatment.

For a cut point `k`, the compressed model generates with its emitted token **overridden
to the reference trajectory for steps `< k`**, then free-runs to the answer.

**Critical implementation property.** During the clamped segment the compressed model
still executes its own forward pass at every step; only the token appended to the
context is replaced. Direct per-step damage is therefore present on 100% of steps in
every condition, and `k` varies **only** how much of the conditioning context is
treatment-generated.

This is the separation E07 could not make. E07 varied the *intervention window*, which
moves direct-damage dose and trajectory contamination together — which is why it could
only conclude "positional, not cumulative" and explicitly could not obtain a
dose-response. Clamping holds direct damage fixed and varies mediation alone.

It also has a practical consequence that decides the whole program: **clamping never
modifies the model mid-generation**, so it applies unchanged to Wanda, SparseGPT, AWQ
and GPTQ. An E07-style weight-swapping schedule does not.

## 4. The three prefixes, and the control the design needs

A two-arm version (free-running vs reference-clamped) is **confounded**, and this is my
addition to the design rather than a point inherited from the review. The reference
prefix is not only untreated, it is also *correct* — we condition on the full model
being right. So "untreated" and "correct" vary together, and any effect is equally
readable as ordinary error propagation.

Three prefixes are required:

| arm | prefix at steps `< k` | treated? | correct? |
|---|---|---|---|
| **F** free-running | `Z(T)`, the compressed model's own | yes | no |
| **R** reference-clamped | `Z(0)`, the full model's | no | yes |
| **R̃** corrupted-reference-clamped | `Z(0)` with errors injected to a matched rate | no | no |

Decomposition of the total mediation:

```
  Y(T,R)  - Y(T,F)    total trajectory mediation
  Y(T,R)  - Y(T,R̃)    the part explained by the prefix CONTENT being worse
                       (ordinary error propagation / exposure bias)
  Y(T,R̃) - Y(T,F)     RESIDUAL: attributable to the prefix having been produced
                       under the same perturbation, beyond its surface error content
```

**The residual is what makes this a new object rather than exposure bias.** If it is
~0, the honest reading is error propagation, which is adjacent to what RAC already
owns, and the paper's ceiling drops accordingly — this is stated in the outcome table
in §8 and is not to be argued away afterwards.

A residual is mechanistically plausible: the compressed model's own prefix is drawn
from *its* distribution and can be off-manifold for its own remaining computation —
E05 measured degeneration at 0.87 under readout truncation — whereas corrupted
reference text is not.

**Matching criterion for R̃, fixed in advance.** `Z(0)` is perturbed by resampling
tokens from the full model at a temperature tuned per (model, intervention, cell) so
that the fraction of clamped prefixes containing a task-level error (for GSM8K: a wrong
intermediate arithmetic result, checked by the calculator annotations) equals that of
`Z(T)` to within 0.05. **Known limitation, recorded now:** this matches error *rate*,
not error *type*. A reviewer may say the residual reflects a type mismatch. The
secondary state-refresh experiment (§6) is the answer to that, which is why it is in
the program rather than optional.

## 5. Stage 1 — the primary experiment

**Design.** `trajectory dependence × depth`, within item. Capability does not appear.

|  | early cut | late cut |
|---|---|---|
| clamped (R, R̃) | cell 1 | cell 2 |
| free-running (F) | cell 3 | cell 4 |

`k` is drawn per item from a preregistered grid expressed as a fraction of that item's
reference answer position `L₀`: `k/L₀ ∈ {0, 0.25, 0.5, 0.75, 1.0}`. `k = 0` is pure
free-running; `k = L₀` clamps through the answer. Assignment is by a seed independent
of the item, so depth is exogenous.

**Primary estimand.**

```
  Δ = [ Y(late) - Y(early) ]_free-running  -  [ Y(late) - Y(early) ]_clamped
```

`Δ ≪ 0`, stable across compressors and model families, is the result. It says
generation depth is not itself the problem; depth *of treatment-generated context* is.

**Secondary, per item:** next-step top-1 survival, first-divergence hazard as a
function of position, margin at the divergence step, and the distance from first
divergence to the answer. E03c's `replay` already computes the first four on a forced
prefix and is reused; the new runner adds the free-run continuation and answer scoring.

**Tasks.** GSM8K plus one second computation family with verifiable reference
trajectories (MATH-500). Two computation families is a hard requirement — a result on
GSM8K alone is a kill under §8.

**Models, Stage 1.** Llama-3.1-8B-Instruct and Qwen2.5-7B-Instruct.

**Interventions, Stage 1.** Readout truncation (the inherited, cheapest intervention)
plus one parameter-locus method. Stage 1 is about whether the effect exists and is
identified, not about coverage.

## 6. Stage 2 — state refresh

Only if Stage 1 passes. Mid-trajectory, re-externalize one intermediate state that the
reference trajectory had already produced and that is verified load-bearing.

Three conditions, and the third is the one that matters:

| condition | injected |
|---|---|
| no refresh | — |
| correct-state refresh | the same intermediate value the reference trajectory computed |
| matched irrelevant refresh | text matched in length, position and surface form, carrying no task information |

**The refresh must not supply new knowledge.** It re-externalizes a state the model had
already derived. If correct refresh specifically restores the compressed free-running
trajectory while matched irrelevant text does not, the mediation bridge is identified
and the error-type objection to §4 is answered.

## 7. Stage 3 — external validity and consequence

Only if Stages 1-2 pass.

- **Compressors:** Wanda and SparseGPT at 50% unstructured, AWQ or GPTQ at 4-bit
  weight-only — UniComp's settings, so no severity argument is needed. Calibration data
  is fixed across all arms and is deliberately **not** task-matched; task-matched
  calibration is RAC's paper and AYOT's paper.
- **Model families:** at least two, ideally a third from the local cache.
- **Consequence:** how much of a published capability-retention gap the mechanism
  accounts for. Take UniComp's `knowledge bias` rows and Takeshita et al.'s Table 3 and
  re-estimate with trajectory dependence controlled. **Preregistered reading: we do not
  require the headline to be overturned.** "The mechanism accounts for 40% of the
  reported gap; the remainder is a genuine capability effect" is a good result and is
  more credible than a total reversal. The UniComp GPQA-Diamond prediction is the
  sharpest test — their own untested conjecture that its robustness is "likely
  attributable to its multiple-choice format" is this mechanism's prediction, and it can
  be checked directly by running GPQA-Diamond under free generation.

## 8. Outcomes, fixed in advance

| result | verdict |
|---|---|
| clamping largely removes the depth slope; free-running keeps it | **Stage 1 PASS** — causal first stage established |
| residual `Y(T,R̃) - Y(T,F)` substantial | new object; exposure bias cannot absorb the paper |
| residual ~0, total mediation large | honest error-propagation result; ceiling drops toward Findings; Stage 2 becomes mandatory before any Main claim |
| clamped and free-running slopes equal | **trajectory-mediation hypothesis FAILS** |
| correct-state refresh restores, matched irrelevant does not | mechanism strengthened |
| holds for readout truncation but for none of Wanda/SparseGPT/AWQ/GPTQ | not a compression paper; Main route killed |
| holds on GSM8K but not the second computation family | **severe downgrade / likely KILL** |
| UniComp knowledge bias unchanged after control | mechanism survives, C3 significance downgraded |
| knowledge bias shrinks substantially **and** GPQA free-generation moves as predicted | **strong C3** |

**Forbidden rescues.** On a kill the package may not retreat to: "multiple choice and
generation still differ" (owned by Wen et al. and Song et al.); the `C3.2` no-crossing
count (demoted 2026-09-14); the observational 14/15-vs-1/15 slope table (it is the
motivation, not a result); or a benchmark-auditing paper.

**Authorization gate.** This file authorizes **Stage 1 only**, and only after the
runner in §9 passes its validation. Stage 3's SOTA-compression compute is authorized by
a separate decision recorded against the Stage 1 outcome.

## 9. Implementation and validation, before any treatment run

New runner `scripts/run_e12_clamp.py`. Required validations, each of which can fail:

1. `k = 0` must reproduce the existing free-running numbers exactly for every
   (model, cell, intervention). This is the analogue of E07's `all`-schedule check and
   is non-negotiable.
2. `k = L₀` under the reference prefix must reproduce full-model accuracy on the
   clamped span, confirming the override is applied where intended.
3. **Corrected 2026-09-14, before any run.** The draft asserted that per-item step
   counts match between F and R. That is false and would have been a bad check: once
   the clamp releases at `k`, the two arms free-run differently and their lengths
   legitimately diverge. The real invariant is that **the intervention is active on
   100% of `lm_head` forward passes in every arm** — clamping overrides the emitted
   token, never the computation — plus the trivial one that steps `< k` are identical
   by construction. Verified by hook-level forward-pass counting, not by output length.
4. Tokenization: the reference trajectory is re-tokenized under the same tokenizer, and
   the clamp operates on token ids, not text, so no retokenization drift enters.
5. The R̃ temperature calibration is fit on a held-out item split, not the evaluation
   split.

## 10. Compute

Local environment only: `/home/xiang/miniconda3/envs/verl-clean/bin/python`. No new
environment, no package install or upgrade.

GPUs from idle cards on `fvcrc10`, `fvcrc11`, `fvcrc12`, `fvcrc13`, `fvcrc15`.
**At most four cards at a time for L08.** Idle cards checked before launch; host/card
assignment recorded in the launch log.

Stage 1 is cheap relative to the historical E-series: 2 models x 2 interventions x
2 tasks x 5 cut points x 3 prefix arms, 300-500 items per cell, greedy.
