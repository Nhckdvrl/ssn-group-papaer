# Answer-Ownership Re-Audit — 2026-09-15

Target: ACL / EMNLP / NAACL Main.

Purpose: correct a failure mode exposed by L37. Novelty must be checked against the **strongest successful paper conclusion**, not only against our terminology, exact experiment, or method combination.

## Decision summary

| candidate | decision | reason |
|---|---|---|
| **L33 — Where Does Agreement Go Wrong?** | **KEEP — PILOT-AUTHORIZED E01 ONLY** | The state-distortion vs access/retrieval distinction is deliberately inherited from mature human psycholinguistics. That is acceptable and useful: the modern contribution is to make the old distinction causally identifiable inside a decoder-only Transformer and test where attraction enters model computation. No direct LM owner was found that performs the same state-vs-late-access causal decomposition on attraction errors. |
| **L37 — Semantic Label Boundary** | **ARCHIVED / NO-GO; authorization revoked** | Missed direct answer owner. Halawi et al. (ICLR 2024) already show truthful/intermediate computation followed by late override under false/permuted demonstrations and analyze semantically meaningful vs opaque labels; Tao et al. (EMNLP Findings 2024) already own the inference→verbalization causal factorization/interchange tool. The strongest L37 result compresses to their combination. |
| **L40 — Unit of Learned Attention** | **ARCHIVED / NO-GO current identity; authorization revoked** | The core scientific distinction is already substantially owned: classic associative-learning work establishes outcome-specific learned predictiveness, and recent SLA work directly contrasts wholesale morphological transfer with feature-by-feature transfer. L40's randomized-history + matched-current-state design is cleaner identification, but cleaner identification alone is insufficient independent Main-level novelty. |

## L33 clarification — why human ownership does not kill it

L33 is intentionally a **classic-problem modernization**.

Human psycholinguistics has long debated whether agreement attraction reflects:

- distortion/corruption of the number representation; or
- retrieval/access interference at agreement computation.

Recent human work continues to argue for distortion and hybrid accounts. This is not treated as a novelty defect. The reason L33 can remain alive is that decoder-only Transformers expose a new causal object:

> whether distractor influence is already integrated into the derived pre-verb state, or enters freshly through later causal access to the distractor.

The E01 operation attempts to separate these channels with `STATE-CLEAN`, `ACCESS-CLEAN`, and `BOTH-CLEAN` interventions under causal masking.

The Main-level burden remains high: a result should explain model computation and ideally a construction boundary, not merely report that Transformers resemble one side of an old human debate. But the human theoretical lineage is a **source of scientific pressure**, not a direct collision.

## L37 revocation

The failed novelty audit searched too much under our own labels:

- semantic labels;
- inference vs verbalization;
- task vectors;
- semantic anchors.

It failed to search the answer under alternative terminology:

- false demonstrations;
- permuted labels;
- truthful intermediate prediction;
- late override;
- false induction;
- context following versus parametric truth.

Under that vocabulary, the direct owner is obvious.

**Lesson:** exact-setting novelty is insufficient. Search the strongest conclusion in multiple vocabularies.

## L40 revocation

The old defense was that L40 randomizes linguistic history, forces current-state equivalence, and applies the same future update. Those are strong controls, but they do not change the fact that the main answer space is already familiar:

> cue-global associability / wholesale transfer

versus

> outcome- or feature-specific associability / transfer.

A possible new question remains:

> after observational convergence, can different histories remain distinguishable only through future learning?

That is broader latent path dependence and requires a new candidate identity. It is not an authorized L40 rescue.

## Workflow correction

Before any future `PILOT-AUTHORIZED` decision, write the strongest plausible abstract-level conclusion first and perform **answer-ownership search** using multiple vocabularies.

Minimum search object:

> `If the cleanest possible result occurs, what is the one sentence readers would remember?`

Then search for papers that already establish that sentence even if they:

- use different terminology;
- use humans rather than LMs;
- use a different intervention;
- use a broader or neighboring setting;
- predate the current fashionable framing.

A new experiment cell, cleaner causal design, or combination of two existing literatures is not sufficient by itself.

## Canonical status after this audit

```yaml
L33: PILOT_AUTHORIZED_E01_ONLY
L37: ARCHIVED_NO_GO_ANSWER_OWNERSHIP_COLLISION
L40: ARCHIVED_NO_GO_CURRENT_IDENTITY_INSUFFICIENT_ANSWER_NOVELTY
```
