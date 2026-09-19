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


---

# FINAL ADDENDUM — Sep 17–19 artifacts

The broad scan was already scheduled to stop. This addendum only records **genuinely new objects** that appeared in the last few days and materially sharpen existing gates.

No new candidate is generated.

---

# S120 — Live data can be compiled into runtime weights: another distinct knowledge location

**Infinite-Parameter LLMs: Generating and Adapting Weights from Live Data**  
arXiv:2609.18842, Sep 16 2026.

The usual deployed-model choices for new information are:

- keep it in prompt/context;
- retrieve it externally;
- update a persistent memory/harness;
- periodically fine-tune/adapt weights.

This work proposes another location:

> **compile live interaction into low-rank effective weights at runtime.**

A compact hypernetwork maps live data into a latent code and low-rank modulation of a shared base network. Unlike one-shot weight generators, the model maintains a Bayesian belief over the latent code and updates that belief during the session, repeatedly re-deriving the effective weights.

### Primitive change

\[
\text{live knowledge} \rightarrow \text{re-read from prompt/RAG}
\]

becomes

\[
\text{live knowledge} \rightarrow \text{generated runtime weights}
\]

The claimed advantages are not merely storage:
- context-window capacity is freed;
- repeated re-reading can be amortized;
- information can persist across turns;
- weight-resident knowledge may generalize differently from in-context use.

### Why this matters for the existing Knowledge Location Audit

"Where is knowledge stored?" now has at least:

1. raw context;
2. retrieved external memory;
3. recurrent / fast-weight state;
4. persistent harness/skill memory;
5. adapter/LoRA bank;
6. **runtime-generated weights conditioned on live data**;
7. ordinary base weights.

These locations differ in:
- write cost;
- read cost;
- persistence;
- interference;
- compositionality;
- amortization;
- editability.

Do not collapse them into "memory."

### Current artifact status

This is a strong architecture/research thesis, but it should not be treated as a cheap ready-made pilot until runnable checkpoints/code are verified.

---

# S121 — Working software can be a specification source, not only a verifier

**ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks**  
arXiv:2609.18805, Sep 16 2026.

Coding benchmarks usually provide desired behavior as:
- issue text;
- tests;
- instructions.

ProgramDistill asks a different question:

> what if the desired behavior is only observable in a working application?

The agent receives:
- a working reference whose source is hidden;
- an editable incomplete application.

It must:
1. interact with the reference;
2. infer intended behavior;
3. implement that behavior;
4. validate the repair.

The pipeline mines 1,975 replay-verified behaviors from 26 applications and builds 4,063 tasks.

---

## S121.1 Executable artifact has multiple epistemic roles

The same working program can act as:

### Specification source
Its behavior tells the agent what must be reconstructed.

### Exploration oracle
The agent probes it to discover hidden behavior/state dependencies.

### Verification source
Replay traces check whether repaired behavior matches.

### Curriculum generator
Prerequisite lineages create controllable restoration depth.

This extends the earlier Oracle Role Separation rule.

"Executable oracle" is too coarse.

We must also ask:

> **Where does the desired specification come from?**

---

## S121.2 ProgramDistill, MindForge, ScienceIDE and Vinci are complementary rather than contradictory

### MindForge-style setting
Hide source and use executable behavior to elicit a specification.

### ProgramDistill
A working reference is the behavioral specification source, while replay traces verify restoration.

### ScienceIDE
The scientific source code is editable/visible and correctness is defined by recompiled numerical/physical cases.

### Vinci evaluator audit
Runtime success or visible tests may be useful feedback but can be far too weak for final certification.

So the lesson is not:

> executable artifacts are reliable or unreliable.

It is:

> **their authority depends on which role they are assigned.**

---

## S121.3 Restoration depth is a clean difficulty operator

ProgramDistill factorizes interactive applications into prerequisite behavior lineages.

Increasing restoration depth:
- requires recovering more dependent behaviors;
- changes the information-seeking burden;
- systematically lowers agent success.

This is better than attaching an arbitrary "easy/medium/hard" label.

The difficulty axis is generated by the structure of the executable specification itself.

---

# S122 — Composition can be scientific when interactions are the hypothesis

**Continual Learning Mechanisms Compose for Long-Horizon Memorization**  
arXiv:2609.06986, Sep 7 2026.  
Official code/data: compose-cl.

This paper corrects one possible overreaction in our existing taste:

> "simple method good; multiple modules bad."

That rule is too crude.

The actual distinction should be:

> **arbitrary stacking is bad; mechanism composition can be the scientific object when the mechanisms correspond to distinct failure sources and their interactions are explicitly tested.**

---

## S122.1 The paper separates two design dimensions

### What prior information should an update preserve?
- data anchor: replay;
- function anchor: self-distillation;
- weight anchor: SI / online EWC.

### Where should successive updates be retained?
- shared LoRA;
- merged LoRA;
- other low-rank allocation variants.

This decomposition precedes the final recipe.

The modules do not enter as:
> "four things that might help."

They enter as:
> different hypotheses about catastrophic forgetting.

---

## S122.2 Long horizon provides the negative result that motivates composition

The setting uses:
- Qwen3-4B-Base;
- 100 sequential QA tasks;
- three datasets;
- three seeds.

Naive sequential fine-tuning retains only about 1.2% on average after 100 tasks.

More importantly:

> **no single continual-learning mechanism remains strong across the full horizon.**

The failure of individual mechanisms is the reason composition becomes scientifically justified.

---

## S122.3 Full factorial distinguishes component value from interaction

The authors run a complete \(2^4\) factorial over:
- replay;
- self-distillation;
- weight anchoring;
- merged LoRA.

The best composition reaches 34.9% average final retention.

Replay and merged LoRA have the largest main effects and, crucially, interact **super-additively on all three datasets**.

This is fundamentally different from:

> stack A+B+C+D, then remove one module at a time.

A normal leave-one-out ablation cannot cleanly establish synergy.

A factorial design can.

---

## S122.4 Their search procedure is itself a cheap-proxy pattern

The full design space begins with 90 candidate configurations.

Task-level successive halving prunes at:
- task 10;
- task 20;
- task 50;

before only the strongest configurations complete the full 100-task horizon.

This is another good example of:

> **cheap early horizon as a selection proxy, full horizon as confirmation.**

But proxy fidelity still needs auditing:
> an early-horizon winner need not preserve rankings at task 100.

The authors' explicit successive-halving procedure makes that risk measurable rather than hidden.

---

## S122.5 New rule

Do not penalize a paper merely because it has multiple modules.

Instead ask:

1. Does each module map to a distinct hypothesized failure source?
2. Is the interaction itself predicted before the final benchmark result?
3. Is there factorial / targeted interaction evidence?
4. Can the full combination beat what additive independent effects predict?
5. Is the composition still understandable when module names are removed?

If yes:
> composition may itself be the scientific contribution.

If no:
> it remains module stacking.

---

# S123 — An SFT loss mask can silently determine later RL exploration

**Don't Mask the Environment: Observation Supervision Changes How Agents Explore Under RL**  
arXiv:2609.20715, Sep 17 2026.

This is one of the strongest last-wave examples for our preferred research taste.

---

## S123.1 The hidden convention

An agent trajectory contains:

\[
a_t,\; o_{t+1},\; a_{t+1},\; o_{t+2}, \ldots
\]

where:
- \(a\) = model action/tool call;
- \(o\) = environment observation.

Standard agent SFT commonly computes loss only on:
> model-authored action tokens.

Environment observations are visible as context but masked from the training loss because:
> the model will not generate them at deployment.

That convention sounds natural.

But it implicitly assumes:

> prediction targets should correspond only to tokens the deployed policy emits.

---

## S123.2 ActObs changes no data, parameters, tokens or forward passes

ActObs simply also supervises the observation tokens already present in the trajectory.

The model is therefore trained to predict:
> what the environment will return after its actions.

This is not a new world-model module.

It is a change in:
> **which existing trajectory tokens count as supervision.**

---

## S123.3 SFT endpoint barely reveals the difference; RL does

After SFT, the methods can look similar.

After the same GRPO stage:
- Qwen3-4B ActObs has higher pass@k at every tested sampling budget on Terminal-Bench 2.0;
- Qwen3-8B trades some pass@1 reliability for higher pass@16 and more distinct solved tasks;
- the advantage transfers to unseen cross-domain code editing on aider-polyglot.

This is particularly important:

> the meaningful effect is not necessarily visible at the stage where the intervention is applied.

The SFT target changes:
> the state from which downstream RL starts.

---

## S123.4 Mechanism: action and observation gradients separate

The paper reports:
- action and observation gradients rapidly become nearly orthogonal;
- action-only SFT leaves a large residual observation gradient;
- environment-prediction ability can fall below the base model;
- joint supervision prevents this one-sided specialization.

During RL, ActObs:
- retains more policy entropy;
- needs less policy movement;
- remains closer to its SFT initialization.

### Causal story

\[
\text{loss masking}
\rightarrow
\text{consequence-model preservation}
\rightarrow
\text{different RL exploration geometry}
\rightarrow
\text{higher pass@k / broader solved-task set}
\]

This is far stronger than:
> "adding another auxiliary loss helps."

The intervention exposes a hidden assumption in a standard recipe.

---

## S123.5 New audit dimension: target masking

For any sequence / trajectory training recipe, ask:

> **Which observed variables are prediction targets, and which are context-only?**

The choice may encode a hidden theory of:
- what knowledge matters;
- what causal consequence the model should internalize;
- what future stage will need.

"Not generated at deployment" does **not** imply:
> "useless as a training target."

---

# S124 — Multimodal systems may need different prediction horizons for different modalities

**Agile-WAM: An Agile Tactile World Action Model for Contact-Rich Robot Control**  
arXiv:2609.20761, Sep 17 2026.

A common multimodal design assumes:
> all modalities can be aligned to the same timestep and predicted with the same temporal target.

Agile-WAM argues that this is physically wrong for vision + touch.

---

## S124.1 Vision and tactile streams evolve at different rates

Adjacent visual frames are often highly similar.

Tactile signals may change abruptly exactly when contact occurs.

Therefore equal next-step prediction horizons can allocate supervision poorly:
- vision target may be too trivial/redundant;
- tactile target must preserve high-frequency contact dynamics.

---

## S124.2 Multi-horizon supervision follows from physical timescale mismatch

Agile-WAM predicts:
- visual latent at a **larger temporal offset**;
- tactile latent at the **next frame**.

The design principle is:

\[
\text{prediction horizon} \propto \text{modality dynamics}
\]

rather than:
> one global horizon for all streams.

Across nine simulated and five real contact-rich tasks, the paper reports improved success with low inference latency.

---

## S124.3 This is not generic "multi-rate modeling"

The scientific object is specific:

> **the supervision horizon should match the information timescale of each modality.**

Different modalities may require distinct:
- sampling rates;
- state lifetimes;
- prediction offsets;
- correction frequencies.

This connects to:
- audio/video realtime models;
- streaming geometry;
- tactile control;

but the physics must be re-derived per domain.

---

# S125 — Structured perception: the basic evidence unit can be a set of observed states, not one observation

**FAMOS: Feed-Forward 3D Articulation Modeling from Sparse Observations**  
arXiv:2609.20817, Sep 17 2026.

Most feed-forward articulation methods infer:
- movable parts;
- joints;
- motion parameters

from one observation.

Under sparse monocular sensing, one view reveals only partial geometry and motion.

That forces the model to rely heavily on:
> category-level shape priors.

FAMOS changes the evidence unit.

---

## S125.1 Multi-state evidence is unordered and partial

Input:
> a sparse, unordered set of partial point clouds from different object states.

The model jointly reasons over them with:
- state-wise attention;
- global cross-state attention.

The target includes:
> the observed articulation span across the supplied states.

### Primitive change

single observation + learned category prior
→ observed motion evidence across multiple partial states.

This is a clean example of changing:
> **what constitutes one training/inference example.**

---

## S125.2 Relation to Panda Diplomacy: domain structure can live below task semantics

**Panda Diplomacy** (arXiv:2609.00611) independently shows a point-cloud self-distillation recipe can pretrain across:
- LArTPC;
- collider TPC;
- water Cherenkov

with minimal detector-specific changes.

Using only 1,000 labeled images downstream, it reports strong label-efficiency gains, and simple probes recover physically meaningful latent structure such as particle causality and track curvature.

The commonality is not "point clouds."

It is:

> **when sensor-level structure is the true shared object, experiment/task-specific architecture may be too high-level a unit.**

FAMOS asks:
> observed state set vs category prior.

Panda asks:
> common sensor geometry vs detector-specific foundation models.

Do not collapse them into one 3D method family.

---

# S126 — Final artifact/freshness corrections

A broad scan must also record what **did not** qualify as a new genealogy.

---

## S126.1 Pelican-Sim: strong consumer evidence, but current artifact maturity is lower than the thesis

Pelican-Sim 1.0 reports:
- a 28-D unified action space;
- numerical + URDF-rendered visual action conditioning;
- sparse MoE;
- four-step generation with 5.67× reported speedup;
- one million real/sim trajectories.

Its downstream results are unusually consumer-oriented:
- 500 generated trajectories added to 50 real demonstrations raise RoboTwin policy success from 70% to 93%;
- simulator policy evaluation correlates at Pearson 0.994 across five checkpoints;
- action-selection and policy-improvement gains are reported.

This is good world-model evaluation design:
> judge the simulator by downstream policy use, not just video metrics.

However, the project page currently marks:
> **Code / Models — Coming soon.**

Therefore:

- thesis value: high;
- current instrument value: **C/D**, not A.

Never count promised artifacts as available ones.

---

## S126.2 General Intuition: strong lineage, no need to invent a new September artifact

General Intuition remains a valuable world-model/action-model taste source through work such as MIRA and its prior game/world-model lineage.

But this final Sep 18–19 scan did not reveal an equally detailed new matched artifact that would justify a separate new genealogy.

Action:
> monitor only.

Company visibility is not evidence of a changed premise.

---

## S126.3 Research-page recency is not paper recency

A company can newly highlight an older research result.

For example, a September research page may surface a paper whose underlying arXiv submission is from February 2026.

Therefore:
> always date the technical artifact itself, not the page that re-promotes it.

This closes the Recency Discipline loop.

---

# S127 — Final additions to canonical taste

The last wave adds five refinements.

## 1. Composition is allowed when interaction is the claim
Do not worship single-knob simplicity.

Good composition:
- distinct causal roles;
- interaction predicted/tested;
- factorial or targeted evidence.

Bad composition:
- add modules until benchmark rises.

## 2. Supervision masks are scientific assumptions
Which parts of a trajectory receive loss can determine what latent consequence model survives into later training.

## 3. Specification source is a first-class variable
Desired behavior may come from:
- instruction;
- tests;
- executable reference;
- demonstration;
- scientific numerical contract;
- user feedback.

These are not equivalent supervision channels.

## 4. Multi-modal time is not automatically one clock
A shared timestamp does not imply a shared information timescale or prediction horizon.

## 5. Runtime-generated parameters are a distinct memory location
Do not collapse:
- context;
- retrieval;
- fast state;
- adapters;
- generated weights;
- base weights.

---

# S128 — Broad scan is now closed for real

This addendum does **not** reopen broad crawling.

The final-wave stopping rule remains:

Future search is triggered only by:
1. a concrete CT candidate;
2. dangerous nearest-prior overlap;
3. a released artifact that materially lowers pilot cost;
4. a trend entering a correction/negative-result phase;
5. an unmistakably changed premise.

No default weekly HF/company sweep.

The calibration goal has been achieved:
> not knowing every new model, but knowing how to identify which new artifacts actually change the scientific problem.
