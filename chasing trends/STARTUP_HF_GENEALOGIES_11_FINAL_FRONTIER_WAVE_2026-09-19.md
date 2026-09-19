# Startup & Hugging Face Genealogies 11 — Final Frontier Wave — 2026-09-19

> **Status: FINAL broad literature-calibration wave.**
>
> After this file, broad startup/Hugging-Face scanning is intentionally stopped.
>
> Future literature search should be:
> - candidate-specific,
> - dangerous-prior-specific,
> - or triggered by a genuinely changed premise.
>
> **NO new CT candidate is generated here.**
>
> This final wave focuses only on artifacts that satisfy at least one of:
>
> 1. expose a real failure boundary;
> 2. provide a small/matched public experimental artifact;
> 3. promote an old system variable into a new training/inference operator;
> 4. provide a controlled test of what pretraining/world-modeling is actually buying.

---

# Relation tags

- **DIRECT** — explicit predecessor/successor relation.
- **FIELD** — same research family.
- **CROSS-LAB** — independent convergence; no causal influence claimed.
- **RECONSTRUCTED** — conceptual reconstruction for research taste only.

---

# S111 — Robot pretraining value decomposes: peak task learning, environment transfer, and in-context task learning are different claims

The robotics field often says:

> foundation-model pretraining improves downstream robotics.

That sentence is too coarse.

Recent Figure and Skild releases make the ambiguity explicit.

---

## S111.1 Conventional interpretation: pretraining buys better downstream finetuning

A typical robotics-pretraining claim is:

pretrain broadly
→ finetune on task
→ higher task success / less robot data.

But this leaves a difficult question:

> if downstream task data becomes dense enough, does pretraining still matter?

A sufficiently large task-specific dataset can sometimes let a specialist trained from scratch catch up.

So final downstream peak performance is not necessarily the cleanest measure of foundation-model value.

---

## S111.2 Skild S1 changes the target to in-context task acquisition [FIELD]

Skild's August 2026 S1 release states the issue directly:

> if dense task-specific post-training can eventually train a strong specialist, the real purpose of broad pretraining should be to let a robot learn a **new task from context**, without updating weights.

S1 is pretrained with task identity supplied through an in-context video demonstration.

At inference:
- show one task video;
- no finetuning;
- execute the task in the robot's own scene/embodiment.

The reported target includes:
- novel atomic skills;
- unseen skill compositions;
- long-horizon tasks up to roughly 10 minutes.

### Primitive change

pretraining value = better initialization for finetuning
→ pretraining value = learned ability to infer the task from demonstration at test time.

This is a major changed premise.

---

## S111.3 Figure Helix 2.5 isolates another value: environment generalization [DIRECT]

Figure's September 17 Helix 2.5 announcement finally provides a more controlled pretraining ablation than most company robotics demos.

Reported comparison:
- same downstream task-specification data;
- same architecture;
- same optimization/hyperparameters;
- same evaluation;
- only difference: Index human-behavior pretraining vs random initialization.

Reported strict zero-shot full-task success across 30 unseen homes:
- from-scratch: **9%**
- Index-pretrained: **56%**

The behaviors were still specified with task-specific data collected elsewhere.

So "zero-shot" here means:
> no data/adaptation in the evaluation homes or on their manipulated objects.

It does **not** mean:
> unseen task from one demonstration.

### Primitive change

pretraining value = downstream peak score
→ pretraining value = transfer of a learned behavior across unseen environments/objects.

---

## S111.4 Figure also exposes a scale-transfer claim, but the proxy must be separated from task success

Figure reports:
> repeatedly doubling Index pretraining data gives a smooth downstream robot-action-prediction loss trend that forecasts the largest run closely.

This is potentially useful as a cheap/full-scale design principle.

But two quantities must not be conflated:

1. action-prediction validation loss;
2. zero-shot household task completion.

The controlled 9→56 experiment gives downstream evidence that pretraining matters.

It does **not** automatically prove:
> the action-prediction scaling curve is itself a sufficient predictor of household reliability.

### Canonical lesson

A scaling proxy is scientifically useful only if we check:
> how faithfully it predicts the downstream consumer quantity.

---

## S111.5 Robotics "pretraining helps" must now be decomposed

At least five distinct claims exist:

### A. Peak finetuned performance
Does pretrained initialization improve the best achievable specialist?

### B. Finetuning sample efficiency
How much task-specific robot data is needed?

### C. Environment/object transfer
Does the same learned behavior work in unseen physical settings?

### D. In-context task learning
Can a new behavior be specified from a demonstration with no weight update?

### E. Adaptation speed
How rapidly can the model adjust to a new embodiment/task?

Skild and Figure optimize different columns.

Therefore:
> they should not be collapsed into one "robot foundation model scaling" story.

---

# S112 — World-model quality is defined by the consumer contract, not one universal fidelity metric

By September 2026, "world model" is so overloaded that product pages themselves reveal incompatible objectives.

The useful genealogy is no longer:
> who has the best video generator?

It is:
> **what downstream consumer is the model supposed to support?**

---

## S112.1 World Labs: world model functions must be separated [DIRECT]

World Labs' June taxonomy explicitly distinguishes:
- **renderer**
- **simulator**
- **planner**

This matters because each function requires different correctness.

A renderer can prioritize:
> spatial/visual consistency.

A simulator must preserve:
> action-conditioned dynamics.

A planner additionally needs:
> dynamics accurate enough that alternative actions can be ranked correctly.

Thus:
> visual realism is not a sufficient universal world-model metric.

---

## S112.2 R2S2R moves simulator quality toward decision fidelity [DIRECT]

World Labs / SceniX's July R2S2R work uses simulation to:
- expand one real task into controlled variations;
- train robot policies;
- predict which policies/checkpoints will transfer to hardware;
- identify failure regions before costly real trials.

The key contract is not:

simulation success rate exactly equals reality.

A simulator can be useful if it preserves:
> **the development decision**.

For example:
- policy A should rank above B in both sim and real;
- a checkpoint improvement in sim should transfer to hardware;
- the same failure region should be exposed.

### Primitive change

simulator fidelity = state/pixel similarity
→ simulator fidelity = decision fidelity for a specified consumer.

---

## S112.3 Decart Oasis 3: world model as realtime training infrastructure [CROSS-LAB]

Oasis 3 is explicitly built as:
- action-conditioned;
- synchronized multi-camera;
- geometry-aware;
- closed-loop;
- <200ms end-to-end / 22 FPS at the reported configuration;
- available through an API.

Its contract is:
> a policy must be able to act inside the generated world fast enough for online training/testing loops.

So the important dimension is not only fidelity.

It is:
> **fidelity under realtime controllability.**

A visually stronger but slow/offline world generator may fail this contract.

---

## S112.4 Odyssey-3: frozen world representations as cross-embodiment physical prior [DIRECT]

Odyssey-3's September 15 release takes a different route.

A single pretrained autoregressive diffusion world model is kept largely as a common physical representation, then relatively small task/action components are learned for:
- robot arms;
- humanoids;
- cars;
- drones;
- games.

Examples reported:
- tens of hours of robot data;
- 20 hours of simulated driving data;
- tens of hours of humanoid teleoperation;
- frozen pretrained backbone for several downstream control settings.

The central thesis is:

> broad visual dynamics pretraining can provide a reusable physical prior, while task-specific control is learned in a smaller action decoder/policy.

### Primitive change

world model as simulator only
→ world model as reusable representation layer for multiple control systems.

This is closer to:
> foundation representation transfer
than to Decart's simulator-as-a-service contract.

---

## S112.5 Odyssey's own genealogy shows why "world model" keeps changing

Odyssey-2 Max emphasized:
- causal next-state prediction;
- long-horizon rollout stability;
- interaction;
- realtime inference;
- physics scores.

Odyssey-3 extends the object:
> use that representation to control multiple physical/virtual systems with much less task-specific experience.

Thus the "consumer" moved from:
> simulation quality
to
> downstream policy adaptation.

---

## S112.6 General Intuition: high inspiration, currently weaker public intervention artifact

General Intuition publicly frames its program around:
- action models;
- world models;
- action-labeled gameplay;
- virtual→physical transfer.

MIRA with Kyutai is a strong existing technical artifact.

But as of this final scan:
> the company's newest high-level physical-AI thesis is more public than a new matched September technical-report/model family.

Therefore:

- **frontier-pressure value: high**
- **new public experimental-instrument value: currently lower**

Do not promote company narrative into a new genealogy without the artifact.

---

## S112.7 World-model audit must start with the consumer

Before comparing two world models, write:

### Consumer
- human viewer?
- policy learner?
- policy evaluator?
- planner?
- robot controller?
- synthetic-data generator?

### Required invariants
- visual consistency?
- action causality?
- multi-view geometry?
- long-term state?
- rare-event coverage?
- policy ranking?
- realtime latency?

### Failure consequence
What does a world-model error actually break downstream?

Without this:
> "better world model" is scientifically underspecified.

---

# S113 — Adding a new modality: full integration, parameter separation, or frozen-backbone extension are competing abstractions

Recent speech models now expose at least three fundamentally different answers to:

> how should a strong text model acquire audio capability without destroying what it already knows?

---

## S113.1 Full integration creates interference risk [FIELD]

Unified audio-language models can:
- train language/audio jointly;
- deeply share parameters;
- enable rich cross-modal interaction.

But recent work repeatedly observes a real cost:
> new modality training can degrade text/semantic ability.

The question is no longer simply:
> "how do we add audio?"

It is:
> **where should new modality learning be allowed to modify the pretrained computation?**

---

## S113.2 Lychee-FD: diagnose interference, then separate deep parameters [FIELD]

Lychee-FD analyzes full-duplex training and attributes semantic degradation partly to:
> acoustic–semantic gradient conflicts under deep parameter sharing.

Its response is:
> hierarchical parameter separation.

This keeps some shared/aligned structure but prevents the highest-conflict computation from being fully shared.

The logic is:

observed semantic degradation
→ optimization-conflict diagnosis
→ targeted parameter separation.

---

## S113.3 StepAudio 3 Gen: multimodal capability preservation is a training-design requirement [FIELD]

StepAudio 3 Gen's general-audio generation program explicitly treats:
> acquiring broad audio generation capability without catastrophically degrading the LLM's existing text intelligence

as a design constraint.

It chooses a discrete autoregressive audio formulation with its own token/codebook structure rather than merely grafting a diffusion generator onto the language stack.

Again:
> capability preservation is part of the architecture/training contract.

---

## S113.4 A.X K2 ALM chooses the extreme solution: freeze the LLM entirely [DIRECT]

SK Telecom's A.X K2 ALM takes a particularly clean production-motivated position:

> the deployed LLM's text-response quality must remain unchanged.

Therefore:
- freeze A.X K2 Light completely;
- train speech encoder;
- adapter;
- VAD;
- speech decoder;
- perform speech alignment + frozen-LLM-in-the-loop self-distillation.

The responsibility for mapping audio to the existing language computation is moved to:
> the speech-side interface.

### Primitive change

multimodal extension = update the foundation model
→ multimodal extension = learn an input/output interface around an immutable foundation model.

---

## S113.5 Integrated VAD is another example of interface relocation

A.X K2 ALM replaces a purely external VAD with lightweight classifiers that read:
- adapter representations;
- frozen-LLM hidden states.

This lets the system use:
> linguistic/contextual evidence

to distinguish:
- real turn completion;
- backchannels;
- hesitation;
- non-speech noise.

So even with frozen LLM weights:
> internal language representations can become signals for new realtime control heads.

---

## S113.6 Artifact boundary matters

A.X K2 ALM has a detailed model card/technical report, but the current card says:
> model weights are planned for public release / coming soon.

Therefore:

- thesis value: high;
- present instrument value: **not high yet**.

A model card is not an open experimental artifact until:
> weights/code needed for the proposed experiment actually exist.

This becomes a hard repo rule.

---

## S113.7 Competing modality-extension strategies

We can now distinguish:

### Full integration
Allow cross-modal weights to co-adapt strongly.

Benefit:
- maximal fusion.

Risk:
- forgetting/interference.

### Selective separation
Share some computation, separate high-conflict modules.

Benefit:
- preserve interaction with less interference.

Risk:
- architectural complexity / hand-chosen boundary.

### Frozen backbone + learned interface
Keep original model immutable.

Benefit:
- exact text-capability preservation.

Risk:
- modality adapter may hit an information/interface ceiling.

There is no universally superior choice.

The right design depends on:
> whether the new modality requires changing the pretrained computation or only translating into it.

---

# S114 — Sparse attention selector training: dense attention is not necessarily the correct teacher

Tencent's September SAS release is a clean example of questioning the **training target** of a popular efficiency component.

---

## S114.1 Existing trainable sparse attention often distills dense attention ranking [FIELD]

A selector predicts which KV blocks/tokens should remain.

Hard Top-K selection blocks gradients from the final language-modeling loss.

A common workaround:
> train the selector to imitate the dense model's attention distribution.

Hidden assumption:

> high dense-attention weight = high marginal utility under a sparse budget.

These are not necessarily identical.

---

## S114.2 The new pressure appears under tight budget [DIRECT]

When only a small number of blocks can be kept:

> ranking quality matters more than reproducing the dense attention distribution.

A dense model can spread weight over many positions it can afford to read.

A sparse model cannot.

Thus the relevant target is:

> which subset minimizes downstream LM loss under the actual fixed budget?

---

## S114.3 SAS reopens the gradient path to the downstream objective [DIRECT]

SAS adds continuous gates inside attention logits during training.

That lets:
> language-modeling loss directly update context ranking.

It also keeps:
- hard/sparse deployment;
- a FlashAttention/Triton-style efficient implementation;
- released Qwen3-based checkpoints/code.

### Primitive change

selector target = imitate dense attention
→ selector target = optimize downstream prediction under sparse-resource constraints.

This is an excellent general research move:

> **a proxy teacher is only justified if it preserves the downstream ordering relevant under the constrained regime.**

---

## S114.4 Why this is not "just objective mismatch"

The concrete objects matter:

- dense-attention ranking;
- sparse-budget marginal utility;
- discrete Top-K;
- gradient blocking;
- continuous training gate.

Without those details:
> "proxy mismatch" is empty terminology.

---

# S115 — Coverage → residual capability: learner-relative data construction after broad data saturation

WeVisDoc is data-centric and therefore not a default execution direction for this project.

It is still useful as research-taste calibration.

---

## S115.1 Stage I solves coverage [DIRECT]

Document parsing data is biased toward:
- common layouts;
- clean digital pages.

Stage I broadens:
- semantic coverage;
- structural coverage;
- visual appearance;
- structure-preserving degradation.

This is the natural first response:
> expand the dataset.

---

## S115.2 Once coverage expands, "more diversity" no longer tells you what to add [DIRECT]

After a broad first stage, the model still has residual failures.

WeVisDoc:
- runs a held-out probe;
- measures residual errors inside fixed visual/structural clusters;
- uses these diagnostics to construct targeted data and reallocate the target-token budget.

### Primitive change

data value = intrinsic coverage/diversity
→ data value = unresolved residual capability of the current learner.

This independently resembles:
- Echoverse learner-relative environments;
- DiagEvo unresolved failure memory;
- failure-driven agent task generation.

But the domain and intervention differ.

---

## S115.3 Why we still would not automatically choose this as a topic

The project can easily become:
- data engineering;
- cluster taxonomy;
- synthetic degradation;
- benchmark/evaluator work.

That is not the user's preferred default.

What is worth learning is the question-forming move:

> after broad coverage saturates, diagnose **where the current model remains weak** before expanding data further.

Not:
> build another targeted dataset pipeline.

---

# S116 — Latest-release freshness and public-artifact maturity are separate axes

This final scan surfaced several good examples.

---

## S116.1 Fresh and experimentally open

### WeVisDoc
- Sep 17 paper;
- 2B/4B HF checkpoints;
- GitHub inference stack.

Freshness: high  
Instrument value: high.

### SAS
- Sep 11 paper;
- open checkpoints;
- code.

Freshness: high  
Instrument value: high.

---

## S116.2 Fresh and strong thesis, but closed/heavy

### Figure Helix 2.5
- Sep 17;
- unusually good controlled pretraining ablation;
- no open weights/data.

Freshness: high  
Inspiration: high  
Instrument: F/C.

### Odyssey-3
- Sep 15;
- strong cross-embodiment thesis;
- public release promised, not yet a small matched artifact in this scan.

Freshness: high  
Inspiration: high  
Instrument: currently low.

---

## S116.3 Detailed card does not equal released weights

### A.X K2 ALM
- detailed technical card/report;
- current card says weights coming soon.

Therefore:
> **do not score future artifact availability as current experimental access.**

---

## S116.4 Company thesis without a new technical artifact

### General Intuition
- strong research lineage (IRIS → Δ-IRIS → DIAMOND → GAIA-2 → MIRA);
- clear physical-AI thesis;
- no equally detailed new Sep 18/19 model artifact found in this scan.

Therefore:
> monitor, do not manufacture novelty from recency/company visibility.

---

# S117 — Final rule: changed premise beats company name, recency, and benchmark strength

Across the last several waves, the useful releases were not uniformly:
- largest;
- most liked;
- newest;
- highest benchmark score.

They were useful because they offered one or more of:

### Controlled premise change
Figure:
> human-data pretraining vs from-scratch under fixed downstream setup.

### Corrected training target
SAS:
> downstream sparse utility vs dense-attention imitation.

### Public intervention pair
Kyutai:
> chronological vs shuffled pretraining.

### Failure-localized repair
LACI:
> onset detection + rollback instead of global intervention.

### Intermediate failure state
Instella:
> specialization gain + capability regression + consolidation repair.

### Domain-structure placement
JEPA-DNA / BioMatrix / Lunar FM:
> objective/token/context choices expose different assumptions.

### Consumer-contract change
World Labs / Decart / Odyssey:
> simulator/world-model value depends on the downstream operator.

This is the final broad-search criterion.

---

# S118 — Final new hard gates

## Pretraining Value Decomposition Gate

Any claim:
> "pretraining helps"

must specify which quantity improves:

- peak downstream performance;
- sample efficiency;
- adaptation speed;
- environment transfer;
- task ICL;
- embodiment transfer;
- robustness;
- calibration.

Do not merge these.

---

## World-Model Consumer Contract Gate

Before comparing world models, specify:
- consumer;
- required state;
- required action conditioning;
- latency;
- temporal horizon;
- fidelity quantity;
- downstream failure consequence.

No universal "world-model quality" score is assumed.

---

## Modality Extension Placement Gate

When adding a modality to an existing foundation model, ask:

1. what existing capability must be preserved?
2. does the new modality require changing internal reasoning, or only translating into/out of it?
3. where is gradient conflict measured?
4. which parameters are shared/frozen/separated?
5. what capability is lost under full integration?
6. what ceiling appears under freezing?

Do not choose:
> frozen / shared / separated
as style preferences.

---

## Public Artifact Maturity Gate

Artifact stages:

### A — runnable matched artifact now
Weights/code/data/control pair accessible.

### B — runnable but heavy/confounded
Useful, but expensive or bundled.

### C — technical report/model card only
Enough for pressure/taste, not pilot.

### D — roadmap/announced future release
Do not count as present access.

### F — proprietary-only.

"Coming soon" = D/C, not A.

---

## Proxy-to-Consumer Fidelity Gate

If a cheap/full-scale pipeline uses proxy P for consumer metric Y:

Require evidence for at least one of:
- method ranking preserved;
- effect sign preserved;
- mechanism variable preserved;
- downstream improvement tracks proxy change.

If:
> proxy scales smoothly but consumer relation is untested,

record it as:
> scale evidence, not consumer evidence.

---

# S119 — Broad literature calibration stopping rule

The broad scan is now intentionally closed.

Reason:
> marginal value of adding another company/model name is falling,
while the risk of pattern-shopping and trend bias is increasing.

From now on, literature reading should reactivate only when:

1. auditing a concrete CT candidate;
2. checking dangerous nearest prior;
3. a genuinely new changed premise appears;
4. a released artifact materially changes pilot feasibility;
5. a current trend enters a correction/negative-result phase.

Do **not** restart weekly broad HF crawling by default.

The goal was not:
> know every model.

The goal was:
> build enough genealogy, evidence discipline, artifact awareness, and execution calibration to recognize a real research opening when one appears.

That calibration phase is complete.
