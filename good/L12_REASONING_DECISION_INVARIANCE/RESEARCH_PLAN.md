# L12 Research Plan

**Status:** evidence program complete; manuscript synthesis next

## Core RQ

> Why do reasoning models become invariant to some changes in presentation while
> remaining sensitive to others, and does reasoning reallocate causal decision
> control from prompt form toward an evidence-bearing trajectory and its state?

## Final explanatory chain

1. **Construction:** natural reasoning develops decision direction before the
   explicit commitment; the commitment strongly consolidates it.
2. **Carrier:** the trajectory builds a late pre-answer state that can transfer
   decision direction without donor text.
3. **Reallocation:** reasoning regimes give the trajectory/state more relative
   control than standard instruction regimes.
4. **Selective consequence:** the new controller suppresses sensitivity to form
   while preserving or amplifying sensitivity to evidence.

## Completed load-bearing program

| Claim layer | Lead evidence | Breadth/confirmation |
|---|---|---|
| Construction and consolidation | E07 terminal stripping and opposite trajectories; E08 state profile | E11 frozen state replication; E19 on 48 natural decisions; E15 external triangulation |
| Causal-control reallocation | E09 prompt-by-trajectory factorial | E10 36 decisions; E12 DPO persistence; E13 Qwen same weights; E17 151 decisions; E18 untouched confirmation |
| Selective sensitivity | E20 prospective 2 form x 2 evidence behavior | E20-C trajectory control; E21 state content; E22 external Llama ecosystem |

E18P rules out low generation count as the source of OLMo's heldout behavioral
null. E18L is a completed but inconclusive appendix diagnosis because 100-trial
raw tables cause severe reasoning truncation. Neither is a headline claim.

## Manuscript work plan

1. Build the introduction around the ambiguity of behavioral invariance, not
   activation patching.
2. Present E18's OLMo dissociation as the observation that reveals a construct
   confound, then preserve chronology into prospective E20.
3. Use three claims only: construction/state, control reallocation, selective
   evidence sensitivity.
4. Keep model/checkpoint results under those claims rather than promoting every
   replication into a contribution.
5. Regenerate all tables and the three-panel story figure from tracked summaries.
6. Run an adversarial compression review against the closest current papers in
   `RELATED_WORK.md` before freezing the abstract.

## Expansion rule

No more model-zoo, layer-search, snippet, or truncation experiments are planned.
A new experiment must answer a specific inference exposed by manuscript review
and must deepen the three-claim chain. A surprising result may reconstruct the
story only if it survives an independent confirmatory design; it may not become a
post-hoc subgroup claim.

## Decision rule

- **GO:** the present state. Prospective selective sensitivity, causal trajectory
  control, state mediation, and external breadth all agree.
- **RECONSTRUCT:** a manuscript-level audit finds that form/evidence selectivity
  is fully compressed by a direct prior or that the causal bridge cannot support
  the narrative.
- **HOLD/KILL:** raw/result provenance fails, the independent-unit analysis does
  not regenerate, or a fresh paper owns the entire identity rather than one
  ingredient.
