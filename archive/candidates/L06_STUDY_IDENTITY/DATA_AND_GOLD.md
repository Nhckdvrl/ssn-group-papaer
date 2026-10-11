# L06 — Data and Independent Gold

**Core rule:** study identity must come from an external evidence-synthesis source, not from our own guess that two papers “look related.”

---

## 1. Primary substrate — CochraneForest

Pronesti et al. (ACL 2025) build CochraneForest from Cochrane systematic reviews.

Verified published statistics:
- 202 forest plots;
- 48 systematic reviews;
- 263 unique studies;
- 923 research-question–study records;
- mean studies per review: 5.67;
- mean papers per review: 6.87;
- mean papers per study: **1.82**;
- maximum papers per study: **5**;
- mean studies per forest plot: 4.57.

Source:
- https://aclanthology.org/2025.acl-long.1359/
- https://aclanthology.org/2025.acl-long.1359.pdf

This is unusually useful because it exposes both:
1. the **document layer** (papers);
2. the **evidence-unit layer** (studies).

## 2. Load-bearing unit

For each forest plot/research question:

- set of included studies;
- set of accessible papers;
- oracle paper→study membership;
- study-specific conclusion;
- when available, underlying numeric evidence / effect estimate;
- overall forest-plot context.

The decisive experimental input is a **fixed paper multiset**.

The manipulated variable is only:
> paper→study membership information.

## 3. Experimental conditions

### A. ORACLE
Provide the exact provider/review-defined grouping.

### B. FLAT / NO IDENTITY
Give the same papers without study membership.

Do not change:
- paper content;
- paper count;
- question;
- token budget.

### C. PREDICTED
Use an automatic linkage model/rule to infer grouping.

This condition tests whether the quantity is necessary but can be recovered automatically.

### D. WRONG SPLIT
Take one true multi-report study and present its reports as two or more independent studies.

Scientific consequence tested:
> duplicate evidence inflation.

### E. WRONG MERGE
Take two independent studies and present them as one study.

Scientific consequence tested:
> evidence collapse / under-counting.

### F. PARTIAL
Reveal some but not all membership information.

This supports a graded boundary analysis.

## 4. Direct gold

### Study membership
Directly supplied by the systematic-review/CochraneForest organization.

### Study-level conclusion
CochraneForest provides study-specific conclusions associated with forest plots.

### Numeric evidence
The ACL/EMNLP follow-up resources expose outcome-specific numeric data/effect estimates for study-level inference.

Relevant source:
- https://aclanthology.org/2025.emnlp-main.1544/

No LLM judge should create the load-bearing truth labels.

## 5. Primary sampling frame

For the minimum decisive pilot, prioritize forest plots with:
- at least 3 studies;
- at least one study represented by ≥2 papers;
- at least one independent study that can serve as a merge counterpart;
- accessible full text;
- recoverable study conclusion/effect information.

A pilot dominated by one-paper-per-study cases has no leverage and should not be run.

## 6. Metrics

### Paper/study inference
- study-specific conclusion F1/accuracy;
- numeric extraction accuracy;
- effect-estimate error where available.

### Evidence-unit integrity
- number of inferred independent evidence units;
- false split rate;
- false merge rate;
- duplicate-vote / duplicate-weight inflation.

### Synthesis consequence
- pooled direction preserved vs changed;
- conclusion/significance preserved vs changed;
- ranking/weight shifts;
- answer/conclusion consistency under grouping interventions.

### Mechanism separation
Compare:
- paper-level extraction accuracy;
- study-level inference accuracy;
- final synthesis accuracy.

The strongest result is:
> extraction stays correct while wrong identity changes synthesis.

That directly identifies the load-bearing stage.

## 7. Naturalness controls

Do not create artificial fake papers.

Wrong split/merge manipulations operate only on **membership metadata** over genuine papers.

The underlying document evidence remains untouched.

## 8. Data-validity kill conditions

KILL or reconstruct if:
- multi-report studies are too rare for a stable sample;
- paper→study membership cannot be verified independently;
- study-level conclusions cannot be recovered;
- oracle vs flat conditions accidentally change evidence/token budget;
- synthesis outcome is not defined strongly enough to distinguish counting errors;
- the experiment reduces to publication-linkage accuracy.

## 9. Replication route

Primary:
- CochraneForest / Cochrane reviews.

Secondary possibilities after pilot:
- other systematic-review resources with explicit study/report links;
- trial-registry identifiers linking multiple publications;
- PubMed linked/duplicate-publication metadata.

Do not require a second provider before the first decisive pilot; require it before claiming universal evidence-unit necessity.

## 10. Data Gate verdict

**GOOD DATA: YES.**

Unlike L02, the decisive scientific quantity—paper→study identity—is directly and independently supplied by the source.
