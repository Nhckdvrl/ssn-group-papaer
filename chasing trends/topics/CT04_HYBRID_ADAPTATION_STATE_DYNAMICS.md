# CT04 — What Moves During Hybrid Adaptation? State-Dynamics Drift in Recurrent–Attention LMs

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Re-audited / reframed:** 2026-09-20  
**Primary target:** ICLR / ICML / NeurIPS; ACL/EMNLP Main is plausible if the final paper centers post-training behavior.  
**Core mode:** exploratory identification → causal localization → method.  
**Resource envelope:** 4×/8× RTX PRO 6000 96GB; 0.5B–4B main experiments, optional 7B confirmation; no from-scratch pretraining.

---

# 1. Mother question

Hybrid recurrent–attention LMs now expose two qualitatively different memory/computation channels:

- full attention / KV gives precise access to earlier tokens;
- recurrent linear-attention / SSM state provides bounded, continuously updated state.

Recent post-training results are difficult to reconcile from benchmark tables alone:

- component-specific LoRA can be destructive on the recurrent path of a **sequential** hybrid but constructive on a **parallel** hybrid;
- tuning only the recurrent initial/state variables can be remarkably effective;
- causal cache interventions show attention KV and recurrent state carry different functional roles;
- CoT fine-tuning can damage long-range memory in hybrid models through highly localized routing drift.

CT04 therefore asks a broader experimental question:

> **When a pretrained hybrid LM is adapted, what actually moves: the recurrent transition dynamics, the operating state, the division of labor between attention and recurrence, or only generic representations?**

A second question follows:

> **Which of those changes are responsible for useful task adaptation, and which cause collateral forgetting / memory failure?**

The project does **not** assume in advance that recurrent LoRA is bad, that one GDN operation is uniquely brittle, or that one mechanism will dominate. The purpose of the first phase is to identify the causal object.

---

# 2. Why this is a real problem now

## 2.1 Hybrid architectures are no longer niche

Qwen3.5 / Qwen3-Next, Kimi Linear, Falcon-H1, Nemotron-H and Olmo Hybrid make recurrent–attention hybrids a real open-weight post-training target.

Ai2's Olmo Hybrid is especially useful as a research artifact: it is a controlled 7B hybrid/Transformer family with base, mid-training, long-context-extension, SFT and DPO checkpoints plus intermediate checkpoints.

Thus the field is moving from:

> should hybrid architectures work?

to:

> how should their qualitatively different internal channels be post-trained without destroying what pretraining established?

## 2.2 Component placement gives an unexplained topology-dependent result

**Where Should LoRA Go? Component-Type Placement in Hybrid Language Models** (2026) compares:

- sequential Qwen3.5: GatedDeltaNet layers interleaved with attention;
- parallel Falcon-H1: Mamba-2 and attention branches inside blocks.

It reports:

- attention-only LoRA is highly parameter efficient;
- recurrent-only adaptation is strongly destructive on sequential Qwen3.5 in a tested math setting;
- recurrent-only adaptation is constructive on parallel Falcon-H1;
- transfer/forgetting patterns differ by topology.

That paper establishes **where** adaptation behaves differently. It does not causally establish **what internal dynamical change explains the difference**.

## 2.3 State tuning gives an apparently opposite clue

**State-offset Tuning** (ACL 2025) and **S0 Tuning** (2026) show that direct adaptation of recurrent state can outperform conventional prompt/LoRA alternatives in recurrent or hybrid models.

S0 Tuning reports large gains on Qwen3.5-4B while freezing model weights.

So:

> recurrent computation can be a strong adaptation surface even when recurrent **weight** adaptation is brittle.

This creates a state-vs-transition distinction that benchmark-only PEFT comparisons do not resolve.

## 2.4 The channels have different causal functions

**What Attention Recalls and Recurrence Controls in Hybrid Language Models** (2026) uses Split-prefill and State-swap interventions and finds:

- exact retrieval follows attention KV;
- language/persona/control signals follow recurrent state much more strongly.

This gives CT04 an intervention toolkit and makes "hybrid memory" scientifically non-homogeneous.

But that paper studies inference-time functional roles, not how fine-tuning changes those roles.

## 2.5 Adaptation can damage a memory mechanism locally

**Attention Amnesia in Hybrid LLMs** (EMNLP 2026) shows CoT-SFT can collapse long-context recall in tested hybrid models and localizes much of the failure to (W_Q/W_K) drift in retained softmax-attention layers; restoring those matrices recovers much of the lost capability.

This is an important precedent:

> fine-tuning damage can be localized to a memory operation rather than explained by global parameter drift.

CT04 asks whether an analogous—or different—causal decomposition exists for recurrent state dynamics and for the interface between the two channels.

## 2.6 Architecture work says recurrent memory editing is itself structured

NVIDIA's **Gated DeltaNet-2** explicitly separates erase and write gates because editing bounded recurrent memory is not one scalar operation. DASC further finds heterogeneous retention horizons across recurrent heads/channels.

These results do not answer CT04, but they make a monolithic "recurrent block LoRA" scientifically coarse.

---

# 3. Exact novelty boundary

CT04 is **not**:

- another PEFT benchmark;
- another LoRA target_modules sweep;
- the first state-based adaptation method;
- the first demonstration that attention and recurrence have different functions;
- the first catastrophic-forgetting paper;
- the first hybrid architecture analysis.

The intended new object is:

> **the causal state-dynamics change induced by post-training in a hybrid model.**

The paper must connect:

[
	ext{adaptation intervention}
ightarrow
	ext{state / transition / channel change}
ightarrow
	ext{target gain and collateral behavior}.
]

A successful paper should explain at least one previously puzzling adaptation outcome, then derive a method from that explanation.

---

# 4. Competing causal worlds

The first phase is explicitly a model-discrimination study. Multiple outcomes are scientifically useful.

## World A — transition-dynamics drift

Fine-tuning changes the recurrent update law itself:

- retention horizons shift;
- write/erase balance changes;
- identical prefixes generate increasingly different state trajectories;
- memory failures travel with the adapted transition parameters.

**Method implication:** preserve/anchor selected transition dynamics while adapting task-relevant paths.

## World B — operating-point / state-distribution drift

The transition remains locally functional, but fine-tuning moves recurrent states into a different region:

- state norm/spectrum/distribution shifts;
- re-centering or initial-state intervention rescues behavior;
- S0/state-offset adaptation can reproduce useful task steering without changing the transition.

**Method implication:** state-conditioned / state-recentering adaptation rather than transition-weight updates.

## World C — channel-interface reallocation

The main change is the division of labor between attention and recurrence:

- Split-prefill / State-swap contribution ratios change after adaptation;
- information that used to be served by one channel migrates toward the other;
- the failure depends on sequential vs parallel topology.

**Method implication:** interface-aware adaptation, channel anchoring, or calibrated residual/gating updates.

## World D — operation-local recurrent drift

Inside GDN/Mamba, only certain operations dominate:

- address/read;
- content write;
- retention/decay;
- erase/write strength;
- output/readout.

**Method implication:** operation-aware adapters or selective preservation.

## World E — mostly generic representation drift

Hybrid-specific diagnostics explain little; a matched pure Transformer exhibits the same adaptation/forgetting geometry.

**Knowledge implication:** reject the tempting hybrid-specific story. The useful contribution would have to move toward a more general adaptation-drift account rather than forcing a recurrent-memory narrative.

The project is not committed to A–D. The experiment is designed to tell these worlds apart.

---

# 5. Experimental identification program

## 5.1 Models

Use at least two different hybrid topologies:

- **Qwen3.5-0.8B / 2B / 4B** — sequential GatedDeltaNet + full attention;
- **Falcon-H1-0.5B / 3B or 7B** — parallel Mamba-2 + attention.

Strong optional third family:

- **Olmo Hybrid 7B** — sequential open hybrid with unusually rich stage checkpoints.

Control:

- a similarly sized pure Transformer.

No architecture needs to be pretrained from scratch.

## 5.2 Adaptation interventions

Use existing data and a small matrix, not a giant adapter zoo:

- attention-only LoRA;
- recurrent-only LoRA;
- all-eligible LoRA;
- state/S0 adaptation where supported;
- one or two operation-local recurrent adaptations after the first diagnostics.

Use math + code or instruction data so that the result is not tied to one task.

## 5.3 Measure behavior and dynamics together

### Target adaptation
- GSM8K / MATH / selected reasoning;
- HumanEval / MBPP or executable code.

### Collateral behavior
- general capability/retention;
- long-context retrieval / RULER-style diagnostics;
- instruction/style control where useful.

### Recurrent-state trajectory
For identical prompts before/after adaptation measure:
- state norm and spectrum;
- state trajectory divergence by layer/time;
- update magnitude;
- empirical decay / retention horizon;
- state-to-logit sensitivity.

### Channel contribution
Reuse causal interventions:
- Split-prefill: retain only attention KV or recurrent state;
- State-swap: combine KV from one run/model with recurrent state from another;
- base/adapted state or cache crosses.

### Parameter/function drift
Compare:
- raw weight drift;
- activation/state drift;
- function-space output drift;
- recurrent update Jacobian / local transition sensitivity where tractable.

The point is to determine which quantity best predicts target gain and collateral loss.

---

# 6. Critical crossed interventions

These are more important than adding benchmarks.

## 6.1 Base/adapted state × base/adapted weights

At selected layers/positions, cross:

- base weights + base state;
- base weights + adapted state;
- adapted weights + base state;
- adapted weights + adapted state.

Ask whether the changed behavior travels with the **state** or with the **transition parameters**.

## 6.2 Channel swap before and after adaptation

Use the same input but swap:

- base/adapted attention KV;
- base/adapted recurrent state.

Ask whether adaptation changes which channel carries the task-relevant behavior.

## 6.3 Dependency-structure manipulation

Construct matched tasks where the same type of output depends on:

- local information;
- distant exact recall;
- accumulated / state-tracking information;
- behavioral/instruction context.

This tests whether adaptation plasticity follows the **required memory contract**, not merely dataset identity.

## 6.4 Sequential vs parallel topology

Do not infer topology from two benchmark scores alone.

Ask whether the same diagnostic variable predicts behavior in:

- sequential hybrids;
- parallel hybrids.

The goal is to explain why an apparently similar recurrent adaptation can have opposite effects.

---

# 7. How methods grow from diagnosis

No final method is pre-selected.

## If transition drift dominates

Develop **dynamics-anchored adaptation**:

- preserve base-model state transition on a small calibration corpus;
- constrain retention horizon / recurrent update function;
- leave task-relevant readout/content paths plastic.

## If operating-point drift dominates

Develop **state-recentered adaptation**:

- learned S0 / state offset;
- state-normalization or calibration;
- possibly combine state adaptation with attention LoRA while freezing recurrent transition.

## If interface reallocation dominates

Develop **channel-balanced adaptation**:

- preserve the base attention↔recurrence causal allocation;
- calibrate residual/gating scales;
- adapt one channel while distilling the other's functional contribution.

## If operation-local drift dominates

Develop **operation-aware PEFT** using the discovered safe/plastic operations rather than component identity.

The method paper should then benchmark the derived rule against:
- attention-only LoRA;
- recurrent-only LoRA;
- ordinary all-module LoRA;
- S0/state-based tuning;
- relevant restoration/preservation baselines.

---

# 8. Why this is exploratory rather than a one-sign gamble

A diagnostic run is useful if it distinguishes causal worlds, even when it contradicts the motivating paper.

Examples:

- if recurrent-LoRA degradation reproduces only under one recipe, **recipe sensitivity itself becomes evidence about the mechanism**;
- if state dynamics remain stable while channel contribution changes, transition-drift is rejected and interface reallocation becomes the object;
- if S0 rescues behavior without repairing weights, operating-point drift is supported;
- if sequential and parallel hybrids differ only after state/transition decomposition, topology gets a mechanistic explanation;
- if none of the hybrid variables explain the effect beyond a Transformer control, the hybrid-specific hypothesis is falsified rather than cosmetically rescued.

The stopping condition is therefore **not** "a predicted sign failed."

The project should stop only if careful matched experiments reveal no reproducible structure—e.g. all diagnostics are unstable across seeds/recipes, no variable explains behavior beyond generic parameter drift, and no coherent causal distinction survives.

---

# 9. Real-paper novelty test

## Reviewer: "This is Where Should LoRA Go? with mechanistic plots."

That criticism is valid unless CT04 explains **why** the topology-dependent adaptation outcomes occur and demonstrates a causal intervention/rescue that follows the identified variable.

## Reviewer: "What Attention Recalls already separates the two channels."

That paper separates inference-time functional roles. CT04 studies how post-training **moves those roles or their state dynamics**.

## Reviewer: "This is S0 Tuning."

S0 Tuning provides one adaptation surface. CT04 uses state adaptation as a causal contrast against transition-weight adaptation; the final method may or may not use S0.

## Reviewer: "Attention Amnesia already localizes fine-tuning damage."

It localizes a softmax-attention Q/K failure in its tested hybrids. CT04 asks whether recurrent-state and channel-interface dynamics explain another class of adaptation behavior, especially native GDN/Mamba hybrids.

## Reviewer: "This is generic catastrophic forgetting."

Then the hybrid story must lose. A pure-Transformer control and state/channel interventions are mandatory precisely to separate generic drift from hybrid-specific state dynamics.

---

# 10. Data and compute

This is comfortably within the local resource envelope.

Exploration:
- Qwen3.5-0.8B / Falcon-H1-0.5B;
- 1–3K existing SFT examples;
- LoRA / state tuning;
- dense diagnostics;
- several seeds for only the important crossed conditions.

Mechanism confirmation:
- Qwen3.5-2B / 4B;
- Falcon-H1-3B/7B or Olmo Hybrid 7B;
- narrowed intervention set.

4×96GB is sufficient; 8×96GB mainly accelerates model-family crosses, seeds and long-context probes.

No new dataset, large-scale RL, or from-scratch pretraining is required.

---

# 11. Formal continuation / stopping criterion

CT04 remains worth pursuing while the experiment is reducing uncertainty among the causal worlds above.

It should be stopped or radically reframed only if, after matched optimization and multiple seeds:

- adaptation effects are dominated by unreproducible recipe noise;
- state/transition/channel diagnostics have no stable relationship with either adaptation gain or collateral loss;
- pure-Transformer controls explain the phenomena equally well with no hybrid-specific residual;
- or a direct new paper already performs the same causal decomposition and derives the same method.

Do **not** stop merely because:
- recurrent-only LoRA is not destructive in one reproduction;
- a hypothesized operation is not brittle;
- S0 does not win;
- the sequential/parallel contrast changes magnitude.

Those are experimental outcomes, not failed bets.

---

# 12. Expected paper forms

The project can mature into several legitimate paper forms without changing the mother question.

### Mechanism-first form
> Post-training changes hybrid LMs primarily by shifting X, not Y; this explains topology-dependent transfer and forgetting.

### Method-first form
> Preserving / adapting X according to the diagnosed state-dynamics rule improves target adaptation while preserving memory and general capability.

### Architecture/post-training interface form
> Sequential and parallel hybrids differ in where adaptation pressure is absorbed; a topology-aware adaptation rule follows.

The strongest version contains both diagnosis and a simple method.

---

# 13. Verdict

> **PILOT-AUTHORIZED — exploratory identification program**

This is not authorization to run a giant target-module sweep.

The first milestone is:

> **build a small crossed intervention matrix that can tell whether adaptation behavior travels with recurrent state, recurrent transition, or attention↔recurrence channel allocation.**

Only after that diagnosis should a method be fixed.
