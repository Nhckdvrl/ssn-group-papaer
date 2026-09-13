# 2026-09-13 — Pressure-First Search XX

Continuation after `PRESSURE_FIRST_SEARCH_XIX.md`. This batch records several high-salience pressures that fail either exact-owner, anti-resurrection, or independent-parent tests. P73 remains under a separate full Selection audit; nothing here promotes it. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## P100 — LM-head gradient bottleneck: lost norm or lost useful learning signal?

**Status:** `DROP / EXACT 2026 CAUSAL FOLLOW-UP OWNER`

### Prior pressure
`PRESSURE_FIRST_SEARCH_XII.md` recorded the tension created by *Lost in Backpropagation: The LM Head is a Gradient Bottleneck*: projecting vocabulary-space gradients through `D << V` removes roughly 95–99% of gradient norm, and the paper interprets this as a harmful optimization bottleneck. The open identification question was whether the discarded norm is actually useful learnable signal or largely irrelevant/null-space energy.

### Why now dead
An August 17, 2026 follow-up, *Does the LM Head Create a Harmful Gradient Bottleneck? A Causal Test* (arXiv:2608.16671), now performs essentially the missing intervention. It holds the ordinary forward logits and LM-head update fixed while reducing only the backward feedback rank into the Transformer. This separates geometric compression from the stronger claim that the removed vocabulary-space directions are required for useful learning. The study reports that the geometric bottleneck is real but the causal harmful-optimization interpretation is not established in the simple way implied by norm loss.

This is exactly the decisive operation P62 was waiting for.

**Anti-resurrection:** do not reopen `95–99% gradient norm loss = useful-signal loss?`, backward-rank LM-head interventions, or `norm compression vs optimization harm` with another model/task. A future output-head question needs a different scientific estimand.

---

## P101 — Redundant factual-retrieval paths: native parallel routes or intervention-induced backup routes?

**Status:** `DROP / K191 + PATCHING-IDENTIFICATION PARENT`

### Pressure
ACL 2026 Main work on factual retrieval reports multiple functionally equivalent, distributed, non-contiguous retrieval paths. Combined with 2026 causal-mediation theory showing backup compensation and multiple-mediator interactions can distort activation-patching interpretations, an attractive question is whether the reported routes are simultaneously used during native recall or whether some become important only after another path is perturbed.

### Why dead
This does not introduce a sufficiently new scientific object relative to the existing project history. L31/K191 already incorporated the ACL 2026 redundant-path result and explicitly hard-bans generic factual-memory route switching. P60 separately records the broader activation-patching identification issue: noising/denoising and mediator/bypass interactions can reveal compensatory mechanisms that are not equivalent to native pathway contribution.

The new wording is the intersection of two known parents rather than an independent question.

**Anti-resurrection:** do not reopen factual-memory `native route vs backup route`, simultaneous-vs-compensatory retrieval, or another path-patching protocol. New factual-memory work must introduce a different quantity than route redundancy/selection.

---

## P102 — Resource-rational memory: strategic allocation or generic noise-robust learning?

**Status:** `DROP CURRENT FORM / PAPER-LOCAL ABLATION, NOT INDEPENDENT PARENT`

### Pressure
ACL 2026 Best *Memory Efficiency and Resource-Rational Encoding in Sentence Processing* trains a Transformer under a noisy memory representation with a resource/precision constraint and obtains more compressed, categorical context representations plus improved alignment with human sentence-processing signatures. A natural identification challenge is whether the categoricalization specifically reflects strategic resource allocation or would arise under matched fixed-noise/noise-robust training without the resource-rational allocation mechanism.

### Why not a project
A matched fixed-noise control could be scientifically useful for adjudicating the paper's explanation, but the strongest result remains tightly local to one bespoke cognitive model: `the award paper's representation effect requires (or does not require) adaptive resource allocation rather than generic noisy training`. The pressure does not independently exist as a modern-LM phenomenon outside that model, and the growth path would be dominated by reconstructing the same cognitive simulation rather than revealing a broader model-computation law.

**Reviewer compression:** `resource-rational noisy-memory model + missing matched noise-only control = explanatory ablation`, not a new Main-level parent for this portfolio.

**Anti-resurrection:** do not promote merely because a Best Paper leaves an alternative explanation untested. The scientific object must survive removal of the focal paper's custom model.

---

## P103 — Attention sinks: optimization artifact, anti-overmixing device, or algorithmic workspace?

**Status:** `DROP / MATURE 2025–2026 MECHANISM PROGRAM`

Attention sinks superficially fit both `structural default/anomaly -> mechanism` and `widely believed explanation -> causal test`. However by 2025–2026 the space is already decomposed by direct work: first-token attention has been explained through over-mixing avoidance; NeurIPS 2025 develops a catch–tag–release computational account; ACL 2026 gives mechanistic/circuit analyses; and theoretical work shows sink-like behavior can be required for softmax attention on specific trigger-style computations. The natural explanation space is no longer open enough for a generic Main parent.

**Anti-resurrection:** do not reopen `why do sinks exist`, `sink as workspace vs trash can`, or another sink ablation/circuit localization without a genuinely new same-quantity contradiction.

---

## P69 ownership re-audit — implicit noisy-channel model inside a vanilla LM

**Status:** `HOLD / OWNERSHIP OPAQUE — NO COMPUTE`

The core pressure remains scientifically live: EMNLP 2025 *Resource-Rational Noisy-Channel Language Processing* uses a language model as the language/world prior and adds a separate explicit error model plus inference procedure, leaving open whether a vanilla next-token LM itself computes an operation-specific channel likelihood beyond plausibility. Human work shows comprehenders adapt to the type and prevalence of corruption.

The ownership blocker has not cleared. Public sources still list a 2025 Gawel & Ryskin poster titled *Noisy Channel Inference in Large Language Models*, but no public abstract/paper/preprint sufficient to determine whether it already owns `prior-only vs implicit channel likelihood` or channel-specific adaptation. Later 2026 lab work visible publicly focuses on memory in noisy-channel comprehension rather than exposing the poster's exact LLM estimand.

Absence of a public abstract is not novelty evidence. Therefore P69 remains HOLD. Do not authorize compute until the poster's scientific claim can be bounded or a clearly distinct estimand is identified.

---

## P73 exact-owner sweep checkpoint

**Status:** `FULL SELECTION AUDIT CONTINUES — NO COMPUTE FROM THIS FILE`

Search was repeated using the estimand rather than the structural-priming vocabulary: `same demonstration / same observation`, causal pre-example expectation, surprise-controlled update size, counterfactual expectation before evidence, causal prediction error in ICL, and 2026 successors/citations of the NAACL 2025 mother.

The closest public owners remain:

1. **NAACL 2025 Zhou et al.** — natural verb-bias × observed-structure IFE, used diagnostically to infer error-driven ICL.
2. **EMNLP 2025 Surprise Calibration** — observational/derived surprise is used as a signal for dynamic class-prior shifts and as a calibration method.
3. **Zhou, McCoy & Frank 2026** — counterfactual causal editing of continuous verb bias changes downstream structural preference; error-signal-like information is encoded, but those error-related aspects are not naturally causally used in downstream production, and connecting continuous variables to ICL is left unresolved.

No public work was found that estimates the proposed quantity:

`do(pre-observation model expectation) -> identical observed example -> later native in-context update`.

This does **not** authorize the candidate; it only clears the exact-owner blocker provisionally. Selection still needs an identifying temporal/path intervention with a substantial symmetric expectation first stage and feasible resolution under verb-clustered uncertainty.

Published substrate is unusually convenient but must not be over-counted: the mother repository contains 92,400 trial combinations from 22 ditransitive verbs, 50 targets per verb, and four structural pairings, but the load-bearing expectation variable is primarily verb-level. Effective inferential support must therefore respect the 22-verb cluster structure rather than treating tens of thousands of sentence pairs as independent units.

---

# Round checkpoint

**New survivor in this file: 0.**

This is not a search closeout. Broad pressure-first search continues. P73 remains the only current object in full Selection; P69 remains blocked by opaque ownership; all P100–P103 routes are closed in their current forms.