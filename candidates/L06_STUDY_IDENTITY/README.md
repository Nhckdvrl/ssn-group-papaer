# L06 — Study Identity Is Not Document Identity

**Status:** SERIOUS CANDIDATE / PILOT-READY  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-08

> **Plain-language thesis:** A clinical study may produce several papers. An evidence-synthesis system must combine those papers as one study without accidentally turning multiple reports into multiple independent pieces of evidence.

---

## 1. One-sentence research question

> When an LLM receives the same natural collection of trial papers, is **explicit study identity** still necessary for correct evidence synthesis, or can end-to-end generation recover which papers belong to the same underlying study well enough that oracle grouping can be removed?

Even more plainly:

> **Do we still need to tell an LLM which papers came from the same study?**

This is not a paper-linkage benchmark. The scientific question is whether **study identity is a load-bearing evidence representation** once modern models can read and synthesize multiple full papers directly.

## 2. Natural object

The real-world object is independently defined by evidence synthesis:

- **paper/report** = a publication;
- **study/trial** = the underlying experiment or investigation;
- one study may have multiple reports describing different outcomes, follow-up times, analyses, or subsets.

Cochrane explicitly warns that multiple reports from the same study can create substantial bias if inadvertently included more than once in a meta-analysis.

The distinction therefore predates our system and is not an author-invented label.

## 3. Why ACL / NLP cares

Modern scientific IE and evidence-synthesis systems increasingly consume papers directly. This creates a new modeling choice:

### Traditional pipeline
papers → explicit study linkage → study-level extraction → synthesis

### LLM-era possibility
all papers → long-context / retrieval-conditioned generation → synthesis

The unresolved question is whether the old explicit intermediate unit can safely disappear.

If the answer is YES:
- publication-linkage infrastructure may be unnecessary for some end-to-end synthesis regimes;
- the LLM can reconstruct the true evidence unit implicitly.

If the answer is NO:
- document-level generation is structurally unsafe even when individual paper extraction is correct;
- evidence synthesis must retain or recover explicit study membership before counting/combining evidence.

## 4. Competing accounts

### Account A — Oracle study identity is dispensable

The papers themselves contain enough shared information—trial identifiers, authors, sample sizes, sites, intervention details, recruitment periods—that a strong model can implicitly avoid double-counting.

Prediction:
- flat/no-grouping ≈ oracle grouping on study-level and synthesis-level conclusions;
- predicted grouping may match oracle grouping closely enough for practical use.

### Account B — Study identity is load-bearing

Even strong models treat separate reports as separate evidence units unless grouping is made explicit.

Prediction:
- extraction from each paper can remain accurate while synthesis becomes wrong;
- wrong splits inflate evidence count/weight;
- wrong merges erase genuinely independent evidence.

### Account C — Conditional necessity

Explicit identity matters only when:
- one study has multiple reports;
- reports emphasize different outcomes/time points;
- trial identifiers are absent or inconsistent;
- papers are lexically dissimilar;
- a review contains both overlapping and independent studies.

This yields a decision map rather than a single failure rate.

## 5. Outcome robustness

This topic does **not** depend on finding double-counting failures.

If flat ≈ oracle:
> modern LLM synthesis can reconstruct study identity implicitly under specified conditions, making an old pipeline state largely dispensable.

If oracle > flat:
> study identity remains a necessary evidence representation even for end-to-end generative synthesis.

If errors are conditional:
> the paper identifies when study linkage can be safely omitted and when it cannot.

If predicted grouping closes the gap:
> the consequence is a modular design rule: study linkage is necessary as a quantity but need not be oracle-provided.

## 6. Paper identity

**Primary identity:** evidence-unit representation / classic modeling-decision necessity in automated scientific synthesis.

**Not the identity:**
- a publication-linkage benchmark;
- duplicate detection;
- another CochraneForest model;
- another retrieval/clustering method;
- “study ≠ paper” as a new observation.

## 7. Planned C1 → C2 → C3

### C1 — Necessity
On the **same exact papers**, compare oracle study identity against no identity.

### C2 — Attribution and boundaries
Intervene on study membership:
- correct oracle grouping;
- flat/no grouping;
- predicted grouping;
- controlled wrong split;
- controlled wrong merge;
- partial/incomplete grouping.

Ask whether grouping errors affect:
1. paper-level extraction;
2. study-level inference;
3. final evidence-synthesis conclusion.

### C3 — Consequence
Determine whether automated evidence synthesis should:
- keep study identity as an explicit intermediate representation;
- infer it automatically before synthesis;
- or omit it in validated regimes.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Evidence synthesis is defined over studies, while studies can have multiple reports. |
| SCIENTIFIC TENSION | **YES** | Modern LLMs may reconstruct study identity implicitly; explicit grouping may still be necessary. |
| GOOD DATA | **YES** | CochraneForest directly provides study↔paper membership and study-level conclusions/evidence. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | CochraneForest assumes study identity; it does not test its necessity under matched paper sets. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Dispensable, necessary, and conditional outcomes all change system design. |

## 9. Main danger

Reviewer compression:

> **“This is just a CochraneForest grouping ablation.”**

That attack wins if the paper only toggles a grouping flag and reports F1.

It is false only if the paper establishes the broader evidence-unit conclusion by:
- holding papers fixed;
- causally manipulating study identity;
- separating extraction from evidence accounting;
- testing wrong split vs wrong merge;
- showing whether scientific synthesis conclusions are preserved.

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)

This is a serious candidate and currently looks pilot-ready, but it is not yet registered in `good/`.
