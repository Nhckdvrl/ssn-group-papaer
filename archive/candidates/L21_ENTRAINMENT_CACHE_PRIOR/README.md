# L21 — When Is Contextual Entrainment Rational?

**Status:** **SERIOUS / PRE-PILOT — IDENTIFICATION BLOCKER — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **Is contextual entrainment a learned online-cache prior calibrated to real lexical self-recurrence, or an overgeneralized / distribution-insensitive copying bias?**

The question remains scientifically interesting because contextual entrainment is replicated across multiple papers/models, natural language has classic self-trigger/cache structure, and Pythia provides public training data/order/checkpoints.

However, the previous E01 authorization was too early.

## Why pilot authorization is revoked

### 1. The comparator is not yet identified cleanly

The proposed corpus statistic

```text
R(w,d) = log P_train(w_t | earlier w in distance window d) - log P_train(w_t)
```

mixes lexical self-trigger with topic continuity, discourse/coreference, syntax and other semantic reasons that a word legitimately recurs.

The mother entrainment phenomenon is especially striking in **irrelevant/random-token contexts**. Therefore it is not yet established that `R(w,d)` from natural discourse is the correct normative quantity against which random-context entrainment should be called calibrated or miscalibrated.

A correlation or mismatch between `R` and entrainment would be difficult to interpret causally without first closing this DGP mismatch.

### 2. Novelty is narrower after fresh audit

Guan & Huang (Findings ACL 2023), *Mitigating the Learning Bias towards Repetition by Self-Contrastive Training for Open-Ended Generation*, already studies systematic overestimation of token-level repetition probability and explains it as an MLE learning bias toward simple repetition patterns.

Additional neighboring ownership includes:
- Niu et al. 2025: contextual entrainment phenomenon and causal entrainment heads;
- Kukreja et al. 2026: semantic/non-semantic entrainment scaling;
- classic cache/self-trigger language models;
- burstiness / induction-head training-distribution work;
- NAACL 2025 *Language Models “Grok” to Copy*: training dynamics of copying skill.

The unowned cell is therefore specifically **training-distribution self-recurrence ↔ contextual-entrainment calibration**, not repetition bias or copy-skill emergence generally. That exact cell is not enough by itself if its comparator is not scientifically identified.

## What would reopen E01

Before any model run, one of the following must be secured:

1. **A clean conditional recurrence target** that matches the entrainment intervention while separating legitimate semantic/discourse recurrence from blind recent-token repetition; or
2. **A controlled natural/synthetic DGP** where self-recurrence can be manipulated independently of unigram frequency, local n-grams and semantic structure, together with a clear argument that the resulting estimand generalizes beyond another burstiness/induction experiment.

The solution cannot be an author-chosen statistic whose interpretation changes after results are seen.

## Identity fence

L21 is not:
- L18 / alias or semantic transfer;
- historical 014 reference-identity entrainment;
- sentence-level entrainment;
- another model-size scaling paper;
- another copying-emergence / induction-head paper;
- generic repetition-loop mitigation.

## Current verdict

```yaml
natural_question: PASS
replication_risk: LOW
exact_external_owner: NOT_FOUND
neighbor_density: HIGH
new_estimand: PLAUSIBLE_BUT_NOT_YET_IDENTIFIED
primary_blocker: CORPUS_RECURRENCE_IS_NOT_YET_A_CLEAN_NORMATIVE_TARGET_FOR_RANDOM_CONTEXT_ENTRAINMENT
pilot_cost: LOW
pilot: NOT_AUTHORIZED
verdict: SERIOUS_PRE_PILOT
```

Do not run E01 until the identification blocker is closed. Evidence from earlier entrainment work survives; pilot authorization does not.
