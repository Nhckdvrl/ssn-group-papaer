# L09 — Related Work and Paper-Level Novelty

**Candidate:** RLVR Disagreement: Erased or Suppressed?

---

## 1. Direct parent — EACL 2026

Ni et al., **“Can Reasoning Help Large Language Models Capture Human Annotator Disagreement?”**:
- studies disagreement modeling directly;
- compares reasoning settings;
- includes RLVR-style reasoning;
- evaluates 60 setups across 3 tasks;
- finds RLVR degrades disagreement modeling.

Source:
- https://aclanthology.org/2026.eacl-long.3/

Official companion repository:
- https://github.com/EdisonNi-hku/Disagreement_Prediction

What it owns:
- disagreement modeling as an LLM evaluation target;
- the RLVR behavioral degradation;
- task/model/steering comparisons;
- qualitative suggestions about why reasoning may favor a single guideline-consistent answer.

We cannot claim any of those as new.

## 2. Internal ambiguity representation neighbor

Zhang et al., EMNLP 2025, **“Sparse Neurons Carry Strong Signals of Question Ambiguity in LLMs”**:
- shows ambiguity is linearly encoded;
- finds sparse ambiguity-encoding neurons;
- detects ambiguity across datasets;
- manipulates those neurons to shift answering toward abstention.

Source:
- https://aclanthology.org/2025.emnlp-main.813/

This is an important feasibility/neighbor paper:
- internal ambiguity information can be measured and causally controlled.

It does not test:
- RLVR pre/post change;
- human annotator distributions;
- representation erasure vs readout suppression.

## 3. Human-disagreement representation work

EMNLP 2025 **“When Annotators Disagree, Topology Explains”** studies embedding geometry/ambiguity under annotator disagreement.

Source:
- https://aclanthology.org/2025.emnlp-main.426/

It owns:
- representation geometry around ambiguous examples in a fine-tuned classifier setting.

It does not own:
> matched post-training change and causal preservation/suppression in reasoning LLMs.

## 4. Calibration / RLVR neighborhood

Recent RLVR work studies:
- calibration;
- confidence;
- token-distribution shifts;
- reasoning behavior.

These are collision pressure because a readout-collapse story can sound like calibration.

The paper must therefore show that its load-bearing quantity is:
> **human disagreement information**, not generic confidence.

A model can be miscalibrated while still preserving human disagreement, or calibrated to majority-label correctness while erasing minority interpretations.

## 5. What part is new

The paper must own:

1. natural repeated human annotations define a target distribution;
2. behavioral parent already shows RLVR worsens distribution matching;
3. we trace that loss through model layers;
4. controlled pre/post RLVR or matched reasoning checkpoints identify whether information disappears or survives;
5. causal interventions test whether preserved information can restore behavioral disagreement;
6. conclusion distinguishes representational loss from policy/readout suppression.

## 6. Reviewer compression

### Attack 1
> “EACL 2026 + linear probes.”

Fatal if there is no causal intervention.

### Attack 2
> “Ambiguity neurons after RLVR.”

Rebuttal:
> ambiguity detection is one subtype; our target is the full repeated human label distribution across hate speech, emotion, preference, and high-variance examples.

### Attack 3
> “RLVR calibration.”

Rebuttal:
> calibration is correctness-vs-confidence; our target can contain genuinely plural human judgments with no single noise-free answer.

## 7. Kill-level collision definition

KILL if a paper already:
- compares matched pre/post RLVR models;
- measures human-disagreement distributions;
- probes layerwise preservation;
- causally distinguishes representation erasure from output/readout suppression;
- and tests behavioral recovery.

Behavior-only disagreement work or generic uncertainty probes do not kill.

## 8. Strong top-conference alignment

This candidate follows a strong Main/Outstanding scientific shape:
> established behavior → competing mechanisms → causal intervention → practical/conceptual consequence.

It is especially aligned with mechanistic papers where probing alone is not enough and causal editing validates interpretation.

## 9. Current verdict

**SERIOUS / A-.**

The exact novelty is not “RLVR loses nuance”; it is:
> **what happened internally to the information corresponding to human disagreement?**
