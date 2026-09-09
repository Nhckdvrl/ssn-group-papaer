# L12 — Reasoning Training: Canonicalization or Policy Override?

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-09

> **Plain-language thesis:** Reasoning-trained models can become much less sensitive to how the same risky choice is framed or presented. The open question is whether reasoning training actually converts different presentations into a common internal decision representation, or whether the framing information survives internally but is simply overruled by a stronger decision policy.

---

## 1. One-sentence research question

> When reasoning post-training makes an LLM behave more invariantly across equivalent decision framings, does the training canonicalize the underlying representation, or does it preserve contextual/framing information while changing how that information controls the final choice?

Plain version:

> **Did the model learn to see different framings as the same problem, or did it merely learn to ignore the framing when choosing?**

That distinction changes what we mean when we say reasoning training makes a model “more rational.”

---

## 2. Established parent phenomenon

ACL 2026 Outstanding Paper **“Mind the (DH) Gap!”** studies risky decisions across many frontier/open models and matched manipulations.

The paper reports that reasoning-oriented models are often:
- closer to expected-payoff-maximizing behavior;
- less sensitive to gain/loss framing;
- less sensitive to option order;
- less sensitive to some explanation manipulations;
- less separated by description-vs-experience format.

It further studies open-model training stages and argues that reasoning-oriented SFT is an important differentiator.

Primary source:
- https://aclanthology.org/2026.acl-long.479/

Therefore L12 does **not** ask:
> “Are reasoning models less framing-sensitive?”

The parent has already established the behavioral phenomenon.

L12 asks:
> **What computation changed to produce that invariance?**

---

## 3. Why the question matters

Two models can produce the same invariant answer for very different reasons.

### Possibility 1
The model transforms different surface forms into a shared task-relevant representation.

That would mean reasoning training creates a form of:
> **semantic canonicalization / abstraction.**

### Possibility 2
The model still represents the framing strongly, but a later policy/readout component dominates the choice.

That would mean:
> **behavioral invariance does not imply representational invariance.**

These imply different conclusions about:
- reasoning post-training;
- robustness;
- hidden context sensitivity;
- interpretability;
- transfer outside easy arithmetic decisions.

---

## 4. Current scientific accounts

These are working accounts, not a fixed mechanistic ontology.

### Account A — Representational canonicalization
Equivalent risky choices converge toward a shared representation of:
- probability;
- payoff;
- expected value;
- option preference.

Prediction:
- framing/interface identity becomes less separable or less causally relevant after reasoning SFT;
- cross-frame representations become more similar in task-relevant layers/subspaces.

### Account B — Policy/readout override
Framing information remains available, but the final action policy relies much more strongly on an expected-value / calculation-oriented signal.

Prediction:
- framing remains decodable or causally recoverable;
- weakening/altering the late decision signal can restore framing sensitivity.

### Account C — Inference-time deliberation
The weights may not be invariant by themselves. A reasoning trace may recompute the problem and wash out the initial framing.

Prediction:
- invariance depends strongly on reasoning mode / deliberation path;
- direct/no-think variants preserve more sensitivity.

### Account D — Arithmetic specialization / boundary
The apparent invariance may hold mainly when the choice is easily reduced to explicit arithmetic.

Prediction:
- preserve the same uncertainty/choice structure but reduce arithmetic transparency;
- framing sensitivity may reappear.

### Account E — Another training-induced mechanism
Allowed if it yields a clearer causal explanation.

Do not force the paper into A–D.

---

## 5. Why the data situation is unusually good

The parent provides:
- matched risky-choice stimuli;
- explicit framing manipulations;
- a strong established behavioral effect.

Open OLMo-style training lineages provide:
- same-family checkpoints;
- reasoning/instruction variants;
- training-stage comparisons.

This allows us to ask a **training-transition mechanism question** rather than compare unrelated proprietary model families.

---

## 6. Paper identity

Preferred identity:

> **Established reasoning-induced decision invariance  
> → identify whether the change occurs in representation, deliberation, or decision policy  
> → use controlled training-stage / causal comparisons  
> → identify boundaries where invariance holds or fails  
> → reinterpret what reasoning-induced “rationality” actually means.**

The exact interpretability method is intentionally not fixed.

### Not the identity:
- another cognitive-bias benchmark;
- “reasoning models are more rational”;
- one more framing-effect survey;
- probe-only representation analysis;
- a generic activation-steering paper.

---

## 7. Flexible paper depth

Possible strong paper shapes include:

### Canonicalization story
Reasoning training genuinely maps different interfaces to a shared internal decision variable.

### Suppression story
Surface/context information remains intact but is downstream-suppressed by a stronger decision policy.

### Deliberation story
The main source of invariance is inference-time reasoning rather than a static representational rewrite.

### Boundary story
Invariance depends on whether the task can be converted into an explicit arithmetic representation.

### Training-stage story
A specific training transition reorganizes how contextual information influences choice.

Any can support the topic if the evidence is decisive and the paper remains Main-level.

---

## 8. Six selection gates

| Gate | Verdict | Why |
|---|---|---|
| Natural / important | **PASS++** | Same choice, different framing, different or invariant decision is immediately understandable. |
| Genuine tension | **PASS++** | Canonicalization, suppression, deliberation and specialization make different predictions. |
| Data / identification | **PASS++** | Parent stimuli + same-family training checkpoints provide unusually controlled evidence. |
| Paper-level novelty | **PASS** | Related work owns behavioral framing effects and some representation studies, but not this full training-transition mechanism story. |
| Outcome robustness | **PASS++** | Every major account produces a meaningful reinterpretation/boundary. |
| Main-level calibration | **PASS++** | Strong parent, simple question, causal mechanism opportunity, clear consequence. |

---

## 9. Reviewer-compression attacks

### “This is just Mind the (DH) Gap! + probes.”
Fatal if the paper only adds decodability plots.

### “This is just another framing-effects paper.”
Fatal if the project expands horizontally over many biases without mechanism.

### “This is just activation patching on risky choice.”
Fatal if the method becomes the paper rather than the scientific question.

The paper must distinguish **why training-induced invariance appears** and what that says about reasoning models.

---

## 10. Main-level standard

Methods are flexible, but the final paper should match strong ACL/EMNLP/NAACL Main work on:
- naturalness of the central question;
- quality of the controlled comparison;
- causal/mechanistic leverage;
- paper-level novelty;
- breadth through a meaningful boundary rather than benchmark accumulation;
- a conclusion that changes how we interpret reasoning post-training.

---

## 11. Current authorization

**PILOT-AUTHORIZED.**

This does not mean:
- canonicalization is expected to win;
- activation probing is mandatory;
- OLMo is the only allowable model family;
- the full paper design is frozen.

It means the question is strong enough to justify the smallest decisive pilot.

See:
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
- [PILOT_CARD.md](PILOT_CARD.md)
