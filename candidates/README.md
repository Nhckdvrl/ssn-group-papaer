# Serious Candidate Portfolio — 2026-09-09

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Current user-selected execution priority:** **L08**

> candidates/ contains serious topics under active comparison.  
> good/ contains candidates that have already crossed the current pre-pilot authorization bar.  
> Neither directory protects a topic from later death.

For execution, start from **../LOCAL_AGENT_START.md** and then the chosen candidate package.

---

# Current eight-topic pool

| ID | Candidate | Status | Canonical package |
|---|---|---|---|
| **L03** | Table Value ≠ Observation Status | **PILOT-AUTHORIZED** | [../good/L03_TYPED_OBSERVATION/](../good/L03_TYPED_OBSERVATION/) |
| **L06** | Study Identity Is Not Document Identity | **SERIOUS / PILOT-READY** | [L06_STUDY_IDENTITY/](L06_STUDY_IDENTITY/) |
| **L07** | Official Correction ≠ Current Scholarly Claim | **SERIOUS / DATA AUDIT FIRST** | [L07_OFFICIAL_CORRECTION/](L07_OFFICIAL_CORRECTION/) |
| **L08** | Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning | **SERIOUS / CURRENT PRIORITY** | [L08_READOUT_DIMENSION/](L08_READOUT_DIMENSION/) |
| **L09** | RLVR Disagreement: Erased or Suppressed? | **SERIOUS** | [L09_RLVR_DISAGREEMENT/](L09_RLVR_DISAGREEMENT/) |
| **L10** | Success Teaches, Failure Doesn't? | **SERIOUS** | [L10_SUCCESS_FAILURE_ASYMMETRY/](L10_SUCCESS_FAILURE_ASYMMETRY/) |
| **L11** | Task Gradient ≠ Learning Pressure | **PILOT-AUTHORIZED** | [../good/L11_TASK_GRADIENT_PRESSURE/](../good/L11_TASK_GRADIENT_PRESSURE/) |
| **L12** | Reasoning Training: Canonicalization or Policy Override? | **PILOT-AUTHORIZED** | [../good/L12_REASONING_DECISION_INVARIANCE/](../good/L12_REASONING_DECISION_INVARIANCE/) |

Eight active candidates ≠ eight approved projects.

---

# Portfolio rule

Every candidate must keep answering:

1. What is the simple natural RQ?
2. What is genuinely uncertain?
3. What data/intervention actually identifies it?
4. What does prior work already own?
5. What is our paper-level identity?
6. If the expected first account loses, what remains scientifically meaningful?
7. What is the smallest decisive next experiment?
8. What exactly kills or reconstructs the topic?
9. Does the developing paper still look like a strong ACL/EMNLP/NAACL Main contribution?

Use **../RESEARCH_TOPIC_SELECTION.md** for the authoritative gates.

---

# Candidate-package flexibility

Candidate documents should not rigidly prescribe the answer.

They should:
- protect the natural RQ;
- define the evidence standard;
- record novelty ownership;
- prevent reviewer-compressible drift;
- preserve outcome robustness;
- keep Main-level calibration explicit.

They may leave open:
- exact method;
- exact account;
- exact analysis stack;
- exact claim ordering;
- stronger reconstructions discovered during pilots.

A method is replaceable. The scientific standard is not.

---

# Current candidate notes

## L03
External-state / measurement candidate. Main risk: becoming code-decoding or missing-value evaluation rather than a consequential observation-state representation question.

## L06
Hold paper contents fixed and manipulate study identity only. Main risk: collapsing to a grouping ablation instead of an evidence-unit representation result.

## L07
Do proposition-level old→new correction-yield audit before target-model compute. Main risk: most official corrections being metadata/typo changes rather than scientific-claim updates.

## L08 — current priority
Parent anomaly is already established; novelty must explain it. First useful split remains teacher forcing vs free running, but the final mechanism is not pre-committed.

## L09
Must distinguish representation erasure from output/readout suppression, preferably with causal recovery. Probe-only evidence is below the intended identity.

## L10
Must preserve matched positive-vs-negative experience and stage decomposition. Do not regress to generic “agents do not learn from failure.”

## L11 — newly pilot-authorized
Established multi-task RL gradient/gain paradox. Keep the paper on:
- source and meaning of optimization loudness;
- parameter vs functional learning pressure;
- causal validation;
- consequence for multi-task post-training.

Do not regress to gradient balancing.

## L12 — newly pilot-authorized
Established reasoning-induced risky-decision invariance. Keep the paper on:
- training-induced mechanism;
- canonicalization vs preserved-context/policy override vs other decisive accounts;
- same-family controlled transition;
- causal/boundary evidence;
- consequence for interpreting reasoning-model rationality.

Do not regress to another framing benchmark or probe-only paper.

---

# Package discipline

Canonical five research documents:
- README.md
- DATA_AND_GOLD.md
- RELATED_WORK_AND_NOVELTY.md
- RESEARCH_PLAN.md
- PILOT_CARD.md

During execution, keep code/data/results/claims/experiments inside that candidate directory.

Do not create more top-level process documents.
