# L03 — Related Work and Paper-Level Novelty

**Candidate:** Table Value ≠ Observation Status  
**Novelty rule:** the contribution must be the new paper-level scientific story, not the fact that tables contain missing or irregular values.

---

## 1. Classical and mature TableQA neighborhood

The field already owns:
- numerical and symbolic reasoning over tables;
- table structure understanding;
- hybrid table/text reasoning;
- missing-value and irregular-table cases;
- robustness to formatting and structure;
- generative answering over tables.

Therefore none of those broad claims can carry L03.

The target must remain narrower in mechanism but broader in scientific consequence:

> **What is the semantic output unit of a real statistical table cell when the provider itself says the cell represents a status rather than a scalar?**

---

## 2. Closest 2026 neighbors

### Yang et al., ACL 2026
**“When LLMs Read Tables Carelessly: Measuring and Reducing Data Referencing Errors.”**  
https://aclanthology.org/2026.acl-long.762/

Owns:
- systematic analysis of data referencing errors;
- cases where models incorrectly cite or omit table values;
- critic-based mitigation;
- the importance of reliable table value referencing.

Collision pressure:
- L03 cannot be framed generically as “LLMs misread table cells.”

Surviving axis:
- the ACL 2026 paper centers on whether table **values** are cited correctly;
- L03 centers on cases where a scalar value is **not the correct semantic object at all**.

### Yang et al., ACL 2026
**“CompTab: A Comprehensive Benchmark for Real-World TableQA with Complex Reasoning and Irregular Tables.”**  
ACL Anthology ID: 2026.acl-long.1279

Owns:
- real-world irregular TableQA;
- semantic ambiguity, multi-hop reasoning, transposed tables, merged cells, missing values, and outliers;
- broad evaluation of many LLMs under irregular table conditions.

Collision pressure:
- L03 cannot claim that missing values or irregular real tables are unstudied;
- a generic benchmark of odd cells would collapse into CompTab territory.

Surviving axis:
- CompTab’s missing-value category treats missingness as one irregularity among several;
- L03 asks whether provider-defined **non-value states are themselves denotations** that require a typed output ontology and source-local documentation.

---

## 3. Official-statistics semantics as the independent scientific substrate

The U.S. Census ACS API documentation explicitly defines annotation variables as character representations used when ordinary numeric information is not the correct representation. It gives paired estimate/annotation behavior such as a sentinel estimate with “(X)” meaning not applicable or not available.

Core sources:
- https://www.census.gov/data/developers/data-sets/acs-5year.html
- https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html

This matters for novelty because the ontology is not invented by the paper. The provider already says:
- sometimes a number is the answer;
- sometimes a typed annotation carries the meaning.

---

## 4. Cross-provider relevance

CDC/NCHS documentation provides an independent neighboring object: official health statistics can suppress or flag estimates because of reliability, precision, small sample sizes, or disclosure concerns.

Representative official sources:
- https://www.cdc.gov/nchs/hus/sources-definitions/statistical-reliability.htm
- https://www.cdc.gov/united-states-cancer-statistics/technical-notes/suppression.html
- https://www.cdc.gov/nchs/dqs/user-guide/index.html

Important distinction:
- these sources establish that typed/qualified non-values are a general official-statistics object;
- they are **not yet automatically part of the load-bearing experimental gold** until an exact machine-readable table/status mapping is verified.

---

## 5. What part of the full paper-level story is actually new?

The candidate must own the full chain:

1. a real provider defines non-scalar observation states independently of the model;
2. the model receives the local table plus source documentation;
3. the target is the provider-defined **typed observation**, not a generic missing-value answer;
4. direct generation is compared with an explicit status→value representation;
5. transfer to unfamiliar source conventions tests dynamic ontology reconstruction rather than memorization;
6. the result changes a conclusion about how real-world TableQA should define its output and evaluation.

A new dataset cell, prompt, or error category alone is not sufficient.

---

## 6. Reviewer compression

### Attack 1
> **“This is just missing-value TableQA.”**

Rebuttal:
> missing-value QA asks whether a desired value is absent or recoverable; L03 asks whether the official **state itself** is the answer and whether the output space must represent it.

### Attack 2
> **“This is just table data-referencing errors.”**

Rebuttal:
> referencing errors assume a value should be referenced; L03 includes cases where treating the cell as a value is already semantically wrong.

### Attack 3
> **“This is just footnote reading.”**

Rebuttal:
> footnotes/documentation are the mechanism by which the source defines the ontology. The scientific estimand is whether modern generation can reconstruct that ontology without an explicit status layer.

---

## 7. Kill-level collision definition

KILL if a prior paper is found that already does essentially all of:

- real provider-defined value/status gold;
- status itself is the QA target;
- documentation-conditioned recovery of source-local statuses;
- direct generation vs explicit typed-status modeling;
- conclusion about whether value-only TableQA is an invalid abstraction or explicit status parsing is unnecessary.

Broad missing-value, irregular-table, or table-error work is not enough by itself.

---

## 8. Allowed and forbidden claims

### Potentially defensible if supported

- “Provider-defined observation status is a load-bearing output unit for real statistical TableQA.”
- “Document-conditioned generation can/cannot safely replace explicit source-specific status parsing.”
- “Value-only evaluation changes conclusions on status-bearing cells.”
- “The need for explicit typing has identifiable source/status boundaries.”

### Forbidden / already crowded

- “Real tables contain missing values.”
- “LLMs make table mistakes.”
- “Footnotes matter.”
- “Irregular tables are hard.”
- “We introduce another broad real-world TableQA benchmark.”

---

## 9. Fresh-search status through 2026-09-07

Current audit includes:
- ACL 2026 table data-referencing errors;
- ACL 2026 CompTab irregular TableQA;
- official ACS status/annotation semantics;
- official CDC/NCHS suppression/reliability semantics.

No searched paper currently owns the same full **typed-observation output ontology + representation necessity** story.

Re-run this audit before mainline approval.
