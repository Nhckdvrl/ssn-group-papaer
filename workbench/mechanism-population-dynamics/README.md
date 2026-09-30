# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. What is registered

We are not registering a final RQ, method, or expected anomaly.

The registered exploration object is:

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

The model population is the experimental object.

Current state:
- final paper identity: **none**
- established claims: **0**
- method commitment: **none**
- training requirement for entry: **none**

## 1. Why this is worth inhabiting

The required artifacts already exist.

PolyPythias exposes independent training runs and dense checkpoints for small Pythia models. That lets us study mechanism formation as a population without paying to pretrain the population ourselves.

The closest literature also makes the naive versions of the story illegal:
- PolyPythias already owns population-level training variation;
- Tigges et al. already show circuit/component turnover across training/scale;
- Crosscoding Through Time already studies causal feature development across checkpoints;
- Polymorphism Is Rotation shows cross-seed internal coordinates can differ mainly by rotation and explicitly studies independent Pythia-70M seeds;
- Pre-carved Niches studies formation dynamics across Pythia training trajectories.

So this workbench cannot be:
> “different seeds have different internals.”

It must determine what **survives the right controls and abstraction changes**.

## 2. Primary substrate

Start with **Pythia / PolyPythia 70M**.

Why:
- canonical run + independent seeds are public;
- dense checkpoints are public;
- cheap enough for broad causal sweeps;
- existing interpretability tooling is mature.

Do **not** begin with 410M/1B+.

160M is only the next scale after the 70M harness is stable.

## 3. First mechanism

Begin with one known, cheap mechanistic object:

> **induction behavior / induction-head measurement + causal ablation**

The purpose is instrument validation, not novelty.

Only after we reproduce a parent measurement are population comparisons interpretable.

## 4. Phase-1 execution

### R0 — artifact integrity audit

Before science:
- pin exact model repositories / revisions;
- build accepted-checkpoint manifest;
- check missing/duplicated/inconsistent checkpoints;
- record hashes/tensor sanity where feasible.

Artifact bugs go to `PAIN_LOG.md`; they are not paper findings by default.

### E01 — known-mechanism reproduction

One canonical Pythia-70M trajectory.

Reproduce:
- behavioral induction metric;
- mechanistic/head score;
- causal ablation effect;
- several checkpoints covering pre-emergence → emergence → later training.

Goal:
> confirm our harness measures the parent object.

No population claim yet.

### E02 — population sweep

Only if E01 is valid:
- canonical + 9 independent 70M runs;
- ~12–20 phase/log-spaced checkpoints;
- same examples / intervention protocol;
- record behavior, mechanistic score, causal effect, component identity, emergence / turnover.

Do not average away runs.

The **training run/seed** is the unit for population claims.

### E03 — abstraction ladder

Before saying “mechanisms differ”, distinguish:
1. exact component identity;
2. coordinate / alignment difference;
3. causal role;
4. algorithm / functional computation;
5. developmental ordering;
6. timing.

Representation alignment / Procrustes-style controls are mandatory if raw cross-seed internal differences matter.

## 5. What counts as a useful signal

High-value signals include:
- matched behavior but different **causal role / algorithm**, not merely different head IDs;
- stable algorithm but unstable exact components, revealing the correct abstraction level;
- multiple developmental routes with different functional consequences;
- one route is systematically associated with robustness/generalization/intervention response;
- apparent diversity disappears under alignment, showing the previous mechanistic object was mis-specified.

Low-value signals:
- different head numbers;
- different raw activation coordinates;
- slightly different emergence step;
- one spectacular outlier seed;
- more error bars on an existing circuit figure.

## 6. Triggered branches only

### Second mechanism
Only after E01–E03 reveal a stable population-level distinction.

Use another established causal object (e.g. IOI/FV/copying-style mechanism) to test whether the result is induction-specific.

### Larger scale
160M only after 70M gives a clear measurement object.
410M+ only after the distinction survives.

### External model family
Only after the central distinction is clear. Do not add families merely to tick L3.

### Training intervention
Only if:
> stable population structure → plausible selector/bottleneck → cheap controllable action.

Do not train models just to “complete the paper”.

## 7. Ownership / compression rules

Continuously test against:
- PolyPythias;
- Tigges et al.;
- Crosscoding Through Time;
- Polymorphism Is Rotation;
- Pre-carved Niches;
- IOI developmental replication / sign-flip work;
- current causal-abstraction / mechanism-reliability papers.

A promising lead must answer:
> Why is this not existing mechanism analysis + more seeds?

and:
> Why is this not just a coordinate/alignment artifact?

Strong 2026 preprints own claims too.

## 8. Paper shape card

- **Current one-line thesis:** not set.
- **Current contribution count:** 0.
- **Current claim count:** 0.
- **Likely shapes if earned:** measurement/science; failure + consequence; training-dynamics explanation; minimal intervention.
- **Not allowed as final story:** “mechanisms differ across seeds”.
- **Evidence floor for a real mechanism claim:** causal intervention, held-out prompts, population-level uncertainty, alignment/control against coordinate freedom.
- **Candidate gate:** one simple field-level conclusion that survives at least one independent mechanistic object or an equally strong external-validity test.

## 9. Stop / human-review triggers

Stop autonomous expansion and request human review when:
- E01 does not reproduce the parent object;
- E02 shows a stable nontrivial population structure;
- alignment removes the main effect;
- a direct 2026/2027 prior owns the emerging claim;
- a second mechanism or larger model is about to be added;
- any model training is proposed;
- the paper identity becomes clearer enough to write a one-line thesis;
- scientific yield appears weak after the baseline + measurement residency.

## 10. What not to do

- no anomaly hunting across hundreds of tasks;
- no cherry-picked seed;
- no “head turnover = different algorithm”;
- no SAE/probe zoo before the baseline causal object works;
- no new mechanism extractor at entry;
- no large-model scaling before 70M earns it;
- no training just because training-dynamics is in the title;
- no claim that one representation alignment metric defines mechanism equivalence;
- no fixed paper story before the population measurement exists.

## 11. Decision record

- 2026-09-29: old exploratory note created; never fully registered under v4.
- **2026-10-01: human selected this territory as the sole ACTIVE-EXPLORE line.**
  - reason: strong public multi-run substrate;
  - first scientific loop is inference/causal-analysis only;
  - avoids the high up-front RL cost that paused `multi-llm-collaboration`;
  - current nearest priors make the required novelty boundary explicit rather than forcing an anomaly bet.

## 12. Assets

- claims: `CLAIMS.md`
- pain log: `PAIN_LOG.md`
- experiment cards/scripts: `experiments/`
- ideas only after real signals: `ideas/`
- human reviews: `logs/`
- large checkpoints / caches: local storage only; repo records exact source/revision/manifest
