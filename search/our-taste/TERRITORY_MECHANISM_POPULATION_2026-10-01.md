# Territory Card — Mechanism Population Dynamics — 2026-10-01

- **Lane:** our-taste / mechanistic interpretability / model science
- **Status:** selected for ACTIVE-EXPLORE
- **Target venues:** ICML 2027 / NeurIPS 2027
- **Core constraint:** first meaningful scientific evidence must come from public checkpoints + inference/causal intervention; no model training is required to enter the workbench.

## 1. Territory object

> **Across independently trained model instances, what level of a mechanistic claim is actually reproducible: exact component, causal role, algorithm, developmental ordering, or only behavior?**

This is a territory, not a registered final RQ.

Do not pre-register:
- mechanisms are unstable;
- different seeds learn different algorithms;
- one seed is representative;
- population analysis itself is novel.

The purpose is to measure the population structure first.

## 2. Why this territory is scientifically live

Several mature lines now meet:

1. developmental circuit work shows mechanisms can be tracked over training;
2. PolyPythias provides many independently trained trajectories and dense checkpoints;
3. cross-seed alignment work shows raw coordinate/component differences can be misleading;
4. developmental feature work can align causal features across checkpoints;
5. new 2026 work is already probing formation dynamics, so any contribution must be stronger than “look across seeds”.

This creates a concrete changed premise:

> **A mechanistic statement about one trained realization may not automatically be a statement about the model family.**

But whether this matters at the component, role, algorithm, or developmental level is still an empirical question.

## 3. Strong ownership / compression risks

### Already owned or too close

- **PolyPythias:** model populations, seed variation, dense checkpoints.
- **Tigges et al.:** circuit consistency across training and scale; component identity can turn over while high-level computation remains similar.
- **Crosscoding Through Time:** feature emergence / maintenance / discontinuation across training checkpoints.
- **Polymorphism Is Rotation (2026):** cross-seed representation differences can largely be explained by orthogonal rotation; includes independently trained Pythia-70M seeds and checkpoint analysis.
- **Pre-carved Niches (2026):** follows attribution-defined modular structure during early Pythia training across two trajectories.
- **IOI sign-flip replication work:** shows one developmental causal phenomenon can replicate across variants.

Therefore we cannot claim:
- “different seeds have different internal representations”;
- “head IDs change”;
- “mechanisms should be checked on multiple seeds”;
- “training trajectories differ”;
- “features emerge at different times”.

### Compression test

A future paper must survive:

> “Isn’t this just PolyPythias + an existing circuit metric?”

and:

> “Isn’t cross-seed difference just the rotation / alignment issue already identified?”

The delta must change what counts as a defensible mechanistic claim, expose functionally distinct developmental routes, or identify a consequence/action surface that nearest priors do not own.

## 4. Foothold

### Primary substrate

PolyPythias / Pythia small models:
- 70M first;
- 10 independently trained runs available at this size;
- dense intermediate checkpoints;
- public weights;
- small enough for large causal sweeps on one local GPU.

160M is the next scale only after the 70M harness is stable.

### Mechanism entry point

Begin with one **already established** mechanistic object with released or easily reproducible measurement:
- induction-head behavior / score;
- causal ablation of the relevant heads/components.

The first goal is not discovery. It is instrument validation.

### Compute profile

Phase-1 work is:
- checkpoint download / audit;
- forward passes;
- activation collection;
- ablations / patching;
- statistics.

No pretraining / finetuning / RL is required.

## 5. Pressure families

### A. Abstraction
At what level does reproducibility appear?
- exact head / component;
- causal role;
- algorithm/function;
- developmental ordering;
- emergence timing.

### B. Developmental route
Can matched final behavior arise through genuinely different causal developmental routes after alignment/control?

### C. Functional consequence
If routes differ, do they differ in robustness, generalization, intervention response, or downstream behavior?

### D. Measurement validity
How much apparent population variation is extraction noise, basis rotation, alignment choice, checkpoint corruption, or metric instability?

### E. Training pressure
Only after a stable population distinction exists: what training variation predicts or selects the route?

## 6. First residency block

### R0 — artifact integrity
Audit the exact 70M seed/checkpoint artifacts used. Record:
- model repo/revision;
- checkpoint IDs;
- hashes where feasible;
- missing/duplicated/inconsistent checkpoints;
- accepted manifest.

Do not treat hosting bugs as scientific findings.

### E01 — parent mechanism reproduction
On one canonical Pythia-70M trajectory:
- reproduce the chosen induction behavior metric;
- reproduce the mechanistic score;
- reproduce a causal ablation effect;
- check several training checkpoints.

No new claim.

### E02 — cheap population measurement
Only after E01 works:
- canonical + 9 seeds;
- ~12–20 phase/log-spaced checkpoints, not every checkpoint;
- same held-out examples and intervention protocol;
- record behavior, mechanistic score, causal effect, component identity, emergence/turnover.

The training run/seed is the experimental unit.

### E03 — abstraction ladder
Before calling anything “different mechanism”, separate:
1. component identity;
2. coordinate/alignment difference;
3. causal role;
4. algorithmic function;
5. developmental ordering/timing.

Alignment is a control, not a result generator.

## 7. Decision branches

- **Only exact components differ; causal role/algorithm is stable** → investigate the correct abstraction level of mechanistic reproducibility.
- **Differences disappear after alignment / better extraction** → measurement lesson; do not overclaim population mechanism diversity.
- **Behavior matches but causal role/algorithm differs across ordinary runs** → high-priority lead; test functional consequences before any training intervention.
- **Variation is dominated by outlier/corrupt runs** → audit/instrument problem first.
- **Everything meaningful is trivially identical** → do not force a paper; review scientific yield.
- **Interesting pattern exists only for induction** → no candidate yet; add one independent established mechanism before generalizing.

## 8. Paper shapes that could eventually emerge

Only after evidence:
- **measurement/science:** correct abstraction level for reproducible mechanistic claims;
- **failure + consequence:** single-run mechanism inference fails because multiple causal routes reach matched behavior;
- **training dynamics:** route selection has a stable predictor / training pressure;
- **method/intervention:** a real route-level bottleneck is identified and a minimal intervention changes route or functional consequence.

No method is required at entry.

## 9. Main risks

- direct 2026 prior compresses the same population-level causal claim;
- representation alignment explains most apparent variation;
- induction is too toy/special;
- checkpoint integrity dominates;
- final paper remains “more seeds + error bars”.

## 10. Selection decision

**2026-10-01 — SELECTED → ACTIVE-EXPLORE.**

Reason:
- top-conference-scale scientific object;
- strong public substrate;
- first meaningful experiment is cheap and inference/causal-intervention based;
- matches mechanistic-interpretability / training-dynamics taste;
- multiple pressure families exist without requiring a guessed anomaly;
- expensive training is conditional on later evidence, not required to create the initial experimental object.
