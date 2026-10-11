# L04 — Data and Independent Gold

**Core rule:** realization cardinality must be determined directly from the released paradigm resource, never by asking authors or models whether a form “should exist.”

---

## 1. Primary decisive substrate — Eesthetic / Paralex

Beniamine et al., LREC-COLING 2024  
**“Eesthetic: A Paralex Lexicon of Estonian Paradigms.”**  
https://aclanthology.org/2024.lrec-main.491/

Paralex standard:
https://www.paralex-standard.org/standard/

Eesthetic provides a large machine-readable Estonian paradigm lexicon with explicit non-canonical morphology annotations.

Published scale:
- 5,475 noun lexemes;
- 5,076 verb lexemes;
- 28 noun paradigm cells;
- 51 verb paradigm cells;
- 452,885 inflected-form rows.

The exact current release used for experiments must be version-pinned.

---

## 2. Why the gold is unusually strong

The Paralex standard explicitly separates defectivity from ordinary missing resource information.

### Defectivity

Defective cells:
- must have their own rows;
- should be tagged in defectiveness_tag;
- use DEF in form fields when no well-formed realization exists.

### Missing source/transcription information

MISSING is reserved for incomplete information and **must not** be interpreted as linguistic defectivity.

This prevents a fatal measurement error:

> “resource lacks a form” ≠ “language licenses no form.”

### Overabundance

Multiple valid forms for one lexeme×cell can appear as multiple rows and can be linked with overabundance_tag metadata.

This supports an external 0/1/many mapping.

---

## 3. Deterministic action mapping

For every lexeme×cell group:

### NO_FORM
Use when the resource explicitly encodes defectivity for that cell.

### ONE_FORM
Exactly one licensed non-defective realization remains after excluding:
- missing transcriptions;
- duplicate analyses;
- representation-only duplicates;
- rows that the resource says are not distinct licensed realizations.

### MULTIPLE_FORMS
More than one independently represented licensed realization for the same lexeme×cell, with overabundance/variant semantics checked against the resource metadata.

Important:
- not every duplicate row should automatically count as overabundance;
- analysis variants, phonetic/phonemic variants, source duplicates, and dialectal variants must be separated according to tags.

The mapping script must be audited against the schema before any target-model run.

---

## 4. Required machine-readable target record

Each item should include at least:

- lexeme ID;
- lemma;
- part of speech;
- cell / feature bundle;
- realization cardinality;
- gold orthographic form set;
- defectiveness tag(s);
- overabundance tag(s);
- variants/analysis/epistemic tags;
- source/frequency metadata if available;
- whether the cell is used in canonical benchmark comparison.

---

## 5. Canonical comparison construction

The key scientific comparison requires two views of the **same underlying lexeme×cell relation**:

### Conventional view
One canonical target string per cell where the conventional setup would provide one.

### Relation-aware view
- NO_FORM;
- ONE_FORM + the form;
- MULTIPLE_FORMS + the complete licensed set.

The canonical target must not be author-picked in a way that favors or hurts a model. Use an existing canonical choice where the resource/task defines one; otherwise pre-specify a deterministic selection rule only for the comparison baseline.

---

## 6. Pilot strata

At minimum:

- NO_FORM;
- ONE_FORM;
- MULTIPLE_FORMS.

Useful pre-specified analyses:
- noun vs verb;
- inflection class;
- frequency;
- lexicalized defectivity classes;
- overabundance class;
- cell frequency;
- seen/unseen lexeme split if a trained baseline is used.

Do not oversample only “interesting failures” after seeing model outputs.

---

## 7. Primary metrics

### Cardinality
- NO/ONE/MULTIPLE accuracy;
- macro-F1;
- confusion matrix.

### NO_FORM
- invalid-form generation rate.

### ONE_FORM
- exact form accuracy.

### MULTIPLE_FORMS
- exact-set match;
- set precision;
- set recall;
- partial coverage.

### Measurement validity
- correlation/agreement between canonical and relation-aware scores;
- model ranking agreement;
- per-regime conclusion agreement;
- effect sizes with uncertainty;
- equivalence/non-inferiority tests for preservation claims.

A ranking reversal is strong evidence, not a requirement.

---

## 8. Critical data audits before modeling

1. Reproduce published lexeme/form counts.
2. Count exact NO/ONE/MULTIPLE groups.
3. Inspect all tags that can create duplicate rows.
4. Verify DEF never gets confused with MISSING.
5. Verify enough zero/many groups remain after conservative filtering.
6. Check whether overabundant form frequencies are available and whether they matter for fair evaluation.
7. Freeze the mapping and exclusions.

---

## 9. Replication requirement

Eesthetic gives an unusually clean pilot substrate, but a Main-level measurement claim may require evidence beyond one Estonian resource.

Potential options:
- another Paralex-format lexicon with exact defectivity/overabundance tags;
- another published paradigm resource with independently defined zero/many states.

Do not count a resource as replication until:
- the exact fields are verified;
- the same deterministic mapping is possible;
- no author reconstruction is required.

---

## 10. Data validity kill conditions

KILL or demote if:

- reliable zero/many cases are too few;
- duplicate rows cannot be separated from genuine overabundance;
- defectiveness labels mix source missingness;
- canonical comparison requires arbitrary author choices;
- resource-specific quirks dominate the result;
- multilingual/cross-resource generality cannot be obtained and the effect is too narrow for Main.

The paper lives or dies on the validity of the 0/1/many gold.
