# L36 — Mode-Seeking Stability Transition

**Status:** **ACTIVE — REFRAMED MAIN CANDIDATE / E05 GATE REQUIRED**  
**Primary target:** ACL / EMNLP / NAACL Main  
**Date:** 2026-09-17

Authoritative project definition: [`ACTIVE_PROJECT.md`](ACTIVE_PROJECT.md)  
Sequence-level novelty re-audit: [`SEQUENCE_LANDSCAPE_REAUDIT.md`](SEQUENCE_LANDSCAPE_REAUDIT.md)  
Next decisive experiment: [`E05_SEQUENCE_LANDSCAPE_PREREGISTRATION.md`](E05_SEQUENCE_LANDSCAPE_PREREGISTRATION.md)  
Historical controlled sandbox: [`E02_PREREGISTRATION.md`](E02_PREREGISTRATION.md) · [`results/e02/E02_RESULTS.md`](results/e02/E02_RESULTS.md)

## Current research question

> **Why does progressively mode-seeking search degrade classical sequence models, while many modern post-trained LMs appear more stable, and what structural change in the full sequence-level probability landscape accounts for that transition?**

The same-lineage version is:

> **How do Base → SFT → preference/RL stages reorganize the relation among sequence mode, typical probability mass, multi-token search path, and task utility?**

## What changed on 2026-09-17

The former paper identity, **Learning the Generation Boundary**, was too narrow.

Beam search scores complete multi-token sequences. The immediate `[EOS]` path is one important degenerate candidate, but our own Olmo results show severe wide-search quality loss with zero empty outputs and nearly normal length. Therefore EOS/termination cannot be the universal explanation.

The correct hierarchy is:

```text
mode-seeking degradation
  ├─ termination / empty / short basin          [one channel]
  ├─ generic / off-target high-probability basin
  ├─ source-copy basin
  ├─ repetition / semantic failure basin
  └─ other high-probability model errors
```

The old EOS-rank and controlled-boundary experiments remain useful, but only as channel-specific evidence.

## Novelty boundary

Existing work already owns:

- classical beam degradation and length bias;
- exact empty modes in NMT;
- sequence-level premature termination / oversmoothing;
- multi-token discrepancy explanations of beam degradation;
- MAP/mode vs probability-mass mismatch;
- the generic probability-quality paradox;
- modern observations that LLM-MT is less affected by the classical beam challenge;
- explicit likelihood-quality calibration in LLM-MT;
- post-training semantic diversity / mode collapse.

Therefore L36 must **not** claim novelty for any of those facts individually.

The remaining plausible contribution is the **transition**:

> **how the utility of increasingly mode-like outputs changes from classical/base models to post-trained LMs, and what full-sequence probability reorganization produces that change.**

This is a training-stage / regime-transition question, not a static correlation study.

## Evidence retained from the earlier project

- matched RAW classic-vs-Gemma endpoint difference;
- Olmo and Tülu stage lineages;
- Olmo base non-empty degradation, which proves EOS is not universal;
- termination rank / intervention as a special-channel case study;
- E02 matched SFT as a narrow demonstration of format-conditioned `<END>` placement;
- cross-implementation measurement audits.

## E05 gate

E05 tests the broader story using:

1. raw-beam **search–utility trajectories**;
2. independent likelihood-ranked **Best-of-N** mode seeking;
3. **Mode–Mass Gap** between mode-like outputs and typical samples;
4. **common-candidate cross-stage rescoring** of identical full sequences;
5. **multi-token search-path geometry**, plus a secondary length-conditioned score envelope.

A Main story requires that the transition survive beyond EOS, beyond beam implementation, and beyond candidate-set changes.

## Kill conditions

Downgrade the Main-level reframe if:

- no reproducible mode-seeking-stability transition appears across at least two modern lineages;
- the effect disappears under likelihood-ranked Best-of-N;
- common-candidate rescoring shows no adequate-vs-pathological probability reordering;
- modern post-trained systems have mode–mass gaps comparable to base/classical systems;
- the difference is explained entirely by stopping/normalization/prompting conventions;
- only the termination channel changes while non-empty mode pathology remains unchanged.

## Current verdict

```yaml
status: ACTIVE_REFRAMED_MAIN_CANDIDATE
primary_target: ACL_EMNLP_NAACL_MAIN
scientific_object: SEQUENCE_LEVEL_MODE_SEEKING_STABILITY
old_uncertainty_identity: RETIRED
old_generation_boundary_identity: DEMOTED_TO_SUBMECHANISM
termination_channel: REAL_BUT_PARTIAL
e02_role: NARROW_CAUSAL_SANDBOX
novelty: PLAUSIBLE_REQUIRES_E05
main_ready: NO
next_gate: E05_SEQUENCE_LANDSCAPE_AUDIT
continue: YES
```
