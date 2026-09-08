# L06 — Related Work and Paper-Level Novelty

**Candidate:** Study Identity Is Not Document Identity  
**Novelty rule:** prior work may own study linkage, duplicate-publication risk, CochraneForest, and study-level inference. The new contribution must be the **necessity of study identity as an evidence representation under end-to-end LLM synthesis**.

---

## 1. Classical ownership — multiple reports from one study are not independent evidence

The Cochrane Handbook explicitly treats identification of multiple reports from the same study as a necessary review step and warns that duplicate publication can introduce substantial bias if a study is inadvertently included more than once.

Official source:
- https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04

Therefore we cannot claim:
- study ≠ paper is new;
- duplicate reports can bias meta-analysis is new;
- study linkage is a new preprocessing task.

Those facts are background.

## 2. Closest modern NLP parent — CochraneForest / URCA

Pronesti et al., ACL 2025, **“Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies”**:
- introduces CochraneForest;
- 202 forest plots from 48 Cochrane reviews;
- 263 unique studies;
- full texts associated with studies;
- study-specific conclusions;
- URCA retrieves evidence from the papers associated with a study.

Source:
- https://aclanthology.org/2025.acl-long.1359/

Important detail:
- CochraneForest already recognizes **study ≠ paper**;
- its dataset statistics report an average of 1.82 papers per study and a maximum of 5;
- study membership is part of the task/data organization rather than the scientific variable under test.

### URCA “clustering” is not our intervention

URCA's retrieval clustering operates **within the already known study's papers/passages**. Removing that clustering is not equivalent to removing oracle study membership.

Therefore this candidate must never claim:
> “Nobody has studied grouping.”

The unowned question is:
> **What happens when the model receives the same paper collection but the underlying study membership is hidden, corrupted, or explicitly supplied?**

## 3. Closest follow-up — study-level numeric inference

Pronesti et al., EMNLP 2025, **“Enhancing Study-Level Inference from Clinical Trial Papers via Reinforcement Learning-Based Numeric Reasoning”**:
- extracts numeric evidence;
- derives study-level conclusions/effect estimates;
- evaluates on CochraneForest and related data;
- demonstrates stronger study-level inference.

Source:
- https://aclanthology.org/2025.emnlp-main.1544/

Collision pressure:
- we cannot claim that multi-paper study inference or quantitative evidence synthesis is new.

Surviving axis:
- this work still starts from the study-level unit;
- it does not test whether explicit study membership is necessary when a system begins from a mixed collection of papers.

## 4. Evidence-synthesis literature strengthens importance but not novelty

Cochrane and meta-research show that duplicate/overlapping reports can materially bias pooled conclusions.

A 2024/2025 meta-research example demonstrates that duplicated/overlapping registry-derived studies can materially change pooled estimates:
- https://pubmed.ncbi.nlm.nih.gov/39701398/

This is motivation, not our NLP novelty.

## 5. What prior work already owns

Already owned:
- publication linkage as a task;
- duplicate detection;
- the study/report distinction;
- study-level evidence extraction;
- forest-plot reconstruction;
- within-study retrieval/clustering;
- numerical study inference.

We explicitly do **not** claim any of these.

## 6. What part of the paper-level story is new

The proposed paper must own the chain:

1. use natural paper collections with externally defined study membership;
2. hold the exact paper evidence fixed;
3. manipulate only study identity;
4. compare oracle / absent / predicted / wrong split / wrong merge;
5. trace whether errors first appear in extraction, study inference, or final synthesis;
6. conclude whether explicit study identity remains necessary in LLM-era evidence synthesis.

The central claim is therefore about **representation necessity**, not linkage accuracy.

## 7. Reviewer compression

### Attack 1
> “This is just CochraneForest with an oracle-grouping ablation.”

This compression is fatal if the paper only reports one delta.

Rebuttal requires:
- matched paper sets;
- controlled identity interventions;
- synthesis-level consequences;
- split-vs-merge asymmetry;
- a general decision about the correct evidence unit.

### Attack 2
> “This is just publication linkage.”

Rebuttal:
> linkage quality is an upstream prediction problem; our estimand is the downstream scientific consequence of having or not having the true evidence unit.

### Attack 3
> “Of course duplicate papers should not be double-counted.”

Rebuttal:
> the non-obvious question is whether modern end-to-end LLMs **already infer that constraint implicitly**, making explicit identity dispensable. Both outcomes are plausible before experiment.

## 8. Kill-level collision definition

KILL if a modern paper is found that already:
- holds the same set of reports fixed;
- varies oracle vs absent/predicted/corrupted study membership;
- measures downstream study/synthesis conclusions;
- and draws the same representation-necessity conclusion.

A paper that merely detects duplicate reports or assumes study grouping is not fatal.

## 9. Top-conference alignment

Structurally relevant:
- ACL 2025 CochraneForest: natural scientific object + real full papers + decisive task formulation.
- EMNLP 2025 study-level inference: concrete quantitative consequence.
- Strong Main/award-style methodology papers: old modeling assumption → controlled intervention → decision map.

The candidate is weaker than the bar if it remains a one-benchmark ablation. It approaches the bar if it produces a general evidence-unit decision with clean causal interventions.

## 10. Current verdict

**PAPER-LEVEL NOVELTY: YES, but reviewer-compression pressure is real.**

The decisive novelty must stay at:
> **Is study identity a necessary evidence representation for generative synthesis?**
