# L28 — Canonical Species ID ≠ Source Taxonomic Concept

**Status:** **SERIOUS SEED — DOWNSTREAM CONSEQUENCE / SCALE AUDIT — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## One-sentence RQ

> **When scientific IE / entity linking normalizes species mentions from heterogeneous literature to one canonical taxonomy ID, does that preserve the taxonomic concept intended by each source, or can normalization silently merge evidence that the source taxonomies treat as different or only partially overlapping biological entities?**

## Plain example

Two papers both use the same Latin species name. A standard entity linker maps both mentions to the same current GBIF/NCBI-style species ID. But the two source taxonomies may circumscribe that name differently: one concept can properly include, overlap, or exclude part of what the other source means. Joining their occurrence, trait, or distribution records as if they referred to exactly the same biological entity can therefore create a scientifically invalid aggregation.

## Why this question exists independently of LLMs

This is a long-standing biodiversity-information problem, not a benchmark invention.

The TDWG Taxonomic Concept Transfer Schema (TCS) was created because scientific names do not unambiguously identify taxonomic concepts across different taxonomic viewpoints. It explicitly recommends richer identifiers such as a name plus its defining source (`AccordingTo`). RCC-5 taxonomic alignment represents whether concepts are congruent, disjoint, overlap, or stand in proper-part relations.

The downstream consequence is also pre-existing: biodiversity systems aggregate occurrence, specimen, trait, and distribution records across taxonomies, and classical work shows that name/synonym-based integration loses accuracy when the assumed one-to-one name↔entity mapping fails.

## Why it is newly consequential for NLP / LLM systems

Modern biodiversity/scientific IE systems increasingly extract species mentions, normalize synonyms/common names, and link them to a canonical reference taxonomy or knowledge-graph node. This is convenient for large-scale literature integration, but the standard output unit can collapse the source-relative concept distinction before downstream reasoning begins.

The paper is therefore **not** `can an LLM understand taxonomy?`. It asks whether a common modern NLP operation — canonical entity normalization — is semantics-preserving for a scientific domain whose authoritative representation says entity identity is source-relative.

## Natural gold

A particularly clean public substrate is the RCC-5 alignment of two influential primate classifications (MSW2 vs MSW3):

- 317 vs 483 taxonomic concepts;
- 402 expert input articulations;
- 153,111 logically inferred concept-pair relations;
- the associated paper reports that close to one third of taxonomic names cannot safely stand in for the same meaning across the two treatments.

Additional public RCC-5 alignments exist for other taxonomic revisions, so the route is not necessarily restricted to one taxonomy pair.

## Prior work owns

- the classical name-versus-taxonomic-concept distinction;
- TCS / RCC-5 representations and logic-based taxonomy alignment;
- entity recognition/linking of taxon mentions to NCBI, GBIF, TAXREF and other reference taxonomies;
- dynamic / emerging / obsolete-entity handling in modern entity linking;
- biodiversity knowledge graphs that can represent source-specific taxonomic concepts.

## Potential unowned bridge

Whether **current scientific IE / entity-normalization practice preserves or destroys source-relative taxonomic concept identity**, and what minimum representation is sufficient to avoid invalid cross-source evidence joins.

Current entity-linking work largely asks whether a mention maps to the correct current KB entity. Historical/obsolete-entity work handles changing vocabularies. Neither is identical to the stronger case here: the same accepted name can intentionally denote non-congruent concepts under different authoritative taxonomic treatments.

## Decisive operation

1. Start from expert RCC-5 concept alignments.
2. Apply standard name/canonical-ID normalization to both source taxonomies.
3. Identify cases where normalization collapses two source mentions to one canonical identity although RCC-5 gold says the source concepts are not congruent.
4. Attach or recover natural occurrence / trait / distribution / specimen records that inherit those source concepts.
5. Measure which joins/aggregations become licensed under canonical-ID normalization but are not licensed under concept alignment.
6. Test whether full-text LLM/IE systems can recover the missing source-relative concept state and whether a minimal `<name, source>` / concept-aware output prevents the invalid merge.

The strongest result should be an **identified representation failure with downstream data-integration consequences**, not an error-rate benchmark.

## Successful-result test

- **Many canonical collisions with real invalid joins:** strong evidence that current entity normalization uses the wrong scientific unit.
- **Canonical ID is usually safe, with failures concentrated in particular revision structures:** useful boundary result identifying when cheap normalization is sufficient and when concept-aware linking is necessary.
- **Source metadata alone resolves nearly all cases:** a positive minimal-sufficient-representation result; the paper becomes about which information must survive extraction rather than model failure.
- **Collisions are rare or downstream joins barely change:** kill or demote; do not manufacture a phenomenon by searching for pathological taxa.

The paper does not require LLMs to perform badly. The representation itself can be tested against independent expert concept gold.

## Main blockers before pilot

1. **Downstream consequence:** connect RCC-5 concept relations to paper-scale natural occurrence/trait/distribution records so invalid joins are executable rather than hypothetical.
2. **Scale/diversity:** verify more than one taxonomic revision / organism group or show why one alignment is scientifically representative enough.
3. **Direct-owner refresh:** search specifically for 2025–2026 NLP/LLM work on source-relative taxon-concept linking, not merely taxonomic NER or dynamic KB linking.
4. **NLP identity:** the contribution must change scientific information extraction/integration practice; merely re-demonstrating a known taxonomy problem is insufficient.

## Kill conditions

- a direct recent NLP owner already evaluates source-specific taxon-concept identity under expert concept alignments;
- no scalable natural records can connect concept collapse to an actual downstream integration error;
- only a tiny handpicked set of pathological taxonomic names supports the effect;
- the final takeaway is merely `taxonomy experts already knew names are ambiguous` rather than a new result about modern IE/entity-normalization sufficiency.

## Anchors / sources

- TDWG Taxonomic Concept Transfer Schema: https://github.com/tdwg/tcs
- Franz et al., *Two Influential Primate Classifications Logically Aligned*: https://academic.oup.com/sysbio/article/65/4/561/1753624
- Public RCC-5 alignment data: https://datadryad.org/dataset/doi:10.5061/dryad.6jg71
- Sterner et al., *Wanted: Standards for FAIR taxonomic concept representations and relationships*: https://pmc.ncbi.nlm.nih.gov/articles/PMC9028594/
- TaxoNERD (taxon NER and linking to reference taxonomies): https://github.com/nleguillarme/taxonerd
- OpenBiodiv-O: https://pmc.ncbi.nlm.nih.gov/articles/PMC5774086/
