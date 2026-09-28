# L07 — Data and Independent Gold

**Core rule:** the old→new proposition relation must be explicitly licensed by the publisher/editorial record. We do not infer a correction merely because two texts conflict.

---

## 1. Source layer A — PubMed / NLM linked corrections

NLM links:
- original article;
- correction/erratum notice;
- corrected-and-republished version when applicable.

Official documentation:
- https://www.nlm.nih.gov/bsd/policy/errata.html

Use this layer to obtain reliable document-level update relations.

## 2. Source layer B — Crossref / Crossmark

Crossmark metadata records editorially significant update relations and update types.

Official documentation:
- https://www.crossref.org/services/crossmark/
- https://www.crossref.org/documentation/crossmark/participating-in-crossmark/

Use this layer to:
- broaden coverage beyond PMC/PubMed;
- distinguish official correction/update types;
- validate DOI relationships.

## 3. Source layer C — PMC full correction notices

PMC gives machine-readable/full-text notices for many open-access corrections.

High-value patterns:
- “should read … instead of …”;
- “the sentence should read …”;
- “X was incorrectly reported; corrected to Y”;
- explicit table/figure replacement;
- explicit numeric/method/funding correction.

Representative examples:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12014900/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10478380/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11837133/

## 4. Load-bearing gold unit

Each candidate instance should contain:

- original article identifier;
- correction notice identifier;
- update type;
- exact original span/proposition X;
- exact corrected span/proposition Y;
- location/type: text / number / method / table / figure / qualifier;
- publisher-authored wording establishing replacement.

The gold scientific relation is:
> **X is superseded by Y.**

## 5. Inclusion tiers

### Tier 1 — exact textual replacement
Publisher explicitly supplies both X and Y.

Best primary pilot material.

### Tier 2 — exact location + corrected value/text
The old span is recoverable from the original article and the notice supplies Y.

Allowed if deterministic.

### Tier 3 — figure/table correction
Include only when old and new cell/legend/content can be extracted reliably.

### Exclude from decisive set
- author spelling only;
- affiliation only;
- bibliography formatting only;
- typographic corrections with no semantic change;
- vague “the article has been corrected” notices without recoverable old→new content.

## 6. Mandatory pre-pilot yield audit

Before model compute:

### Sample
Randomly sample ~500 linked PMC/PubMed correction notices across years/journals.

### Deterministic parser categories
- exact proposition replacement;
- exact numeric/table/figure replacement;
- semantic but not directly alignable;
- metadata-only;
- formatting-only;
- unusable.

### Required outputs
- yield of Tier 1/2;
- distribution of correction types;
- publication years;
- journal/domain diversity;
- percentage requiring visual/table extraction.

Manual review can validate parser precision, but **manual annotator judgment must not create the old→new truth**.

## 7. Natural QA/IE rendering

For each instance construct tasks such as:

### QA
Original asks/answers X; correction says X→Y.
Question targets the corrected fact.

### Structured IE
Extract:
- current value;
- current method description;
- current qualifier;
- current figure/table fact.

### Summarization
Summarize the corrected result without repeating obsolete X.

Do not make benchmark contribution the main story; tasks are probes of current-state scholarly interpretation.

## 8. Experimental conditions

1. **ORIGINAL ONLY** — historical baseline.
2. **CORRECTION ONLY** — tests whether notice is self-contained.
3. **ORIGINAL + CORRECTION FLAT** — default end-to-end condition.
4. **EXPLICIT UPDATE STATE** — tell/model X→Y as a structured operation.
5. **UNRELATED CORRECTION CONTROL** — ensures model is using the correct notice.
6. **ORDER SWAP** — correction before/after original to test salience vs semantics.

Optional:
- current online corrected article where publisher has modified the article body.

## 9. Metrics

- current-proposition accuracy;
- superseded-proposition reuse rate;
- blend/contradiction rate;
- exact numeric/value accuracy;
- correction application accuracy;
- false override rate on unchanged content;
- direct-flat vs explicit-update difference.

Important:
> merely mentioning Y somewhere is not enough if the answer still presents X as current.

## 10. Data-validity kill conditions

KILL or reconstruct if:
- substantive proposition-update yield is too low;
- exact old→new pairs mostly require our interpretation;
- notices are dominated by metadata/formatting;
- the corrected proposition cannot be aligned to the original;
- current-state QA becomes trivial lexical copying with no need to reconcile X and Y;
- Crossref/NLM relations are too incomplete for reproducible sampling.

## 11. Replication

Primary:
- PMC/PubMed.

Secondary:
- Crossref/Crossmark publishers outside PMC;
- corrected-and-republished article relations;
- partial retractions as a harder neighboring update operation.

Do not mix retraction/partial retraction into the first pilot.

## 12. Data Gate verdict

**PASSED FOR A 150-ITEM EXPANSION (E000–E002b, 2026-09-08).**

E000 sampled 500 records from a complete 121,396-record PubMed query frame with a fixed seed. After the E000f identifier-scope repair, all 500 have an NLM `ErratumFor` relation, record-level PMCID, and matching correction-notice JATS PMID.

A corrected frozen stratified manual review of 162 notices produced a design-weighted **confirmed T1 yield of 12.81%** (95% CI 9.49–16.13%). Thirteen additional records remain `T2_PENDING`. The 33 directly observed T1 records cover 27 journals, 2015–2026, and four correction classes.

E001 adds a stricter model-item condition: the supplied original excerpt must contain old X and not leak new Y. Fourteen of 32 directly quoted operations expose X in current PMC title/abstract/body, so acquisition must verify article state item by item. E002b uses 10 leak-free items and rejects the immediate lexical-ceiling kill condition, but its forced-choice size is not paper evidence. Exact pointers are in [results/e000/AUDIT_REPORT.md](results/e000/AUDIT_REPORT.md), [results/e001/REPORT.md](results/e001/REPORT.md), and [results/e002b_counterbalanced/REPORT.md](results/e002b_counterbalanced/REPORT.md).

## 13. E003 scaled construction contract

E003 freezes a second, E000-disjoint fixed-seed sample before reviewing outcomes. The completed collection contains 4,000 correction notices selected from 4,100 deterministic candidates; one pre-boundary candidate lacked `ErratumFor` and was replaced from the deterministic reserve. All 4,000 accepted records have a PubMed correction relation, PMCID, and matching JATS PMID.

Candidate creation is deliberately two-stage:

1. deterministic quote-pattern rules propose explicit X→Y spans;
2. an optional local model may add recall proposals, but only when both X and Y survive normalized verbatim-substring checks against publisher text.

Neither route creates gold. Every merged proposal must receive an item-level review label recording whether it is scientifically substantive, correctly directed, nonvisual, and explicitly publisher-licensed. Only accepted pairs proceed to the linked original, where the supplied historical excerpt must contain X and exclude Y. Question/answer construction then receives a separate human check for answer uniqueness and leakage.

The current checkpoint contains 140 deterministic proposals from 72 notices. Model-assisted recall, merge, manual review, original-state validation, and task authoring are not complete. See [results/e003/REPORT.md](results/e003/REPORT.md).
