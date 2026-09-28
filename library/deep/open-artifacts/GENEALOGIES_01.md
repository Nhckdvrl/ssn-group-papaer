# Startup & Hugging Face Genealogies 01 — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal candidate generation.
>
> Scope:
> - recent startups / open research labs;
> - Hugging Face model cards and released artifacts;
> - May–September 2026 emphasis.
>
> This file asks a stricter question than "what interesting models were released?":
>
> > Which research objects are repeatedly changing across startup/open-model lineages, and which public artifacts give us unusually cheap access to those changes?

---

# Relation tags

- DIRECT — explicit predecessor/successor or method lineage.
- FIELD — same literature/technical family.
- CROSS-LAB — independent labs expose the same pressure; no causal influence claimed.
- RECONSTRUCTED — our conceptual reconstruction, not author-intent history.

---

# STARTUP GENEALOGY S01 — Fixed harness → online harness adaptation → harness as data-generating state

This is one of the fastest-forming 2026 clusters.

Surface slogan:
> agents improve their own prompts/tools/memory.

That slogan is already too crowded.

The actual genealogy is more interesting.

---

## S01.1 Parent assumption: the harness is fixed

Coding/agent systems historically package:
- system prompt;
- tools;
- memory;
- subagents;
- context compaction;
- workflow rules.

The model adapts its behavior inside this fixed wrapper.

Academic comparisons often implicitly assume:

harness = evaluation infrastructure

rather than:

harness = part of the learned/adaptive system.

---

## S01.2 Continual Harness: long-horizon partial observability exposes fixed-harness insufficiency [DIRECT]

Continual Harness grows out of Gemini Plays Pokémon.

The important historical path is:
1. a hand-engineered harness helps long-horizon play;
2. humans repeatedly refine it from failures;
3. the agent begins using long-context experience to improve strategy;
4. the paper asks whether the refinement process itself can be automated.

Continual Harness therefore does not start from:
> "self-improvement is cool."

It starts from:
> **human harness engineering is a recurrent adaptation process already happening during deployment.**

It formalizes editable harness state as:
- prompt p;
- subagents G;
- skills K;
- memory M.

A Refiner performs CRUD edits while the environment continues without reset.

Primitive change:

fixed scaffold across episodes
→ reset-free online scaffold adaptation inside one persistent trajectory.

---

## S01.3 Capability floor is a crucial negative result

The open Continual Harness repo records a particularly important boundary:

- Gemini 3 Pro: refinement is Pareto-dominant over minimalist baseline;
- Flash: high variance / marginal gain;
- Flash-Lite: refinement can underperform the baseline.

This means:

> **self-improvement itself requires enough base capability.**

A weak model may not be able to bootstrap the mechanism that is supposed to improve it.

This is much deeper than:
> "better model gets better result."

It implies a threshold phenomenon:

base capability
→ quality of self-diagnosis / edits
→ quality of future scaffold
→ subsequent capability.

Below the threshold the loop can amplify bad edits.

Any paper claiming generic "self-evolving agents" should therefore ask:
> what is the capability floor of the outer loop?

---

## S01.4 RHI: harness adaptation becomes an information-flow optimization problem [FIELD/CROSS-LAB]

Sakana AI's Recursive Harness Self-Improvement starts from a different pressure.

Provider-built agent harnesses increasingly generate traces that may later become training data.

Thus harness quality affects:
1. immediate task performance;
2. future data quality.

RHI represents the harness at prompt level and revises it through pairwise feedback over previous variants.

Reported gains are attributed mainly to:
> better task-specific context management / inter-agent information flow,
not merely longer reasoning.

This moves the research object from:

prompt quality
→ information topology of the agent system.

---

## S01.5 Prime Agent: adaptation becomes a persistent artifact layer [DIRECT/FIELD]

Prime Agent combines:
- Recursive Language Model runtime;
- Continual Harness state.

Its persistent editable layer contains:
- prompt notes;
- memories;
- skills;
- subagent specs.

The base system prompt stays immutable.

Refinement is explicitly framed as:
> something like context compaction, but producing precise reusable Create/Update/Delete edits rather than one temporary summary.

This separates:

ephemeral context
from
persistent harness artifacts.

That is a meaningful systems/scientific distinction.

---

## S01.6 Harness learning, context learning and weight learning are different adaptation channels

Across Continual Harness / Prime / RHI we can now distinguish:

### Context learning
Experience is kept in current prompt/history.

### Harness learning
Experience modifies persistent prompts/skills/subagents/memory.

### Weight learning
Experience changes parameters.

### Environment learning
Experience changes/generated tasks or world model.

These adaptation channels have:
- different persistence;
- different capacity;
- different failure modes;
- different update cost.

So "agent learns from experience" is no longer a sufficiently precise statement.

---

## S01.7 Saturation warning

By September 2026:
- Continual Harness;
- RHI;
- Prime Agent;
- MiniMax self-modifying scaffold;
- ModularRSI-like work;

already make generic "self-improving harness" crowded.

Possible scientific openings, if any, are below the label:
- capability floor;
- edit stability;
- forgetting/rollback;
- credit assignment over harness edits;
- transfer across tasks;
- information-flow diagnostics;
- interaction with weight updates.

This is not a candidate list.
It is the decomposition required before any candidate.

---

# STARTUP GENEALOGY S02 — Pretraining data order: randomization stops being a harmless default

Kyutai's Kairos temporal-pretraining work is one of the cleanest recent examples of turning a nearly invisible preprocessing convention into a scientific variable.

---

## S02.1 Old default: shuffle the corpus

Large-scale pretraining normally:
- collects huge corpora;
- deduplicates/filters;
- mixes domains;
- shuffles examples.

Random ordering is treated as optimization hygiene.

It is rarely discussed as:
> part of the knowledge representation learned by the model.

---

## S02.2 Changed premise: real-world facts themselves evolve

If:
- Barack Obama is president in one time period;
- Donald Trump / Joe Biden etc. in later periods;

then repeated incompatible facts in a shuffled corpus do not simply add data.

They destroy chronological structure.

A shuffled model observes:
> contradictory statements detached from temporal order.

The scientific question becomes:

> Does the randomization convention itself create temporal confusion?

---

## S02.3 Kyutai trains a matched sequential-vs-shuffled family [DIRECT]

The Kairos project trains 6B Helium models on Common Crawl under:
- chronological sequential ordering;
- standard shuffled ordering.

It releases multiple temporal checkpoints:
- sequential_2020;
- sequential_2021;
- sequential_2022;
- sequential_2023;
- sequential_2024;
- final 2025;
- several token-matched shuffled controls;
- non-cooldown counterparts for selected checkpoints.

This is exceptionally high research-instrument value.

It gives a public intervention pair where:
> the major manipulated factor is data chronology.

---

## S02.4 The result is not simply "sequential forgets old things"

Reported:
- sequential training matches shuffled baseline on broad language/common-knowledge tasks;
- temporal factual knowledge is more recent and more precisely associated with periods;
- shuffled training tends to peak on older factual knowledge;
- temporal ordering improves freshness but also creates some recency/forgetting tradeoff.

The authors hypothesize part of the shuffled-model older bias may arise from:
> factual repetition frequency.

This is interesting because chronological order and exposure count interact.

The causal object may not be:
> order alone.

It may be:
> **order × repeated exposure × changing truth state.**

---

## S02.5 Why this is relevant to S03/S09 lessons

The user's previous S03/S09 failures warned against vague training biography.

Kairos is different.

It does not merely say:
> checkpoint 2022 knows X, checkpoint 2024 knows Y.

It creates:
- a specific controlled variable: chronological ordering;
- matched shuffled baselines;
- public temporal checkpoints;
- temporally grounded evaluation.

This is exactly the difference between:

training chronology as narrative
vs
training order as controlled intervention.

---

## S02.6 Cheap pilot value

We cannot reproduce 2.5T-token 6B pretraining.

But we may not need to.

Public artifacts already include:
- matched models;
- matched checkpoints;
- temporal dataset/evaluation.

So many follow-up questions can begin with inference/probing rather than training.

This illustrates the new HF rule:

> **search for a public causal contrast before spending GPU.**

---

# STARTUP GENEALOGY S03 — Full-duplex speech splits into multiple different scientific problems

"Full duplex" is now too broad to be a research category.

Recent open teams expose at least four distinct bottlenecks.

---

## S03.1 Parent: remove turn-based interaction bottleneck [FIELD]

Moshi / Synchronous LLM / Interaction Models / GPT-Live all challenge:
> alternating utterance sequence.

Continuous interaction requires:
- overlapping speech;
- pause;
- interruption;
- backchannel;
- real physical timing.

But once this is solved, new bottlenecks appear.

---

## S03.2 MoshiRAG: factuality vs realtime latency [DIRECT]

Moshi is compact and realtime, but compact models have less factual capacity.

Naive options:
- scale model → too slow/expensive;
- synchronous RAG → stalls conversation.

MoshiRAG notices a physical interaction fact:

> there is often a natural temporal gap between response onset and the moment the response needs the factual payload.

It lets the frontend:
- keep listening/speaking;
- emit acknowledgments/coarse pre-RAG content;

while retrieval runs asynchronously.

When evidence arrives, it is injected back as a stream.

Primitive change:

retrieval before response
→ retrieval concurrent with the early part of response.

This is not just RAG applied to speech.

The method derives from:
> **conversation timing creates a hidden compute window.**

That is the actual transferable research move.

---

## S03.3 DuplexSLA: speech can be full-duplex while action/planning is still turn-bound [FIELD]

DuplexSLA identifies a different missing channel.

Existing duplex models can:
- listen;
- speak;

but planning/tool calling often still:
- waits for a turn;
- runs in an external cascade.

DuplexSLA adds a rate-limited textual action channel aligned to the same ~160ms timeline as speech.

Thus:
- user audio;
- assistant audio;
- planning/tool action

share one clock.

Primitive change:

full-duplex speech
→ full-duplex speech-language-action.

The problem is synchronization of cognition/action, not factual retrieval.

---

## S03.4 Lychee-FD: the bottleneck can be optimization interference inside the backbone [FIELD]

Lychee-FD starts from yet another failure:

> full-duplex training improves interaction but degrades semantic intelligence.

Instead of blaming:
- insufficient data;
- codec quality;
- latency;

the authors perform fine-grained optimization analysis and attribute degradation to:
> gradient conflicts between acoustic and semantic modeling when modalities share deep parameter space.

They then derive:
> hierarchical parameter separation,
while maintaining semantic alignment.

This is exactly a diagnosis-driven architecture paper:

behavioral degradation
→ optimization dynamics
→ modality gradient conflict
→ selective deep separation
→ semantic + interaction gains.

This is one of the best non-LLM-reasoning exemplars in the recent startup/HF scan.

---

## S03.5 Raon-SpeechChat: base SpeechLM competence and full-duplex competence are trained in distinct stages [FIELD]

Raon-Speech first:
1. aligns speech modules;
2. pretrains end-to-end SpeechLM with knowledge distillation;
3. preference-post-trains speech/text tasks.

Raon-SpeechChat then performs another continual-training stack:
1. causal encoder adaptation;
2. full-duplex pretraining;
3. voice/role-controlled duplex fine-tuning.

This implies:
> full-duplex interactivity is not simply a decoding switch on a strong SpeechLM.

It is a separately learned behavior distribution.

The released checkpoints/training pipeline make this useful for stage-level analysis.

---

## S03.6 Kyutai interactivity RL: SFT likelihood is not aligned with interaction-level quality [DIRECT]

Kyutai's June/August work on post-training full-duplex speech argues that token-level supervised likelihood does not directly optimize:
- pause handling;
- turn-taking;
- backchannel;
- interruption.

So interaction itself becomes an RL objective.

This is another objective mismatch:

token prediction quality
≠
interaction timing quality.

---

## S03.7 Four different "full-duplex" research objects

MoshiRAG:
> exploit timing slack for asynchronous knowledge.

DuplexSLA:
> synchronize speech with planning/action.

Lychee-FD:
> reduce acoustic-semantic gradient conflict.

Interactivity RL:
> align token-trained model to conversation-level behaviors.

This is the clearest example of why surface labels cannot be used as idea generators.

---

# STARTUP GENEALOGY S04 — World model: video prediction → persistent state → action operator → deployable simulator

Recent open artifacts make "world model" another overloaded phrase.

---

## S04.1 Passive video generation [FIELD]

A video generator predicts:
> visually plausible future frames.

For entertainment/content this may be sufficient.

For embodied systems:
> the prediction must respond correctly to actions and preserve state over long horizons.

---

## S04.2 Kairos: one world state must serve understanding, generation and action [DIRECT]

ACE Robotics' Kairos 4B builds around three verbs:

### Learn the world
Cross-Embodiment Data Curriculum:
- generic videos;
- human behavior;
- robot interactions.

### Maintain the world
Hybrid Linear Temporal Attention:
- local dynamics;
- mid-range dependencies;
- persistent global memory.

### Run the world
Deployment-aware system design for:
- server;
- consumer/edge hardware;
- observation-action-feedback loops.

The conceptual change:

world model = video generator
→ world model = persistent executable state model.

Kairos3.1 further exposes action-prediction checkpoints for RoboTwin / LIBERO.

---

## S04.3 Cross-embodiment curriculum makes data semantics progressive

The curriculum assumes:
- open video teaches general physical structure;
- human behavior adds intentional action structure;
- robot trajectories ground executable control.

This is not merely:
> concatenate datasets.

It posits a progression in what each data source contributes.

The scientific object is:
> **how increasingly action-grounded experience changes a shared world representation.**

Replication at full scale is expensive,
but stage checkpoints/data sources can potentially expose partial contrasts.

---

## S04.4 Wan-Streamer: persistent world vs event stream [CROSS-LAB]

Wan-AI's July 2026 framing:

video = world + event stream.

World:
- scene;
- subjects;
- acoustic environment;
- voice/identity;
- relatively stable state.

Event stream:
- behavior;
- scene changes;
- speech;
- sound;
- actions.

The same interleaved causal model can then learn:
> predict how the persistent world evolves/responds as events arrive.

This framing is not claimed as a new architecture.
It is a reinterpretation of the pretraining object.

That matters.

A powerful research move can be:
> changing what the same sequence is understood to represent.

---

## S04.5 Qwen-AgentWorld: the same world-model idea appears in symbolic/tool environments [CROSS-LAB]

Qwen-AgentWorld learns environment transitions for:
- terminal;
- web;
- Android;
- search;
- SWE;
- MCP;
- OS.

So world modeling now spans:

pixel/physical world
and
tool/software world.

The shared abstraction is not modality.

It is:
> **action-conditioned state transition.**

This is a cleaner cross-domain bridge than "both are world models."

---

## S04.6 MIRA: multiplayer makes other agents part of world dynamics

Kyutai + General Intuition's MIRA models 2v2 Rocket League in real time.

Multiplayer adds:
- multiple controllable actors;
- opponent/teammate policies;
- joint state evolution.

The reason to study Rocket League is not product utility.

It is a controlled physical-ish environment where:
> interactive future prediction can be stress-tested before real robotics.

This exemplifies synthetic environment as identification instrument rather than end product.

---

# STARTUP GENEALOGY S05 — Global state vs per-observation redundancy

Surflo is useful because it asks an architecture question from geometry rather than from transformer fashion.

---

## S05.1 Observation redundancy comes from the world, not the network

Multiple images of one static scene are:
> different projections of the same 3D geometry.

Existing feed-forward methods often either:
- emit per-view pointmaps that duplicate/inconsistently overlap;
- compress globally but force fixed low-resolution output.

Surflo asks:

> if geometry is one invariant world state, why should representation size grow with the number of views?

---

## S05.2 Global state decouples input count from output resolution [DIRECT]

Surflo:
- maps variable N views to fixed K=128 latent tokens;
- independently samples as many surface points as desired via flow-matching decoder.

So:

number of observations
≠
state representation size

and:

state representation size
≠
output resolution.

This is a very clean factorization.

---

## S05.3 Independent decoding reintroduces inconsistency

Once points decode independently:
> local surface pieces may disagree.

Instead of giving up the scalable decoder,
Surflo adds rendering-based guidance during ODE integration to couple points through shared photometric evidence.

The paper therefore follows a nice progression:

global compression solves redundancy
→ independent decoding creates coherence failure
→ inference guidance restores local consistency.

This is another example:
> the new solution's weakness becomes the next method component.

But unlike bad module stacking,
the component is directly caused by the factorization choice.

---

# STARTUP GENEALOGY S06 — Measurement noise can come from training, not evaluation sampling

The FID Lottery is a strong negative/measurement paper from a small open lab.

---

## S06.1 Default evaluation story

A generative-model paper reports:
> one trained model + one sampling seed + one FID.

If two recipes differ by a small FID margin,
the lower value is treated as better.

---

## S06.2 Kyutai decomposes randomness along two axes

They train hundreds of SiT networks and separately vary:

### Training randomness
- initialization;
- data order;
- flow-matching noise.

### Generation randomness
- sampling seed.

Key result:
> retraining moves FID much more than resampling from one fixed network.

Reported training-side variation is ~3.2× larger in the relevant feature-space comparison.

Increasing:
- model size;
- compute

does not collapse the relative noise floor much.

Thus:

evaluation noise
≠
only sampling noise.

The trained model itself is a draw from a recipe distribution.

---

## S06.3 Why this is more than evaluator work

The result changes what a "training recipe improvement" means.

If a claimed gain is below recipe-induced variance:
> a one-seed comparison does not identify the recipe effect.

They also show:
- per-cell CFG tuning reduces spread;
- lucky seeds can appear up to ~2× more compute-efficient than unlucky ones at matched FID.

So random training trajectory can masquerade as:
> algorithmic efficiency.

That is a scientific attribution problem, not just benchmark hygiene.

---

# STARTUP GENEALOGY S07 — Autoregressive vs diffusion language modeling becomes deployment-mode unification

NVIDIA is not a startup, but its HF release is a particularly instructive open-model artifact and belongs in this track because the model card exposes a clean technical thesis.

---

## S07.1 Old framing: AR and diffusion are different language-model families

Autoregressive:
- strong causal language prior;
- one/few tokens per forward;
- memory-bound decoding.

Diffusion/block generation:
- parallel token updates;
- potentially better throughput;
- different training/inference behavior.

The usual comparison asks:
> which family is better?

---

## S07.2 Nemotron-Labs-Diffusion changes the question to mode compatibility [DIRECT]

The same model is jointly trained to support:

1. AR mode;
2. diffusion mode;
3. self-speculation mode.

Mode switching largely changes attention/decoding behavior rather than replacing the model.

The reported analysis argues:
- diffusion contributes lookahead/parallel drafting;
- AR contributes left-to-right prior / verification;
- diffusion drafts can be verified autoregressively with shared state.

Primitive change:

choose AR or diffusion architecture
→ one learned model exposes multiple generation operators.

---

## S07.3 Deployment concurrency decides which mode is useful

The motivation is not only modeling elegance.

Different serving regimes favor:
- AR compatibility;
- diffusion throughput;
- self-speculation at low concurrency.

So generation algorithm becomes:
> a workload-conditioned control decision.

This parallels model routing/effort control elsewhere.

But here the control occurs:
> inside one model's decoding operator.

---

## S07.4 Small open models make the question accessible

The family includes:
- 3B;
- 8B;
- 14B;
- base/instruct/VL variants.

That makes this technical thesis much more experimentally accessible than a closed frontier system.

Again:
> instrument value matters.

---

# STARTUP GENEALOGY S08 — Failure memory: from difficulty-aware self-play to diagnosis-aware curriculum

DiagEvo is a useful example of a trend becoming more specific.

---

## S08.1 Parent cluster: self-play needs curriculum control [FIELD]

Self-evolving reasoning methods already control generated questions using:
- difficulty;
- diversity;
- learnability;
- external examples/resources.

Generic insight:
> random self-play can plateau.

This surface is crowded.

---

## S08.2 DiagEvo changes the curriculum state from "hardness" to "unresolved cause" [DIRECT]

The diagnostician reads failure history and extracts recurrent error causes.

A hierarchical memory:
- groups errors under skills;
- tracks Active vs Mastered;
- uses recurrence counts.

Question generation then targets:
> unresolved causes,
while retaining some free exploration.

This is more specific than:
> generate harder questions.

Primitive change:

curriculum state = scalar/sample difficulty
→ curriculum state = structured unresolved error causes.

---

## S08.3 Why memory matters here

The "memory" is not user personalization.

It is:
> a state variable for the self-improvement process.

Its job is to prevent:
- repeatedly rediscovering the same failure;
- losing track of mastered failure modes;
- undirected generation.

This is a very different genealogy from conversational long-term memory.

---

## S08.4 Saturation warning

The self-evolution space now includes:
- difficulty-aware;
- learnability-aware;
- diagnosis/error-memory;
- harness refinement;
- environment co-evolution.

So generic:
> use failure history to improve agent/model

is already too broad.

Need a precise failure representation and a causal reason it should improve learning.

---

# STARTUP GENEALOGY S09 — Long-horizon R&D agents: final success separates from research process

Meituan's Beyond Final Scores is industry research, but its evaluation logic belongs in this open/startup genealogy library because it directly diagnoses the new "AI scientist" product/research narrative.

---

## S09.1 Final task score hides distinct process failures

They evaluate 7 frontier models on 36 long-horizon AutoLab tasks.

Process is decomposed into:
- Solution Framing;
- Execution;
- Feedback Control.

The project page reports:
- large avg@3 vs best@3 gaps;
- high run-to-run variability;
- execution scores generally higher than solution framing;
- strong agents often optimize/compose known techniques rather than inventing genuinely new methods.

This tells us:

> peak capability and reliable research capability are different quantities.

---

## S09.2 Controlled experience deletion is more informative than correlating long context with success

The paper tests within-task experience reuse by branching:
- keep the current solution artifact;
- erase accumulated experience/context in one branch;
- compare next decisions.

This is a better identification design than:
> tasks with longer histories perform better.

It manipulates:
> experience availability while holding artifact state.

Results show experience can:
- help;
- sometimes mislead.

So:
> more memory is not monotonic improvement.

---

## S09.3 Harness mainly affects reliability, not magically creates new capability

The paper reports harness design substantially affects performance stability.

This resonates with Prime/RHI/Continual Harness.

But it also prevents an overclaim:
> good harness = smarter scientist.

Harness can make existing ability more reproducible without creating methodological novelty.

That distinction is important.

---

# STARTUP GENEALOGY S10 — Public checkpoints as experimental interventions

This is not a model-method genealogy.
It is a new research workflow made possible by the HF ecosystem.

---

## S10.1 Traditional problem

To ask:
> what changed after SFT/RL/midtraining/quantization?

one often had to train the entire pipeline.

That makes many causal questions infeasible.

---

## S10.2 2026 open releases increasingly expose matched lineage checkpoints

Examples:

### Kyutai Helium
- yearly sequential checkpoints;
- token-matched shuffled controls;
- non-cooldown versions.

### Ling-3.0
- pretrain 30T;
- midtrain;
- WSM merged;
- tiny + flash matched recipe.

### MiniCPM5
- base;
- midtrain;
- SFT;
- RL + OPD;
- small 2B scale.

### Arcee Trinity
- pre-anneal TrueBase;
- full Base;
- Preview;
- Thinking;
- quantized variants.

### Tiny Aya
- English-reasoning vs same-language-reasoning.

### Liquid/NVIDIA/Poolside
- higher precision vs QAD/quantized variants.

### LongCat
- dense vs sparse / smaller mechanism-faithful variants.

---

## S10.3 A model card can therefore function like a natural experiment

These are not perfectly controlled interventions.

But they can provide:
- cheap phenomenon discovery;
- candidate causal contrast;
- parameter/readout analysis;
- boundary testing.

The correct workflow:

public lineage comparison
→ detect robust local difference
→ identify confounds
→ design smallest controlled intervention
→ only then train.

Not:

public checkpoints differ
→ declare training-stage mechanism.

---

## S10.4 This materially changes our topic-search feasibility prior

Before rejecting a question as:
> requires pretraining,

first search whether a matched lineage already exists.

This is especially relevant to the user's compute constraints and S03 lesson.

A large fraction of exploratory training-science questions may now be tested by:
> **artifact archaeology before GPU experimentation.**

That is one of the most important practical lessons from the entire HF scan.

---

# 11. Same surface, different startup genealogies

## "Memory"

Prime/Continual Harness:
> persistent task/harness knowledge.

DiagEvo:
> failure-cause curriculum state.

FwPKM:
> fast episodic parameter-like state.

Kairos world model:
> persistent physical world state.

Reasoning trace preservation:
> protocol state for future turns.

These are not one topic.

---

## "Self-improvement"

Continual Harness:
> edit scaffold online.

RHI:
> optimize information flow in harness.

DiagEvo:
> generate curriculum from failure causes.

Echoverse:
> evolve environment relative to learner.

MiniMax:
> agent modifies training/scaffold code.

Experience Distillation:
> internalize interaction experience into weights.

The phrase "self-improvement" now has essentially zero scientific specificity.

---

## "Long context"

Kyutai temporal pretraining:
> historical order.

LongCat:
> sparse retrieval/indexing.

Prime:
> programmatic external context computation.

Poolside:
> local memory budget.

Arcee:
> preserve reasoning state across tool calls.

Kairos:
> persistent world state.

Again: same surface label, different causal pressure.

---

# 12. Current startup/HF artifact shortlist by research-instrument value

This is NOT a ranking of topics or papers.

It answers:
> if we later need a cheap pilot, which public artifacts are unusually useful?

## Very high

### Kyutai Sequential_Helium_6B
Why:
- matched sequential/shuffled;
- temporal checkpoints;
- non-cooldown versions;
- KairosQA.

### Ling-3.0 tiny family
Why:
- tiny scale;
- pretrain/midtrain/merge lineage;
- matched scale-up recipe.

### MiniCPM5-2B
Why:
- small;
- modern SFT/RL/OPD stages;
- open data/checkpoints.

### Tiny Aya paired Thinkers
Why:
- one clean reasoning-language manipulation.

### Continual Harness repo
Why:
- explicit minimalist/expert/online-adaptive baselines;
- capability-floor result;
- open persistent environment.

## High but heavier

### LongCat-Flash-Lite-Sparse
- open sparse-attention mechanism;
- dense parent;
- long-context access.

### Kairos 4B World-Action Model
- pretrain / world-model / action variants;
- 4B rather than 100B+.

### MoshiRAG / Raon-Speech
- open full-duplex checkpoints;
- expensive but real speech interaction experiments possible.

### Nemotron-Labs-Diffusion 3B
- one model with multiple decoding operators.

---

# 13. Execution traps exposed by this scan

## Trap A — open weights do not mean trainable for us

Inkling / giant MoE:
> inspectable, not realistically trainable.

## Trap B — "small active params" can still mean huge storage/system complexity

MoE active parameter count is not full resource accounting.

## Trap C — model-card stage pairs still bundle changes

Do not mistake:
> public lineage
for
> randomized controlled experiment.

## Trap D — open agent harness can silently require expensive closed-model calls

Continual Harness / RHI-like experiments may shift cost from GPU to API.

## Trap E — world model demos can hide huge data-generation cost

Kairos / MIRA are useful scientific inspiration but full replication is costly.

---

# 14. What changed in our reading strategy after this batch

Earlier:
> read strongest papers / model cards.

Now:
> read strongest **intervention artifacts**.

For every model card, record:

1. What is the technical thesis?
2. What predecessor/default assumption does it reject?
3. What public matched counterpart exists?
4. What does the counterpart control?
5. What confounds remain?
6. What can be measured inference-only?
7. What tiny model carries the same mechanism?
8. What scale does the claimed effect first appear at?
9. What would kill the effect cheaply?

This moves Hugging Face from:
> model zoo

to:
> **natural-experiment catalog.**

---

# 15. Current conclusion

The startup/HF scan is now revealing two distinct kinds of frontier value.

## Frontier-pressure value
Large/new systems reveal:
> what starts breaking when workloads change.

## Research-instrument value
Open model families reveal:
> what we can test without reproducing the frontier system.

The most promising research workflow for us is therefore not:

find a popular open model
→ improve it.

It is:

frontier pressure
→ recover academic genealogy
→ search HF for an existing matched intervention artifact
→ run a cheap diagnostic
→ only then decide whether training is justified.

This is still literature calibration, not topic generation.
