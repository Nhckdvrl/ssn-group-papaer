# Genealogy Library Index — 2026-09-19

> 这是 chasing trends/ 当前 literature-calibration library 的导航与 coverage audit。
>
> **它不是 idea generator。**
>
> 用法：
>
> 1. 要理解某个 lineage，跳到对应 longitudinal file；
> 2. 要判断“这个 research move 是否已经 crowded”，先看 saturation；
> 3. 要做跨域迁移，先看 source pressure，而不是只看 move 名称；
> 4. 正式找题前，用这个 index 检查是不是又只在同一个 family 内循环。

---

# A. Current longitudinal coverage

## G01 — RLVR learning-signal decomposition

Core sequence:
- DeepSeekMath / GRPO
- DeepSeek-R1
- DAPO
- High-Entropy Minority Tokens
- Negative Reinforcement
- GSPO
- CAPO

Frontier movement:

scalable RL algorithm
→ large capability effect
→ training stability
→ token heterogeneity
→ positive/negative feedback asymmetry
→ optimization-unit alignment
→ calibration / side-objective consistency

What changed:
> “RL signal”不再被当 atomic object。

Saturated surfaces:
- generic entropy weighting
- positive/negative sample reweight
- another GRPO clip
- generic process reward

Execution:
> medium/high; training required, but some diagnosis can be cheap.

File:
> LONGITUDINAL_GENEALOGIES_01_2026-09-19.md

---

## G02 — Test-time scaling / search policy

Core:
- Self-Consistency
- Tree of Thoughts
- process supervision
- compute-optimal TTS
- budget-aware MCTS
- GUARD / critical-transition repair

Movement:

one path
→ path distribution
→ explicit search state
→ intermediate evaluation
→ difficulty-conditioned compute
→ remaining-budget-conditioned policy
→ trajectory-local intervention

What changed:
> compute从“数量”变成“control problem”。

Saturated:
- generic best-of-N
- another tree search
- generic adaptive compute
- generic entropy branch

Execution:
> often moderate; inference-only can be attractive, but verifier/search compute can explode.

---

## G03 — ICL mechanism

Core:
- Induction Heads
- Task Recognition vs Task Learning
- Task Vectors
- Function Vectors
- task-vector structure/boundaries
- Task-oriented Information Removal

Movement:

behavior
→ circuit
→ capability decomposition
→ compact task representation
→ endogenous causal function representations
→ structure/boundary
→ addition explanation challenged by removal/filtering explanation

What changed:
> explanatory primitive。

Saturated:
- find another head
- find another task vector
- another probe showing representation

Execution:
> low/moderate if using open models; causal rigor matters more than scale.

---

## G04 — Diffusion fast sampling

Core:
- solver acceleration
- optimized time steps
- state-conditioned scheduling
- cache family
- TORS unified design-space attribution
- difficulty-aware spatial adaptation

Movement:

better solver
→ where to spend evaluations
→ state-conditioned schedule
→ method zoo
→ matched component attribution
→ geometry-derived schedule
→ local spatial heterogeneity

What changed:
> acceleration method从 isolated trick变成 resource-allocation/design-space problem。

Saturated:
- generic adaptive timestep
- another cache heuristic
- another solver tweak

Execution:
> medium/high depending backbone; training-free diagnostics often possible.

---

## G05 — Robot/VLA action representation

Core:
- single-step BC
- ACT
- Diffusion Policy sibling
- RT-2
- OpenVLA / Octo
- FAST
- async chunk correction / latency work

Movement:

single action
→ action chunk
→ action token interface
→ scalable generalist VLA
→ tokenization becomes learnability bottleneck
→ large-model latency makes chunking a reactivity problem

What changed:
> prediction unit / representation / deployment timing。

Saturated:
- generic action chunk
- generic VLA tokenization
- “use DCT” surface transfer

Execution:
> real robot high; offline datasets lower but deployment claims harder.

---

## G06 — Pretraining scaling / data composition

Core:
- Kaplan scaling
- Chinchilla
- data-mixture optimization
- Scaling Laws for Optimal Data Mixtures
- Data Mixing Phase Transitions
- Datasets/Documents/Repetitions
- Power Lines

Movement:

N,D,C scalar laws
→ compute-optimal allocation revised
→ data composition becomes variable
→ mixture enters scaling law
→ knowledge acquisition can be discontinuous
→ repetition/document exposure matters
→ recipe variables scale too

What changed:
> “data amount”逐渐被解压成 structured resource。

Saturated:
- another scaling coefficient
- another mixture optimizer
- huge sweep without identification

Execution:
> high/very high; mainly taste source, not default project source.

File:
> LONGITUDINAL_GENEALOGIES_02_2026-09-19.md

---

## G07 — SFT and model knowledge

Core:
- instruction tuning / LIMA
- New Knowledge & Hallucination
- SFT token/parameter knowledge analysis
- massive SFT empirical sweeps

Movement:

SFT as behavior adaptation
→ new facts differ from pretrained-known facts
→ supervision is model-state-relative
→ token/parameter updates become object

What changed:
> training example不再只由文本内容定义，而由它相对模型当前 knowledge state定义。

Saturated:
- generic forgetting
- more SFT can hurt
- checkpoint biography

Execution:
> low/moderate for controlled local studies; high if requiring family×recipe matrix.

---

## G08 — Knowledge / CoT distillation

Core:
- standard KD
- MiniLLM
- capacity-gap law
- key-step CoT distillation
- curriculum distillation
- student-trajectory / selective intervention

Movement:

strong teacher → imitate
→ divergence matters
→ stronger teacher can be worse
→ trace supervision is heterogeneous
→ supervision complexity should match student
→ teacher distribution mismatches student rollout

What changed:
> supervision quality从 teacher intrinsic quality变成 teacher–student relation。

Saturated:
- teacher too complex
- key steps
- curriculum
- student-generated trajectory
- stronger teacher not always better

Execution:
> moderate; good small-model opportunities, but crowded.

---

## G09 — Architecture / inductive bias / depth

Core:
- Universal Transformer
- Looped Transformer theory
- Recurrent Depth latent reasoning
- A Little Depth Goes a Long Way
- Body Transformer
- LieRE-like spatial positional bias

Movement:

fixed stack
→ iterative shared computation
→ latent test-time compute

Parallel:
fixed-depth limitation
→ minimal depth growth changes theory

Cross-domain:
generic token architecture
→ physical / geometric structure becomes inductive bias

What changed:
> architecture被理解为“什么 computation/geometry被做得自然”。

Saturated:
- module invention without structural pressure
- recurrence/memory as buzzword
- toy theorem with no bridge

Execution:
> ranges low theoretical → extremely high if from-scratch pretraining.

---

## G10 — VLM interface and visual-token lifecycle

Core:
- Flamingo
- BLIP-2
- LLaVA
- high-res/AnyRes
- FastV family
- ATP/PACT/TopV
- DyCoke
- V2Drop/ApET/DUET
- MetaCompress multi-turn

Movement:

connect modalities
→ freeze experts / learn bridge
→ simple connector + instruction tuning
→ high-res token explosion
→ layer/instance-dependent redundancy
→ actual operator compatibility
→ decoding-time dynamic relevance
→ future-query uncertainty in multi-turn

What changed:
> visual token从“input”变成有 lifecycle / future utility 的 compute-information object。

Saturated:
- visual token pruning almost everything
- attention score replacements
- adaptive ratio
- generic merging

Execution:
> moderate, but novelty bar very high.

File:
> LONGITUDINAL_GENEALOGIES_03_2026-09-19.md

---

## G11 — Latent multimodal reasoning

Core:
- text-centric VLM reasoning
- explicit image/crop/depth intermediate
- Machine Mental Imagery
- Latent Implicit Visual Reasoning
- parallel latent multimodal reasoning work

Movement:

verbalize visual reasoning
→ explicit visual intermediates
→ latent task-adaptive visual computation

What changed:
> reasoning medium itself。

Saturated:
- “latent visual token”
- “mental imagery” surface
- explicit→latent substitution

Execution:
> moderate/high; crowded by 2026.

---

## G12 — Full-duplex speech dialogue

Core:
- ASR→text LLM→TTS pipeline
- speech LM
- Synchronous LLMs
- Moshi

Movement:

turn-based modular pipeline
→ speech token modeling
→ shared real-world clock / concurrent streams
→ direct speech-to-speech
→ text reintroduced internally as aligned semantic scaffold

What changed:
> conversation从 alternating utterances变成 continuous concurrent process。

Saturated:
- full duplex as label
- generic streaming
- just reduce latency

Execution:
> high system/data cost; excellent taste source, poor default project.

---

## G13 — Negative/limits / measurement re-attribution

Core:
- Calibrate Before Use
- Fantastically Ordered Prompts
- modern instruction tuning changed premise
- Flaw or Artifact?
- World-model inductive-bias probe

Movement:

large measured sensitivity/success
→ community interpretation
→ training/evaluation regime changes
→ measurement no longer uniquely identifies interpretation
→ failure/success is re-attributed

What changed:
> “问题发生在哪”而不是 score itself。

Saturated:
- another stress test
- another judge
- another perturbation benchmark

Execution:
> often low/moderate; danger is evaluator project swallowing science.

---

## G14 — Optimization / SAM dynamics

Core:
- SAM
- SAM Operates Far from Home
- SDE/saddle analysis
- Lookahead SAM
- BiSAM
- Tilted SAM
- optimizer memory as implicit loss modification

Movement:

local flatness objective
→ whole-trajectory Hessian dynamics
→ unintended saddle behavior
→ targeted algorithmic correction

Parallel:
same-surrogate minmax
→ objective formulation itself questioned

What changed:
> successful algorithm的 original explanation不再被当 final explanation。

Saturated:
- another SAM variant without new dynamics
- toy sharpness metric
- optimizer acronym

Execution:
> often attractive for controlled low-cost science; theory burden can be high.

---

## G15 — Multimodal pretraining objective relation

Core:
- CLIP-style contrastive
- generative VLP
- BLIP
- CoCa
- BLIP-2
- unified understanding/generation
- understanding-as-reward
- autoencoder reconstruction view

Movement:

contrastive vs generative
→ preserve both capabilities
→ architectural sharing/factorization
→ frozen-expert bridge
→ any-to-any unified models
→ exploit relations/asymmetries among capabilities

What changed:
> from “choose objective” to “what relation should objectives/capabilities satisfy”。

Saturated:
- generic unified model
- add another loss
- self-reward without identified relation

Execution:
> large-scale model training often high; small post-training studies possible but trending/crowded.

File:
> LONGITUDINAL_GENEALOGIES_04_2026-09-19.md

---

## G16 — Speech tokenization

Core:
- neural audio codec
- semantic SSL units
- SpeechTokenizer
- Mimi
- SLM scaling
- DM-Codec

Movement:

reconstruction code
→ semantic unit
→ hierarchical semantic+acoustic code
→ streaming low-rate dialogue code
→ contextual information enters representation

What changed:
> tokenizer从 compression detail变成 downstream learning interface。

Saturated:
- semantic+acoustic token buzzword
- another teacher signal without failure
- codec metric only

Execution:
> audio training can be high; representation probes may be lower.

---

## G17 — CoT faithfulness identification

Core:
- bias/hint intervention
- causal mediation
- model-family dynamics
- FUR unlearning
- causal diagnosticity
- natural/in-the-wild faithfulness

Movement:

is rationale plausible?
→ does intervention alter answer?
→ different training makes CoT play different roles
→ faithful to parametric belief?
→ are faithfulness metrics themselves diagnostic?
→ does phenomenon hold without artificial cue?

What changed:
> concept definition / identification target逐渐收紧。

Saturated:
- CoT can be unfaithful
- another faithfulness metric
- another bias injection

Execution:
> moderate; crowded and evaluator-heavy.

---

## G18 — Video / world-model dynamics

Core:
- video generation
- action-conditioned world modeling
- Dexterous World Models
- VideoWorld 2
- Motus
- autoregressive video / cache correction

Movement:

generate coherent pixels
→ model action-conditioned transition
→ interactive digital twin
→ separate appearance from task dynamics
→ unify action/world/understanding
→ long-horizon autoregression creates compounding state error

What changed:
> video generator从 content model变成 environment-transition model。

Saturated:
- “world model” label
- giant unified architecture
- action-conditioned generation without identification

Execution:
> high data/engineering; mainly pressure source for us.

---

# B. Cross-lineage comparison: same surface, different genealogy

## “Adaptive”

Appears in:
- test-time compute
- diffusion schedule
- VLM pruning
- distillation
- recurrent compute

But source pressure differs:
- TTS: marginal value of inference compute differs by state
- diffusion: trajectory integration error differs by time/state
- VLM: token information value differs by layer/query/time
- KD: supervision learnability differs by student state
- architecture: computation need differs by input/token

Conclusion:
> adaptive本身零 novelty。

---

## “Selective”

Appears in:
- high-entropy RL tokens
- key reasoning distillation
- visual token pruning
- SFT parameter restoration
- failure-onset repair

Underlying reason:
- branching decision
- instructional leverage
- redundancy
- harmful/irrelevant update
- trajectory causal onset

Conclusion:
> selective只是一种 operational consequence，不是 shared scientific problem。

---

## “Latent”

Appears in:
- recurrent latent reasoning
- latent visual reasoning
- video latent dynamics
- task/function vectors

Underlying object:
- computation depth
- modality-specific reasoning representation
- dynamical state
- task representation

Conclusion:
> latent是 location，不能承担 scientific claim。

---

## “Unified”

Appears in:
- VLP objectives
- speech token representations
- multimodal any-to-any
- world model + policy

Fragmentation being repaired differs:
- loss/objective
- information type
- modality/output interface
- system capability

Conclusion:
> unified是 engineering direction，除非先定义 fragmentation为什么有损失。

---

## “Mismatch”

Appears everywhere:
- train/test
- teacher/student
- objective/calibration
- representation/modality
- evaluator/model output
- budget/policy
- deployment/kernel

Conclusion:
> “发现 mismatch”也已经是空词。

必须说明：
- 哪两个 distributions/objects/constraints？
- mismatch如何产生可区别 prediction？
- intervention应该改哪一边？

---

# C. Coverage balance audit

目前 library 已覆盖：

### Training
- pretraining
- SFT
- distillation
- RL/post-training

### Inference
- CoT
- search
- test-time compute
- faithfulness

### Architecture
- depth
- recurrence
- inductive bias
- positional geometry

### Multimodal
- VLM interface
- token compression
- latent visual reasoning
- unified understanding/generation

### Generative modeling
- diffusion sampling
- video/world models

### Embodied
- action representation/chunking
- body structure

### Speech/audio
- full-duplex
- speech tokenizer/scaling

### Optimization/theory
- SAM dynamics
- optimizer memory
- scaling-law assumption

### Negative/limits
- prompt sensitivity
- world-model identification
- CoT faithfulness

这已经比最初 method-first 版本均衡得多。

---

# D. Still underrepresented

不是现在立刻要生成 topic，而是未来 literature study 的盲点：

- memory / state-space models beyond recurrence
- sparse/MoE routing as scientific object
- long-context architecture beyond KV efficiency
- code generation / program synthesis genealogy
- structured prediction / classical NLP problem transformations
- causal representation learning
- self-supervised vision beyond multimodal
- 3D geometry
- probabilistic calibration outside reasoning RL
- continual learning / plasticity-stability
- model editing
- scientific ML

这些不一定都要补齐才找题。

但正式开始候选时，应至少确认：

> 我们没有因为当前阅读池而把所有 question都重写成 reasoning/post-training 问题。

---

# E. Current canonical insight — with warning

目前跨 18 条 lineage 最稳定的 observation不是某种 paper template，而是：

> **Research frontier 往往移动在“field把什么当作 basic object”的层面。**

这个 object可能是：
- token
- step
- trajectory
- reward signal
- teacher
- data amount
- mixture
- representation
- action chunk
- clock
- visual token
- objective
- evaluator
- optimizer state
- world dynamics

但：

> **“换 basic object”也不能变成 generator。**

真正有效的 object change 必须由：
- 已有 contradiction；
- regime shift；
- deployment constraint；
- unexplained asymmetry；
- theory assumption；
- measurement failure；
- method-family saturation；
- physical/statistical structure；

中的真实 pressure逼出来。

所以正确顺序始终是：

literature history
→ current pressure
→ which abstraction blocks progress?
→ only then ask whether object must change

不是：

find an object to redefine
→ invent a story
