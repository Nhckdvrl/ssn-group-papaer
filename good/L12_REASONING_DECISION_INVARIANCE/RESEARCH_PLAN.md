# L12 — Research Plan

**Goal:** explain what reasoning-oriented post-training changes when fact-equivalent presentations stop changing decisions.

---

# Completed

- parent artifact audit;
- sibling Instruct-SFT vs Think-SFT behavioral reproduction;
- frame decodability diagnostic;
- invalidation of naive `</think>` stopping;
- natural reasoning-prefix causal readout test;
- answer-label-free arithmetic-prefix control.

Do not rerun these at scale before the next load-bearing uncertainty.

---

# L12-E07 — Relevant-vs-Irrelevant Context Boundary

## RQ

> Does Think-SFT become invariant specifically to meaning-preserving presentation changes, or broadly less sensitive to context?

## E07a — cheapest pilot

Use the three audited parent prospects.

For each base prospect create:

### Irrelevant / equivalent
Preserve option distributions and objective decision facts while changing gain/loss, order, or one equivalent wording transformation.

### Decision-relevant
Make a minimal factual edit to payoff/probability information that flips the EV-preferred underlying option while keeping presentation format matched.

Gold is computed from displayed facts.

## Models

- sibling Instruct-SFT;
- sibling Think-SFT.

No model zoo.

## Report separately

1. **equivalent-presentation consistency**;
2. **decision-relevant switch accuracy**;
3. branch × context-type interaction.

Do not collapse the first two into one headline score.

## Outcomes

### Selective abstraction
Think gains invariance to equivalent changes **without losing** sensitivity to decision-changing facts.

### Context flattening / causal disengagement
Think gains equivalent invariance but becomes less responsive to decision-changing information.

### No selective boundary
If siblings behave similarly after matched controls, reconstruct before patching.

The three-prospect E07a is route selection only. A successful interaction must later expand to a small natural controlled set, not a giant synthetic benchmark.

---

# L12-E08 — Conclusion-Free Decision-State Causal Substitution

Run only after E07 is stable.

Use matched E07 pairs and natural Think-SFT trajectories.

Choose a pre-answer point **before explicit option labels/conclusion text**. Patch/substitute the corresponding residual state from:
- equivalent-presentation donor;
- decision-changing donor;
- same-target control donor;
- random matched donor.

Scan layers coarsely, then refine only where a causal effect appears.

## Key question

> Does the internal state causally transfer decision-relevant information while remaining insensitive to nuisance presentation?

A strong result is a **semantic selectivity pattern**, not a particular layer number.

---

# Optional later routes

Only after E07/E08:
- arithmetic-transparent vs arithmetic-obscured decisions;
- another same-family reasoning/instruct pair;
- cleaner training lineage;
- intervention that selectively restores missing context use.

---

# Outcome robustness

- selective abstraction wins → reasoning learns semantic relevance;
- flattening wins → behavioral invariance overstates rationality;
- deliberative reconstruction wins → invariance is trajectory-built;
- arithmetic boundary wins → specialized reasoning policy;
- another account wins → reconstruct.

---

# Kill / reconstruct

KILL/demote if the branch contrast disappears, the semantic boundary cannot be objectively identified, only generic trace/readout effects survive, causal work never rises above probes, or current literature compresses the full story.

---

# Main-level shape

> reasoning-induced invariance  
> → semantic-relevance boundary  
> → causal decision-state explanation  
> → meaningful limitation/consequence for reasoning-model rationality

Do not turn it into a 20-bias leaderboard.
