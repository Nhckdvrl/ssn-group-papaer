# 2026-09-15 — Top-Paper-Calibrated Problem-Taste Search Round

**Target:** ACL / EMNLP / NAACL Main  
**Taste calibration:** TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** PROBLEM TASTE FIRST; candidate generation disabled until Layer-1 question passes  
**Outcome:** **0 new L-series; 0 new pilot authorization; NO L42.**

This is a wall-level search record, not a list of paper gaps.

---

# 0. Mandatory taste calibration happened BEFORE generation

This round began by re-reading award-level / strong work and asking only how the scientific question was generated, not what topic could be copied.

Calibration set included:

- ACL 2026 Best / Outstanding work, including **Characterizing the Expressivity of Local Attention in Transformers**, **Memory Efficiency and Resource-Rational Encoding in Sentence Processing**, and **Systematicity between Forms and Meanings across Languages Supports Efficient Communication**;
- ICLR 2026 Outstanding work, including **Transformers are Inherently Succinct** and **LLMs Get Lost in Multi-Turn Conversation**;
- ICML 2026 award work, including **The Flexibility Trap** and **How much can language models memorize?**;
- NeurIPS 2025 award work, including **Does RL Really Incentivize Reasoning Capacity Beyond Base Model?** and **Superposition Yields Robust Neural Scaling**;
- EMNLP 2025 award work, including the CoT-faithfulness / unlearning work;
- TACL work on **What Can String Probability Tell Us About Grammaticality?** and **Can Language Models Learn Typologically Implausible Languages?**.

## Taste lessons retained

### T1 — Strong anomaly papers attack a load-bearing expectation

Examples such as local attention and the Flexibility Trap are not strong because they found an empty comparison cell. A plausible monotonic/default belief (`more/global/flexible should help`) fails on a durable scientific quantity.

### T2 — A new quantity can be more important than a new phenomenon

Strong work sometimes wins by replacing a vague claim with a quantity that can actually falsify it:

- expressivity -> succinctness;
- RL improves reasoning -> reachable capability boundary;
- memorization -> information stored per parameter;
- language-form complexity -> learnability of the meaning-to-form mapping.

### T3 — A new intervention is not itself a question

CoT faithfulness via unlearning is a valid strong-paper provenance, but this repository must not turn `new intervention -> find a distinction` into its default generator.

### T4 — Linking assumptions are scientific objects

The TACL grammaticality/probability work is a useful reminder: if the field routinely treats observable X as evidence for construct Y, a paper can be strong by stating the assumptions under which that inference is valid. This does **not** license generic evaluator/probe papers; the bridge itself must be load-bearing.

---

# 1. Pre-WALL anti-resurrection: information monotonicity

Natural pressure found:

> **Why can adding apparently harmless / non-contradictory information make a model lose a correct answer?**

This passes the 10-second taste test, but repository anti-resurrection takes precedence.

`failed/KILLED_LEDGER.md` already marks **K032 — irrelevant evidence / dilution** as `DO NOT ACTIVATE`, because the parent compresses to semantic leakage / irrelevant-information sensitivity / causal robustness.

Changing the name to `information monotonicity`, or using `C` versus `C + entail(C)`, does not create a new scientific object.

**Decision:** CLOSED BEFORE WALL. No K allocation; no resurrection.

---

# 2. WALL — Why do neural scaling laws exist?

## 10-second question

> **Why do neural / language-model losses follow such stable power laws as model size and data scale?**

## Pressure

> Power-law scaling persists over enormous ranges and guides billion-dollar training decisions, yet a power law is not implied merely by “bigger model + more data”.

This is an excellent standing problem. It also survives deletion of current frontier papers.

## Rival explanatory lineages reconstructed

### A — data manifold / kernel-spectrum account

Bahri et al. and related work derive scaling regimes from finite-size convergence, smooth data manifolds, kernel spectra, and resolution limits.

### B — quantized-skills / heavy-tail account

The Quantization Model explains power laws by discrete skills learned in frequency order when skills themselves have heavy-tailed occurrence frequencies.

### C — superposition geometry account

NeurIPS 2025 runner-up **Superposition Yields Robust Neural Scaling** argues that strong superposition can itself produce robust inverse scaling even when feature-frequency statistics do not have the originally assumed power-law form.

### D — direct natural-language statistics

2026 work attempts to derive data-scaling exponents from measurable statistics of language such as token-correlation decay / conditional-entropy decay.

### E — random-structure counterpressure

2026 random-graph work reports scaling behavior even on processes lacking the natural-language-style power-law correlations that some data-centric accounts require.

## Why no project survives

The first-layer question is excellent, but the modern literature has become a **direct explanation program**, not a collection of isolated observations.

The tempting move would be to force A/B/C into a toy factorial until one theory loses. That fails the new doctrine because:

- the accounts often target different scaling axes/regimes rather than cleanly disagreeing on one natural quantity;
- superposition work already manipulates feature-frequency structure and superposition strength;
- an artificial distribution manufactured only to separate theories would make Layer-3 identification more interesting than Layer-1 science.

**Decision:** KEEP AS STANDING IMPORTANT PROBLEM; CLOSED AS CURRENT TOPIC GENERATOR. No L42.

---

# 3. WALL — What can next-token prediction identify about the world?

## 10-second question

> **Can predicting the future uniquely determine what hidden state the world is in?**

## Pressure

> If two latent states induce the same distribution over every observable future, a pure prediction objective has no reason to distinguish them, yet “world-model” claims often treat a learned internal state as the underlying ontology itself.

## Old theory reconstruction

Computational Mechanics / predictive-state theory already provides the exact old object: histories are equivalent when they induce the same conditional distribution over futures, and causal states form a minimal sufficient statistic for prediction.

Thus prediction naturally identifies a **predictive equivalence class**, not arbitrary hidden ontology.

## Modern owner map

Current work already directly studies the bridge:

- HMM / Transformer work on belief-state geometry;
- ICML 2025 **A Causal World Model Underlying Next Token Prediction**;
- ICLR 2025 **Belief State Transformer**;
- ICLR 2026 latent-concept identifiability theory;
- ACL 2026 work comparing NTP and MTP for belief-state / world-model convergence.

## Why no project survives

`Does a Transformer learn the minimal predictive state / causal state?` compresses to:

> classic predictive-state theory × modern Transformer.

Adding probes, SAEs, patching, or a more complex hidden-state intervention would not make the scientific inference newer.

**Decision:** CLOSED. No L42.

---

# 4. WALL — What does process supervision actually buy?

## 10-second question

> **If final-outcome supervision is not statistically harder than step-by-step supervision, what does process supervision actually buy?**

## Pressure

> The common explanation is easier long-horizon credit assignment, but ICML 2025 theory shows that under appropriate coverage, outcome supervision need not be intrinsically more statistically difficult; practical process signal can still help substantially.

## Critical theoretical update

Jia, Rakhlin & Xie (ICML 2025), **Do We Need to Verify Step by Step?**, show under their assumptions that outcome-supervised RL is not statistically more difficult than process-supervised RL up to polynomial horizon factors, and that a policy advantage function can serve as an optimal process reward when it is estimable.

This rules out the lazy explanation:

> process labels always contain essential task information unavailable from outcomes.

## Old theory reconstruction

Classic reward-shaping theory already shows that dense shaping can change optimization speed dramatically without changing the optimal policy; potential-based shaping gives policy-invariance conditions.

Therefore the real decomposition is at least:

1. **more task information**;
2. **easier optimization / variance reduction / denser shaping**;
3. **a genuinely changed objective**.

## Modern density

2025–2026 PRM / process-RL / reward-shaping / outcome-to-process internalization work already occupies these axes.

## Why no project survives

The attractive residual `information vs optimization` reviewer-compresses to:

> Jia 2025 + classic reward shaping + modern reasoning RL.

A new LLM factorial would be a theory-identification descendant, not a new mother question.

**Decision:** CLOSED AS CURRENT TOPIC GENERATOR. Retain the three-way decomposition as an audit rule. No L42.

---

# 5. WALL — What determines the scope of a learning update?

This WALL is the disciplined version of the prior WATCH friction:

> **What does an example actually teach a model?**

## 10-second question

> **When training teaches a model one thing, what determines which other, never-supervised behaviors change with it?**

## Pressure

> Shared parameters guarantee some spillover, but semantic content alone clearly does not predict its scope: narrow fine-tuning can cause broad changes, and even semantically unrelated teacher-generated sequences can transmit a teacher trait.

## Old explanatory lineage

The parent is not new:

- multi-task / transfer learning studies positive and negative transfer;
- task affinity is often expressed via gradient alignment / interference;
- influence-function and kernel views approximate how a training update changes predictions on other points;
- ICML 2023 **A Kernel-Based View of Language Model Fine-Tuning** directly tests an NTK-like account for pre-trained LM fine-tuning.

At small / linearized update scale, “where does an update generalize?” already has a natural mathematical answer in terms of local gradient/kernel geometry.

## Frontier evidence / owners

### Nature 2026 — subliminal learning

**Language models transmit behavioural traits through hidden signals in data** shows teacher traits transmitted through semantically unrelated numbers, math traces, or code. The paper proves that when teacher and student share an initialization, a sufficiently small teacher update and imitation update are generically aligned in parameter space.

### ICML 2025 / Nature 2026 — emergent misalignment

Narrow insecure-code fine-tuning can cause broad unrelated misalignment.

### ICLR 2026 — broad vs narrow solution

**Emergent Misalignment is Easy, Narrow Misalignment is Hard** directly studies why a broad general solution may be more stable / efficient than a narrow one.

### ACL 2026 — feature-superposition geometry

**Understanding Emergent Misalignment via Feature Superposition Geometry** gives a gradient-level geometric account in which updating a target feature can strengthen nearby harmful features because representations overlap under superposition.

## Why no project survives

The broad question remains scientifically important, but the obvious project identities are occupied:

- semantic versus non-semantic transfer;
- gradient similarity / task affinity;
- local kernel influence;
- subliminal same-initialization transfer;
- narrow-to-broad emergent misalignment;
- feature-superposition spillover.

Renaming the residual `generalization radius`, `update scope`, or `semantic spillover` does not create a new parent.

**Decision:** keep `What does an example actually teach?` as a **WATCH standing friction**, but suppress candidate generation until a genuinely new natural quantity or failed prediction appears. NO L42.

---

# 6. WALL — How little grounding is enough to fix meaning?

This WALL deliberately moved into language science after several model-optimization walls.

## 10-second question

> **How little contact with the world is enough to give an otherwise text-trained language system stable meaning/reference?**

## Pressure

> Pure text can reveal rich relational structure while leaving reference underdetermined; if a handful of grounded anchors can orient the whole structure, the usual `text-only versus grounded` binary is scientifically too coarse.

## Old ancestry

- symbol grounding (Harnad);
- indeterminacy of reference / translation (Quine);
- distributional semantics;
- Bender & Koller’s 2020 Octopus argument;
- later rebuttals arguing that higher-order linguistic statistics may carry substantial referential information.

## Direct 2026 quantity owner

Louwerse (Psychonomic Bulletin & Review, published 2026-08-31), **Minimal symbol grounding through language statistics: An information theoretic approach quantifying uncertainty**, explicitly asks how much uncertainty about meaning is reduced by language-internal statistics, direct grounding, and their combination.

The paper operationalizes this with conditional entropy and tests how a small number of grounded seed words propagates through embedding structure, using valence as a tractable semantic dimension.

## Why no project survives

The attractive residual is obvious:

> extend beyond valence / use LLMs / use a synthetic world / test richer reference.

But that is precisely:

> direct strong paper -> stated limitation -> larger modern setting.

It violates the generator discipline even if the larger experiment would be technically clean.

**Decision:** mother problem remains important; current paper surface CLOSED. No L42.

---

# 7. Round-level searcher update

This round strengthens four rules.

## R1 — Every round must begin with fresh top-paper taste calibration

Do not assume yesterday’s searcher remains calibrated. Before generating candidates, re-read a small but serious set of Best / Outstanding / Runner-up / TACL work and reconstruct idea provenance.

## R2 — Strong mother question != available paper

Scaling laws, predictive world state, process supervision, update scope, and symbol grounding are all excellent questions. Several are currently poor project generators because modern theory already occupies their explanatory axes.

## R3 — Prefer a new scientific quantity over a new residual cell

When a field is stuck because the observable is too coarse, a new quantity may create a paper. When the field already has the right quantity and multiple active explanations, another factorial is usually not enough.

## R4 — An owner can close a wall without owning the exact experiment

The relevant test is whether the modern literature already constitutes a continuous theory/explanation program around the mother uncertainty. If yes, do not shrink until an untested cell appears.

---

# 8. Portfolio consequence

**New L-series:** 0.  
**New pilot authorization:** 0.  
**L42:** NOT CREATED.  
**Existing L40 / L41 authorizations:** unchanged.  

Standing-state updates:

1. **Origin of neural scaling laws** — high-value standing problem; suppress generation under current dense theory program.
2. **What does an example actually teach / what determines update scope?** — WATCH only; generic gradient / semantic-spillover formulations suppressed.
3. **Process-supervision audits** — distinguish task information, optimization/shaping, and objective change.
4. **Grounding** — the binary `text-only vs grounded` is scientifically too coarse, but the minimal-grounding quantity now has a direct 2026 owner; do not limitation-follow-up.

This is a healthy zero-survivor round because each WALL was entered from an independently important question and closed at the **mother-program** level, not because a list of small gaps was owner-killed.
