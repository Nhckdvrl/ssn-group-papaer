# Current Research-Question Search — 2026-09-06 Terminal Audit

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 1 — L02  
**Live leads remaining from L01/L02/L05:** 0

> This document records the terminal deep audit of L01, L02, and L05.
>
> Result: **L01 KILL · L02 PROMOTE TO `good/` FOR MINIMUM DECISIVE PILOT · L05 KILL**

---

# L01 — Comparison-Class Inference for Gradable Meaning

## Final verdict

# **KILL CURRENT FORM**

**Primary failure:** `NOVELTY_PARENT_COLLISION`  
**Secondary:** `CROWDED_PARENT`

## Why it was genuinely attractive

Plain-language question:

> When someone says an object is “tall”, “warm”, or “expensive” without saying what it is being compared against, does a model merely use stored category statistics, or infer the comparison class the speaker must have intended?

This is natural, easy to explain, and has unusually strong pre-existing human materials.

Tessler & Goodman (2022), *Warm (for Winter): Inferring Comparison Classes in Communication*, provide:
- a large-scale preregistered human experiment;
- open data/materials;
- a pragmatic speaker-reasoning account;
- a literal Bayesian account;
- qualitative predictions that diverge in direction.

So REAL OBJECT and GOOD DATA were strong.

## Why it nevertheless dies

The project's novelty rule is parent-level:

> **Changing the population from humans to LLMs does not itself create a new parent scientific question.**

Tessler & Goodman already own the central parent:

> how a listener recovers an implicit comparison class from a vague gradable expression and world knowledge.

The obvious LLM bridge is also no longer empty. Lipkin et al. (2023), *Evaluating statistical language models as pragmatic reasoners*, directly evaluate LLM threshold interpretation for gradable adjectives and include an explicit **Comparison Classes** experiment such as “strong for a novice player.”

More recent work further crowds the scalar-adjective neighborhood, including:
- SIGA (LREC-COLING 2024);
- MASP (CCL 2025);
- CrosSing (SCiL 2026), which compares LLM and human scalar-adjective reasoning and studies overinformative contexts.

The remaining distinction—

> **using an explicitly supplied comparison class vs reconstructing an implicit one**

—is real and interesting, but under aggressive reviewer compression the proposed paper becomes:

> **“Tessler & Goodman 2022 run on LLMs, with Lipkin 2023 as the explicit-context control.”**

That is not a sufficiently secure NEW PARENT for this project.

## Why a strong result would not rescue it

Even if models show a striking literal/pragmatic split, the decisive theoretical alternatives and experimental contrast come from prior human work.

More models, causal probing, hidden-state analysis, multilingual expansion, or a cleaner explicit-vs-implicit control would deepen the evidence but would not change ownership of the parent question.

## Reopen only if

A future formulation discovers a broader structural law about **context reconstruction vs context use** that:
1. is independently motivated beyond gradable adjectives;
2. makes common predictions across multiple natural NLP objects; and
3. cannot be reviewer-compressed to a model replication of Tessler & Goodman.

---

# L02 — Semantic Role Completion vs Referential Commitment

## Final verdict

# **PROMOTE TO `good/` — MINIMUM DECISIVE PILOT AUTHORIZED**

See: `good/L02_REFERENTIAL_COMMITMENT.md`

## Plain-language question

> When language leaves something unstated, how can a generative model know whether there is a specific missing entity to recover at all?

The core distinction can be explained without linguistic terminology:

- “The court convicted him, but the charges were later dropped.” A missing participant may refer to a particular entity recoverable from discourse.
- “She already ate.” We understand an eating event involves something ingestible, but the sentence need not refer to any particular food item.

The scientific quantity is therefore not merely:

> “Can the model guess a missing argument?”

It is:

> **Does semantic role completion license referential commitment?**

## Why the old literature does not kill it

The classic literature already knew this distinction. FrameNet distinguishes:
- **DNI:** a missing role has a specific contextually recoverable referent;
- **INI:** the role is semantically understood but no particular referent is recoverable.

SemEval-2010 Task 10 operationalized the distinction explicitly:
1. find a null instantiation;
2. decide whether it is definite;
3. **only if definite**, locate its filler.

That fact would kill a naive paper titled:

> “Can LLMs distinguish DNI from INI?”

But modern generative argument extraction changes a load-bearing modeling assumption.

Recent work such as:
- ACL 2024 *Explicating the Implicit*;
- EMNLP 2024 *Explicit, Implicit, and Scattered*;
- EMNLP Findings 2025 *REGen*

moves argument extraction toward document-level inference and free-form generation, with “implicit” commonly defined as **unstated but inferable**.

The new question is therefore an **Old Problem / New Method** question:

> **Did free-form generative extraction make an old explicit distinction between “role exists” and “specific referent exists” load-bearing again?**

No direct 2024–2026 collision was found that makes referential status / non-specific omission the central evaluation axis for generative LLM argument extraction.

## Data/gold audit

This survives GOOD DATA without synthetic worlds.

### Primary classic substrate: SemEval-2010 Task 10

Published statistics:
- train: 438 sentences, 303 DNIs, 277 INIs;
- test: 525 sentences, 349 DNIs, 361 INIs;
- linked/resolved DNI annotations are provided for a large subset.

The task data are running text and were released with gold semantic argument and null-instantiation linking information.

### Scale/replication substrate: FrameNet

FrameNet contains approximately **55,700 null-instantiation labels**, distinguishing constructional and lexically licensed omissions, including DNI/INI.

Thus the decisive labels predate our hypothesis and do not rely on an LLM judge or author-created synthetic gold.

## Competing accounts

### Account A — End-to-end generative completion

> A sufficiently capable generative model can jointly infer whether an omitted role has a concrete referent and recover it when appropriate; the old detect-definiteness-then-resolve factorization is no longer necessary.

Prediction:
- strong separation of DNI and INI;
- specific fillers for DNI;
- abstention / non-specific output for INI;
- little benefit from explicit typed factorization.

### Account B — Referential overcommitment

> Free-form generation makes role plausibility leak into entity commitment: once a role is semantically expected, the model tends to produce a plausible concrete filler even when no particular referent is licensed.

Prediction:
- plausible but unsupported fillers on INI;
- models may know the role/type while still overcommitting to an entity;
- explicit status prediction or typed output materially improves correctness.

Both outcomes change how generative implicit-argument modeling should be structured.

## Why this is not phenomenon gambling

If Account B wins:
> modern generative extraction has reintroduced a semantic error that classical pipelines explicitly avoided.

If Account A wins:
> modern LLM generation has made the classical DNI/INI→resolution factorization empirically unnecessary for this task.

If behavior is heterogeneous:
> we get a principled boundary specifying which predicates/frames/contexts require explicit referential-status modeling.

So the paper does not require one quirky failure to exist.

## Main-level claim architecture if pilot survives

**C1 — Referential commitment is a distinct step from semantic role completion.**  
Measure whether modern generative models preserve or collapse this boundary.

**C2 — Identify the boundary / computation.**  
Separate role/type knowledge from specific-entity commitment and test whether explicit typed factorization changes behavior.

**C3 — Consequence for task definition/evaluation.**  
Show whether generative implicit-argument systems should use an output space that distinguishes:
1. overt/span argument;
2. recoverable omitted referent;
3. non-specific omitted role.

The strongest possible paper is not “a DNI/INI benchmark.” It is:

> **Generative extraction needs to know when not to invent an entity.**

---

# L05 — Rational Redundancy in Referring Expressions

## Final verdict

# **KILL**

**Primary failure:** `NOVELTY_PARENT_COLLISION`

## Why it looked excellent

Plain-language question:

> If “the cup” already uniquely identifies an object, can saying “the blue cup” still be rational because the extra color helps the listener find it faster?

Human psycholinguistic work gives:
- natural visual-search tasks;
- human behavioral data;
- competing efficiency accounts;
- open materials.

So REAL OBJECT, GOOD DATA, and explainability were excellent.

## Exact collision

Unfortunately the parent is now directly occupied.

Muchovej, Rubio-Fernández & Jara-Ettinger (2026), *Theory of Mind Beyond Beliefs: Testing Attention-Based Social Micro-Processes in LLMs*, asks essentially the exact question:
- humans add redundant color adjectives when they help listener visual search;
- usefulness is manipulated through set size / color distribution;
- VLMs are tested on whether they adopt the same attention-guiding strategy.

The paper finds VLMs can generate successful references but lack the human attention-guiding strategy.

A second close collision is Ma et al. (COLM 2025), *Vision-Language Models Are Not Pragmatically Competent in Referring Expression Generation*, which directly evaluates pragmatic failures and excessive/irrelevant information in VLM referring-expression generation.

## Reviewer compression

> **“This is Muchovej et al. 2026 with another VLM/dataset, inside the REG pragmatic-competence program already established by Ma et al. 2025.”**

No amount of model scaling, cleaner human stimuli, additional modalities, or causal probing restores parent novelty.

---

# Final ranking after deep audit

| lead | REAL OBJECT | NEW AXIS | GOOD DATA | NEW PARENT | DECISIVE PAPER | final |
|---|---|---|---|---|---|---|
| **L02 Referential Commitment** | YES | YES — old distinction becomes load-bearing under generation | YES | **YES, provisional but survived direct search** | YES | **PROMOTE / PILOT** |
| L01 Comparison-Class Inference | YES | YES | YES | **NO** | plausible | **KILL** |
| L05 Rational Redundancy | YES | YES | YES | **NO — direct 2026 collision** | — | **KILL** |

---

# Search state after this audit

There is currently:

- **1 pilot-authorized candidate:** L02;
- **0 approved paper mainlines;**
- L01 and L05 are archived and must not be revived merely with new models/data.

The next work on L02, if undertaken later, should be a **minimum decisive pilot**, not more topic search hidden inside the experiment.
