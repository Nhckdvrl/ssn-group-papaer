
# Territory Card — In-Context Evidence Structure — 2026-10-05

- **Lane:** Sasano-fit / in-context learning / model science
- **Status:** PROPOSED; human-requested registration, training-free baseline residency allowed; does not change current ACTIVE allocation
- **Target venues:** ICML / ICLR / NeurIPS / ACL; choose only after evidence clarifies paper shape
- **Core constraint:** first scientific evidence comes from frozen pretrained LMs + exact-gold procedural prompts. No finetuning/RL is required to enter.
- **One-line territory object:** **Can a frozen LM infer the statistical structure of its in-context evidence—when examples should be treated as an exchangeable set, versus a correlated or evolving sequence—and adapt how it weights evidence accordingly?**

## 1. Why this is a territory rather than an order-sensitivity paper

The durable scientific object is **evidence structure in ICL**, not "order matters".

A learner should not use one fixed aggregation rule for every prompt:
- under one stationary rule with independent demonstrations, order is nuisance and exchangeability/permutation invariance is the natural symmetry;
- under sequential dependence, correlation changes effective evidence;
- under regime change, position/recency is informative and old evidence may need to be downweighted;
- under random corruption, isolated contradictions should not automatically be interpreted as a persistent rule change.

The central question is therefore whether a pretrained LM can infer **what kind of evidence process produced the context** and use the appropriate symmetry/weighting, rather than merely exhibiting a fixed primacy/recency bias.

This framing supports several pressure families even if the first stationary-vs-change hypothesis is false.

## 2. Literature tension that creates the workbench

### A. Exchangeable / stationary demonstrations
- Falck et al., ICML 2024, *Is In-Context Learning in Large Language Models Bayesian? A Martingale Perspective*:
  https://proceedings.mlr.press/v235/falck24a.html
  - formalizes exchangeability/martingale tests for i.i.d. in-context data;
  - finds modern LLMs violate the martingale property and Bayesian scaling in controlled tasks.
- Fang et al., ICLR 2025, *Rethinking Invariance in In-context Learning*:
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/01e8ecf628f8d9f62a1fd433d44d34ab-Abstract-Conference.html
  - treats order sensitivity among mutually independent demonstrations as a defect;
  - proposes InvICL to enforce permutation invariance while preserving context interdependence.
- Li et al., 2025, *Order Matters: Rethinking Prompt Construction in In-Context Learning*:
  https://arxiv.org/abs/2511.09700
  - shows order-induced performance variance can be comparable to changing the example set.

These works already own generic "ICL is order sensitive" and "iid demos should be invariant".

### B. Nonstationary / sequential demonstrations
- Qin et al., ICLR 2026, *Learning to Adapt: In-Context Learning Beyond Stationarity*:
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/8c1df8153bc1b1366fe27f0785e5fdd4-Abstract-Conference.html
  - analyzes nonstationary regression;
  - shows gated linear attention can implement learnable recency and outperform ordinary linear attention.
- Dudley et al., 2026, *In-Context Learning Under Regime Change*:
  https://arxiv.org/abs/2604.16988
  - formalizes in-context change-point detection;
  - studies synthetic regression/dynamical systems and pretrained foundation-model forecasting around shifts.
- Letey et al., 2026, *Sequential Correlations Change In-Context Learning: Effective Context Length and Architectural Mismatch*:
  https://arxiv.org/abs/2607.03660
  - shows within-context correlation changes effective context length and the value of architecture choice.
- Shen et al., AAAI 2026, *Towards Understanding In-Context Learning of Transformers Under Non-I.I.D. Scenarios*:
  https://ojs.aaai.org/index.php/AAAI/article/view/39724
  - gives generalization bounds under non-i.i.d. data; demonstration count and query alignment matter.

These works already own generic "recency can help under drift", "ICL under change points", and "correlation changes ICL".

### C. Conflicting / noisy demonstrations
- Jiao et al., 2026, *Understanding the Dynamics of Demonstration Conflict in In-Context Learning*:
  https://arxiv.org/abs/2603.04464
  - a single corrupted demonstration can strongly hurt rule induction;
  - probes/logit lens/causal ablations identify a two-phase conflict process and position-sensitive heads.

This work and the noisy-label ICL literature already own generic "conflicting demonstrations hurt" and simple noisy-demo mechanism stories.

## 3. The comparison we will inhabit

The strong prior work studies the regimes mostly **one at a time**:
- stationary independent demos -> invariance/order pathology;
- nonstationary sequence -> recency/change detection;
- correlated sequence -> effective context;
- corrupted demos -> conflict/noise robustness.

Fresh search through 2026-10-05 did not locate a direct study whose main object is:

> **whether the same pretrained frozen LM infers which statistical relation holds among its demonstrations and changes its evidence aggregation accordingly.**

This is not claimed as a permanent empty gap. It is the current workbench foothold and must be re-audited whenever the story changes.

### Reviewer-compression test
Any future lead must survive:
> "Isn't this just ICLR'25 order invariance + ICLR'26 nonstationary ICL put in one table?"

A sufficient delta cannot be "we evaluated both". It must establish a **structure-selective quantity**:
- behavior changes in the normatively appropriate direction as evidence for exchangeability / dependence / regime change changes;
- or it fails in a systematic way that distinguishes fixed positional bias from actual statistical-structure inference;
- preferably with a predictive account that transfers to held-out context structures.

## 4. What is explicitly NOT novel here

Do not claim:
- order matters in ICL;
- LLMs violate exchangeability;
- permutation invariance helps independent demonstrations;
- recency helps after concept drift;
- transformers can detect change points;
- correlated examples reduce effective sample size;
- one corrupted demo can mislead ICL;
- sequential tasks can cause in-context interference/forgetting;
- temporary task representations/task vectors exist.

All of those are baselines / parent facts.

## 5. First substrate: exact-gold latent-rule streams

We will build a small procedural generator rather than start from MMLU/GSM8K.

### 5.1 Task-learning core
Each episode contains examples of a hidden rule over nonce attributes and nonce output labels.

Initial simple hypothesis class:
- input: 3 binary attributes with freshly randomized nonce names per episode;
- hidden rule: one of the six single-attribute concepts (which attribute controls the label × polarity);
- output labels: two nonce tokens, with mapping counterbalanced across episodes;
- query: a held-out attribute combination.

Why:
- exact finite hypothesis space -> exact Bayesian/set/sequence baselines are available;
- episode-wise nonce renaming suppresses direct pretraining-label semantics;
- held-out query prevents literal demonstration copying;
- task is simple enough that a medium open LM should have headroom, but E00 must verify this before E01.

If this task is too easy/saturated or too hard, move one step within the same generator family (conjunctions / parity / larger attribute space) rather than switching to a benchmark.

### 5.2 Statistical structures over the same task family
Generate contexts with identical surface protocol but different latent processes:

1. **EXCHANGEABLE / STABLE:** one hidden rule for the whole context; optional independent label noise.
2. **CHANGE:** old rule -> one latent change point -> new rule; final query follows the current rule.
3. **CORRELATED / REDUNDANT:** one stable rule, but demonstrations are correlated/repeated so nominal shot count exceeds effective evidence.
4. **AMBIGUOUS NOISE-vs-CHANGE:** contexts with the same number of contradictions but different temporal organization; isolated/dispersed violations support noise, clustered persistent violations support regime change.

For the core noise-vs-change family, compute exact posterior quantities under the known finite generative process:
- P(stable/noise | context)
- P(change | context)
- posterior over current rule
- Bayes-optimal query probability
- per-demonstration influence under the set and sequential models.

This provides a normative target rather than an arbitrary benchmark score.

## 6. External substrates (calibration / generalization, not novelty)

### A. Demonstration-dependent rule induction
Jiao et al. release:
https://github.com/difanj0713/Understanding-ICL-Demo-Conflict

Useful because:
- operator_induction_text has near-chance zero-shot and strong few-shot dependence;
- public scripts test 4/6/8-shot corruption and position effects;
- can validate our harness against a known conflict effect.

Do not reuse their single-corrupted-demo story as ours.

### B. Formal-language learning
Ghosh et al. ACL 2026 release:
https://github.com/bishwamittra/formaLLM

Useful generators:
- DFA / PFSA / PCFG / PCSG and programmatic benchmark generation.
Use only after the simple latent-rule stream reveals a structure worth testing on a qualitatively different task family.

### C. Sequential-correlation theory code
Pehlevan Group release:
https://github.com/Pehlevan-Group/sequential-correlations-in-context-regression

Use as a theoretical/positive-control reference for correlation/effective-context effects. Do not make "correlation shortens context" a claim.

## 7. Standard measurement

The workbench should measure **evidence weighting**, not only final accuracy.

### M1. Stationary permutation dispersion
For a fixed exchangeable multiset D and K permutations:
- accuracy variance;
- std / range of target-label log odds;
- JS divergence across output distributions when available.

### M2. Counterfactual demonstration influence kernel
For each demonstration position t, replace/flip that demo while holding all others fixed:
- delta_t = change in target-label log odds.
This estimates how much each location controls the prediction.

### M3. Set-vs-sequence oracle fit
For each episode compute:
- set oracle: one stable-rule posterior;
- sequence oracle: posterior over a possible change point/current rule;
- mixture/meta oracle: posterior over which structure generated the context.

Compare LM probabilities against all three. A model that merely has fixed recency bias can perform on some change episodes without actually inferring structure.

### M4. Structure selectivity
Primary descriptive quantity:
> Does the model's evidence-weighting kernel move toward set-like symmetry when the evidence supports stationarity, and toward selective recency/segmentation when the evidence supports a regime change?

Do not freeze one formula before E00 establishes stable readouts. Candidate statistics include:
- difference in fitted sequence-oracle weight between CHANGE and STABLE;
- correlation between LM log odds and exact log Bayes factor for change vs noise;
- stationary permutation dispersion vs change-aware current-rule accuracy.

## 8. First residency sequence

### E00 — task-learning instrument validation
- frozen Qwen3-8B first;
- clean stable episodes only;
- zero-shot chance control;
- few-shot held-out generalization;
- nonce-label/attribute remapping;
- several random episode seeds.
Goal: establish that the chosen synthetic family supports genuine demonstration-dependent learning with enough headroom.

### E01 — two-extreme calibration
Cross the same rule family with:
- clean exchangeable/stable contexts;
- obvious single-change contexts.

Measure M1/M2/M3.
This is not novelty. It checks whether the instrument can distinguish a regime in which order should not matter from one in which order should.

### E02 — decisive structure-inference pilot
Construct **noise-vs-change** contexts with matched:
- number of demonstrations;
- token budget;
- input marginal;
- label marginal / contradiction count where feasible;
- nonce dictionary;
- query distance.

Vary only the temporal organization / persistence of contradictory evidence.

Competing accounts:
1. **fixed positional prior:** essentially the same recency/primacy kernel regardless of evidence structure;
2. **set learner:** treats context largely exchangeably and under-reacts to persistent changes;
3. **sequence heuristic:** favors recent examples even when contradictions are isolated noise;
4. **adaptive structure learner:** shifts toward the appropriate set/sequence oracle as statistical evidence for a regime changes.

All four make different predictions before white-box analysis.

### E03 — only if E02 is informative
Add one orthogonal structure:
- correlated/redundant demonstrations, or
- a second task family (formal language / operator induction).

Only then consider internal readouts/interventions.

## 9. Confound audit

Must control:
- **recency vs structure:** equalize prompt length/query distance; counterbalance positions; compare clustered change evidence to dispersed noise with matched counts;
- **task recognition vs task learning:** episode-randomized nonce names/labels and held-out inputs;
- **label semantics:** rotate nonce output dictionaries;
- **prompt wording:** one fixed neutral instruction; explicit "order matters" only as an upper-bound control;
- **arithmetic/reasoning ability:** primary generator uses simple categorical attributes, not math;
- **copy/retrieval:** held-out query and hypothesis-class generalization;
- **difficulty:** E00 establishes single-regime headroom before structure experiments;
- **position-token artifacts:** multiple context lengths and mirrored placements;
- **post-hoc slicing:** E02 decision table is written before running.

## 10. Pressure families

A. **Symmetry:** does the model respect exchangeability when order truly carries no information?
B. **Dependence:** does it discount redundant/correlated evidence rather than count nominal shots?
C. **Nonstationarity:** does it selectively downweight stale evidence after genuine changes?
D. **Structure inference:** can the model decide which of A–C applies from the context itself?
E. **Conflict attribution:** does contradictory evidence become "noise/outlier" or "new regime", and when?
F. **Transfer:** does the same structure-selective behavior survive a new task family / natural-ish setting?
G. **Mechanism (conditional):** only after behavior distinguishes accounts, ask how the model implements the switch.

## 11. Sasano-fit / lab-collision fence

Why this matches the advisor's research shape:
- one-minute natural question: **"When should example order matter to an LLM, and does the model know the difference?"**
- both outcomes are informative;
- the first runs measure a stable phenomenon; later runs ask why;
- every expansion is tied to competing explanations;
- no capability race / benchmark-score objective;
- initial exploration is entirely frozen-model inference.

Lab collision fence:
- not Utami AI-writing change;
- not Yano/Han frame semantics;
- not Sato character-knowledge acquisition;
- not Tsukagoshi/Kisako embedding/compression;
- not Hamdi real-vs-fiction representation;
- not Tanaka survey/value simulation;
- not Kurauchi audience-adapted explanation;
- not Kan idioms;
- not Guo annotation.

## 12. Registration decision

**2026-10-05 — REGISTERED AS PROPOSED.**

Rationale:
- strong, recent parents create a genuine tension instead of an invented empty gap;
- no direct owner was found for adaptive inference of demonstration statistical structure in one frozen pretrained LM;
- exact-gold procedural data can test the object cheaply;
- E00/E01 are calibration; E02 directly separates four computational accounts;
- the territory can survive a null first result: a fixed-recency or set-only learner is itself a structured answer and points to the next discriminating experiment;
- no training is needed to discover the first scientific object.
