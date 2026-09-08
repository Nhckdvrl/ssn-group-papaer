# L09 — Minimum Decisive Pilot Card

**Candidate:** RLVR Disagreement: Erased or Suppressed?  
**Status:** SERIOUS / A-  
**Goal:** Determine whether RLVR removes human-disagreement information from representation or merely suppresses its expression.

## Established parent result
EACL 2026 establishes that RLVR-style reasoning degrades modeling of human annotator disagreement across multiple tasks.

We do **not** re-claim the behavioral degradation.

## Gold
Use datasets with repeated human labels / distributions from the parent setup, including suitable subsets of:
- GoEmotions;
- Gab Hate Corpus;
- HelpSteer2 / preference-style data.

The load-bearing target is the **human label distribution / disagreement quantity**, not a synthetic ambiguity label.

## Model requirement
Need a credible matched pre/post reasoning-training pair:
- released open checkpoints with clear lineage; or
- train one controlled open 7B/8B pair with modest RLVR/GRPO and save intermediate checkpoints.

If lineage confounds cannot be controlled, do not make causal training claims.

## Stage 1 — Behavioral reproduction
Reproduce the human-disagreement degradation on at least two task types.

## Stage 2 — Representation preservation
Collect hidden states layerwise before/after RLVR.

Measure whether human-distribution quantities remain decodable:
- entropy/disagreement level;
- minority-label probability;
- full label distribution where feasible.

Use cross-validated probes and cross-check with representation similarity.

Probe results alone are **not enough**.

## Stage 3 — Causal test
At minimum one:
- activation patching pre→post;
- targeted steering along a disagreement-related direction;
- readout/logit intervention.

Decisive question:
> Can disagreement behavior be restored without undoing reasoning gains?

## Informative outcomes
### A — Erasure
Internal disagreement information declines and pre→post patching restores it.

### B — Suppression
Information remains internally decodable; late/readout intervention restores expression.

### C — Selective change
Ambiguity, subjectivity, emotion, or preference disagreement behave differently.

### D — Calibration/format artifact
Alternative elicitation/temperature recovers the distribution without representation intervention.

All are valid.

## Required controls
- base vs post-RLVR same tokenizer/architecture;
- temperature/output-format controls;
- single-label accuracy so disagreement recovery is not just worse classification;
- reasoning-performance preservation under any recovery intervention.

## Kill conditions
Kill if:
- only probe accuracy changes;
- model-pair confounds dominate;
- degradation is fully output-format/temperature artifact with no broader measurement conclusion;
- no causal intervention is feasible;
- a direct modern paper already performs the same matched representation-vs-readout decomposition.
