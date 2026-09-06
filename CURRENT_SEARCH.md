# Current Research-Question Search — 2026-09-06

**Target:** NAACL Main  
**Status:** active search  
**Approved mainline:** NONE  
**Pilot-authorized candidates in `good/`:** NONE  
**Current live leads:** 2

> This file stores promising leads **before** they pass all five hard gates.
>
> Do not confuse “survived an initial search pass” with “good candidate.”

---

# Search-direction update

The current search should move away from two bad extremes:

1. **mechanism-first / phenomenon hunting**, and
2. **overly specialized linguistic puzzles that require heavy formal background before the RQ is understandable.**

Preferred shape:

> **A familiar language/NLP object that a non-specialist can understand immediately, but with a genuinely non-obvious scientific axis inside it.**

Working slogan:

> **Easy to understand, hard to answer.**

Local Sasano-lab-adjacent examples remain useful as a search prior because they start from concrete objects such as factual/fictional reference, lexical explanation, document/citation structure, choice, and syntax-vs-semantic shortcuts. We should not copy those topics; we should copy the concreteness.

---

# Live Lead L01 — Comparison-Class Inference for Gradable Meaning

## Plain-language RQ

> When someone says an object is “tall”, “expensive”, or “fast”, does a language model interpret the word using a fixed category stereotype, or infer what comparison group the speaker must have had in mind?

Example intuition:

> “This is a tall 12-year-old” and “This is a tall basketball player” use the same adjective, but “tall” means different numerical regions because the relevant comparison class changes.

The question is understandable without formal semantics.

## Why it currently looks strong

### REAL OBJECT — likely YES

Context-sensitive adjective meaning and comparison classes are ordinary, persistent language phenomena.

### NEW AXIS — promising

Two pre-result accounts can make different predictions:

**Account A — prototype/category-threshold account**

> The model mainly anchors “tall/expensive/fast” to learned category-level distributions or prototypes.

**Account B — pragmatic speaker-inference account**

> The model uses the utterance and context to infer why the speaker chose that adjective, thereby reconstructing the intended comparison class/threshold.

The useful axis is not “does the model know that tall is context-sensitive?” but:

> **What determines the contextual standard: stored category statistics or speaker-conditioned inference?**

### GOOD DATA — promising

A published human line of work appears to provide reusable experimental materials, human judgments, and code rather than requiring us to invent a synthetic world. An earlier pass identified a 2022 human study with roughly 90 item sets and explicit competing accounts.

**Still required:** exact dataset/license/material retrieval and a clean mapping from human dependent variables to an LLM estimand.

### NEW PARENT — initial search survived, not yet cleared

Initial 2024–2026 searches did not reveal an obvious direct LLM paper owning the exact category-prototype-vs-speaker-inference parent.

**Still required:** aggressive searches across:
- gradable adjectives in LLMs;
- comparison-class inference;
- scalar semantics / adjective standards;
- pragmatic threshold inference;
- contextual adjective interpretation;
- computational psycholinguistics and multimodal grounding.

### DECISIVE PAPER — plausible

Possible claim architecture:

**C1:** characterize how model adjective standards shift across contexts.

**C2:** discriminate prototype/statistical anchoring from speaker-conditioned pragmatic inference using contexts where they predict differently.

**C3:** show the consequence for what counts as semantic competence / contextual meaning evaluation, potentially demonstrating that lexical knowledge alone is insufficient to explain successful interpretation.

## Main risk

This must not collapse to:

> “LLMs understand context-sensitive adjectives.”

That would be a competence benchmark.

## Current verdict

**STRONG LIVE LEAD — NOT YET IN `good/`.**

Promotion requires finishing the exact novelty and data audit.

---

# Live Lead L02 — Referential vs Non-Referential Missing Arguments

## Plain-language RQ

> When a sentence leaves an argument unstated, should a language model always try to recover a missing entity, or can it recognize that sometimes no specific missing entity is intended at all?

Simple intuition:

- “John arrived and ate.” Often we understand that John ate **something**, but the speaker may not have any particular thing in mind.
- In other cases, an omitted participant is recoverable from the discourse and really does refer back to a specific entity.

This is a natural issue for information extraction, semantic parsing, implicit arguments, and generation.

## The scientific axis

Traditional implicit-argument work distinguishes at least two importantly different cases:

- **definite/recoverable null instantiation (DNI-like):** a specific missing participant is recoverable from context;
- **indefinite/non-referential null instantiation (INI-like):** the role is semantically licensed but no specific discourse referent needs to be recovered.

The modern concern is that generative LLM-based extraction/recovery may implicitly turn both into:

> “find/generate the missing entity.”

That changes the measurement target.

## Why it currently looks promising

### REAL OBJECT — YES

Implicit arguments and omitted participants are real, established NLP/semantic-role phenomena with direct relevance to semantic parsing and information extraction.

### NEW AXIS — promising only under the rewritten identity

The weak question is already dead:

> “Can LLMs recover implicit arguments?”

That is not novel.

The stronger candidate is:

> **Does current generative recovery evaluation conflate two different semantic targets: recoverable reference vs licensed non-reference?**

Possible accounts:

**Account A — universal recovery account**

> Better semantic understanding should monotonically improve explicit entity recovery for omitted roles.

**Account B — typed-omission account**

> Correct semantic understanding sometimes requires **not** producing a concrete entity because the omission is non-referential/indefinite.

This creates a measurement-level tension rather than a textbook competence test.

### GOOD DATA — promising

Frame-semantic resources and implicit-argument corpora contain annotated null-instantiation distinctions, potentially giving independent gold without author-created worlds.

**Still required:** identify the cleanest downloadable resource, confirm annotation coverage/licensing, and quantify enough DNI-vs-INI examples for a decisive analysis.

### NEW PARENT — not yet cleared

Generic implicit argument recovery and LLM-based argument completion are already occupied.

The candidate survives only if the parent is specifically:

> **evaluation/representation should distinguish recoverable missing entities from non-referential omissions.**

Need exact collision search on:
- null instantiation + language models;
- DNI / INI computational modeling;
- implicit argument evaluation;
- generative semantic role labeling;
- hallucinated arguments / over-explicitation.

### DECISIVE PAPER — plausible

**C1:** show whether current generative models systematically over-recover concrete entities in non-referential omission cases, or whether existing metrics reward such behavior.

**C2:** establish the DNI-vs-INI boundary and separate genuine reference recovery from generic role completion.

**C3:** propose/evaluate a typed evaluation unit or output space that changes conclusions about implicit-argument competence.

## Main risk

The topic becomes too linguistic if framed around terminology.

The paper must use the plain-language object:

> **Sometimes missing words refer to a specific omitted thing; sometimes they do not. Should our models and metrics treat these as the same task?**

## Current verdict

**STRONG LIVE LEAD — NOT YET IN `good/`.**

Promotion requires a resource audit and a direct novelty assassination focused on the evaluation rewrite.

---

# Newly killed routes in this search pass

The following were attractive because they have real linguistic objects, but were rejected before promotion:

1. **Generic coercion / compositional coercion in LLMs**
   - recent work already occupies broad model competence around coercion/composition;
   - remaining cells risk textbook-capability evaluation.

2. **Generic presupposition / presupposition projection**
   - LLM pragmatic/presupposition work is already substantial;
   - a new trigger or condition is unlikely to create a new parent.

3. **Generic continuous WSD / soft sense mixtures**
   - contextualized/polysemy/graded-sense representation is already heavily occupied;
   - “replace discrete senses with continuous representations” is not a fresh parent.

4. **Polysemy / copredication as dual-facet representation**
   - contextualized ambiguity, copredication acceptability, semantic-type detection, and recent copredication resources already crowd the parent;
   - “can the model represent both facets of book?” is too close to existing lexical-ambiguity work.

These are appended to `failed/KILLED_LEDGER.md`.

---

# Next search policy

Continue searching for five eventual `good/` candidates, but bias toward:

- reference and entity access;
- lexical/contextual meaning that is explainable with everyday examples;
- inference and missing information;
- discourse/document structure;
- evaluation units that conflate two naturally distinct targets;
- existing human/corpus/resource data with independent gold.

Avoid spending much search budget on deeply technical formal-linguistic puzzles unless the RQ can be explained in one paragraph to a non-specialist.

> **The desired topic should feel simple before it feels technical.**
