# Territory Bank

**Purpose:** reusable scientific territories, not ready-made paper ideas.

A territory belongs here when it is broad enough to accumulate expertise across multiple projects, but concrete enough that we can name strong baselines, recurring assumptions, and natural empirical objects.

---

## T01 — Post-training / learning-signal dynamics

**Why keep inhabiting it**

Modern post-training is no longer just “SFT vs DPO vs RL”. Strong work increasingly asks what the actual learning signal is doing: which samples/tokens update the policy, what the pretrained prior contributes, where calibration/diversity move, and which behaviors are written vs merely elicited.

**Recurring assumptions worth auditing**

- all tokens in a trajectory contribute equally;
- correct and incorrect samples are symmetric learning signals;
- reward unit = optimization unit;
- benchmark gain implies the intended mechanism improved;
- a stage label (SFT/RL/etc.) is itself a scientific variable.

**Baseline / observation first**

Use strong open recipes and checkpoints; inspect learning curves, sample classes, entropy, calibration, behavior retention, and modest recipe perturbations before proposing mechanism.

**High-risk failure mode**

One optimizer / LR / budget trajectory becomes a “law”.

**Anchors:** PT01–PT09, B06–B09.

---

## T02 — Reasoning / test-time compute as a policy

**Why keep inhabiting it**

The field moved from “does more reasoning help?” to **where, when, and how compute should be spent**.

**Recurring assumptions**

- more samples are uniformly useful;
- every reasoning step has equal marginal value;
- final-answer verification is enough;
- problem difficulty can be treated as a single scalar;
- explicit CoT is the only useful computation carrier.

**Natural observations**

- failure onset;
- marginal value of additional branches;
- compute allocation by state;
- search/verification disagreement;
- when extra computation stops helping.

**High-risk failure mode**

Another adaptive-compute heuristic with no new scientific object.

**Anchors:** RS01–RS04, PT05, B08–B09.

---

## T03 — Iterative / recurrent-depth computation

**Why keep inhabiting it**

Looped and depth-recurrent models reopen a basic architecture assumption: depth normally means distinct parameters. They let us separate **parameter count, number of computation steps, inter-visit state, and explicit vs latent reasoning**.

**Recurring assumptions**

- each additional computation step needs new parameters;
- latent repeated computation behaves like deeper feed-forward computation;
- the full residual stream must cross every visit;
- recurrence naturally preserves a stable “workspace”.

**Natural observations**

- what changes across visits;
- minimum state required between visits;
- task/depth dependence of state demand;
- whether useful computation is reconstructive, persistent, or repeatedly recreated.

**High-risk failure mode**

Synthetic tasks define the mechanism we later “discover”; or incomparable training recipes are treated as architecture-only controls.

**Anchors:** AR05–AR09, MI05, B02.

---

## T04 — Memory / long context / knowledge location

**Why keep inhabiting it**

“Memory” now spans several physically different objects: attention KV, recurrent state, compressive memory, test-time learned memory, external retrieval, prompt context, adapters, and runtime-generated state/weights.

**Recurring assumptions**

- compressed state substitutes for exact access;
- retention = accessibility;
- long-context success implies stored information is usable under the same query;
- retrieval, persistent state, and parameter adaptation are interchangeable.

**Natural observations**

- exact vs compressed memory demand;
- what information survives compression;
- when queries become informative enough to retrieve;
- persistence after removing exact context;
- write/read/persistence/interference trade-offs.

**High-risk failure mode**

Rebranding ordinary RAG/KV pruning as “memory science”.

**Anchors:** AR01–AR07, B11–B12.

---

## T05 — MoE / sparse routing / structured decisions

**Why keep inhabiting it**

Routing is a clean place to study the gap between **scores, surrogates, discrete Top-K decisions, specialization, and downstream utility**.

**Recurring assumptions**

- router score ranks true expert utility;
- pairwise preference implies Top-K adoption;
- load balance and specialization are aligned;
- better local route value necessarily improves generation.

**Natural observations**

- decision-consistency failures;
- outside-set competitors;
- expert specialization across training;
- route utility vs router logits;
- downstream sensitivity to route interventions.

**High-risk failure mode**

Good diagnostic signal → endless loss search.

**Anchors:** MOE01–MOE03; repository observation `../observations/ROUTE_PREFERENCE_DECISION_CONSISTENCY.md`.

---

## T06 — Mechanistic interpretability / model science

**Why keep inhabiting it**

The strongest direction is not “find another neuron/head”; it is to improve the **explanatory decomposition** of model computation and connect representation to causal use.

**Recurring assumptions**

- neuron is the right unit;
- readable representation = causally used representation;
- one linear direction = one mechanism;
- a probe that predicts behavior explains behavior;
- mechanisms scale unchanged across model size/family.

**Natural observations**

- causal transport / intervention;
- cross-layer/visit reconstruction;
- representation-use dissociation;
- changed mechanisms across scale or training stage.

**High-risk failure mode**

New probe / SAE / lens without a scientific inference that changes.

**Anchors:** MI01–MI05, B03–B05.

---

## T07 — Omni / speech / realtime interaction

**Why keep inhabiting it**

Speech introduces something text systems largely avoid: **physical time**. Streaming, overlap, turn-taking, codec rate, semantic/acoustic information, and latency become model variables rather than serving details.

**Recurring assumptions**

- ASR→LLM→TTS decomposition is lossless;
- text is a sufficient intermediate representation;
- turn boundaries are discrete and externally known;
- semantic vs acoustic tokenization is a complete factorization.

**Natural observations**

- interruption / overlap handling;
- information lost at text bottlenecks;
- latency-quality tradeoffs;
- where turn-taking information lives;
- whether streaming changes representation requirements.

**High-risk failure mode**

Pure system-latency engineering with no scientific quantity.

**Anchors:** VO01–VO02.

---

## T08 — VLA / action representation / embodied control

**Why keep inhabiting it**

Robotics turns sequence-model design into a closed-loop question. Action interface, chunking, tokenization, control frequency, feedback delay, and multimodality all become load-bearing.

**Recurring assumptions**

- one-step actions are the natural output;
- text-like tokenization is adequate for continuous control;
- larger chunks always reduce compounding error;
- semantic pretraining transfers cleanly to action;
- offline action quality predicts closed-loop behavior.

**Natural observations**

- action representation bottlenecks;
- chunk horizon vs feedback;
- tokenization failure at high frequency;
- open-loop vs closed-loop gaps;
- transfer across embodiments/action spaces.

**High-risk failure mode**

Data collection and benchmark construction become the paper.

**Anchors:** VLA01–VLA05.

---

## T09 — Re-attribution / negative results / measurement

**Role**

This is a **question-forming source**, not a preferred benchmark-paper track.

Strong negative work often shows:

> the reported phenomenon is real, but the accepted explanation / measurement is wrong.

**Recurring targets**

- metric vs actual capability;
- parser/post-processing artifacts;
- decoding vs learned distribution;
- model effect vs scale/recipe effect;
- proxy vs deployed decision.

**Natural first move**

Make the strongest baseline boringly correct, then find where the claimed story survives.

**Anchors:** RC01, XD01–XD03, B01, B03.

---

## T10 — Cross-domain method formation: diffusion / optimization / CV

**Role**

Use these fields to learn **how questions are formed**, not to mechanically transfer methods.

Useful patterns:
- method zoo → explicit design space;
- endpoint explanation → trajectory dynamics;
- weak baseline → strong baseline overturns narrative;
- one global schedule → state/sample-dependent allocation.

**Anchors:** RC01, XD01–XD03, B14–B15.

---

## T11 — AI4Quant / structured multivariate models

Current repository territories:
- `../AI4Quant/territories/state-coverage-vs-exposure-coverage.md`
- `../AI4Quant/territories/forecast-skill-vs-structural-skill.md`

Use finance only when it supplies a load-bearing structural oracle, intervention, or decision consequence—not merely a new dataset.

---

## T12 — Agents / search / tools

**Role:** mostly deployment-pressure and experimental-object source; not a default execution track.

Useful scientific objects:
- adaptive information acquisition;
- memory/action coupling;
- search-state evolution;
- tool semantics vs executed effects;
- long-horizon credit / correction.

**Risk**

Environment, tool schema, evaluator, and simulator engineering can dominate the scientific contribution.

**Anchors:** B08, B13.
