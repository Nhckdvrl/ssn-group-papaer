# L07 — Official Correction ≠ Current Scholarly Claim

**Status:** SERIOUS CANDIDATE / PILOT-READY AFTER DATA-YIELD AUDIT  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-08

> **Plain-language thesis:** Once a paper is officially corrected, the original statement is part of the historical record but is no longer necessarily the current scholarly claim.

---

## 1. One-sentence research question

> Can an LLM reading an original paper together with its official correction reliably recover the **current scholarly proposition**, or does automated scientific QA/IE need an explicit update/supersession operation to avoid repeating the obsolete claim?

Plain version:

> **A paper says X. Its publisher later says “this should read Y instead.” Which claim will an NLP system actually treat as current?**

The key object is not recency and not two conflicting documents. It is an **editorially adjudicated update**.

## 2. Natural object

Scholarly publishing already defines correction operations:
- correction / corrigendum / erratum;
- partial retraction;
- corrected-and-republished article;
- clarification / addendum in some infrastructures.

NLM links original PubMed records to erratum notices. Crossref/Crossmark records editorially significant updates and distinguishes them from minor spelling/formatting changes.

Therefore:
> original proposition → official correction operation → corrected proposition

exists independently of this project.

## 3. Why ACL / NLP cares

Scientific QA, literature assistants, citation generation, evidence extraction, and scholarly search increasingly answer questions from published papers.

A common implicit assumption is:
> retrieve relevant documents → aggregate their content.

But an official correction is **not another independent evidence document**. It changes the status of content in the original paper.

This creates a real LLM-era modeling question:
- can end-to-end document reading correctly apply the update relation?
- or should scholarly NLP explicitly represent “superseded by / corrected to”?

## 4. Competing accounts

### Account A — Direct reading is sufficient

Given the original text and correction notice, a strong LLM treats the correction as authoritative and answers with the corrected proposition.

Implication:
- explicit scholarly-state tracking may be unnecessary when authoritative update notices are present.

### Account B — Corrections require explicit state

Models blend the original and correction, repeat the more salient original claim, or treat the two as ordinary conflicting evidence.

Implication:
- scientific QA/IE needs an explicit update graph or proposition-state representation.

### Account C — Conditional sufficiency

Direct generation succeeds for local numeric/text replacements but fails for:
- figures/tables;
- multi-sentence changes;
- qualifications;
- method changes;
- corrections that require linking multiple locations.

This yields a practical boundary map.

## 5. Outcome robustness

If models almost always recover Y:
> official correction notices are strong enough natural supervision for current-state scholarly QA, and explicit state tracking may be dispensable under documented conditions.

If they often return X or X+Y:
> retrieval over “all relevant documents” is a semantically invalid abstraction for corrected scholarship.

If only some correction types fail:
> task design should condition on update type/operation complexity.

No “surprising failure” is required.

## 6. Paper identity

**Primary identity:** scholarly-document state / version-aware scientific QA and IE.

**Not the identity:**
- generic temporal QA;
- retraction awareness;
- LLM self-correction;
- factual error correction;
- contradiction detection;
- another correction-notice dataset.

## 7. Planned C1 → C2 → C3

### C1 — Current proposition recovery
Original + official correction → recover corrected proposition and reject superseded proposition.

### C2 — Mechanism / boundary
Cross:
- correction type;
- locality;
- text vs table/figure;
- explicit “should read X instead of Y” vs diffuse notice;
- original-first vs correction-first;
- direct generation vs explicit update representation.

### C3 — Consequence
Decide whether scholarly QA/IE should:
- ingest all relevant documents flatly;
- explicitly apply correction relations;
- or rely on direct reading for simple update forms only.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Publishers/NLM/Crossref explicitly define corrections and link them to originals. |
| SCIENTIFIC TENSION | **YES** | End-to-end LLM reading may make explicit update state unnecessary—or not. |
| GOOD DATA | **PROMISING / audit required** | PMC contains publisher-authored old→new replacements; Crossref/NLM provide update links. Need exact yield. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | Nearby work studies self-correction, factual correction, and scientific critique, not official proposition supersession. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Success, failure, and correction-type boundaries all support a modeling conclusion. |

## 9. Main danger

Reviewer compression:

> **“This is just temporal QA over errata.”**

That wins if the task is only:
> read newest document and answer.

It is false only if the paper shows that official correction is a distinct **scholarly update operation**, with:
- externally linked original/update pairs;
- explicit old→new proposition gold;
- direct-vs-stateful comparison;
- consequences for scientific QA/IE.

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)

This candidate should not enter `good/` until the proposition-level correction yield is audited on a sufficiently large random sample.
