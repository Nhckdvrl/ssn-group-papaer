# RLVR Disagreement — Minimum Decisive Pilot

## Pilot question

> After RLVR reduces agreement with human annotator distributions, is the missing alternative-label information still present in hidden states?

## 1. Minimal model pair

Use one model family with a clean pre-RLVR / RLVR pair if available. Add a second family only after the mechanism is visible.

The pilot should avoid unrelated-model comparisons.

## 2. Pilot data

Reuse one or two disagreement datasets from EACL 2026 with full annotator distributions. Sample enough items to cover:
- high agreement;
- moderate disagreement;
- high disagreement.

Use held-out lexical/topic splits for probing.

## 3. Stage A — behavioral replication

Confirm:
- RLVR distribution is more concentrated than RLHF/pre-RLVR;
- majority-label accuracy is not enough to explain the difference;
- the parent effect is present in the chosen checkpoints.

If this fails, stop.

## 4. Stage B — representation test

At multiple layers decode:
- human disagreement degree;
- probability/evidence for the minority label;
- full human label distribution when feasible.

Compare RLHF vs RLVR under identical prompts and decision positions.

Critical result patterns:
- RLVR behavioral collapse + preserved hidden signal -> suppression candidate;
- behavioral collapse + hidden signal collapse -> erasure candidate.

## 5. Stage C — causal recovery

Minimum one:
- patch RLHF activations into RLVR;
- train a lightweight frozen-representation readout;
- steering along a disagreement/alternative-label direction.

Success criterion is **selective recovery toward the human distribution without generic accuracy collapse**.

## 6. Outcome branches

### A — Information preserved and recoverable
Strong promotion: RLVR changes readout/action expression more than representation. C3 can test cheap recovery.

### B — Information erased
Strong promotion if matched checkpoints and controls support it. This implies post-training removes a meaningful type of information.

### C — Selective preservation
Promote if there is a stable boundary by task/disagreement type/layer and it explains the behavioral result.

### D — Probe signal ambiguous, no causal recovery
Do not promote to Main merely on probe accuracy. KILL or redesign.

## 7. Controls

- majority-label-only probe;
- shuffled human distributions;
- label-frequency baseline;
- random-direction steering;
- matched intervention magnitude;
- check that recovery is not just entropy inflation.

## 8. Main-level promotion condition

The pilot must tell us **whether the information was lost or merely silenced**. Anything weaker is an incremental follow-up to EACL 2026.