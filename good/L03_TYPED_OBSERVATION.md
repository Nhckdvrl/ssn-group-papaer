# L03 — Table Value ≠ Observation Status

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Date promoted:** 2026-09-07

> **Plain-language thesis:** A table cell that does not contain an ordinary number is not necessarily “missing”; it may encode a typed observation state such as not applicable, unavailable, suppressed, or statistically inappropriate.

---

# 1. One-sentence RQ

> In real statistical tables, can modern generative systems recover the **typed observation represented by a cell**—including non-value states defined by local documentation—rather than collapsing every cell into a scalar/string answer or generic missingness?

---

# 2. Why ACL / NLP should care

TableQA and document understanding increasingly use LLMs to answer natural-language questions over heterogeneous tables. Real tables do not contain only values: legends, annotations, footnotes, and source-specific conventions can make a cell denote a qualified non-value whose semantics determines the correct answer.

The question is therefore about the output ontology of table understanding, not about memorizing a particular sentinel code.

---

# 3. REAL OBJECT

The object predates LLMs:

> **Statistical tables distinguish observed values from typed non-value / qualified-observation states.**

Simple example:

- `0` = a measured zero;
- `(X)` = not applicable / not available in an ACS table;
- another source may use a symbol for suppressed, unreliable, below-detection, or otherwise non-reportable data.

These states can imply different downstream actions even when the visible cell lacks a normal number.

**Gate: YES.**

---

# 4. What LLMs newly enable

Traditional pipelines can hard-code one provider's sentinel dictionary. That is not the scientific contribution.

Long-context generative systems can instead receive:

1. the table;
2. the table's own legend / footnote / documentation;
3. a natural-language question;

and dynamically recover the locally defined observation ontology at inference time.

This makes it possible to test whether explicit source-specific status parsers are still necessary, or whether document-conditioned generation can directly recover the correct typed observation.

---

# 5. Competing accounts

## Account A — Context-rich generation makes the explicit status layer obsolete

A strong LLM can read the table together with its local documentation and directly produce the correct semantic answer.

Prediction:
- values remain values;
- not-applicable / unavailable / suppressed / qualified cases are not scalarized;
- a separate typed-status intermediate representation adds little.

## Account B — Scalarization collapse

Current TableQA systems still implicitly treat cells as values/strings and fail when the cell denotes a non-value status.

Prediction:
- sentinel values are copied as numbers;
- suppressed / not-applicable / unavailable cases collapse into generic `N/A` or zero;
- providing the legend is insufficient unless the system explicitly factorizes observation status from value recovery.

Both accounts are plausible before the pilot and imply different task definitions.

---

# 6. GOOD DATA + independent gold

## Primary substrate — U.S. Census American Community Survey (ACS)

Official ACS APIs expose estimate variables together with annotation variables. Census documentation states that annotation variables are character representations used when ordinary numeric information is not the correct representation; when an estimate annotation exists it should be used in place of the estimate.

Concrete official behavior includes sentinel estimate values paired with annotations such as `(X)` for not applicable / not available.

Sources:
- https://www.census.gov/data/developers/data-sets/acs-5year.html
- https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-api-variable-types.html
- https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html

This provides:
- natural real tables/data;
- machine-readable status supervision independent of evaluated LLMs;
- scalable paired value/annotation cases;
- source documentation that can be supplied as inference context without author-created semantics.

## Replication / transfer substrate

Use at least one independent public statistical/health data source with official suppression/reliability/non-applicability semantics (e.g. CDC/NCHS) after verifying exact machine-readable fields.

The replication is important to distinguish dynamic documentation reading from memorizing ACS conventions.

**Gate: YES.**

---

# 7. Action mapping

Represent the answer as a typed observation, for example:

```text
{
  observation_status: VALUE | NOT_APPLICABLE | NOT_AVAILABLE | SUPPRESSED | QUALIFIED | ...,
  value_if_defined: ...,
  qualification: ...
}
```

The exact label inventory is derived from each source's official documentation rather than invented by the authors.

Correct action is externally forced:
- when an official status says no scalar estimate applies, outputting the sentinel as a scalar is wrong;
- when a genuine numeric estimate exists, replacing it with generic missingness is wrong.

---

# 8. NEW PARENT — novelty assassination

## Closest modern neighbors

- Yang et al. (ACL 2026), *When LLMs Read Tables Carelessly: Measuring and Reducing Data Referencing Errors* — studies incorrectly citing or omitting table **values** and critic-based mitigation.
- CompTab (ACL 2026) — includes irregular real-world TableQA and missing-value reasoning.
- broader TableQA work studies noise, missing information, structure, and reasoning.

Fresh searches through 2024–2026 did **not** find a paper whose parent is:

> **a non-value status is itself the semantic denotation to recover, with source-local documentation defining the output ontology.**

The distinction from ordinary missing-value QA is load-bearing:

> missing / unanswerable means a desired value cannot be obtained;
> typed absence means the official state itself is the answer and may explicitly say that a scalar is inapplicable, suppressed, controlled, or otherwise qualified.

### Reviewer compression

> “This is just missing-value / footnote-aware TableQA.”

### Why that compression is currently false

The primary estimand is not whether a missing scalar can be inferred. It is whether the task's output unit should be a **typed observation** rather than a scalar/string, using independent provider-defined semantics.

If a direct 2024–2026 paper owning this typed-observation task-definition rewrite is found, KILL immediately.

**Gate: YES, survived current direct audit.**

---

# 9. DECISIVE PAPER

## C1 — Core finding

Measure whether strong generative TableQA systems preserve the distinction between scalar values and provider-defined observation states.

## C2 — Why / boundary

Cross:
- value vs typed non-value;
- visible sentinel vs display annotation;
- documentation absent vs provided;
- familiar source vs unseen source;
- direct generation vs explicit two-stage status→value factorization.

## C3 — Consequence

Test whether replacing value-only evaluation with typed-observation evaluation changes:
- model ranking;
- conclusions about whether table+legend context is sufficient;
- the need for explicit structured intermediate states.

The strongest Main-level consequence is a **ranking or conclusion reversal** under the corrected output ontology.

### Outcome map

| outcome | scientific meaning | informative? |
|---|---|---|
| Account A wins | LLM document conditioning makes hand-coded status parsers largely obsolete | YES |
| Account B wins | scalar/string TableQA is an invalid task abstraction for status-bearing cells | YES |
| heterogeneous | identify which status/document conditions require explicit typing | YES |
| ranking reversal | conventional TableQA conclusions mismeasure real statistical-table understanding | YES, strongest |

**Gate: YES.**

---

# 10. Minimum decisive pilot

1. Automatically sample a balanced ACS subset using estimate + annotation variable pairs.
2. Render natural table snippets plus the corresponding official legend/documentation.
3. Ask a small set of strong current LLMs natural questions whose correct answer sometimes is a scalar and sometimes a typed status.
4. Compare:
   - ordinary direct answer;
   - structured typed-observation answer;
   - two-stage status→value factorization;
   - documentation absent vs present.
5. Primary estimands:
   - false-scalarization rate;
   - status accuracy;
   - value accuracy conditional on `VALUE`;
   - ranking change between conventional answer accuracy and typed-observation accuracy.
6. Replicate zero-shot on one independent official data source.

### Pilot kill condition

KILL if:
- the status cases are vanishingly rare / impossible to sample at useful scale;
- all strong models are near ceiling and typed factorization changes neither errors nor conclusions;
- a direct modern-parent collision appears;
- the result reduces to symbol memorization rather than documentation-conditioned semantics.

### Pilot continuation condition

Continue if either:
- direct generation systematically scalarizes/merges semantically distinct states; or
- strong models robustly recover unseen source-defined observation ontologies, supporting the opposite conclusion that explicit status parsers are no longer necessary.

---

# 11. Five hard gates

| Gate | Verdict | Reason |
|---|---|---|
| REAL OBJECT | **YES** | Official statistical products intrinsically distinguish values from typed observation states. |
| NEW AXIS | **YES** | Rewrites the TableQA output unit from scalar/string to provider-defined typed observation. |
| GOOD DATA | **YES** | ACS exposes official paired estimate/annotation semantics at scale; replication can use another official source. |
| NEW PARENT | **YES, survived current direct audit** | Missing-value and data-referencing work do not currently own typed non-value denotation as the task target. |
| DECISIVE PAPER | **YES** | Either end-to-end generation makes explicit typing obsolete or current value-centric TableQA is structurally mis-specified. |

# Final status

# **PILOT-AUTHORIZED**

Not paper-mainline-approved.
