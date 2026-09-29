# Mechanism Population Dynamics — Workbench

**Lane:** our-taste / model science  
**Status:** ACTIVE, exploratory — **not a candidate**  
**Created:** 2026-09-29

## 0. Territory

This workbench treats a model's internal mechanism and its developmental trajectory as a **random variable over training histories**, not as a fact established by one trained realization.

The mother territory is:

> Under matched objectives / data distributions, which properties of learned computation are developmental invariants across training runs, which are path-dependent, and what training variation selects among alternative implementations?

This is **not**:
- “run the same circuit paper with more seeds”;
- “find another training-time anomaly”;
- “prove circuits are unstable”;
- “explain one PolyPythia outlier”;
- a fixed claim that data order / initialization must change algorithms.

The workbench exists because several mature lineages now make this question experimentally accessible.

---

## 1. Parent lineage and why the object exists now

### Parent A — mechanisms can be tracked over training

**Tigges et al., LLM Circuit Analyses Are Consistent Across Training and Scale (NeurIPS 2024)**  
https://proceedings.neurips.cc/paper_files/paper/2024/hash/47c7edadfee365b394b2a3bd416048da-Abstract-Conference.html

Tracks circuit formation across Pythia scales and checkpoints. The high-level algorithm can remain stable while individual heads turn over.

**Pressure created:** exact components and functional mechanism are different levels of description.

### Parent B — competing ICL mechanisms can be developmentally related

**Yin & Steinhardt, Which Attention Heads Matter for In-Context Learning? (ICML 2025)**  
https://proceedings.mlr.press/v267/yin25e.html

Induction heads and function-vector heads are compared in one causal frame; many FV heads begin as induction heads before transitioning.

**Pressure created:** mechanisms are not only static alternatives; one computational role can develop into another.

### Parent C — training distribution can select the learned algorithm

**Kawata et al., From Shortcut to Induction Head (NeurIPS 2025)**  
https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html

A controlled setting shows that data diversity selects between a positional shortcut and a generalizable induction algorithm while both can fit the training objective.

**Pressure created:** successful behavior does not identify the internal algorithm; training pressure can choose among alternatives.

### Parent D — representation development is now observable longitudinally

**Bayazit et al., Crosscoding Through Time (ACL 2026)**  
https://aclanthology.org/2026.acl-long.60/

Crosscoders align features across checkpoints and expose feature emergence, maintenance, discontinuation, and causal importance over training.

**Pressure created:** developmental interpretability can study trajectories rather than final snapshots.

### Parent E — pretraining itself should be treated as a population

**van der Wal et al., PolyPythias (ICLR 2025)**  
https://proceedings.iclr.cc/paper_files/paper/2025/hash/d611d06e3207330555fbc10810e70163-Abstract-Conference.html

45 additional runs + 5 originals, 10 seeds per size, 5 sizes (14M–410M), ~7k checkpoints.

They study:
- downstream behavior;
- linguistic representation;
- parameter/training-map dynamics.

They find substantial population-level regularity plus identifiable outlier runs.

**Changed premise for this workbench:**

> If behavioral / representational conclusions require multiple training realizations, mechanistic conclusions may also require a population view.

PolyPythias does **not** itself perform a population-level mechanistic analysis.

### Strong nearest prior — one mechanism can already be replicated across training variants

**Dahiya & Blondin, A Training-Time Sign Flip During the Formation of an IOI Circuit (ICML 2026 MI Workshop)**  
https://github.com/Tejas7007/ICML_2026_MIW_IOI_Sign_Flip

Replicates an IOI training-time intervention reversal across six Pythia scales, nine PolyPythia variants, and Stanford GPT-2 Small.

This is an important baseline, not a reason to close the territory.

It shows:
- developmental causal measurements can be repeated across runs;
- one phenomenon can be robust even when component identities / training histories differ.

It does **not** establish the population statistics of mechanism formation across tasks or abstraction levels.

---

## 2. Broader scientific object / top-conference ceiling

Local substrate:

> dense multi-seed checkpoints + known mechanistic objects.

Broader object:

> **What is a reproducible mechanistic fact about a learned model family?**

Possible field-level consequences include:
- showing that single-run circuit conclusions are reliable only at a particular functional abstraction level;
- showing that equivalent behavior can arise through multiple developmental routes;
- identifying which training randomness controls mechanism selection;
- separating coordinate/component variability from genuine algorithmic variability;
- establishing population-level standards for developmental mechanistic claims.

The ceiling is not “Pythia seeds behave differently”.

A candidate-worthy outcome must matter for how mechanistic interpretability makes claims about *classes of trained models*, not one checkpoint.

---

## 3. Why this is not just Prior A + PolyPythias

The parents leave complementary gaps:

- Tigges: mechanism × training × scale, mostly one training realization per model size.
- Yin: developmental transition between two known ICL mechanisms, not a population study.
- Crosscoding Through Time: feature development along selected training trajectories, not stochastic population structure.
- PolyPythias: population training dynamics, but behavior / probes / parameter-state maps rather than detailed computation.
- Polymorphism-style work: cross-seed representational alignment / coordinate freedom, mainly final-state or representation-level.
- IOI sign-flip work: one developmental causal phenomenon replicated broadly.

The workbench asks whether there are **population laws of computation formation**, and at what abstraction level they exist.

That scientific object cannot be answered by adding error bars to one existing circuit figure.

---

## 4. Artifact substrate

### Primary: PolyPythias

Public assets include:
- 10 training runs per model size;
- 14M / 31M / 70M / 160M / 410M;
- 154 checkpoint positions per run;
- public pre-shuffled data variants / metadata.

Good starting sizes:
- 70M for cheap full-population sweeps;
- 160M for richer head/layer structure;
- 410M only after the harness is stable.

### External-validity substrate: OLMo-2

OLMo-2 exposes real training branches.

Useful natural experiment:
- same Stage-1 parent;
- multiple Stage-2 runs with different random seeds / data order;
- 1B final branches are directly available;
- 7B/13B training includes multiple Stage-2 branches and final weight-averaged “soups”.

This gives a realistic late-training population distinct from Pythia pretraining.

Do **not** begin with 7B/13B soup experiments. Earn them after the small-model population analysis yields a meaningful distinction.

### Existing mechanism code

Prefer existing released code before writing new extraction infrastructure:
- ICL induction / FV head analyses from Yin & Steinhardt;
- IOI sign-flip release;
- TransformerLens / pyvene as needed;
- Crosscoding Through Time only if feature-level trajectory becomes necessary.

---

## 5. R0 — artifact integrity audit (mandatory)

Pythia / PolyPythia checkpoint artifacts have known 2026 GitHub reports of corrupted or inconsistent branches.

Known risks include:
- Pythia-2.8B: many labelled intermediate branches appear to serve duplicated final-era weight files;
- Pythia-12B: reported mid-training shard anomalies;
- PolyPythia 160M `weight-seed` variants: reported mismatch between published step-0 initialization and later trajectory;
- several individual 410M checkpoints are missing.

Therefore:

1. hash / tensor-continuity audit every selected model family before analysis;
2. write a machine-readable manifest of accepted/rejected checkpoints;
3. do not use Pythia-2.8B for developmental conclusions unless independently repaired/audited;
4. do not treat the current 160M `weight-seed` variants as clean initialization-only controls;
5. prefer ordinary 70M/160M/410M PolyPythia seeds initially;
6. replicate important conclusions on OLMo-2 or another independent suite before candidate promotion.

Artifact failure is not a paper finding unless it changes a broader scientific conclusion.

---

## 6. First-night baseline residency

Agent execution should optimize **information gain**, not exhaustively run every checkpoint.

### N0 — reproduce a known developmental mechanism

On one canonical Pythia run, reproduce one or two strong parent measurements:

- induction-head score + causal ablation;
- FV-head score + causal ablation where model/task support permits;
- IOI developmental intervention / suppressor trajectory.

Goal:

> verify the harness measures the same object as the parent paper.

No new claim.

### N1 — population replicate

Run a cheap population grid first:

- model: Pythia / PolyPythia 70M or 160M;
- runs: canonical + 9 seeds;
- checkpoints: ~12–20 log-/phase-spaced checkpoints, not all 154;
- mechanism: begin with induction because it is cheap and well-defined.

Record per run/checkpoint:
- behavioral task metric;
- mechanistic score;
- causal ablation effect;
- layer/head identity;
- emergence time;
- disappearance / turnover;
- functional role after emergence.

Do not average away the population.

### N2 — abstraction ladder

Compare stability at multiple levels:

1. **exact object:** same layer/head/component;
2. **role:** some component performs the same causal function;
3. **algorithm:** the same input-output computation is implemented;
4. **developmental ordering:** the same computational stages appear in the same order;
5. **timing:** stages appear at the same training fraction/token count.

This is crucial.

If exact heads differ but role/algorithm is stable, that is not “mechanistic instability”.

If role and algorithm differ while behavior is matched, that is a much stronger signal.

### N3 — natural population variation

Use PolyPythia runs that are already known to be ordinary vs outlier training histories.

Ask descriptively:
- do outlier runs traverse the same mechanistic states at shifted times?
- skip a state?
- select a different functional solution?
- differ only at parameter/behavior level while mechanism remains invariant?

No prediction is pre-registered.

### N4 — second mechanism / second task

Do not build a paper around induction alone.

If N1–N3 produce useful structure, add another existing mechanistic object:
- IOI repeated-name suppression;
- FV-head development;
- another well-established copying/successor mechanism with released evaluation code.

Purpose:

> distinguish an induction-specific biography from a population-level property of computation.

---

## 7. Phase-2 analyses only if the first night earns them

### P1 — isolate sources of randomness

PolyPythia provides data-order variants, but initialization-only variants currently have an integrity warning.

Use only audited controls.

Potential sources:
- batch/data order;
- initialization;
- stage-specific continuation seed;
- model size.

Do not claim causal attribution to initialization if the artifact is not trustworthy.

### P2 — OLMo-2 Stage-2 natural experiment

Use OLMo-2 1B first.

Same Stage-1 parent → multiple Stage-2 branches.

This is unusually clean for asking whether late training:
- preserves a shared mechanism;
- creates branch-specific implementations;
- changes only component identities;
- produces different computational routes with similar final behavior.

### P3 — model soup, only if branch diversity exists

OLMo-2 7B / 13B include weight-averaged final models.

If individual branches show mechanistic diversity, then — and only then — inspect the soup.

Possible questions:
- does averaging preserve the common functional core?
- does it average away branch-specific mechanisms?
- can a behaviorally strong soup implement a mechanism not cleanly attributable to any branch?

This is an exploratory branch, not the registered mother question.

### P4 — representation alignment as a control

If cross-seed mechanisms look different, test whether the difference is merely a coordinate/basis transformation.

Use alignment / Procrustes-style controls before calling two runs mechanistically different.

Do not confuse:
- rotated representation;
- different component allocation;
- different algorithm.

---

## 8. Statistical unit and evidence discipline

The **training run/seed is the experimental unit**, not the prompt.

For population claims:
- report distributions across runs;
- use bootstrap / hierarchical uncertainty where appropriate;
- show every run, not just mean ± prompt-level CI;
- predefine functional-equivalence metrics before cherry-picking an “interesting” seed;
- distinguish extraction noise from training-run variance.

For any mechanism:
- readability / attribution is insufficient;
- include causal ablation or intervention where feasible;
- test the same functional claim on held-out prompts.

---

## 9. Multiple plausible outcomes

The workbench is deliberately useful under several outcomes.

### Outcome A — exact components vary, functional algorithm is invariant

Then the important scientific object is the **correct abstraction level of mechanistic reproducibility**.

This would strengthen, not weaken, single-run MI — but only at the functional level.

### Outcome B — multiple developmental routes reach similar behavior

Then mechanistic biography is path-dependent.

Ask what training variation selects the route and whether routes differ in robustness/generalization.

### Outcome C — one route dominates across nearly all runs

Then mechanism formation may be a strong inductive bias of the architecture/data regime.

The next question becomes why that route is selected so reliably.

### Outcome D — variation is concentrated in known training outliers

Then developmental mechanism may diagnose or explain training instability, but do not turn this into forecasting unless the scientific boundary is distinct from existing capability-forecast work.

### Outcome E — apparent cross-seed differences vanish after alignment / better extraction

Then the valuable result is that previous object-level variation was largely coordinate/extraction noise.

### Outcome F — mechanism extraction noise dominates seed variance

Then the immediate bottleneck is the instrument. Demote unless a broader measurement question emerges that is not already owned by MI reliability work.

No outcome is assumed in advance.

---

## 10. What not to optimize

Do not:
- hunt for a spectacular sign flip;
- scan hundreds of tasks for the most anomalous seed;
- treat head-ID turnover as algorithmic change;
- claim “same mechanism” from representation similarity alone;
- train a new SAE/circuit extractor before strong parent measurements are reproduced;
- local-optimize one Pythia result after the population pattern says the object is weak;
- turn a checkpoint-hosting bug into the research story;
- call a result novel merely because previous work used one seed.

The agent should be allowed to pivot among mechanism objects while preserving the mother territory.

---

## 11. Workbench ceiling

```
multi-seed / branched training histories
→ population distribution of mechanistic trajectories
→ identify developmental invariants vs path-dependent computation
→ connect invariance/variation to training pressure or functional consequences
→ possible general principle for mechanistic claims about trained model families
```

This is the ceiling, not a promised paper.

A top-conference paper should eventually simplify to one central finding, not report a zoo of seed statistics.

---

## 12. Demotion / kill conditions

Demote this workbench if:

1. after proper alignment and causal validation, all meaningful mechanisms are trivially identical across runs and the only novelty is adding seed error bars;
2. all observed variation is extraction noise / checkpoint corruption;
3. the only surviving result is exact-head identity variation already explained by coordinate freedom / known polymorphism;
4. the interesting phenomenon exists only for one toy mechanism/task;
5. the OLMo or independent-model replication fails and the result remains Pythia-specific;
6. a direct contemporary paper already performs the same population-level mechanistic analysis across realistic runs and owns the broader conclusion.

Do **not** kill it merely because one expected mechanism does not vary.

Failure of an expected contrast should update which abstraction level or mechanism is worth studying.

---

## 13. Candidate promotion gate

Remain a workbench until there is a paper identity simpler than this README.

Before candidate promotion require at least:

- one audited multi-run substrate;
- at least two mechanistic objects or a compelling reason one object is field-level;
- causal validation, not only probes;
- a stable population-level result;
- evidence separating component/coordinate variation from algorithmic variation;
- at least one independent external-validity substrate (e.g. OLMo-2 branch experiment);
- nearest-prior comparison against Tigges, PolyPythias, Yin, Crosscoding Through Time, Polymorphism-style cross-seed work, Pre-carved Niches, and the IOI sign-flip work;
- a central conclusion that is not “mechanisms differ across seeds”.

Until then: **WORKBENCH ONLY**.
