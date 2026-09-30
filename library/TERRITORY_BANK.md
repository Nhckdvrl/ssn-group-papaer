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

**Anchors:** AR06–AR07, AR09, MI05, B02.

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

**Anchors:** AR01–AR08, B11–B12.

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

**Anchors:** MOE01–MOE03; repository observation `../workbench/moe-route-preference/README.md`.

---

## T06 — Mechanistic interpretability / model science

**Why keep inhabiting it**

The frontier has moved beyond “find another neuron/head”. By 2025–2026, major pressure sits on the **validity of mechanistic evidence itself**: what the causal mediator is, whether an explanation is identified or merely one convenient decomposition, whether interventions reflect natural computation, and whether an interpretation provides actionable information beyond cheaper behavioral/logit baselines.

**Recurring assumptions worth auditing**

- neuron / SAE feature / circuit edge is the right causal unit;
- readable or linearly decodable representation = naturally used representation;
- higher IIA / attribution score = better mechanistic explanation;
- a more expressive alignment map is always better;
- one SAE dictionary is a canonical feature inventory;
- structurally different circuits imply different mechanisms;
- successful steering proves the steered direction is the natural mechanism;
- a narrow model organism is representative of broad post-training;
- internal interpretability has comparative advantage over black-box/logit/activation-difference baselines.

**Natural observations**

- mediator complexity vs held-out intervention generalization;
- negative-control success/failure (random/wrong-task models, shuffled variables);
- cross-seed / cross-method explanation stability;
- structural difference vs functional interchangeability;
- intervention naturality / off-manifold effects;
- proxy metric vs practical/actionable outcome;
- internal model-diff signals vs simple output/logit differences;
- explanation transfer across prompts, distributions, checkpoints, and model pairs.

**Baseline / observation first**

Start from MIB / causal abstraction / SAEBench / established model-diffing harnesses. Reproduce strong simple baselines and negative controls before proposing a new mediator, SAE, circuit algorithm, or steering method.

**High-risk failure modes**

- behavior anomaly → synthetic task → probe/SAE/DAS → “mechanism”;
- another SAE/probe/lens without changing a scientific inference;
- using only one toy or narrow fine-tune and generalizing to LLM mechanisms;
- treating a flexible analysis pipeline's fit as evidence that the model itself implements the proposed abstraction.

**Deep map:** `deep/academic/INTERPRETABILITY_LANDSCAPE_2026.md`  
**Tool map:** `deep/open-artifacts/INTERPRETABILITY_TOOLING_2026.md`  
**Anchors:** MI01–MI05 plus MIB, SAEBench, causal abstraction, Non-Linear Representation Dilemma, 2026 SAE consistency / model-diffing work.

---

## T07 — Omni / speech / realtime interaction

**Why keep inhabiting it**

Speech introduces something text systems largely avoid: **physical time**. Streaming, overlap, turn-taking, codec rate, semantic/acoustic information, and latency become model variables rather than serving details.

By 2026 the territory extends beyond speech modeling itself: grounded agents increasingly observe partial input, generate, call tools, receive results, and run background tasks **while interaction continues**. This makes the transition from sequential/turn-based capability to realtime/streaming/asynchronous capability a reusable scientific object rather than a serving detail.

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

**Anchors:** VO01–VO12.

**Current workbench:** `../workbench/realtime-agent-capability-transition/README.md`.

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
- `../workbench/ai4quant/territories/state-coverage-vs-exposure-coverage.md`
- `../workbench/ai4quant/territories/forecast-skill-vs-structural-skill.md`

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


---

## T13 — Game NPCs / interactive characters

**Why keep inhabiting it**

Foundation-model NPCs are not merely dialogue generators. In actual games they sit at the junction of **character identity, memory, shared world state, social reasoning, action/control, narrative authority, latency, and player experience**. Recent work increasingly shows that optimizing one of these in isolation can move another in the wrong direction.

**Recurring assumptions worth auditing**

- fluent / persona-consistent dialogue implies a good NPC;
- remembered text implies stable relationship or behavior;
- more open-ended interaction is monotonically better;
- the LLM should own world state, social state, planning, and low-level action;
- dialogue-only evaluation predicts co-play quality;
- LLM-as-judge roleplay scores are sufficient evidence;
- adding more context/memory is always helpful;
- a believable social simulation is behaviorally faithful;
- visual realism in a game world model implies state-aware NPC behavior.

**Natural observations**

- which component owns or validates each state transition;
- linguistic persona vs action/trajectory persona;
- verbal vs non-verbal social behavior;
- player/NPC shared-state disagreement;
- long-horizon commitment survival;
- role/task dependence of structure vs openness;
- deliberative vs reflexive control timescales;
- player outcome / cognitive-load changes that disagree with response-quality scores.

**Baseline / observation first**

Prefer public substrates where the NPC actually interacts with a game loop: CPDC, collaborative Minecraft NPCs, NCP-Bench, MineAmongUs/ARIA, ReactiveGWM, or other released environments. Start by reproducing the strongest baseline and mapping which state/action/evaluation dependency is load-bearing before inventing a memory module, planner, or personality method.

**High-risk failure modes**

- “NPC” becomes a cosmetic wrapper around an ordinary chatbot benchmark;
- simulator/game engineering dominates the science;
- another generic memory/RAG/persona method;
- player-study conclusions without a clear computational object;
- chasing proprietary production NPCs that cannot be reproduced.

**Deep map:** `deep/academic/GAME_NPC_LANDSCAPE.md`.
**Anchors:** NPC01–NPC12, B19–B22.


---

## T14 — Cross-lingual capability formation / multilingual learning dynamics

**Why keep inhabiting it**

Modern multilingual LMs exhibit translation, NLU transfer, reasoning transfer, factual consistency, language control and shared internal representations, but recent controlled work shows these do **not** behave like one scalar “multilingual ability”.

A useful pressure is that explicit bilingual bridges can be nearly indispensable for translation while other cross-lingual tasks remain strong; meanwhile middle-layer semantic alignment can be causally important for NLU, language-specific representation can interfere with reasoning, and factual transfer is often weak/frequency-dominated.

**Recurring assumptions worth auditing**

- shared vocabulary / parallel data is necessary for cross-lingual transfer;
- stronger representation alignment always means stronger functional transfer;
- word/sentence/concept alignment is interchangeable;
- translation, NLU, reasoning and factual transfer rely on the same bridge;
- English-pivot structure is universal multilingual structure;
- final-model geometry reveals how multilinguality formed;
- more language-specific signal is always beneficial for target-language performance.

**Natural observations**

- capability-specific sensitivity to bilingual-data removal;
- lexical vs sentence vs concept alignment over training;
- transfer vs alignment dissociations;
- early vs late cross-lingual transfer;
- language-specific vs language-neutral information by layer;
- shared routing/parameter use across languages;
- target-language generation vs central semantic/reasoning computation;
- factual transfer after controlling prior exposure.

**Baseline / observation first**

Use existing expensive interventions and public trajectories before training anything large:

- MONOWEB/FINEWEB intervention models;
- XLM-R Across Time;
- BLOOM checkpoints;
- OLMo-7B factual-acquisition trajectory;
- MEXA/DALI/shared-concept-space causal tooling;
- False Friends / Macaroni for cheap controlled pretraining.

**High-risk failure modes**

- another “language X is worse than English” benchmark;
- correlating language distance/resource size with performance;
- treating English alignment as the scientific endpoint;
- one more code-switching recipe without a changed premise;
- synthetic-only mechanism claims;
- recreating company-scale multilingual pretraining/scaling studies.

**Deep map:** `deep/academic/CROSS_LINGUAL_CAPABILITY_FORMATION_2026.md`  
**Anchors:** ML01–ML23.
