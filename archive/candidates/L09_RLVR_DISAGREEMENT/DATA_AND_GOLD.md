# L09 — Data, Gold, and Training Interventions

**Core rule:** human disagreement is measured from repeated human annotations, not inferred from an LLM judge.

---

## 1. Primary natural data — EACL 2026 companion resources

The official repository for Ni et al. includes test data and prompts for:

### Gab Hate Corpus (GHC)
Target:
- human variation in hate-speech judgments.

### HelpSteer2
Target:
- human preference / response-quality variation.

### GoEmotions
Subsets include:
- positive;
- negative;
- ambiguous examples.

The repository distinguishes:
- HighVar disagreement subsets;
- random subsets;
- sampled-distribution vs verbalized-distribution evaluation.

Source:
- https://github.com/EdisonNi-hku/Disagreement_Prediction

## 2. Load-bearing gold

For item i with repeated human annotations:

p_human(y | x_i)

is the direct target distribution.

Do not collapse to majority label for the core analysis.

Derived quantities may include:
- entropy;
- disagreement rate;
- modal probability;
- Jensen-Shannon/KL distance between model and human distributions.

The repeated labels are the gold observation.

## 3. Behavioral reproduction

First reproduce:
- RLHF/base reasoning setting;
- naive CoT;
- RLVR-style reasoning;
- sampled vs verbalized distribution.

Primary behavior metric:
> distance between model output distribution and human annotation distribution.

This anchors the mechanism study to the published phenomenon.

## 4. Open-weight requirement

Mechanistic analysis requires open activations.

Use two complementary strategies.

### Strategy A — existing open reasoning checkpoints

Use open RLVR/reasoning models with compatible base/instruction relatives where available.

Treat imperfect training-history matches cautiously.

### Strategy B — controlled matched RLVR pair

Preferred causal route:

1. start from one open instruction/RLHF-style checkpoint;
2. retain a frozen copy;
3. apply a controlled RLVR-style training stage on an objective verifiable-reward task;
4. evaluate both before/after on the same disagreement data.

This isolates the effect of the RLVR training operation better than unrelated released models.

The RLVR training task must be separate from the disagreement datasets.

## 5. Representation measurements

For each layer/token position:

### Decodability
Train probes to predict:
- human modal label;
- human label probability/distribution;
- entropy/high-vs-low disagreement.

Important:
> probe accuracy alone is diagnostic, not sufficient evidence for preservation.

### Representational similarity
- CKA/linear alignment;
- pre/post shift by disagreement level;
- class/ambiguity geometry.

### Readout
Measure:
- output-logit margin;
- entropy;
- probability assigned to minority labels.

## 6. Causal interventions

### Activation patching
Patch pre-RLVR activations into post-RLVR model at selected layers.

Question:
> does disagreement behavior recover?

### Steering
Use disagreement/ambiguity directions derived without test leakage.

Question:
> can the post-RLVR model express the lost distribution if internal information survives?

### Readout intervention
Alter only final-layer/readout mapping where feasible.

Question:
> is the collapse downstream of preserved representations?

### Representation ablation
If a specific disagreement subspace is identified:
- ablate it pre-RLVR;
- test whether pre-RLVR behavior becomes RLVR-like.

## 7. Metrics

Behavior:
- JS divergence / KL where well-defined;
- Brier-style distribution error;
- entropy difference;
- majority-label accuracy as secondary only.

Representation:
- probe cross-validated performance;
- cross-checkpoint probe transfer;
- layerwise information curves.

Causal:
- behavioral recovery under patching/steering;
- change in human-distribution distance;
- specificity controls on low-disagreement examples.

## 8. Critical controls

- same prompt/output format;
- temperature matched;
- HighVar and random subsets;
- majority-label accuracy controlled;
- task type separated;
- model confidence controlled;
- representation probes trained without test leakage;
- patching controls with random examples/layers.

## 9. Data/intervention kill conditions

KILL or reconstruct if:
- published behavioral gap cannot be reproduced;
- there is no accessible model pair enabling credible pre/post attribution;
- hidden-state differences cannot be causally linked to output behavior;
- only linear-probe accuracy changes with no intervention;
- result collapses to generic calibration.

## 10. Data Gate verdict

**YES for behavioral gold; MECHANISM IDENTIFICATION requires an open matched training/checkpoint design.**
