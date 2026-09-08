# Study Identity Is Not Document Identity

**Status:** SERIOUS CANDIDATE / PILOT-WORTHY  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-08

> **Plain-language thesis:** A clinical study can produce several papers. An evidence-synthesis system must combine those papers as one study without accidentally counting them as independent evidence.

---

## 1. One-sentence research question

> When an LLM receives the same natural set of papers for evidence synthesis, is **explicit study identity** still necessary to combine information correctly without increasing the effective evidence count, or can an end-to-end model infer and preserve the study unit implicitly?

A simpler version:

> **Do LLMs need to know which papers came from the same study?**

## 2. Natural object

A study is not a paper. One randomized trial may generate:
- a main results paper;
- a follow-up report;
- a subgroup analysis;
- a safety report;
- a longer-term outcome paper.

Systematic reviews explicitly group multiple reports that arise from the same study. Cochrane warns that counting duplicate reports as separate studies can bias meta-analysis.

This identity exists outside the NLP system and is not an author-invented latent label.

## 3. Why ACL / NLP cares

Scientific-document NLP increasingly moves from paper retrieval toward evidence synthesis. Current LLMs can jointly read many documents, creating a genuine modern question:

> If the model can see all papers and reason across them, can it reconstruct the evidence unit itself, or must the pipeline explicitly supply study membership?

This is a representation-necessity question for multi-document scientific NLP, not a publication-linkage benchmark.

## 4. Competing accounts

### Account A — End-to-end inference is sufficient

A strong LLM can infer that several reports describe the same underlying study and internally avoid double-counting them.

If this wins:
- explicit study-linkage modules may be unnecessary in well-specified synthesis settings;
- oracle study membership in current datasets is scaffolding rather than a load-bearing representation;
- end-to-end evidence synthesis becomes more plausible.

### Account B — Study identity is load-bearing

Even if the model extracts facts correctly from each paper, without explicit grouping it treats multiple reports as independent pieces of evidence or fails to merge complementary information.

If this wins:
- study identity must remain an explicit intermediate representation;
- publication-linkage errors propagate into synthesis even when document-level extraction is correct;
- paper-level RAG is an invalid abstraction for some evidence-synthesis tasks.

### Account C — Conditional necessity

Explicit identity matters only when:
- one study has multiple reports;
- reports contain complementary outcomes/time points;
- duplicate reports differ strongly in wording/authorship;
- the synthesis decision is sensitive to evidence multiplicity.

This yields a decision map rather than a one-effect story.

## 5. Outcome robustness

The paper survives all major outcomes:
- **flat ≈ oracle:** modern LLMs implicitly reconstruct study identity under tested conditions;
- **oracle > flat:** study identity is a necessary evidence representation;
- **predicted ≈ oracle:** automatic linkage is sufficient;
- **wrong split ≫ wrong merge or vice versa:** different identity errors have different scientific consequences;
- **heterogeneous:** identify when explicit grouping is necessary.

## 6. Paper identity

**Primary identity:** evidence-unit representation / necessity paper for multi-document scientific synthesis.

**Not the identity:**
- publication matching accuracy;
- duplicate-paper detection;
- another CochraneForest model;
- generic RAG over multiple documents;
- a clustering method.

## 7. Planned C1 → C2 → C3

### C1 — Core scientific answer
Hold the natural papers fixed and intervene only on study membership:
- oracle grouping;
- no grouping / flat papers;
- predicted grouping;
- controlled wrong split;
- controlled wrong merge.

Measure study-level inference and downstream synthesis.

### C2 — Mechanism / boundary
Separate two failure pathways:
1. **information merging failure** — complementary reports are not integrated;
2. **evidence-counting failure** — repeated reports are treated as independent votes.

Stratify by papers-per-study, report overlap, outcome complementarity, and textual similarity.

### C3 — Consequence
Determine whether scientific NLP pipelines should represent evidence as:
- papers;
- linked studies;
- or end-to-end document sets with inferred latent study structure.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Cochrane explicitly distinguishes studies from their multiple reports. |
| SCIENTIFIC TENSION | **YES** | Long-context LLMs may infer identity implicitly, but double-counting is a real risk. |
| GOOD DATA | **YES** | CochraneForest already supplies papers grouped by study plus study-level conclusions. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | CochraneForest assumes oracle study membership; its clustering is within-study passage clustering, not an intervention on study identity. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Oracle/flat/predicted/split/merge outcomes all answer the necessity question. |

## 9. Main danger

Reviewer compression:

> **“This is just a CochraneForest grouping ablation.”**

That compression wins if the paper only removes a grouping field and reports F1.

It loses only if we establish a general scientific chain:

> paper set → evidence-unit identity → information merging / evidence counting → study conclusion → synthesis conclusion.

## 10. Canonical sources

- Pronesti et al., ACL 2025, *Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies* / CochraneForest: https://aclanthology.org/2025.acl-long.1359/
- Cochrane Handbook, identifying multiple reports from the same study: https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04
- Tramèr et al., BMJ 1997, duplicate publication can bias meta-analysis: https://www.bmj.com/content/315/7109/635

## 11. Directory map

- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `PILOT_CARD.md`
