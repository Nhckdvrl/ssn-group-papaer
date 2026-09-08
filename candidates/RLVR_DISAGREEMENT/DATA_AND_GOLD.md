# RLVR Disagreement — Data and Gold

## 1. Load-bearing gold

The scientific target is the **human annotator distribution**, not a majority-vote label.

For each item, gold should include counts/proportions over human labels so we can ask whether model distributions preserve meaningful variation.

The EACL 2026 parent already evaluates disagreement modeling on three tasks and should be reused where licensing/release permits.

Source: https://aclanthology.org/2026.eacl-long.3/

## 2. Required model comparison

Strongest identification uses matched or near-matched model families:
- RLHF/instruction model;
- RLVR/reasoning-tuned counterpart;
- ideally base checkpoint where available.

Avoid comparing unrelated models and attributing all differences to RLVR.

## 3. Behavioral quantities

For each item/model:
- predicted label distribution under the parent paper's established elicitation methods;
- majority-label accuracy;
- divergence from human distribution (e.g. JS/KL/TV as appropriate);
- entropy / concentration;
- calibration secondary.

The paper is not about maximizing one metric; it is about locating where information is lost.

## 4. Representation quantities

At multiple layers extract states from a fixed decision position and test:
- linear/nonlinear decoding of the human distribution or disagreement degree;
- alternative-label evidence;
- similarity of RLHF vs RLVR representations;
- whether human-distribution information survives after controlling majority-label information.

Probe split must prevent lexical/item leakage.

## 5. Causal interventions

At least one is required for Main-level mechanism:

### A. Activation steering
Derive a direction/subspace associated with higher probability of the underexpressed human alternative and intervene during RLVR inference.

### B. Activation patching
Patch hidden states from matched RLHF into RLVR at selected layers/positions and test whether disagreement distribution is restored.

### C. Readout replacement/calibration
Apply a lightweight learned readout on frozen RLVR representations. If human distribution is recovered without changing representations, this supports suppression/readout mismatch.

A probe alone is insufficient.

## 6. Task stratification

Use disagreement types close to the parent datasets and, where possible, separate:
- lexical/semantic ambiguity;
- subjective judgment;
- affect/emotion;
- socially/value-sensitive labels.

Do not invent disagreement-type labels unless an existing taxonomy or deterministic dataset mapping exists; otherwise use dataset/task identity as the primary boundary.

## 7. Primary metrics

- human-distribution divergence;
- majority-label accuracy;
- disagreement-preservation score;
- probe/decoding performance with leakage controls;
- causal intervention recovery amount;
- accuracy–distribution tradeoff.

## 8. Data-validity kill conditions

KILL/demote if:
- datasets provide only majority labels rather than annotator distributions;
- no matched RLHF/RLVR comparison can be constructed;
- apparent hidden-state signal disappears under held-out-item/probe controls;
- steering changes outputs generically without selectively restoring human disagreement;
- RLVR behavioral degradation does not replicate on available checkpoints.
