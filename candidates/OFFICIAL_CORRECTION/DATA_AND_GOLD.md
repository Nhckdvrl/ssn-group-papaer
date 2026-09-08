# Official Correction — Data and Independent Gold

## 1. Load-bearing estimand

The target is not “does this paper have a correction?” It is:

> **What proposition in the scholarly record is current after an official editorial correction?**

The strongest gold has the form:

`original proposition X -> official correction notice -> corrected proposition Y`

The correction relation and replacement content must come from the publisher/NLM record, not from our own interpretation of two conflicting papers.

## 2. Primary sources

### PubMed / NLM
NLM links erratum notices to original articles and treats corrections, corrigenda, addenda, partial retractions, and corrections to text/tables/graphs/statements as errata.

Source: https://www.nlm.nih.gov/bsd/policy/errata.html

### PMC
PMC requires correction notices to specify the nature of the error and structured citation information for the corrected article; corrected/re-published versions remain linked to originals.

Source: https://pmc.ncbi.nlm.nih.gov/about/guidelines/

## 3. Gold tiers

### Tier A — Exact publisher-authored replacement
Correction explicitly contains wording such as:
- “X should read Y”;
- “instead of X, the correct value is Y”;
- “the following sentence should be replaced by …”.

This is ideal direct gold.

### Tier B — Exact location + corrected content
Notice identifies table/figure/paragraph/number and provides corrected content, but the original value must be extracted from the original article deterministically.

Usable after automated alignment plus manual spot audit.

### Tier C — Semantic correction without exact replacement
Notice describes the corrected meaning but does not provide a simple old→new pair.

Keep for later generalization only; do not make this load-bearing pilot gold unless mapping is deterministic.

### Tier D — Metadata/editorial-only correction
Author names, affiliations, references, spelling, formatting, pagination, etc.

Exclude from the primary semantic experiment; retain as negative/control category.

## 4. Mandatory pre-pilot yield audit

Before any model experiment:
1. sample at least 300 correction notices from PMC/PubMed-linked records;
2. classify them into Tier A/B/C/D using a deterministic rubric;
3. report exact proportions and inter-auditor agreement for ambiguous cases;
4. estimate how many semantic old→new pairs can be collected automatically at realistic scale.

Promotion condition is not a magical percentage. The decisive question is whether enough Tier A/B examples exist to support multiple correction types and train/test separation without author-created labels.

## 5. Experimental unit

For each correction instance store:
- original article ID/DOI/PMID;
- correction notice ID;
- original passage/table cell;
- corrected passage/value;
- correction type;
- location;
- publication dates only as metadata;
- official relation type.

## 6. Natural input conditions

Construct evidence packages from the real scholarly record:
- original article excerpt + correction notice;
- full original article + notice where context is required;
- retrieval setting with both documents among distractors;
- correction relation explicitly shown vs only inferable from document text/metadata.

Do not manufacture contradictory propositions.

## 7. Primary metrics

- corrected-proposition accuracy;
- obsolete-proposition persistence rate;
- update-direction error (old↔new inversion);
- correction-type macro-F1;
- retrieval-success conditional answer accuracy;
- answer correctness conditional on original salience/order;
- exact value accuracy for numeric/table corrections.

## 8. Required controls

- original-only baseline;
- correction-only baseline;
- original + correction in both orders;
- matched unrelated newer article to show the model is not using recency alone;
- metadata-only correction negative controls;
- explicit “this corrects X” relation vs relation hidden from prompt.

## 9. Replication

Strong Main version should include at least two publisher/journal families or two correction formats so the result does not reduce to one publisher template.

Crossref/Crossmark may be used to broaden update discovery, but proposition-level gold must still be verified from the linked correction content.

## 10. Data-validity kill conditions

KILL/demote if:
- Tier A/B semantic corrections are too rare;
- mapping old→new requires substantial author interpretation;
- original content cannot be reliably recovered;
- most examples are trivial spelling/metadata edits;
- the task can be solved by publication date alone;
- correction notices systematically reveal the answer through artificial formatting not present in natural use.
