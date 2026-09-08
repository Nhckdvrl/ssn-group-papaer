# L09 — Research Plan

**Candidate:** RLVR Disagreement: Erased or Suppressed?

---

## 1. Minimum decisive pilot

### Stage 1 — behavior reproduction
Use the official EACL data.

Select:
- one hate-speech task;
- one GoEmotions ambiguity subset;
- one preference task if compute allows.

Reproduce the RLHF/CoT/RLVR disagreement gap.

### Stage 2 — open model pair
Choose one open-weight before/after reasoning-training pair or create a controlled small RLVR pair.

### Stage 3 — layerwise diagnostic
For ~500–2,000 items:
- collect hidden states;
- predict human disagreement quantities layerwise;
- compare pre/post RLVR.

### Stage 4 — one causal test
Patch or steer the strongest candidate layer/subspace.

The topic should not be promoted on probe results alone.

## 2. Outcome routes

### Route A — Erasure
Post-RLVR representations lose human-distribution information broadly.

Needed evidence:
- reduced cross-validated decodability;
- pre→post patch restores behavior;
- later readout-only intervention cannot recover it.

Scientific claim:
> RLVR training trades away a real class of plural-interpretation information.

### Route B — Suppression
Representation information remains, but output distribution collapses.

Needed evidence:
- comparable internal decodability;
- later-layer/readout intervention restores disagreement behavior.

Scientific claim:
> post-training changes expression/action, not underlying interpretation.

### Route C — Selective change
Different disagreement types/local layers behave differently.

Scientific claim:
> RLVR preserves some ambiguity but suppresses value/subjectivity information, or vice versa.

### Route D — Calibration/expression artifact
Alternative elicitation recovers the human distribution without hidden-state change.

Scientific claim:
> behavioral disagreement metrics overstate representational information loss.

## 3. Controlled RLVR training design

If released checkpoint lineage is too messy:

- base: one 7B/8B open instruction model;
- objective training: math/logic or other verifiable-reward data;
- algorithm: GRPO/RLVR-style;
- modest training sufficient to induce the known reasoning-policy shift;
- save checkpoints through training.

Then measure:
> disagreement behavior + representation trajectory over RLVR steps.

This can be especially strong because it turns “before vs after” into a training-time causal curve.

## 4. Phase 2 — Layer localization

Questions:
- does disagreement information disappear early, mid, or only near output?
- does RLVR change minority-label directions or only the decision boundary?
- are HighVar examples affected more strongly?

Use:
- cross-layer probes;
- representational alignment;
- causal patch windows.

## 5. Phase 3 — Recovery

The decisive Main-level move:

> If information is still present, can we restore human-distribution behavior **without undoing reasoning capability**?

Test a small intervention:
- steering;
- readout adjustment;
- activation patching.

Measure both:
- disagreement modeling;
- original reasoning performance.

A selective recovery result is much stronger than probing.

## 6. Planned C1 → C2 → C3

### C1
Did RLVR erase disagreement information or merely suppress expression?

### C2
Where/how does the change happen, and which disagreement types are affected?

### C3
Can plural human interpretations be recovered without sacrificing reasoning capability?

## 7. Kill conditions

KILL if:
- only probe metrics differ;
- no causal recovery/erasure test is possible;
- model-pair confounds dominate;
- the effect is fully explained by sampling temperature/output formatting;
- a direct modern paper already performs the same representation-vs-readout decomposition.

## 8. Main-level expansion

Require:
- ≥2 disagreement task types;
- ≥2 model/training settings;
- repeated-human-label gold;
- causal intervention;
- reasoning-performance preservation check;
- clear separation from generic uncertainty calibration.

## 9. Paper skeleton

1. Established RLVR disagreement degradation.
2. Erasure vs suppression hypotheses.
3. Matched/open model setup.
4. Layerwise information trajectory.
5. Causal patch/steering.
6. Task-type boundaries.
7. Recoverability vs reasoning trade-off.

## Final pilot verdict

**SERIOUS / PILOT-WORTHY once a clean open pre/post RLVR pair is secured.**
