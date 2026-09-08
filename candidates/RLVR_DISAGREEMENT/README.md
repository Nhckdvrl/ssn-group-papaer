# RLVR Disagreement: Representation Erasure or Output Suppression?

**Status:** SERIOUS CANDIDATE / A-  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-08

> **Plain-language thesis:** RLVR-style reasoning models become worse at matching genuine human disagreement. The key question is whether alternative interpretations were erased from the model or remain internally represented but suppressed at output.

## 1. One-sentence RQ

> When RLVR-style reasoning collapses a human disagreement distribution toward one answer, **did training erase the alternative interpretations, or are they still represented internally but no longer expressed?**

## 2. Established phenomenon

EACL 2026 shows across 3 tasks and 60 experimental settings that RLVR-style reasoning degrades modeling of human annotator disagreement, while naive CoT can improve RLHF models.

Source: https://aclanthology.org/2026.eacl-long.3/

Therefore we do not need to discover the behavioral effect.

## 3. Natural object

Human disagreement is often meaningful rather than annotation noise:
- ambiguity;
- subjectivity;
- different perspectives/value systems.

If post-training collapses these distributions, two very different scientific stories are possible:

### Account A — Representation erasure
Alternative interpretations are no longer recoverable from hidden states.

### Account B — Readout/output suppression
Internal states still encode disagreement, but decision/output layers force a single answer.

### Account C — Selective erasure
Some disagreement types survive internally while others are genuinely removed.

## 4. Why ACL / NLP cares

The conclusion determines whether recovering human variation requires:
- retraining/model changes;
- a different readout/calibration layer;
- or task-specific steering.

It also changes how reasoning-trained models should be used as annotator substitutes.

## 5. Outcome robustness

All outcomes matter:
- hidden disagreement preserved and causally recoverable -> output collapse;
- hidden disagreement absent -> representation loss;
- layer/type-specific preservation -> mechanistic boundary map;
- RLHF and RLVR differ only in calibration but not representation -> narrower but still clear readout conclusion.

## 6. Paper identity

**Primary identity:** post-training mechanism / representation-preservation paper for human variation.

**Not:**
- another disagreement benchmark;
- another “RLVR hurts calibration” result;
- generic probing;
- fairness/bias measurement alone.

## 7. C1 → C2 → C3

### C1
Replicate the behavioral disagreement gap in matched model pairs/checkpoints.

### C2
Determine whether human disagreement information remains decodable and causally actionable across layers after RLVR.

### C3
Test whether a lightweight readout/steering intervention can recover human distributions without sacrificing task accuracy, or whether representation must be relearned.

## 8. Five gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Human label distributions are externally observed and meaningful. |
| SCIENTIFIC TENSION | **YES** | Erasure vs suppression make very different predictions. |
| GOOD DATA | **YES** | Existing disagreement datasets provide full human label distributions; matched model/checkpoint outputs are directly measurable. |
| NOVELTY | **PROVISIONAL YES** | EACL 2026 establishes behavioral degradation but does not causally decompose representation erasure vs readout suppression. |
| OUTCOME ROBUST | **YES** | Preserved, erased, or selective representations all support substantive conclusions. |

## 9. Main danger

> **“This is just EACL 2026 + a linear probe.”**

Fatal if true. The paper needs causal recovery or intervention, not merely decodability.

## 10. Directory map
- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `PILOT_CARD.md`
