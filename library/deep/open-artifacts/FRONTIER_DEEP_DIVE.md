# Startup & Hugging Face Frontier Deep Dive — 2026-09-19

> Status: research-taste / frontier-artifact calibration only.
>
> NO formal CT candidate generation.
>
> This track expands beyond frontier foundation-model incumbents.
>
> The motivation is not "small startups are more innovative."
>
> It is:
>
> Research-oriented startups and Hugging Face model releases often expose a single technical thesis more clearly than giant integrated frontier systems do.
>
> They also frequently release intermediate checkpoints, base/post-trained pairs, quantized/full-precision pairs, specialist/merged-student pairs, training data, and model cards with concrete integration constraints. These artifacts can be far more valuable for a small academic team than a closed trillion-parameter model, even when the closed model is scientifically more capable.

---

# 0. How to read the Hugging Face frontier

Hugging Face's Summer 2026 ecosystem analysis provides an important warning:

> community attention and actual adoption are different signals.

HF reports that likes and downloads identify very different model sets; small models still dominate practical download volume; frontier trillion-scale releases dominate attention but not necessarily deployment; and derivative ecosystems can matter more than one flagship checkpoint.

Therefore:

> HF trending / likes are discovery signals, not research-taste signals.

For our purposes, the useful model-card question is:

> What does this release expose that lets us ask or test a sharper scientific question?

---

# 1. Artifact-value taxonomy

Every HF/startup release should be tagged independently on three axes.

## A. Technical-thesis value

Does the release make a concrete claim such as:
- a different training objective;
- a changed architecture unit;
- a changed RL temporal structure;
- a representation hypothesis;
- a deployment-induced learning constraint?

This is idea/taste value.

## B. Experimental-artifact value

Does it release:
- base checkpoint;
- intermediate checkpoint;
- post-training stages;
- teacher/student pair;
- quantized/full precision pair;
- open data;
- logs;
- training code?

This is pilot-enabling value.

A release can be scientifically ordinary but experimentally priceless.

## C. Ecosystem/deployment value

Does it reveal:
- local-device constraints;
- harness compatibility;
- reasoning serialization;
- tool-call contract;
- cache constraints;
- precision/hardware requirements?

This is deployment-pressure value.

---

# 2. Thinking Machines Lab — a coherent startup research thesis

Primary artifacts:
- Inkling / Inkling-Small model cards
- Tinker
- Interaction Models
- financial expert-judgment RL
- ReViSQL collaboration
- forecasting collaboration

Thinking Machines is useful because these artifacts form a coherent research program rather than unrelated releases.

---

## 2.1 Inkling: effort is trained, not merely prompted

Inkling is an open-weight multimodal MoE model with roughly 975B total / 41B active parameters, native text/image/audio support, around 1M context, and large-scale RL after a relatively small SFT phase.

Inkling-Small has 276B total / 12B active parameters and shares the broad architecture/training philosophy.

The important object is variable effort.

During RL, the system varies:
- a system-level effort instruction;
- a per-token cost.

The model learns to trade reward against computation.

Primitive change:

reasoning length as an emergent byproduct
→ reasoning effort as a trained conditional behavior.

---

## 2.2 RL can compress the language of reasoning without a style reward

Thinking Machines reports that as Inkling optimizes efficiency, reasoning traces become more telegraphic / abbreviated.

The reward does not directly ask the model to write shorter grammatical reasoning.

The pressure is:
> spend fewer tokens while retaining reward.

This creates an important distinction:

semantic computation compression
vs
linguistic surface compression.

A shorter CoT may arise because:
- computation is genuinely reduced;
- the same computation is encoded more densely;
- some computation moves into hidden state;
- the policy learns terse shorthand.

This is a useful changed-premise warning for any study that treats CoT token count as reasoning amount.

---

## 2.3 Inkling-Small: recipe/data can reverse expected scale ordering

Inkling-Small is roughly a quarter the total size of Inkling but reportedly matches or exceeds it on some tasks.

The lesson is not "small models are enough."

It is:

> model scale and model generation/recipe are not a clean causal axis.

A newer smaller model can inherit improved:
- pretraining mixture;
- optimizer/recipe;
- RL;
- multimodal alignment.

Therefore cross-generation scale analyses are dangerous when model families are not recipe matched.

---

## 2.4 Tinker: training infrastructure becomes an abstraction boundary

Tinker lets researchers specify locally:
- data;
- environment;
- loss;
- training loop;

while remote infrastructure handles:
- distributed execution;
- failure recovery;
- large-model training.

Historically, "can we test this post-training idea?" was partly an infrastructure question.

With systems such as Tinker, the infrastructure boundary moves downward, although compute cost does not disappear.

Thinking Machines' LoRA materials also distinguish regimes where LoRA works well for RL / small-medium SFT from larger-data SFT regimes where low-rank parameterization can become limiting.

This is precisely the kind of practical algorithmic boundary model-platform documentation can expose before it becomes a conventional conference topic.

---

## 2.5 Interaction Models: sequence modeling is not enough for interaction

Thinking Machines' May 2026 Interaction Models work trains a realtime multimodal model from scratch around:
- continuous audio/video/text;
- 200ms micro-turns;
- interleaved input/output;
- asynchronous background reasoning.

The underlying changed object is:

dialogue = alternating messages
→ dialogue = continuous time-aligned bidirectional process.

Important details:
- realtime interaction remains on the fast path;
- deep reasoning can happen asynchronously;
- system/kernel design targets predictable latency.

This independently converges with OpenAI GPT-Live and ByteDance SeedRealtime.

The startup contribution is useful because it makes the interaction abstraction itself the research object.

---

## 2.6 Financial expert judgment: tacit expertise can be a training signal

Thinking Machines + Bridgewater AIA study repeated micro-tasks in financial-information triage.

Frontier prompting initially underperforms the desired expert threshold.

The training process uses:
- expert-labeled proprietary data;
- disagreement-driven human verification;
- RL;
- CISPO / asymmetric clipping;
- on-policy distillation;
- validation-best teacher promotion.

The deeper question-forming move is:

> some domain expertise is difficult to specify as a prompt or written rule, but can still be represented in repeated expert decisions.

Thus:

expert knowledge = explicit instructions

is challenged by:

expert knowledge = latent judgment recoverable from labeled decisions.

The scientific object is tacit judgment.

---

## 2.7 ReViSQL: scaffold knowledge can belong in the training objective

Thinking Machines' Aug 27 post revisits Text-to-SQL.

The field had increasingly built decomposition pipelines, correction steps, and schema-reasoning scaffolds.

ReViSQL argues that a substantial remaining limitation is model capability and training quality, not insufficient scaffolding.

Two audits matter.

### Data audit

They report substantial annotation/data errors in the original training data. Cleaning alone gives a large RLVR gain.

### Reward audit

Standard execution-match reward can be wrong because a generated SQL query can coincidentally return the same result on one database instance while being semantically inequivalent.

They add task-specific verification/evidence signals.

Question-forming move:

task expertise as external pipeline
→ task expertise as training signal.

This does not imply fine-tune instead of scaffold universally. It is task- and data-dependent.

---

## 2.8 Forecasting: task specialization can create complementary intelligence

Thinking Machines/Mantic fine-tune a forecasting model on roughly 10k temporally valid event questions.

The useful result is not only that performance improves.

The specialized model reportedly becomes valuable in an ensemble partly because its errors are decorrelated from frontier general-purpose models.

Research-taste lesson:

> task specialization can matter through error complementarity, not only through best-single-model score.

---

# 3. Prime Intellect — the harness becomes mutable state

Primary artifacts:
- Prime Agent, Aug 2026
- arXiv 2608.23552
- open implementation

Prime Agent questions a hidden assumption in almost every agent paper:

> the harness is fixed.

---

## 3.1 RLM: context becomes programmable data

Prime Agent uses a Recursive Language Model style interface:
- context stored as variables;
- persistent IPython environment;
- recursive/sub-agent calls;
- programmatic manipulation of long context.

Instead of rereading the full context every step, the model can inspect/search/transform context programmatically, delegate subproblems, and retain structured intermediate state.

The research object becomes external computation over context.

---

## 3.2 Continual Harness: prompts, skills and subagents can change from experience

Prime Agent makes supplemental prompts, skills, memory, and subagent specifications mutable through CRUD operations.

A refinement procedure proposes small evidence-backed modifications from trajectory experience.

Important constraints:
- base system prompt remains immutable;
- modifications can be rolled back;
- subagents persist;
- session/kernel history can be restored.

Changed object:

harness = fixed inference-time scaffolding
→ harness = persistent learnable state.

Long-term adaptation now includes at least:
- weight learning;
- context learning;
- memory learning;
- harness learning.

---

## 3.3 Harness self-modification is already becoming a cluster

Sakana RHI appears independently.
ModularRSI appears immediately afterward.
MiniMax reports self-modifying agent scaffolds.

Therefore:

> "let the agent improve its own harness" is already a crowded conceptual move.

Open scientific questions have moved below that phrase.

---

# 4. Sakana AI — harness optimization and memory as separate objects

Sakana is useful because projects often isolate one structural hypothesis rather than only scaling a flagship model.

---

## 4.1 Recursive Harness Self-Improvement

RHI represents an agent harness as a prompt-level specification of roles, contracts and workflow.

The agent executes a task, receives pairwise feedback against prior iterations, then revises its harness.

Reported on 30 synthetic ML-research tasks:
- a few iterations can improve low-effort agents;
- performance can exceed the tested max-effort fixed-harness baseline;
- inference cost can drop;
- gains are attributed more to task-specific context/information flow than simply longer reasoning.

Strong question-forming move:

> what if the bottleneck is the information topology of the agent system rather than model reasoning capacity?

---

## 4.2 A downscaled reproduction is a valuable contrast

An open downscaled reproduction reported:
- the first revision improved;
- the second revision lost the gain;
- the static high-effort control remained stronger overall in that setup.

This does not settle the original claim, but it prevents a universalized story.

Harness self-improvement may be strongly dependent on:
- base model;
- judge;
- task family;
- update count.

---

## 4.3 Fast-weight Product Key Memory

FwPKM addresses a different problem.

Softmax attention offers high storage with quadratic cost.
Linear/recurrent models offer efficiency with limited fixed-size state.

FwPKM turns Product Key Memory into a dynamic fast-weight episodic memory updated during training and inference using local chunk-level optimization.

Changed object:

model parameters = slow learned weights
→ some parameters/state = fast episodic memory updated online.

This is a richer memory object than external retrieval and sits between weights, recurrent state and external memory.

---

# 5. Liquid AI — deployment constraints define the learning problem

Liquid's core thesis is that useful intelligence should run locally/on-device.

That changes model design from the beginning.

---

## 5.1 LFM2.5: agent model under local-compute constraints

LFM2.5-2.6B uses a hybrid architecture with many short-convolution blocks, fewer global attention blocks, compact footprint and long context.

The model is designed for CPU, Apple devices, edge/mobile and local agent workflows.

This is not "compress a cloud model later."

It is choosing an architecture whose steady-state resource profile fits the target deployment.

---

## 5.2 Agentic RL inside real harnesses

Liquid reports agentic RL inside popular harnesses.

The model sees during training:
- tool schemas;
- system prompts;
- interaction patterns;
- harness-specific execution contracts.

Changed premise:

tool use = general skill evaluated through one harness
→ harness distribution itself is part of agent training.

This independently converges with DeepSeek, Tencent Hy3, Cohere North Mini Code and Holo.

---

## 5.3 Quantization-aware distillation

Instead of:

train BF16 → quantize → accept degradation,

Liquid treats the quantized model as a constrained student.

A higher-precision teacher supplies a KL learning signal to recover behavior.

Research move:

quantization error = numerical approximation problem
→ quantization error = constrained student/teacher learning problem.

NVIDIA independently uses a similar framing.

---

# 6. H Company — benchmark capability to production-distribution robustness

Holo is a useful computer-use genealogy.

Holo 1.5 emphasizes:
- GUI/computer-use foundation;
- high-resolution perception;
- SFT + online GRPO;
- click/action data.

Holo 3.1 then frames real deployment shift along:
1. environment: web / desktop / mobile;
2. harness: different agent interfaces / tool encodings;
3. deployment target: cloud vs local/quantized.

It adds mobile, native function calling, multiple sizes and quantized variants.

Changed object:

computer-use benchmark score
→ robustness across environment × harness × deployment target.

This is more useful than "another GUI model."

---

# 7. InclusionAI Ling-3.0 — training schedule as an offline-search object

Ling-3.0 is one of the most interesting HF artifacts for our resource philosophy.

---

## 7.1 Warmup–Stable–Merge

Standard pretraining uses warmup → stable/high LR → decay.

The decay phase is expensive because different decay schedules require rerunning training and the schedule is embedded in the online trajectory.

Ling proposes retaining checkpoints during stable training and constructing the final model through weighted checkpoint merging.

Changed object:

learning-rate decay profile = online trajectory commitment
→ decay behavior = partially explorable after training through checkpoint geometry.

This is a genuine question-forming move, not merely a scheduler acronym.

---

## 7.2 Why it matters for continual/dynamic pretraining

If data keeps changing, new corpora arrive and the training horizon extends, hard-coded decay makes continuation awkward.

WSM is motivated partly by keeping the model in a stable trainable regime longer.

This fits the industrial reality that pretraining datasets and horizons are not perfectly known at day one.

---

## 7.3 Ling releases a useful scale ladder

The family exposes pretrain, midtrain and merged checkpoints plus multiple model sizes.

The team explicitly supports validating strategies at smaller scale before expensive scaling.

For us:

> the research artifact itself contains a built-in cheap-to-large validation path.

This should be a major HF scanning criterion.

---

# 8. OpenBMB MiniCPM5-2B — tiny model, unusually rich post-training artifact

This is one of the highest-execution-value recent HF releases for our purposes.

---

## 8.1 The 2B scale matters

MiniCPM5-2B is small enough that:
- inference is cheap;
- short full/LoRA post-training is realistic;
- multi-seed experiments are possible.

Yet the release contains a modern post-training stack.

---

## 8.2 Stage checkpoints matter more than the final leaderboard

The release ecosystem exposes:
- base;
- midtraining;
- SFT-only;
- final RL + OPD stages;
- associated data.

A research group can inspect behavioral changes introduced by each stage without reproducing pretraining.

---

## 8.3 JustRL II creates a small-model long-CoT testbed

JustRL II uses:
- audited math pool;
- dynamic sampling;
- learned critic/value model;
- token-level GAE-like advantages;
- long rollout budgets.

Whatever one thinks of the algorithmic novelty, the open artifact is useful for studying:
- token credit;
- rollout length;
- critic calibration;
- data difficulty.

---

## 8.4 OPD combines 16 expert models

MiniCPM reports 16 RL experts, including five agent specialists.

OPD reuses RL prompts and uses full-vocabulary student/teacher reverse-KL style guidance.

This pattern now appears repeatedly:
- Kimi;
- MiniCPM;
- GigaChat;
- MiMo;
- other industrial reports.

Therefore:

> multi-teacher on-policy distillation is already a crowded industrial recipe family.

It is infrastructure, not a novelty generator.

---

# 9. IFM K2-Horizon — checkpoint transparency as a scientific affordance

The K2-Horizon family is less famous but its release style is useful.

It exposes:
- multiple sizes;
- multi-teacher distillation;
- training-phase checkpoints;
- logs / detailed appendix.

A transparent small model can be more scientifically valuable to us than a stronger opaque model because it lets us ask when a behavior emerged and which post-training stage changed it.

Important discipline:

This does not revive S03-style training biography.

Stage comparison is only useful when the measured quantity is local/stable enough to survive recipe perturbations.

---

# 10. Zyphra — architecture, hardware stack and non-language foundation models

Zyphra is useful because its releases are heterogeneous.

---

## 10.1 ZAYA1-8B: reasoning from pretraining onward

ZAYA1-8B:
- 8B total / roughly 700M active;
- full-stack AMD training;
- reasoning data from pretraining;
- answer-preserving trimming;
- multi-stage RL cascade.

It also proposes Markovian RSA: recursively aggregate parallel reasoning traces while carrying forward only a bounded reasoning tail.

Changed resource view:

retain full previous reasoning state
→ retain only bounded sufficient tail between aggregation rounds.

This is an explicit hypothesis about how much reasoning history remains useful.

---

## 10.2 ZAYA as hardware-stack experiment

Zyphra emphasizes end-to-end AMD compute/networking/software.

This is mainly industrial systems evidence.

Useful pressure:

> frontier model design can be constrained by the full hardware/software stack, not CUDA assumptions.

---

## 10.3 ZUNA1.1: flexible masking changes a foundation model's repair operator

ZUNA is a 380M masked diffusion autoencoder for EEG:
- denoising;
- missing-channel reconstruction;
- spatial upsampling.

ZUNA1.1 adds variable sequence-length masking and user-selected bad segments.

The model is not trained for one downstream classifier.

It learns a prior over physically located multichannel signals and exposes reconstruction/repair as a reusable primitive.

Cross-field lesson:

> foundation modeling does not have to mean next-token prediction + chat.

A foundation model can be organized around conditional reconstruction under arbitrary missingness.

---

# 11. Cognition — long-horizon asynchronous coding as the post-training regime

Cognition's SWE-1.7 is closed, so evidence is weaker than an open technical report.

But the training description exposes a clear pressure.

---

## 11.1 Additional RL after an already-post-trained base

SWE-1.7 starts from Kimi K2.7 and applies additional RL.

Cognition highlights that large gains remain after the base already underwent substantial post-training.

This does not prove infinite RL scaling, but weakens the simplistic idea of a universal post-training ceiling.

---

## 11.2 Long-horizon asynchronous work changes training requirements

Cognition attributes gains to:
- more stable RL;
- multi-datacenter rollout;
- stricter task filtering;
- reward-hacking defense;
- learned self-compaction for tasks beyond raw context.

The interesting variable is:

> task duration relative to context window and rollout infrastructure.

This resembles Kimi/MiniMax findings where long trajectories make infrastructure choices part of the training distribution.

---

# 12. Poolside — local agentic coding as a model-design constraint

Laguna XS 2.1:
- roughly 33B total / 3B active;
- 256K context;
- 3:1 sliding/global attention;
- FP8 KV option;
- FP8/NVFP4/INT4 variants;
- reasoning/tool integration;
- DFlash speculator.

It is designed for long-horizon agentic coding on a local machine.

---

## 12.1 Locality changes which resources matter

For a cloud model, aggregate GPU throughput and fleet batching can dominate.

For a local workstation:
- memory footprint;
- KV size;
- active parameters;
- quantization;
- per-user latency

become first-class.

Changed product object:

agent intelligence at cloud scale
→ useful long-horizon agent within a fixed local memory envelope.

---

## 12.2 Reasoning state is part of the agent protocol

Poolside's model card notes:
- interleaved thinking;
- preserved reasoning between tool calls;
- per-request thinking control.

This matches Arcee's explicit finding that dropping reasoning content from history degrades multi-step behavior.

Model-card lesson:

> reasoning tokens can be serialized recurrent state required by the trained interaction protocol, not merely explanation text.

---

# 13. Arcee AI — checkpoint lineage as a research instrument

Arcee's Trinity family is valuable because it exposes multiple checkpoints from one large training run.

Examples:
- TrueBase: ~10T tokens, before LR anneal, no instruction/RL;
- Base: full ~17T pretraining + midtraining/annealing;
- Preview: light post-training;
- Thinking: reasoning/agentic post-training;
- multiple quantizations.

---

## 13.1 Why this is scientifically valuable

Instead of comparing Qwen vs Llama vs DeepSeek with completely different recipes, one can compare the same architecture lineage across training stages.

This controls many confounds.

Not all:
- data;
- LR;
- duration;
- objective

still change.

So stage labels are not causal variables by themselves.

The right use is:
> identify candidate behavioral changes cheaply, then design a controlled intervention.

---

## 13.2 Reasoning history is explicitly required

Trinity-Large-Thinking's model card says multi-turn/tool performance requires preserving the model's reasoning content in history.

Omitting it degrades performance.

Thus:

reasoning trace = explanation only

is false for this model.

The trace is also future-state input.

That changes how reasoning-removal and CoT-faithfulness studies should interpret the intervention.

---

# 14. Cohere Labs — small specialist models as first-class releases

Cohere is larger than a narrow startup, but its 2026 Labs releases deliberately span small specialist models.

---

## 14.1 North Micro Vision — 2.4B customizable VLM

North Micro Vision:
- 2.4B;
- native-resolution images;
- multi-image;
- multilingual;
- OCR/chart/document/grounding;
- explicit focus on fine-tuning and edge/mobile experimentation.

Release thesis:

> make multimodal specialization cheap enough that downstream training is expected.

This is a different role for a base model than maximizing frontier benchmark score.

---

## 14.2 North Mini Code — harness diversity is trained in

North Mini Code:
- 30B total / 3B active;
- 256K context;
- agentic coding specialization.

Cohere explicitly says it trains on multiple scaffolds rather than optimizing for one.

This reinforces industrial convergence:
- DeepSeek;
- Tencent;
- H Company;
- Liquid;
- Cohere.

"Harness robustness" is becoming industrial hygiene, not novelty by itself.

---

## 14.3 Tiny Aya Thinker — reasoning language and answer language are decoupled

Cohere releases:
- Tiny Aya En-Thinker: reasoning trace in English, answer in user language;
- Tiny Aya L2-Thinker: reasoning in prompt language.

This exposes a clean scientific dimension:

language of reasoning
vs
language of answer.

The matched family is a cheap instrument for studying multilingual reasoning behavior.

This is a good example of a modest HF release creating a more useful research instrument than a flagship model.

---

# 15. Meituan LongCat — deployment reality moves the sparse-attention bottleneck

LongCat-2.0 is huge, but its smaller sparse variants make part of the thesis accessible.

---

## 15.1 Parent: sparse attention solves one bottleneck and exposes another

DeepSeek Sparse Attention's Lightning Indexer reduces attention work.

LongCat identifies practical bottlenecks:
- index scoring itself remains expensive;
- selected addresses create fragmented, hardware-inefficient memory access.

Classic genealogy:

algorithm reduces theoretical attention work
→ deployment exposes indexer + memory-access bottleneck.

---

## 15.2 LSA attacks three distinct dimensions

LongCat Sparse Attention:
1. streaming-aware indexing: mix contiguous hardware-friendly reads with dynamic selection;
2. cross-layer indexing: exploit adjacent-layer saliency similarity and use cross-layer distillation;
3. hierarchical indexing: coarse-to-fine candidate filtering.

This is hardware–algorithm co-design after the indexer becomes the new bottleneck.

---

## 15.3 Smaller sparse checkpoints matter more to us than the 1.6T model

The trillion-scale model is not executable for us.

But mechanism-faithful smaller LSA variants can become experimental instruments.

Rule:

> when a huge-model paper ships a smaller mechanism-faithful checkpoint, the smaller artifact is often the one we should care about.

---

# 16. Arcee / Essential / Reflection / other lower-priority monitors

## Essential AI — Rnj-1.5

Useful:
- 8B dense;
- code/STEM;
- open base/instruct lineage;
- long-context variant.

Current public materials do not expose a sufficiently distinctive fresh thesis relative to stronger sources above.

Status:
> monitor / artifact source, not current taste anchor.

## Reflection AI

Current HF organization has no public model weights.
Recent work is mainly evaluation research.

Status:
> do not invent a model story that is not public.

## Command A+ / large enterprise models

Useful background and convergence evidence, but not every updated quantization is a new research thesis.

---

# 17. A new reading axis: research-instrument value

This axis was missing from the original industry scan.

A release can be worth reading because it gives us an experiment, even when the model itself is not scientifically novel.

High instrument-value examples:

### MiniCPM5
- 2B;
- staged checkpoints;
- open data;
- SFT/RL/OPD separation.

### Arcee Trinity
- same training run across pre-anneal/base/post-train/thinking stages.

### Tiny Aya Thinker pair
- English-reasoning vs same-language-reasoning variants.

### Liquid / Poolside quantized pairs
- BF16 vs multiple low-precision variants.

### LongCat smaller sparse variants
- mechanism-faithful access to a trillion-model architecture thesis.

### ZUNA / ZUNA1.1
- controlled masking/objective change in a non-language modality.

---

# 18. Instrument-value gate for future topic search

Before saying "this question requires us to train X," search HF/model cards for an existing intervention pair.

Specifically search for:
- base vs instruct;
- SFT vs RL;
- pre-anneal vs post-anneal;
- teacher vs student;
- expert vs merged model;
- BF16 vs quantized;
- high-effort vs low-effort;
- thinking vs no-thinking;
- different reasoning languages;
- old vs new tokenizer;
- different context-management modes;
- same architecture at multiple sizes.

If the needed contrast already exists publicly:

> use it before spending GPU.

This can dramatically reduce pilot cost.

---

# 19. Recent startup/model-card technical-thesis map

## Training / post-training
- Thinking Machines: effort-conditioned RL; task expertise as training signal.
- InclusionAI: WSM transforms LR decay into checkpoint-merge search.
- MiniCPM: critic RL + multi-expert OPD.
- Cognition: extra RL on already-post-trained coding base; long-horizon compaction.
- Sakana: harness optimization rather than model update.
- Prime Intellect: mutable continual harness.

## Architecture
- Zyphra: compressed attention / MoE and bounded reasoning-state aggregation.
- LongCat: sparse indexing + hardware co-design.
- Liquid: hybrid conv/attention for local inference.
- Poolside: sparse local coding model under memory constraints.

## Multimodal / interaction
- Thinking Machines: interaction-native micro-turn model.
- H Company: computer-use across environment/harness/deployment shift.
- Cohere: small native-resolution VLM as customization substrate.
- ZUNA: reconstructive foundation model for EEG.

## Memory / state
- Sakana FwPKM: inference-time fast weights.
- Prime Agent: persistent external/harness state.
- Poolside/Arcee: preserved reasoning as protocol state.

---

# 20. What is becoming saturated even in startup-land

After this scan, several phrases should be treated as already crowded:

- self-evolving harness;
- agentic RL;
- domain experts + on-policy distillation;
- reasoning effort control;
- hybrid sliding/global attention;
- tiny active MoE;
- harness diversity;
- 1M context;
- quantization-aware distillation;
- local agent model;
- active/synthetic environment scaling.

A startup doing it does not make it new.

The useful question is:

> what specific failure forced this design?

---

# 21. Most important startup-vs-incumbent difference

Large incumbents often reveal:
> system pressure at scale.

Startups/open-model labs often reveal:
> a sharper thesis about how to respond to that pressure.

Example:

Industrial pressure:
> agent loops make persistent context expensive.

Different responses:
- Prime: programmable context/harness;
- Poolside: small-active local agent model;
- Liquid: on-device architecture;
- Sakana: optimize harness information flow.

These are competing abstractions, not one method family.

That competition is where research questions can emerge:

> which abstraction addresses the pressure, under which regime?

---

# 22. Current execution-value highlights

Not topic rankings. Only artifact usefulness for a small lab.

## Very high instrument value
- MiniCPM5-2B staged checkpoints/data
- Tiny Aya paired reasoning-language models
- ZUNA/ZUNA1.1
- small LongCat sparse variants
- Prime Agent open harness
- open RHI reproduction ecosystem

## Medium
- Poolside Laguna XS 2.1
- Liquid LFM2.5
- Arcee Trinity stages
- Holo models
- Ling smaller variants

## Low direct execution / high inspiration
- Inkling
- Kimi K3
- LongCat-2.0
- Cognition SWE-1.7
- industrial full-duplex models

---

# 23. Final rule for HF scanning

Never ask only:

> What interesting models came out this week?

Ask four questions:

1. What technical thesis does this model card make?
2. What matched artifact does it release that could function as an experiment?
3. What changed workload/deployment regime motivated it?
4. Can we test the underlying relation without reproducing the whole model?

If question 2 or 4 has a good answer:
> the release may be disproportionately valuable to us.

If only benchmark numbers are public:
> log it, but do not let it shape research taste.
