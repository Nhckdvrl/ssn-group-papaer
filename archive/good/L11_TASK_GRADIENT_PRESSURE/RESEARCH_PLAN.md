# L11 — Research Plan

**Goal:** explain what makes a language task optimization-loud in multi-task RL and determine what that loudness actually means.

> **This plan is intentionally flexible.**  
> It gives a strong starting route, not a fixed recipe.  
> Methods may change if a better identification strategy appears.  
> The hard constraints are the scientific question, credible evidence, paper-level novelty, and ACL/EMNLP/NAACL Main-level depth.

---

## 1. First objective: recover one clean parent contrast

Before mechanism work:
- reproduce one strong high-gradient vs low-gradient task contrast;
- confirm that the ordering does not trivially mirror learning gain;
- verify reward/advantage/length statistics.

Prefer a cheap same-domain contrast when possible.

Do not expand to many tasks until the anomaly is reproducible in our stack.

---

## 2. First mechanism pass

The most informative current route is a **gradient anatomy**.

Possible decomposition axes:
- reward/advantage;
- per-example score sensitivity;
- token/chunk cancellation;
- example-level coherence;
- aggregate task gradient;
- local function-space movement.

The exact decomposition can change if implementation or theory suggests a cleaner route.

The goal is not to calculate every metric.

The goal is:
> **find which part of the update pipeline actually explains why one task is louder.**

---

## 3. Stronger-than-correlation requirement

A Main-level mechanism story should not end at:
> “metric X correlates with task gradient magnitude.”

Once a plausible source is identified, seek a controlled manipulation.

Potential families:
- within-task high/low update-coherence subsets;
- matched output representations;
- matched response structures;
- another natural perturbation that changes the suspected source while preserving the underlying task/reward.

Choose the intervention that best separates competing explanations.

---

## 4. Parameter-space vs function-space calibration

A promising second axis is:

> **Does a much larger parameter gradient actually cause proportionally larger policy change?**

Possible measurements:
- policy KL;
- log-prob movement;
- output distribution change;
- held-out reward change;
- another principled functional quantity.

This is not mandatory if another mechanism yields a stronger paper.

It is currently attractive because it converts the parent anomaly into a measurement question with practical consequence.

---

## 5. Generalization only after identification

After a clean causal result, expand selectively:
- second task family;
- second model;
- earlier/later training checkpoints;
- different task mixtures.

Breadth should test whether the mechanism is general, not pad the paper.

---

## 6. Possible paper shapes

### Route A — Update coherence
Task dominance is largely driven by coherent/redundant example updates.

Possible consequence:
> task mixture design should reason about update diversity, not only sample counts or rewards.

### Route B — Output parameterization
Equivalent tasks can induce very different optimization pressure because of how outputs are represented.

Possible consequence:
> raw cross-task gradient magnitudes can reflect interface/parameterization artifacts.

### Route C — Function-space miscalibration
Raw parameter norm greatly exaggerates or misorders actual policy movement.

Possible consequence:
> use a function-calibrated notion of task pressure.

### Route D — Multi-mechanism map
Different tasks become loud for different reasons.

Possible consequence:
> a diagnostic map tells us when different correction strategies are appropriate.

### Route E — A stronger discovered explanation
Allowed and encouraged.

Do not force the final paper into Routes A–D.

---

## 7. Main-level depth requirement

Before paper-mainline approval, the project should have a natural structure roughly equivalent to:

- **Core answer:** what task gradient loudness actually comes from;
- **Validation / why:** causal or otherwise decisive discrimination;
- **Consequence:** how this changes interpretation or practice in multi-task RL.

It need not literally use a C1/C2/C3 format.

---

## 8. Reconstruct / kill logic

### Reconstruct if:
- a different mechanism wins;
- the effect is strongly task-dependent but forms a useful boundary;
- a better measurement framing emerges;
- an intervention reveals that the parent’s task-level interpretation was too coarse.

### Kill if:
- the anomaly does not reproduce after careful fidelity checks;
- the entire story reduces to one already-known trivial confound;
- no credible manipulation can distinguish explanations;
- the final contribution is only another optimizer or balancing heuristic;
- current literature already owns the complete paper identity.

---

## 9. Conference alignment during execution

At every major decision, compare the developing work against strong ACL/EMNLP/NAACL Main papers.

Ask:
- Is the RQ still simple and important?
- Did the method create new leverage or merely add machinery?
- Does the evidence really identify the mechanism?
- Is the conclusion broader than the chosen benchmark pair?
- Can a reviewer remember the paper in one sentence?
- Does the story still belong to us at the paper level?

Do not let a convenient implementation lower the intended paper level.
