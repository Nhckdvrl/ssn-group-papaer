# L28 — Canonical Species ID ≠ Source Taxonomic Concept

**Status:** **NO-GO / KILL CURRENT FORM — DIRECT DOMAIN-PARENT COLLISION**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## Former RQ

> When scientific IE / entity linking normalizes species mentions from heterogeneous literature to one canonical taxonomy ID, does that preserve the taxonomic concept intended by each source, or can normalization silently merge evidence that the source taxonomies treat as different or only partially overlapping biological entities?

## Why it looked strong

The classical problem is real and unusually well grounded. Taxonomic names do not uniquely identify source-relative taxonomic concepts; TCS / RCC-5 explicitly represent concept identity and relations, public expert alignments exist, and biodiversity data integration has real consequences when non-congruent concepts are merged.

The modern bridge initially looked attractive because scientific IE/entity linking commonly normalizes mentions to canonical taxonomy IDs, apparently creating a direct old-problem → modern-operation question.

## Exact kill reason

Fresh domain-owner search showed that the load-bearing bridge is already explicitly owned inside biodiversity informatics, not merely by old taxonomy theory.

- Müller, von Raab-Straube & Berendsohn (2024), *A Taxonomic Concept Mapping Service for Taxonomic Information Aggregators*, states that linking local taxon-related information to larger/global aggregators requires not only name matching but explicit comparison and mapping of taxonomic concepts.
- Rees, Franz & Sterner (2026), *A scalable exemplar-based method for aligning biological taxonomies*, treats checklist rows as taxonomic concepts, builds scalable concept-aware RCC-5 alignments, and directly targets reconciliation/transfer of information across taxonomies.

Thus the strongest intended conclusion — canonical/name-level normalization is not sufficient for safe cross-source information integration and concept-aware mapping is required — is already a direct domain-level scientific result with an operational remedy.

Adding an LLM/taxon-entity-linking experiment would mainly show that a newer extractor fails to follow an already-established correct representation. That can be useful engineering evidence, but it does not currently own a new ACL/EMNLP/NAACL Main paper identity.

## Reviewer compression

> “Existing taxonomic-concept mapping/alignment, with an LLM entity linker inserted before the already-known integration problem.”

## Why the good gold does not rescue it

RCC-5 alignments and occurrence/trait records could make a clean benchmark, but better gold cannot restore ownership of the parent conclusion. The project would need a qualitatively different NLP scientific estimand, not merely a demonstration that canonical normalization reproduces a known taxonomy-integration failure.

## Reopen only if

A broader, independently motivated scientific-entity identity problem is found across domains where the relevant source/theory-relative identity is not already represented by mature mapping/alignment infrastructure, and the resulting NLP conclusion cannot be compressed to taxonomic concept mapping.

## Key sources

- Müller et al. (2024), *A Taxonomic Concept Mapping Service for Taxonomic Information Aggregators*.
- Rees, Franz & Sterner (2026), *A scalable exemplar-based method for aligning biological taxonomies*.
- TDWG Taxonomic Concept Transfer Schema / RCC-5 literature.

Historical candidate evidence is retained here only to prevent resurrection under a new LLM/entity-linking wrapper.
