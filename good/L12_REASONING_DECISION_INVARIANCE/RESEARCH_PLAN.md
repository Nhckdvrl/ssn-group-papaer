# L12 — Research Plan

**Goal:** determine what changes inside the model when reasoning post-training makes equivalent risky choices behaviorally more invariant to framing/presentation.

> **This is an open research plan, not a rigid implementation contract.**  
> The exact interpretability method may change.  
> The hard requirements are: natural RQ, credible comparison, decisive evidence, paper-level novelty, and ACL/EMNLP/NAACL Main-level contribution.

---

## 1. First step: reproduce a small clean behavioral transition

Use a shared-base model family with matched post-training branches if possible.

Choose only a few parent manipulations with strong effects:
- gain/loss framing;
- description/history;
- option order;
- another clean parent axis if more reproducible.

Question:
> does the reasoning-oriented training transition actually produce greater behavioral invariance in our reproducible open setup?

Do not begin with every cognitive bias.

---

## 2. Locate the change before choosing a mechanism story

For the currently verified OLMo 3 family, the clean first design is:
- common base `Olmo-3-7B`;
- `Olmo-3-7B-Instruct-SFT` sibling branch;
- `Olmo-3-7B-Think-SFT` sibling branch;
- later DPO/final checkpoints only as secondary within-branch evidence.

Do **not** describe Instruct-SFT → Think-SFT as a sequential training transition. The first causal-style contrast should reason from the common base:
> **What changes under base→Instruct versus base→Think post-training?**

The exact family/stages may change if a cleaner public matched design exists.

The purpose is to identify:
> **which training regime is associated with the behavioral invariance strongly enough to support mechanism work.**

---

## 3. Mechanism families

Current useful routes include:

### Representation route
Measure whether task-relevant representations across equivalent framings become more similar.

### Preserved-context route
Test whether framing identity remains available after the model becomes behaviorally invariant.

### Policy/readout route
Identify whether a late decision variable increasingly dominates the final choice.

### Deliberation route
Compare direct/no-think and reasoning trajectories to see whether inference-time computation creates the invariance.

### Boundary route
Test matched decisions that are less easily reduced to explicit arithmetic.

These are route families, not mandatory experiments.

---

## 4. Causal evidence requirement

If the paper makes a mechanism claim, seek a causal test.

Possible tools:
- activation patching;
- causal tracing;
- steering/ablation;
- cross-checkpoint patching;
- controlled reasoning-mode intervention;
- another validated causal method.

Choose the simplest method that actually distinguishes the scientific accounts.

Do not use a fashionable interpretability tool merely because it is available.

---

## 5. Strong possible outcomes

### Outcome A — Canonicalization
Reasoning training reduces the representational influence of surface framing and produces a shared task-relevant decision representation.

Scientific conclusion:
> reasoning training creates semantic normalization across decision interfaces.

### Outcome B — Policy override
Framing information remains present, but a stronger late decision policy suppresses its behavioral effect.

Scientific conclusion:
> behavioral rationality/invariance can coexist with latent context sensitivity.

### Outcome C — Deliberation
Inference-time reasoning largely creates the invariance.

Scientific conclusion:
> the effect is computation-path dependent rather than simply a static representation rewrite.

### Outcome D — Arithmetic boundary
Invariance collapses once the task is less easily converted to arithmetic.

Scientific conclusion:
> apparent rationality reflects a specialized reasoning transformation with a clear boundary.

### Outcome E — A stronger unexpected account
Reconstruct around it.

None of A–D is required to win.

---

## 6. Expansion logic

After the core mechanism is clear, add only experiments that answer:
- does the mechanism generalize across another framing axis?
- does it replicate in another same-family model?
- where is the boundary?
- does the mechanism explain a real behavioral consequence?

Do not broaden into a 20-bias leaderboard.

---

## 7. Main-level paper shape

A strong final paper should roughly achieve:

- **C1 / core answer:** what changed when reasoning training produced decision invariance;
- **C2 / mechanism or boundary:** where/how the change occurs and decisive validation;
- **C3 / consequence:** what this changes about interpreting reasoning-model “rationality,” robustness, or post-training.

The exact section structure is flexible.

---

## 8. Reconstruct / kill logic

### Reconstruct if:
- canonicalization loses but suppression wins;
- reasoning mode rather than training stage explains the effect;
- a clean arithmetic/generalization boundary appears;
- another mechanism provides a stronger unifying story.

### Kill if:
- the parent phenomenon cannot be reproduced in a usable controlled open setup;
- shared-base branch/stage comparisons are too confounded to identify anything;
- all internal results are probe-only and causally uninterpretable;
- the final contribution collapses to another framing benchmark;
- current literature already owns the full paper narrative.

---

## 9. Conference alignment throughout

At every major turn, compare against strong ACL/EMNLP/NAACL Main work.

Ask:
- Is the question still easy to explain?
- Are we resolving a genuine scientific uncertainty?
- Does the evidence distinguish mechanisms rather than decorate the result?
- Is the boundary consequential?
- Does the paper still have an independent identity beside the Outstanding parent and framing-mechanism literature?
- Would the result matter even if the initially expected mechanism loses?

Methods may change. The quality bar does not.
