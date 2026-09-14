# Search Kill Batch — K253

**Date:** 2026-09-14  
**Next kill ID after this file:** **K254**

---

## K253 — Privative adjective inference / adjective–noun ontological commitment

**Parent RQ:** Do LLMs compositionally understand that modifiers such as `fake`, `former`, `stone`, etc. can block ordinary noun entailments (e.g. `fake gun` does not entail `gun`), rather than applying generic intersective adjective–noun composition?

**Status:** **KILL / DO NOT REOPEN**

**Primary failure:** `NOVELTY_PARENT_COLLISION`

### Decisive ownership

This parent is directly occupied rather than merely adjacent:

- COLING 2022, **Testing Large Language Models on Compositionality and Inference with Phrase-Level Adjective-Noun Entailment**, explicitly includes intensional/privative adjectives such as `fake` and tests entailments such as `fake gun` not implying `gun` / `weapon`.
- Hayley Ross’s 2024–2025 research program and 2025 Harvard dissertation **Artificial intelligence and fake reefs: what privative inferences and LLMs tell us about adjective-noun composition** directly studies human and modern-LLM privative inferences, contextual sensitivity, generalization to novel adjective–noun pairs, and composition-vs-analogy explanations.
- *SEM 2026, **Evaluating Adjective-Noun Compositionality in LLMs: Functional vs Representational Perspectives**, continues the exact model-side compositionality program.

### Reviewer compression

Any proposal framed as:

- `fake N` vs `real N`;
- privative vs intersective/subsective modifiers;
- “recognition vs inference” for privative adjectives;
- novel adjective–noun pairs;
- context sensitivity;
- behavior vs representation / mechanism;

will be compressed into the existing adjective–noun compositionality / privative-inference program.

### Do-not-reopen boundary

Do **not** reopen by:

- swapping adjective sets;
- using newer instruction models;
- multilingualizing;
- adding chain-of-thought;
- replacing behavioral evaluation with representation probing, activation patching, SAE features, or causal mediation;
- claiming prior work studied familiar combinations while we study novel ones (novel combinations are already directly studied).

A future proposal must have a genuinely different scientific parent, not a new diagnostic for privative composition.
