# L34 — Does Future Access Shape What Gets Learned?

**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** **PILOT-AUTHORIZED — E01 ONLY**

## 1. Research question

> **Does knowing *how a fact will later be accessed* selectively change how a language model encodes that fact when it is subsequently learned?**

This is not a new knowledge-injection method paper. The scientific question is whether parametric knowledge acquisition is prospectively shaped by an already learned access policy, rather than being a neutral encoding process followed by a separately learned retrieval policy.

## 2. Mother phenomenon and pressure

Jiang et al. (ACL 2024), *Instruction-tuned Language Models are Better Knowledge Learners*, showed that teaching QA access patterns **before** continued pre-training on new documents (pre-instruction-tuning, PIT) substantially improves later closed-book QA. On Llama-2 7B, PIT improves over standard instruction tuning by roughly 17.8 absolute points in the reported setup.

Crucially, the paper explicitly motivates PIT by hypothesizing that prior QA training makes subsequent document encoding take into account **how the knowledge will later be accessed**. The published evidence establishes that moving instruction tuning earlier helps knowledge acquisition, but it does not identify whether the gain is truly query-conditioned prospective encoding rather than generic learning plasticity or a retrieval-policy effect.

Primary owner:
- Jiang et al. 2024, ACL Long: https://aclanthology.org/2024.acl-long.296/

Relevant successors improve knowledge acquisition but do not currently appear to identify the selective prospective-encoding claim:
- Zhang et al. 2025, *Self-Tuning: Instructing LLMs to Effectively Acquire New Knowledge through Self-Teaching*.
- Clinical / domain PIT descendants and 2026 document-internalization work use PIT as a method/baseline rather than testing access-selective encoding.

## 3. Scientific accounts

### A — Prospective encoding

An access policy learned *before* a fact is encountered changes how that later fact is encoded. Pre-access A versus B should therefore produce an **A↔B crossover specifically for knowledge learned after the pre-access phase**.

### B — Generic learnability / plasticity

PIT makes the model a better learner in a general sense. New knowledge may improve overall, but A versus B pre-access should not selectively favor the matching query view.

### C — Retrieval-policy specialization

PIT mainly teaches the model how to answer A-like versus B-like questions. The A↔B preference should therefore appear for knowledge the model already knew before PIT as well as for knowledge learned afterward.

Hybrid outcomes are allowed only as mixtures of these predeclared accounts; a failed result must not be rescued by inventing a new paper identity.

## 4. Decisive estimand

E01 uses a factorial design:

- **pre-access arm:** A vs B;
- **query view at evaluation:** A vs B;
- **knowledge age:** NEW (learned only after the pre-access phase) vs OLD (already known before pre-access).

The target documents and target new facts are **identical** across A/B arms. The pre-access phase must not contain those new facts.

Define the A-vs-B query-view preference within each pre-access arm, then the crossover between arms:

`CROSSOVER(age) = [Atrain(Aview-Bview) - Btrain(Aview-Bview)]_age`

Primary estimand:

> **`PROSPECTIVE = CROSSOVER(NEW) - CROSSOVER(OLD)`**

Predictions:

- Account A: `PROSPECTIVE > 0`; selective crossover is materially stronger for NEW knowledge.
- Account B: little/no crossover; possible overall NEW-knowledge gain.
- Account C: A/B crossover is similar for OLD and NEW, so `PROSPECTIVE ≈ 0` despite view specialization.

The OLD condition is load-bearing: without it, access specialization at retrieval is confounded with prospective encoding.

## 5. Identification controls

E01 must satisfy all of the following:

1. A/B pre-access arms have matched training size, answer distribution, and optimization budget.
2. Target new facts/documents are unseen during pre-access training and identical across arms.
3. A/B evaluation views express the same underlying facts and are counterbalanced for lexical/template identity.
4. Include held-out paraphrases so a crossover cannot be explained solely by memorizing one prompt string.
5. OLD and NEW facts use the same A/B evaluation machinery.
6. No post-document instruction tuning is allowed before the primary evaluation; otherwise encoding and retrieval are re-confounded.
7. Report both accuracy and answer-margin/log-probability measures; extraction rules are fixed before confirmatory evaluation.

## 6. Ownership / reviewer compression

Strongest compression:

> `ACL 2024 PIT + encoding-specificity intuition + later knowledge-acquisition methods = L34.`

What survives:

> Prior work shows that pre-instruction can improve later knowledge acquisition, but does **not** establish that a learned future access structure selectively changes the encoding of subsequently encountered facts, nor separate that claim from generic plasticity and retrieval-policy specialization.

Current novelty judgment: **PLAUSIBLE INDEPENDENT CONTRIBUTION**.

Repository anti-resurrection search on 2026-09-13 found no existing `pre-instruction` / prospective-encoding candidate. L34 is not a generic `capability vs readout` route: the decisive quantity is a **time-directed three-way interaction** that asks whether an access policy present *before learning* selectively changes later acquisition, with OLD knowledge explicitly subtracting retrieval-only specialization.

## 7. Successful-result chain

Strong positive result:

> matched pre-access A/B training → selective A↔B crossover only (or materially more strongly) for subsequently learned NEW facts → access policy before exposure changed what became easiest to retrieve from identical later documents → parametric knowledge acquisition is prospectively conditioned by anticipated use rather than fully neutral storage followed by retrieval.

This would directly strengthen / revise the interpretation of PIT and change how we conceptualize continued learning: **what a model expects to do with future knowledge can shape how that knowledge is learned.**

A generic PIT gain without the NEW-specific crossover does **not** support this claim.

## 8. Pre-result outcome interpretations

- **NEW-specific crossover, OLD small:** supports prospective encoding (A).
- **Comparable OLD and NEW crossover:** supports retrieval-policy specialization (C), and rejects the strong prospective-encoding interpretation.
- **Overall NEW improvement but little A/B crossover:** supports generic learnability/plasticity (B), and rejects the selective prospective-encoding interpretation.
- **No reproducible PIT/new-knowledge benefit in the instrument:** E01 fails the mother/instrument gate; STOP. Do not model-shop.
- **Only one wording/template produces crossover:** construct failure; STOP rather than prompt-search.

A null is allowed to kill L34. No post-hoc conversion to a generic knowledge-injection method paper.

## 9. Resolution / feasibility

The parent effect is large (roughly +17.8 absolute QA points in the reported Llama-2 7B comparison), so a bounded reproduction/instrument audit is feasible before any broad scale-up.

E01 should use one open base model family and a development/confirmation split. The first goal is **not** model-zoo breadth; it is to establish that the A/B access manipulation itself has enough first-stage leverage while preserving the parent PIT phenomenon.

Recommended bounded E01 structure:

- same starting checkpoint for all arms;
- A-pre-access and B-pre-access arms, plus a neutral/no-pre-access baseline only if needed to verify the mother PIT effect;
- multiple seeds for the two causal arms;
- hundreds of independent NEW and OLD facts, with A/B paired evaluation per fact;
- bootstrap over facts and seed-level replication;
- preregister a minimum meaningful NEW-specific crossover before confirmatory runs.

Do not authorize full model-family breadth until the first-stage selective crossover is resolvable.

## 10. Main-level growth path

If E01 passes, the same scientific identity can grow naturally:

- **C1 — identification:** show the NEW-specific A↔B crossover and distinguish A/B/C accounts.
- **C2 — formation:** locate *when during identical document training* the selective advantage emerges and whether it tracks selective parameter/representation updates, without replacing C1 with generic probing.
- **C3 — boundary / consequence:** test whether prospective encoding is specific to factual access or generalizes to different forms of later use, and whether mismatched anticipated access creates predictable blind spots despite equal document exposure.

C2/C3 deepen the same claim; they are not required to rescue a weak E01.

## 11. Exact authorization

**Authorized:** one bounded E01 whose only purpose is to test the predeclared `pre-access × query-view × NEW-vs-OLD` interaction and verify the mother PIT effect has sufficient leverage.

**Not authorized:** large model zoo, broad domain sweeps, RAG comparisons, synthetic-data method optimization, knowledge benchmark construction, mechanistic probing atlases, or a generic PIT-improvement paper.

**Promotion beyond E01 requires:** a reproducible and selective NEW-specific crossover that survives matched OLD-knowledge, paraphrase/template, and seed controls.