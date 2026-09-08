# Study Identity — Data and Independent Gold

## 1. Load-bearing estimand

The decisive variable is not “are two papers textually similar?” It is:

> **Do two or more publications belong to the same underlying study, and what happens to evidence synthesis if that identity is omitted or corrupted?**

The gold must therefore supply an externally defined mapping:

`paper/report -> study identity`

and an independently defined downstream study conclusion.

## 2. Primary substrate — CochraneForest

CochraneForest is unusually well aligned with the question:
- 202 annotated forest plots;
- 48 Cochrane systematic reviews;
- 263 unique studies;
- 923 research-question–study records;
- mean 1.82 papers per study, maximum 5;
- each study is represented by one or more papers and has a study-specific conclusion for a clinical research question.

The ACL 2025 task definition explicitly states that each study contains one or more papers and that the system predicts a conclusion from those papers.

This gives two direct external objects:
1. **study membership** from the systematic-review construction;
2. **study-specific conclusion** from the forest-plot annotation pipeline.

Primary source: https://aclanthology.org/2025.acl-long.1359/

## 3. Why this is direct gold

Cochrane reviewers already perform the scientific operation we care about: identifying which reports belong to the same study. The grouping is not inferred by our model and is not generated to fit our hypothesis.

Cochrane explicitly warns that multiple reports from one study must be linked so a study is not inadvertently included more than once.

Source: https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04

## 4. Unit of analysis

For each clinical research question / forest plot:
- set of all accessible papers;
- oracle study partition;
- study-level conclusion labels;
- optional forest-plot effect information where usable;
- metadata needed for stratification, but not as gold.

The experimental unit should usually be the **review question / forest plot**, because that is where split/merge errors can affect multi-study synthesis.

## 5. Core intervention conditions

All conditions must use the same underlying paper text.

### A. ORACLE
Provide correct paper→study grouping.

### B. FLAT
Provide all papers without study membership.

### C. PREDICTED
Infer study linkage automatically using metadata/text/registry identifiers, then synthesize.

### D. WRONG-SPLIT
Take papers from one multi-report study and present them as if they were distinct studies.

### E. WRONG-MERGE
Merge papers from two genuinely different studies under one identity.

Wrong-split and wrong-merge should be constructed from real studies but the corruption operation itself is controlled and known exactly.

## 6. Required outcome quantities

At minimum:
- per-study conclusion accuracy / macro-F1;
- review-level conclusion or evidence-direction consistency if a deterministic synthesis target can be recovered;
- duplicate-vote / effective-study-count error;
- complementary-information integration accuracy;
- sensitivity to wrong split vs wrong merge;
- calibration/confidence only as secondary evidence.

If a trustworthy review-level synthesis target cannot be deterministically recovered from CochraneForest, do not invent one. The minimum pilot can use study-level conclusion plus controlled vote/count consequence; a Main paper should add a stronger downstream synthesis quantity if possible.

## 7. Natural subset requirements

The primary pilot must enrich, but not fabricate, cases with:
- >=2 papers per study;
- at least two studies in the same forest plot;
- meaningful report complementarity or redundancy;
- enough multi-report studies to make flat/oracle genuinely different.

Report separately:
- single-paper studies;
- two-report studies;
- >=3-report studies.

Single-paper studies are useful negative controls: identity representation should not create an artificial advantage when no grouping ambiguity exists.

## 8. External validity / replication

Preferred replication routes:
- another systematic-review corpus with explicit study↔report links;
- trial-registry identifiers mapping multiple publications to one trial;
- a manually audited small external set only as replication, not primary gold.

Do not make cross-dataset replication mandatory before the first pilot; CochraneForest already directly exposes the load-bearing variable.

## 9. Data-validity kill conditions

KILL or demote if:
- too few CochraneForest examples actually contain multiple papers per study;
- study grouping cannot be reconstructed from released data with high confidence;
- the only measurable consequence is retrieval F1 with no evidence-unit consequence;
- study-level conclusion labels depend on information unavailable to the model in all conditions;
- review-level claims require author-created labels or subjective adjudication;
- wrong-split/merge manipulation changes the text itself rather than only the identity representation.

## 10. Historical consequence as motivation, not experiment gold

Classic meta-research shows that duplicate publications can materially bias synthesis. Tramèr et al. reported a 23% overestimation of treatment efficacy when duplicate reports were included.

Source: https://www.bmj.com/content/315/7109/635

This establishes importance but should not substitute for the modern LLM intervention.