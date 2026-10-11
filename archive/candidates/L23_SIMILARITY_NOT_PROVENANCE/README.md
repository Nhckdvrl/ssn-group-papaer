# L23 — Similarity Is Not Provenance

**Status:** **SERIOUS / PRE-PILOT — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## One-sentence RQ

> **When an LLM-generated scientific idea strongly overlaps with an existing paper, can that observable similarity identify source-specific copying, or can the same level of overlap arise through independent reconstruction from shared antecedent literature?**

## Plain example

A generated proposal has an almost one-to-one methodological mapping to Paper X. That looks like copying. But if the generator was frozen **before Paper X existed** and was given only literature available before X, then the same mapping cannot have come from copying X. The observable overlap is the same; the provenance is different.

## Scientific pressure

This question is created by several independent literatures rather than one unexplained anomaly:

1. ACL 2025 Outstanding *All That Glitters is Not Novel* operationalizes strong one-to-one / substantial methodological overlap with uncited prior work as evidence of smart plagiarism and carefully restricts candidate source papers to the generator's training-cutoff window.
2. 2026 *HindSight* shows that systems restricted to pre-cutoff literature can generate ideas that later appear in real future publications.
3. 2026 *Reconstruction* shows that a model given only a seed paper's pre-publication bibliography can recover the held-out seed idea at non-zero rates.
4. Classical copying/provenance identification distinguishes substantial similarity from copying because coincidence, independent creation, and prior common source can produce similarity without source-specific reliance.

Together these results create an unresolved identification problem: **similarity is observable; provenance is causal.**

## Prior work owns

- AI-generated research can strongly overlap with earlier papers and current plagiarism detectors often miss that overlap.
- LLMs can reconstruct / forecast real research ideas from antecedent literature under temporal information restrictions.
- Training-data attribution and copyright theory both warn that source-specific causal reliance is stronger than output similarity.
- Automated research-idea novelty judgment is already an active benchmark area.

## Prior work does NOT yet own

A controlled NLP experiment where **copying and impossible-copying independent convergence are known by construction**, output overlap is matched, and human/LLM evaluators are tested on whether they can actually infer provenance from the generated idea.

## Decisive operation

Construct two known-DGP conditions:

### A. Impossible-copy / independent reconstruction
Use a fully open model whose entire training/post-training predates the target paper. Give it only references available before that paper. Any generated idea matching the future paper cannot have been copied from that target.

### B. Source-exposed / copying-compatible
Expose the same model to the target idea/source before generation, then produce a proposal without attribution.

Match A and B on observed methodological/semantic overlap with the target, then ask evaluators to classify source reliance / plagiarism-like copying from the output alone.

The key estimand is not raw similarity. It is:

> **P(evaluator infers copying | matched overlap, true provenance DGP)**

## Natural data / hard leverage

Promising substrate: the 2026 *Reconstruction* seed set (ICML 2026 Oral + 2026 Nature Astronomy/Chemistry/Materials/Medicine/Physics papers) with pre-publication bibliographies.

Promising generator: OLMo-2 32B Instruct, released 2025-03-13 with fully open pretraining, mid-training, post-training artifacts. Restrict targets to papers whose first public appearance is demonstrably later than the model's complete training pipeline.

This gives hard temporal negative controls for target-specific copying without author-written scientific gold.

## Successful-result test

All major outcomes are informative:

- **High false-positive copying judgments on impossible-copy matches:** overlap-based plagiarism/provenance judgments are not identified; independent reconstruction creates a real false-positive floor.
- **Near-zero false positives at high overlap:** strong overlap is empirically highly diagnostic even under a hard independent-creation control, strengthening rather than attacking existing plagiarism measurements.
- **Heterogeneous result:** identify which idea/literature structures make independent convergence likely, yielding a boundary for when similarity is or is not provenance evidence.

The paper must not depend on obtaining a large false-positive rate.

## Development path

1. **Identification:** establish hard impossible-copy and source-exposed DGPs.
2. **Matched-overlap test:** compare provenance judgments after controlling observed similarity.
3. **Reconstructability:** estimate how readily an idea follows independently from its antecedent literature and test whether this predicts false provenance attribution.
4. **Consequence:** assess how novelty/plagiarism evaluation changes when similarity is calibrated by independent-reconstruction probability rather than treated as source-specific evidence by itself.

## Strongest reviewer compression

> “All That Glitters + HindSight/Reconstruction, with a temporal cutoff.”

### Why that compression may not win

Those papers establish opposite observable possibilities—strong overlap with prior work, and recovery of future/held-out ideas from prior literature—but none directly asks whether **the same overlap observable identifies the causal provenance that plagiarism/copying language assumes**. The proposed paper's central object is the **specificity of provenance inference under a gold impossible-copy control**, not research-idea generation quality or another plagiarism detector.

## Main risks before pilot

1. **Neighbor risk:** a very recent NLP provenance/plagiarism study may already contain an independent-creation negative control; refresh immediately before authorization.
2. **Generation yield:** the cutoff-safe open model must produce enough high-overlap future-paper reconstructions for overlap-matched comparison. If yield is effectively zero, paper scale may collapse.
3. **Post-training cutoff audit:** every target must postdate every relevant OLMo-2 training/post-training source, not merely pretraining.
4. **Judgment construct:** keep the claim on source-specific copying/provenance identification; do not drift into legal copyright conclusions or intent attribution.

## Minimum kill-oriented pilot — NOT YET AUTHORIZED

Before compute authorization, audit a small target sample for exact first-public dates and confirm that a cutoff-safe open instruct model plus the released pre-publication bibliography can generate scientifically coherent hypotheses. Only then define the smallest overlap-yield pilot.

## Kill conditions

- A direct recent owner already evaluates copying vs independent scientific-idea reconstruction under known exposure DGPs.
- Hard temporal exclusion of target exposure cannot be guaranteed after full pre/mid/post-training audit.
- The only usable generator is too weak to produce meaningful research proposals, making the no-copy condition structurally empty.
- The final contribution compresses merely to better semantic plagiarism detection rather than provenance identifiability.
