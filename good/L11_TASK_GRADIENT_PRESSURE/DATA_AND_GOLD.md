# L11 — Data, Measurement, and Identification

**Core principle:** this project is about the source and meaning of task-level optimization pressure. The experiment must measure the relevant training quantities directly rather than infer mechanism from benchmark accuracy alone.

The details below are recommended starting points, not a frozen protocol.

---

## 1. Preferred experimental substrate

Start from tasks used by the direct parent:

Wu et al., Findings of EACL 2026  
https://aclanthology.org/2026.findings-eacl.164/

Useful families include:
- Code;
- Countdown;
- MATH;
- FinQA;
- DeepScaleR;
- Arithmetic.

### Cheap pilot preference

A same-domain math comparison is attractive because it reduces the trivial explanation that:
> “Code and math are simply different domains.”

But this is not a hard requirement. If another pair provides a cleaner reproducible contrast, use it.

---

## 2. Why these data are suitable

The parent tasks offer:
- objective or near-objective verification;
- natural RLVR rewards;
- direct task-level learning curves;
- observable rollout distributions;
- measurable policy gradients.

No artificial annotation ontology is required.

The scientific quantity comes from training dynamics themselves.

---

## 3. Recommended unit of analysis

Do not keep only one task-level number.

Where compute permits, retain enough information to reconstruct:

> token / response → example → task batch → shared update.

Useful fields include:
- task/prompt/rollout ID;
- reward and advantage;
- prompt/response length;
- response log-probabilities;
- per-example gradient or validated sketch/projection;
- per-token or chunk-level summaries when feasible;
- checkpoint / training step.

If exact full gradients are too expensive, a lower-cost sketch is acceptable **only after validating that it preserves the comparisons needed for the claim**.

---

## 4. Load-bearing scientific quantities

Potential quantities include:

### Task gradient magnitude
The parent quantity and starting anomaly.

### Learning gain
A local change in task performance/reward over nearby training.

### Per-example score sensitivity
$
\|\nabla_\theta \log \pi_\theta(y|x)\|
$

### Within-response alignment/cancellation
How strongly token/chunk updates reinforce or cancel.

### Across-example coherence
How concentrated or redundant the example update directions are.

Possible summaries:
- cosine structure;
- norm-of-mean / mean-norm ratio;
- effective rank;
- spectral concentration;
- other validated geometry summaries.

### Function-space movement
Possible choices:
- local policy KL;
- log-probability movement;
- output-distribution movement;
- held-out reward change;
- Fisher/natural-gradient quantities if useful.

No single metric is mandatory. The metric must serve the scientific distinction.

---

## 5. Identification chains

Examples of valid identification logic:

### If claiming per-example sensitivity
> matched reward/advantage  
> → systematically different score sensitivity  
> → aggregate loudness follows that difference  
> → a controlled representation/task manipulation changes the sensitivity.

### If claiming update coherence
> individual update sizes are similar  
> → aggregate norm differs because directions reinforce/cancel  
> → changing within-task coherence changes aggregate pressure while difficulty/reward remain comparable.

### If claiming parameter/function miscalibration
> raw gradient magnitude differs greatly  
> → actual local policy/function movement differs much less or reverses  
> → a function-calibrated quantity better predicts meaningful training effect.

The project may discover another chain; write it explicitly before claiming mechanism.

---

## 6. Natural causal interventions

Preferred interventions should preserve the scientific object as much as possible.

Possible families:
- high-coherence vs low-coherence subsets within one task;
- semantically equivalent natural output representations;
- matched examples with different response structures;
- controlled resampling that changes update diversity while preserving reward/difficulty distributions.

Avoid artificial string manipulations that create a phenomenon only because the representation is unnatural.

---

## 7. Mandatory confound audit

At minimum track:
- reward/advantage distribution;
- prompt length;
- response length;
- task difficulty / current success rate;
- number of sampled rollouts;
- gradient clipping/normalization;
- optimizer state;
- model checkpoint;
- LoRA vs full-parameter training;
- verifier failures.

The parent already weakens some simple explanations, but our own implementation must not silently reintroduce them.

---

## 8. Model strategy

Pilot:
- one manageable open model close to the parent setup.

Replication:
- a second model family or scale only after a clear mechanism signal.

Do not turn the first experiment into a model zoo.

---

## 9. Data / measurement kill conditions

Kill or reconstruct if:
- the parent anomaly cannot be reproduced after a faithful implementation audit;
- the required gradient quantities are too unstable to support the intended claim;
- a trivial already-known confound explains nearly all of the effect;
- the proposed intervention changes so many factors that no mechanism is identifiable;
- the result can only be stated as “task A has a bigger gradient than task B.”

A preferred account failing is **not** a kill condition.
