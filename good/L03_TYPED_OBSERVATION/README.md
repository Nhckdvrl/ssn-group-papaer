# L03 — Table Value ≠ Observation Status

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-08

> **Plain-language thesis:** A table cell without an ordinary number is not necessarily “missing.” It can itself encode an official observation state such as not applicable, unavailable, suppressed, or unreliable.

---

## 1. One-sentence research question

> In real statistical tables, can modern document-conditioned generative systems recover the **typed observation denoted by a cell**, including provider-defined non-value states, or does reliable understanding still require an explicit observation-status representation before value answering?

The key issue is not whether a model recognizes a Census code. The scientific issue is the **output ontology of table understanding**.

## 2. Natural object

Official statistical products have always distinguished:
- an observed scalar value;
- a true zero;
- a value that is not applicable or not available;
- a suppressed estimate;
- a statistically unreliable or otherwise qualified estimate.

These are not interchangeable forms of generic missingness. They encode different semantics and often imply different downstream actions.

## 3. Why ACL / NLP cares

TableQA, document understanding, and data-grounded generation increasingly operate directly over heterogeneous real tables. Existing task formulations often expect a scalar/string answer. But official tables can use the cell, annotation, legend, and footnote jointly to define a **typed observation state**.

Modern long-context generators create a new possibility:
- read the table;
- read source-local documentation;
- dynamically reconstruct the source’s observation ontology.

The resulting scientific question is:

> **Does document-conditioned generation make explicit provider-specific status parsing unnecessary, or is typed observation status still a load-bearing intermediate state?**

## 4. Competing accounts

### Account A — Documentation-conditioned generation is sufficient

A strong model can infer source-local status semantics directly from the supplied table and documentation.

If this wins:
- hand-coded sentinel/status parsers become largely historical scaffolding;
- typed interpretation may remain useful for evaluation but not necessary as an explicit model stage;
- general-purpose generation can transfer to unfamiliar provider conventions.

### Account B — Value-centric scalarization remains structurally wrong

Models continue to treat cells as values/strings or generic missingness, even when the official semantics says the correct answer is a non-value state.

If this wins:
- TableQA needs an explicit status/value factorization;
- conventional answer evaluation can reward semantically invalid scalarization;
- source-local legends are not sufficient unless the output space explicitly represents observation status.

### Principled heterogeneity

If direct generation succeeds for familiar/simple statuses but fails for suppressed, qualified, or unseen provider conventions, the paper identifies the boundary at which explicit typing remains necessary.

## 5. Outcome robustness

**If the expected scalarization failures do not appear, what is the paper?**

A preservation result is meaningful:

> current generators can robustly reconstruct previously hand-coded source-specific observation ontologies from local documentation, making explicit parsers unnecessary under specified conditions.

This should be tested with transfer to unseen provider conventions; otherwise “models know ACS codes” is too weak.

## 6. Paper identity

**Primary identity:** measurement / construct-validity + representation-necessity paper for real-world TableQA.

**Not the identity:**
- a Census benchmark;
- a missing-value benchmark;
- a symbol-recognition paper;
- another generic “LLMs make table errors” paper.

## 7. Planned C1 → C2 → C3

### C1 — Core scientific answer
Measure whether systems recover VALUE versus provider-defined typed non-value states correctly.

### C2 — Explanation / boundary
Cross:
- familiar vs unseen source;
- documentation absent vs present;
- visible code vs textual footnote;
- direct generation vs explicit status→value factorization;
- simple absence vs suppression/reliability/qualification states.

### C3 — Consequence
Determine whether real-world TableQA should:
- retain scalar/string outputs;
- adopt typed observation outputs;
- or rely on end-to-end documentation-conditioned generation under validated regimes.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Official statistical products intrinsically distinguish values from typed non-value states. |
| SCIENTIFIC TENSION | **YES** | End-to-end documentation reading and explicit status representation are both plausible. |
| GOOD DATA | **YES — strengthened** | ACS exposes official estimate/annotation pairs; Eurostat/SDMX independently exposes machine-readable observation-status flags under a different provider convention. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | 2026 TableQA work covers referencing errors, irregular tables and missing values, but not yet the same provider-defined typed-observation necessity story. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Success, failure, and source-dependent boundaries each change the task/modeling conclusion. |

## 9. Main danger

Reviewer compression:

> **“This is just missing-value / footnote-aware TableQA.”**

That compression wins if:
- all non-value states are merged into generic N/A;
- the task is just code decoding;
- no output-ontology or modeling consequence is demonstrated.

It is false only if the paper shows that the **state itself is the semantic answer**, with provider-defined gold and a decisive direct-generation versus explicit-typing comparison.

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) — modern TableQA neighbors, collision boundary, allowed/forbidden claims.
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md) — ACS contract, provider semantics, replication requirements.
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md) — pilot, full experiments, C1→C2→C3 and development path.

This remains **pilot-authorized only**, not an approved mainline.
