# Study Identity — Related Work and Paper-Level Novelty

## 1. What prior work clearly owns

### CochraneForest / ACL 2025
Owns:
- study ≠ paper as part of the task definition;
- multiple papers per study;
- study-level evidence extraction;
- URCA retrieval that samples uniformly across papers within one study;
- passage clustering before generation.

Therefore we cannot claim:
- discovering that a study may have multiple papers;
- multi-paper study inference is new;
- organizing retrieved passages helps;
- document-level scientific evidence extraction is new.

Primary source: https://aclanthology.org/2025.acl-long.1359/

### Systematic-review methodology
Cochrane and classic meta-research already own the methodological fact that multiple reports from one study should not be counted as independent studies.

Therefore we cannot claim:
- duplicate reports bias meta-analysis;
- study identity matters in classical evidence-based medicine.

Sources:
- https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04
- https://www.bmj.com/content/315/7109/635

### Publication linkage / trial matching
There is broad biomedical-informatics work on linking publications to trials or identifying duplicate reports.

Therefore publication-linkage accuracy itself cannot carry the paper.

## 2. What remains potentially new

The load-bearing paper identity is the **necessity intervention**:

> Existing automated evidence-synthesis work silently receives the correct study unit. If modern LLMs can jointly read all papers, is that external identity still necessary for preserving the scientific evidence quantity?

The decisive experiment holds documents fixed and changes only identity information:

`same papers -> oracle / none / predicted / wrong split / wrong merge -> evidence inference and synthesis consequence`

This is not answered by within-study retrieval or clustering.

## 3. Why CochraneForest's clustering ablation is not the same experiment

URCA's clustering occurs after documents have already been assigned to a study. The ACL 2025 task definition gives a study and its one-or-more papers, then predicts that study's conclusion.

Our intervention changes whether those papers are known to belong to that study in the first place.

Thus:
- URCA clustering asks how to organize evidence **inside a known study**;
- this candidate asks whether the **study boundary itself** is a necessary representation.

If implementation reveals that CochraneForest's released examples cannot reconstruct the original multi-study paper pool and only expose isolated study packages, the pilot must rebuild review-level sets from the released study/paper metadata. If this cannot be done cleanly, demote.

## 4. Closest reviewer compression attacks

### Attack A
> “This is just a CochraneForest oracle-grouping ablation.”

This attack wins if the paper reports only one oracle-vs-flat delta.

The rebuttal requires:
- controlled split and merge interventions;
- mechanism separation between information integration and evidence counting;
- a synthesis-level consequence;
- a general conclusion about the evidence unit, not a model leaderboard.

### Attack B
> “This is just publication linkage.”

This attack wins if success is measured by paper-pair matching accuracy.

The rebuttal is that linkage is only an intermediate condition. The estimand is:

> **Does identity information change the scientific conclusion produced from the same documents?**

### Attack C
> “Of course duplicate papers should not be double-counted.”

The classical rule is indeed known. The non-obvious LLM-era question is whether an end-to-end generator can infer this structure implicitly from natural papers, making explicit grouping dispensable.

## 5. Exact novelty claim we may defend

Potentially defensible:

> “Oracle study identity is / is not a load-bearing representation for modern generative evidence synthesis, with distinct consequences for report merging and evidence counting.”

Not defensible:
- “studies have multiple papers”;
- “duplicate publications are bad”;
- “clustering documents helps”;
- “LLMs can link publications.”

## 6. Kill-level collision definition

KILL if a prior modern paper is found that already does essentially all of:
- the same natural paper sets;
- explicit oracle vs no/predicted study identity;
- controlled split/merge or equivalent identity corruption;
- downstream study/synthesis consequence;
- conclusion about whether explicit study identity is necessary for LLM evidence synthesis.

A publication-linkage benchmark alone is not enough to kill it. A study-level extraction system that assumes gold membership is not enough to kill it.

## 7. Current verdict

**PAPER-LEVEL NOVELTY: PASS, but reviewer-compression pressure is substantial.**

The paper must be written as an evidence-unit necessity study, not as a CochraneForest extension.