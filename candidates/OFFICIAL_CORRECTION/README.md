# Official Correction ≠ Current Scholarly Claim

**Status:** SERIOUS CANDIDATE / PILOT-WORTHY  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-08

> **Plain-language thesis:** When a journal officially corrects a published statement, the original and corrected statements are not two equally valid conflicting sources. The correction is an adjudicated update to the scholarly record.

---

## 1. One-sentence research question

> Can scientific NLP systems recover the **current scholarly proposition after an official correction**, or do they continue to mix, repeat, or prefer the superseded proposition from the original article?

Simpler version:

> **When a paper is officially corrected, does the model know which claim is current?**

## 2. Natural object

Published papers are not immutable. Journals issue corrections, corrigenda, errata, partial retractions, and corrected republications. These can replace:
- numbers;
- units;
- method descriptions;
- table values;
- qualifiers;
- entire sentences or conclusions.

NLM explicitly links erratum notices to the original article and treats corrections to text, tables, graphs, and statements as part of the scholarly record.

## 3. Why ACL / NLP cares

Scientific QA, paper summarization, retrieval, citation generation, evidence synthesis, and scholarly assistants increasingly read large document collections. These systems commonly treat documents as pieces of evidence and resolve conflicts by recency, source preference, or aggregation.

But an official correction has a different semantics:

`old proposition -> editorial correction operation -> current proposition`

It is not ordinary conflicting evidence.

The modern question is whether LLMs can infer this update relation from natural scholarly documents or whether scholarly NLP needs explicit update-state handling.

## 4. Competing accounts

### Account A — Document-conditioned LLMs recover supersession
Given the original article plus correction notice, strong models reliably return the corrected proposition and suppress the obsolete one.

Consequence: explicit correction-aware infrastructure may be unnecessary when the update relation is visible.

### Account B — Original-text dominance persists
Models retain or repeat the original proposition despite a formal correction, especially when the original article is longer, more salient, or more widely repeated.

Consequence: scientific NLP requires explicit scholarly-update representation and correction-aware retrieval/evaluation.

### Account C — Boundary by correction type
Models handle direct numeric replacements but fail on qualifiers, method changes, table corrections, or distributed edits.

Consequence: define when correction-aware structure is necessary.

## 5. Outcome robustness

The paper survives:
- corrected proposition reliably wins -> end-to-end scholarly update resolution is sufficient under specified conditions;
- original proposition persists -> explicit update state is load-bearing;
- heterogeneous -> correction-type decision map;
- retrieval correct but answer wrong -> reasoning/update failure;
- retrieval wrong -> source-selection failure.

## 6. Paper identity

**Primary identity:** scholarly-state / supersession paper for scientific NLP.

**Not the identity:**
- retraction detection;
- temporal QA;
- generic contradictory-document QA;
- correction-notice classification;
- another scientific fact extraction benchmark.

## 7. Planned C1 → C2 → C3

### C1 — Current proposition
Given original + official correction, recover the current claim/value/method statement.

### C2 — Why / when
Cross:
- exact `X should read Y` vs diffuse correction;
- numeric vs textual vs methodological corrections;
- original-only / correction-only / both;
- document order and length;
- explicit update relation vs unlabeled document pair;
- retrieval vs answer-generation errors.

### C3 — Consequence
Determine whether scientific NLP should represent:
- documents as flat evidence;
- versioned propositions;
- or explicit editorial update operations.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Publishers/NLM formally define corrections and link notices to original articles. |
| SCIENTIFIC TENSION | **YES** | Strong models may resolve updates from context, but original-document dominance is plausible. |
| GOOD DATA | **PROVISIONAL YES** | PMC/PubMed expose correction links; many notices contain exact old→new replacements. Exact semantic-yield audit is mandatory before promotion. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | Generic temporal conflict/retraction work does not own adjudicated proposition supersession with correction-level gold and task consequence. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Preservation, failure, and correction-type boundaries all change system-design conclusions. |

## 9. Main danger

Reviewer compression:

> **“This is just temporal conflict QA over errata.”**

That compression wins if the task is merely choosing the newer sentence.

It loses only if the paper demonstrates that **official correction is a distinct scholarly update operation**, with proposition-level gold and consequences for scientific QA/summarization/synthesis.

## 10. Canonical sources

- NLM policy on errata and linked citations: https://www.nlm.nih.gov/bsd/policy/errata.html
- PMC correction policies: https://pmc.ncbi.nlm.nih.gov/about/guidelines/

## 11. Directory map

- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `PILOT_CARD.md`
