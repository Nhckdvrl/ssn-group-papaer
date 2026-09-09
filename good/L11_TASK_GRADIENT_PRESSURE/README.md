# L11 — Task Gradient ≠ Learning Pressure

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-09

> **Plain-language thesis:** In multi-task RL post-training, some tasks can push the shared model much harder in parameter space without learning more. The scientific question is what makes a task optimization-loud, and whether raw task-gradient magnitude is actually a meaningful cross-task measure of learning pressure.

---

## 1. One-sentence research question

> Why can two language/reasoning tasks have similar or even reversed learning gains while one produces dramatically larger policy gradients, and what property of the task, output, or induced update geometry causes that mismatch?

Plain version:

> **Why can one task “shout” much louder during RL even when it has no more useful learning left?**

This is not primarily a gradient-balancing-method topic. It is a mechanism / measurement question about what multi-task RL is actually measuring and optimizing.

---

## 2. Established anomaly: we do not gamble on its existence

Wu et al., Findings of EACL 2026, **“Imbalanced Gradients in RL Post-Training of Multi-Task LLMs”** reports large cross-task gradient imbalance under RLVR/GRPO.

The paper studies both:
- multi-domain mixtures such as Code / Countdown / MATH / FinQA;
- same-domain math mixtures such as DeepScaleR / MATH / Arithmetic.

The important established observation is:

> task gradient magnitude can differ enormously while not tracking task learning gain in a simple way.

The paper also checks several obvious statistics such as reward, advantage, prompt/response length and finds that they do not explain the whole cross-task difference.

Source:
- https://aclanthology.org/2026.findings-eacl.164/

Therefore L11 does **not** ask:
> “Does gradient imbalance exist?”

It asks:
> **What produces the imbalance, what does it mean, and when should we trust it as a training signal?**

---

## 3. Why the question is natural and important

In multi-task RL, gradients from several tasks are ultimately mixed into one shared parameter update.

If one task routinely contributes much larger updates, it can dominate:
- which capabilities are improved;
- which are neglected;
- which examples receive more optimization budget;
- how task sampling or balancing should be interpreted.

A strong paper should therefore answer a basic question:

> **Does a large task gradient mean that the task has more useful learning signal, or can it simply reflect the way that task/output is represented and aggregated in the model’s parameterization?**

This matters independently of any specific optimizer.

---

## 4. Current scientific accounts

These are **working explanations, not a fixed checklist**. They may be merged, replaced, or refined if the pilot reveals a better mechanism.

### Account A — Per-example / per-token sensitivity
Some outputs may sit in regions where
[
\nabla_\theta \log \pi_\theta(y|x)
]
is intrinsically larger.

Then the task is loud before examples are even aggregated.

### Account B — Within-sequence cancellation
Two tasks may have similarly strong token-level signals, but one task’s token updates reinforce one another while another task’s updates partially cancel.

Then sequence structure, not raw learnability, creates the magnitude difference.

### Account C — Across-example coherence / redundancy
Examples from one task may repeatedly request similar parameter changes, while another task contains diverse updates pointing in many directions.

Then the loud task may be:
> **more geometrically coherent / redundant**, not more in need of learning.

### Account D — Parameter-space magnitude is a distorted proxy
A large Euclidean gradient can correspond to a much smaller change in the actual policy/function than the raw norm suggests.

Then the central conclusion may be:
> **parameter loudness ≠ functional learning pressure.**

### Account E — A different mechanism
The project is explicitly allowed to discover another task-conditioned mechanism, provided it is:
- natural;
- identifiable;
- causally testable;
- broad enough to support a Main-level story.

Do not force the data into A–D.

---

## 5. What prior work already owns

Do not claim novelty for:
- the existence of task gradient imbalance;
- the generic idea of balancing task gradients;
- generic gradient conflict;
- generic curvature differences;
- gradient-based task/data selection;
- the statement that Euclidean parameter norms depend on parameterization.

Those ideas already exist in the literature.

The paper must instead own a new **LLM/NLP-level explanatory chain**.

---

## 6. Paper identity

The preferred paper identity is:

> **Established gradient/gain paradox  
> → identify what makes language tasks optimization-loud  
> → distinguish parameter loudness from actual functional movement  
> → validate the explanation with a controlled intervention  
> → derive a consequence for how multi-task RL should measure or mix tasks.**

The exact mechanism and the exact final method are intentionally left open.

### This topic should not collapse into:
- “GradNorm for LLM RL”;
- another multi-domain optimizer;
- another gradient-surgery paper;
- a descriptive gradient-statistics appendix;
- +X% from a new sampler without a new scientific diagnosis.

---

## 7. Flexible paper depth

A strong final paper could take several shapes.

### Mechanism-first
- identify source of gradient loudness;
- causally manipulate it;
- show when it predicts task dominance.

### Measurement-first
- show raw gradient magnitude is systematically miscalibrated across tasks;
- derive/validate a more meaningful cross-task pressure measure;
- show a practical consequence.

### Data-geometry-first
- show task dominance follows example/update coherence rather than nominal task identity;
- derive implications for mixture construction.

### Boundary-first
- different task families may be loud for different reasons;
- map which mechanism dominates when;
- turn that map into a principled decision rule.

Any of these can be acceptable if the final contribution has a clear ACL/EMNLP/NAACL Main-level identity.

---

## 8. Six selection gates

| Gate | Verdict | Why |
|---|---|---|
| Natural / important | **PASS** | Shared task gradients directly determine multi-task RL updates. |
| Genuine tension | **PASS++** | Several plausible mechanisms imply different interpretations and interventions. |
| Data / identification | **PASS** | Objective-verifier tasks and direct gradient measurements make the quantity observable. |
| Paper-level novelty | **PASS — guarded** | Related work owns imbalance/balancing/conflict, but not yet the full explanatory + measurement story. |
| Outcome robustness | **PASS++** | Multiple mechanisms or a correction/boundary result remain scientifically useful. |
| Main-level calibration | **PASS** | Must reach causal explanation/measurement consequence, not remain optimizer engineering. |

---

## 9. Reviewer-compression attacks

### “This is just Imbalanced Gradients + GradNorm.”
That becomes true if the paper only:
> reproduces imbalance → normalizes gradients → reports gains.

### “This is just Modular Gradient Surgery.”
That becomes true if the center becomes generic direction conflict.

### “This is just natural-gradient/Fisher theory.”
That becomes true if the paper never connects geometry to a concrete LLM task/output mechanism and empirical consequence.

The project survives only when the **full paper identity** remains recognizably new.

---

## 10. Main-level standard

Throughout execution, compare the developing paper against strong ACL/EMNLP/NAACL Main work on:
- simplicity of the central question;
- decisiveness of the evidence;
- mechanism or construct validity;
- consequence beyond one benchmark;
- paper-level novelty, not ingredient novelty;
- outcome robustness;
- plain-language memorability.

The candidate is allowed to change methods, analyses, and even its preferred mechanism.

It is **not** allowed to drift into a weaker paper just because an implementation is convenient.

---

## 11. Current authorization

**PILOT-AUTHORIZED.**

This means:
- worth spending limited compute on the smallest decisive experiment;
- not protected from future kill;
- not mainline-approved;
- not locked to one mechanism or one analysis stack.

See:
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
- [PILOT_CARD.md](PILOT_CARD.md)
