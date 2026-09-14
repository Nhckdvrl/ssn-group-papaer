# L36 — Learning the Generation Boundary

**Status:** **ACTIVE — MAIN CANDIDATE**  
**Primary target:** ACL / EMNLP / NAACL Main  
**Fallback:** Findings if replication / external-validity hardening does not clear Main  
**Date:** 2026-09-14

Authoritative project definition: [`ACTIVE_PROJECT.md`](ACTIVE_PROJECT.md)  
Controlled training experiment: [`E02_PREREGISTRATION.md`](E02_PREREGISTRATION.md) · [`results/e02/E02_RESULTS.md`](results/e02/E02_RESULTS.md)  
Historical audit: [`SELECTION.md`](SELECTION.md) · [`results/e00/E00_VERDICT.md`](results/e00/E00_VERDICT.md) · [`results/ext/CEILING_ASSESSMENT.md`](results/ext/CEILING_ASSESSMENT.md)

## Current research question

> **What does post-training teach a language model about when a response is allowed to end, and how does that learned generation boundary determine whether wide search can expose termination pathologies?**

The original intrinsic-uncertainty identity is retired. The active paper is about a **post-training-learned, format-conditional generation boundary** and its consequences for search.

## Why the project is now a Main candidate

The previous Findings ceiling depended on an unresolved reviewer compression: “old NMT work already says EOS/length bias causes the beam curse; modern chat models simply do not emit empty strings.” E02 supplies the missing causal identification.

Using one Qwen2.5-3B base model, identical En→De examples, identical training budget/seed, and a single shared neutral `<END>` symbol across all conditions:

- `A_ONLY` learns the boundary only in A: `p(<END>@true_end) = 0.966 / ~0` on A/B;
- `B_ONLY` gives the **symmetric reversal**: `~0 / 0.961`;
- `MIXED` learns both: `0.962 / 0.963`;
- trained-format decoding stays near reference length and improves from beam 1→64;
- untrained-format decoding runs on to roughly 4× reference length and collapses to BLEU ~6–8.

The result therefore cannot be reduced to different stop-token identities, different stop-set cardinalities, or one globally lower/higher EOS prior. **The boundary follows the format in which response termination was supervised.**

Registered P4 is **falsified**: translation ability is already near final before the boundary is fully learned. The revised claim is that the controlled SFT adds a generation boundary to a model that already has substantial translation competence; do not claim “boundary before capability.”

The masked-boundary arm is supporting only, not load-bearing.

## Full evidence chain

```text
post-training
  -> format-conditional generation boundary       [controlled E02]
  -> stop-event geometry shifts by orders         [Olmo-3 stage lineage]
  -> search exposure scale moves                  [rank / margin instrument]
  -> predicted onset interval is confirmed        [out-of-sample beam 128 vs 512]
  -> termination pathology appears / disappears   [classic vs modern + intervention]
```

Important: `rank_stop <= 2b` is an algorithmic exposure condition, **not** a new scientific law. Its contribution is as an instrument that allowed a pre-search measurement to predict where the termination-collapse channel would become accessible in another model/interface.

Also keep two beam-damage channels separate: termination collapse is not generic mode inadequacy. Olmo-3 base can lose BLEU under wide search with zero empty outputs and nearly full length.

## Main-level claim boundary

The paper may claim:

> **Post-training learns a format-conditional generation boundary that is separable from task competence; by reorganizing stop-event geometry, that learned boundary moves the search-width scale at which a classical termination pathology becomes accessible.**

It must not claim:

- “SFT teaches EOS” as novelty;
- that all beam-search degradation is termination;
- that the neutral-`<END>` E02 itself reproduces classic premature empty collapse;
- that P4 passed;
- that amended P1′ was frozen before all pilot evidence;
- that `NOEOSLOSS` cleanly proves necessity;
- that ACL 2022 is broadly refuted.

## Work remaining before Main-ready

1. Replicate the decisive A_ONLY / B_ONLY / MIXED factorial with additional seeds and preferably a second base-model family.
2. Audit boundary specificity in the untrained format: target-token NLL/accuracy before `<END>`, first-translation-span quality, and the full end-hazard profile. If content also fails badly, use the broader “format-conditional generation contract” wording rather than boundary-only causality.
3. Add one independent natural post-training lineage to the Olmo-3 stage result.
4. Add semantic MT evaluation, bootstrap uncertainty, and modest cross-model/language breadth for the classic↔modern endpoint.

These are claim-hardening and external-validity tasks. The central phenomenon is no longer a pilot gamble.

## Current verdict

```yaml
status: ACTIVE_MAIN_CANDIDATE
primary_target: ACL_EMNLP_NAACL_MAIN
fallback: FINDINGS
paper_identity: POSTTRAINING_LEARNS_FORMAT_CONDITIONAL_GENERATION_BOUNDARIES
original_uncertainty_identity: RETIRED
controlled_E02: PASS
symmetric_reversal: PASS
mixed_rescue: PASS
P4: FALSIFIED_AND_CLAIM_REVISED
out_of_sample_onset_prediction: PASS
classic_modern_termination_regime_shift: SUPPORTED
main_ready: NO_REPLICATION_AND_BOUNDARY_SPECIFICITY_AUDIT_REMAIN
continue: YES
```
