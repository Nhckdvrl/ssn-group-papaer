# L27 — Sample / Effect Count ≠ Independent Evidence Units

**Status:** **NO-GO / ARCHIVED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## RQ

> When automated scientific extraction converts papers into flat effect records, does that representation preserve the independent experimental units and dependence structure required for valid evidence synthesis?

## Why killed

The route has a real statistical basis and natural examples, but it fails the project's topic-selection bar **before** model work:

1. **The scientific question is too implementation-shaped.** The paper identity is driven by a particular extraction schema and the fact that it omits dependence/group structure, rather than by a broadly compelling unresolved NLP/LLM question that exists independently of the benchmark construction.
2. **The data path is cumbersome.** A credible study requires linking article-level extraction records to trial registries or other design metadata and reconstructing dependence structure. That is a high data-engineering burden for a question whose payoff is not proportionally large.
3. **The reviewer-level importance is limited.** Even a strong result risks compressing to: “automatic meta-analysis needs design-aware metadata because effect sizes can be dependent,” which is already standard statistical knowledge.
4. **Finding natural witnesses does not rescue the topic.** Shared-control examples in the released RCT extraction data establish that the representation issue can occur, but they do not make the underlying research question sufficiently important or novel for the intended Main-level paper identity.

## Decision

Do **not** continue prevalence audits, registry linkage, shared-control analysis, crossover/cluster extensions, or model experiments. Preserve the existing evidence only as search history.

## Reopen only if

A substantially broader, independently motivated scientific question appears for which evidence-unit identity is merely one consequence rather than the paper-defining construction.
