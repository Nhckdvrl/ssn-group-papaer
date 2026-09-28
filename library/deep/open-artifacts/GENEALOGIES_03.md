# Startup & Hugging Face Genealogies 03 — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues:
> - GENEALOGIES_01.md
> - GENEALOGIES_02.md
>
> This batch focuses on four things that recent startup/open-lab reports expose unusually well:
>
> 1. **the orchestration layer becoming a learned model rather than infrastructure;**
> 2. **world/interface models redefining what an executable environment is;**
> 3. **robot pretraining being judged by a new adaptation mode rather than only fine-tuning efficiency;**
> 4. **negative training results becoming first-class technical evidence.**
>
> As before:
> - company/model names are not topic generators;
> - public benchmark claims are not taken as causal evidence by themselves;
> - the main goal is to reconstruct the problem-forming move.

---

# S25 — Model selection → learned cognition allocation

Recent model-routing systems are easy to misread as:
> "use a cheaper model for easy questions."

Sakana Fugu is a stronger lineage than that.

---

## S25.1 Parent: heterogeneous model ecosystems already create specialization

By 2026 the model ecosystem is not one scalar ranking.

Different models specialize in:
- coding;
- visual reasoning;
- long-context work;
- fast execution;
- expensive deep reasoning;
- specialist domains.

A fixed workflow therefore faces a new question:

> **which cognitive machinery should be activated for this query and at which stage?**

Historically this is handled by:
- manual routing;
- heuristics;
- benchmark-specific ensembles;
- fixed multi-agent graphs.

---

## S25.2 TRINITY / Conductor → Fugu [DIRECT]

Fugu explicitly builds on two ICLR 2026 Sakana research lines:

### TRINITY
A compact coordinator selects worker models / roles.

### Conductor
A model learns:
- communication topology;
- worker instructions;
- collaboration structure.

Fugu productionizes this into an orchestrator language model.

The orchestrator does not simply output an answer.

It constructs a task-specific scaffold over a model pool.

Primitive change:

\`\`\`
routing = systems configuration
→ routing/orchestration = learned policy
\`\`\`

---

## S25.3 Fugu and Fugu-Ultra expose two different coordination objects [DIRECT]

The June technical report separates:

### Fugu
Optimized for interactive latency.

The orchestration decision is deliberately narrowed:
- lightweight head;
- select one worker;
- avoid expensive role/topology search.

### Fugu-Ultra
Optimized for difficult tasks.

It can:
- select multiple workers;
- decompose work;
- maintain communication topology;
- preserve which agent emitted a function call;
- route tool results back to the correct worker;
- maintain orchestration state across the workflow.

So "orchestrator" itself contains at least two regimes:

\`\`\`
model selection
vs
workflow synthesis / stateful coordination
\`\`\`

They should not be conflated.

---

## S25.4 September Fugu Max / Ultra v2 turns the objective into a Pareto problem [DIRECT]

Sakana's September release explicitly separates:

### Fugu Max
> capability subject to aggressive cost efficiency.

### Fugu Ultra v2
> maximize difficult-task capability with deeper orchestration.

This changes the product/research object from:

\`\`\`
find best model
\`\`\`

to:

\`\`\`
learn a policy over a capability × cost frontier
\`\`\`

This is conceptually closer to resource allocation/control than ordinary model ensembling.

---

## S25.5 Why this is not automatically a good small-team topic

The most interesting Fugu behaviors depend on:
- a heterogeneous model pool;
- API costs;
- model availability;
- task distribution;
- tool runtime;
- orchestration state.

A tiny benchmark router can easily become a toy version of the production problem.

So the useful research pressure is not:
> "train a router."

It is:
> **what information is sufficient to allocate cognitive resources across heterogeneous models/workflow stages?**

That question still requires a separate academic novelty audit.

---

## S25.6 Saturation warning

By September 2026:
- OpenAI routing;
- NVIDIA Switchyard;
- Sakana Fugu;
- model routers in coding products;
- effort-controlled model families

already make "model routing" a crowded surface.

New work needs a deeper object such as:
- state sufficiency;
- routing under uncertainty;
- delayed value of a model choice;
- workflow-stage dependence;
- calibration of cost vs capability;
- model-switch state loss.

Again: these are decomposition axes, not candidate suggestions.

---

# S26 — Code/UI as executable state → generated interface as world state

Runway Solaris is scientifically useful because it shifts "world model" away from physical video.

Primary:
- arXiv:2609.00776
- Runway research release, September 2026.

---

## S26.1 Old software abstraction: behavior is specified before execution

Traditional interfaces rely on an intermediate symbolic representation:
- HTML/CSS/JavaScript;
- Swift/UIKit;
- React;
- explicit state machines;
- view hierarchy;
- event handlers.

The system's possible behaviors are largely encoded in advance.

Generative UI systems often still preserve this abstraction:
> LLM writes code → runtime executes code.

---

## S26.2 Solaris removes the intermediate representation [DIRECT]

Solaris instead models:

\`\`\`
current visual interface + user action
→ next visual interface state
\`\`\`

Mouse interactions are conditioning signals.

The interface is synthesized frame by frame.

No application-specific DOM/state-machine/code representation is required as the immediate generated object.

Primitive change:

\`\`\`
generate program that renders an interface
→ directly model interface transition dynamics
\`\`\`

This makes the software UI itself a kind of world.

---

## S26.3 Real-time world modeling exposes compounding-state error

Solaris combines:
- autoregressive frame generation;
- few-step distillation;
- training on its own outputs.

Why train on its own outputs?

Because interactive deployment creates:

\`\`\`
model-generated state_t
→ action
→ model-generated state_{t+1}
\`\`\`

rather than repeatedly conditioning on clean ground truth.

The model must therefore survive its own state distribution.

This is the same structural pressure seen in:
- autoregressive world models;
- long-horizon agents;
- simulator rollouts.

But the error modes are different.

In interfaces:
- text drift;
- hallucinated confirmation states;
- visual inconsistency;
- broken interaction semantics

are especially damaging.

---

## S26.4 Solaris separates high-level intent from low-level rendering

The system includes a language-model component that interprets:
- user intent;
- desired interaction behavior;

while the visual world model generates the interface state.

This creates another fast/slow or symbolic/generative split:

\`\`\`
semantic intent
→ visual-state transition
\`\`\`

The interesting design question is not "LLM + video model."

It is:
> **which aspects of interface behavior need explicit semantic control and which can be generated as learned dynamics?**

---

## S26.5 UI is a harsher world-model contract than cinematic video

A visually plausible world-model error can be tolerable in a demo.

An interface has semantic commitments:
- a button label must remain stable;
- a form state should correspond to actual action history;
- confirmation should mean something happened;
- text must stay exact.

Thus Solaris illustrates a general principle:

> **downstream contract determines which generative errors are catastrophic.**

This connects to the renderer/simulator/planner taxonomy, but the domain creates a new contract:
> interactive state semantics.

---

## S26.6 Artifact value

Solaris itself is not a cheap research instrument:
- no public weights;
- no public training pipeline.

So:
> technical-thesis value high, execution transferability low.

Do not let an impressive research preview become a false small-team project template.

---

# S27 — Robot pretraining value: initialization → adaptation mode

Skild S1 makes an unusually explicit argument about what foundation pretraining should be judged by.

Primary:
- Skild AI, "Introducing S1: In-Context Learning for Robotics", August 2026.

---

## S27.1 Changed premise comes from a negative comparison

Skild's starting point is not:
> robot foundation models are great.

It points to a problem:

> when downstream demonstrations become sufficiently dense, a task-specific model trained from scratch can approach the peak performance of a post-trained foundation model.

If pretraining only buys:
> fewer task-specific examples before fine-tuning,

then enough downstream data can erase the distinction.

That creates a much stronger question:

> **what capability should expensive pretraining create that task-specific training cannot simply catch up to?**

---

## S27.2 S1 answer: change the adaptation mechanism

S1 is pretrained so the task itself is provided through:
> one video demonstration in context.

No weight update is required for the new task.

Thus foundation-model value becomes:

\`\`\`
better parameter initialization
→ ability to infer a new task at inference time
\`\`\`

Skild explicitly compares this to:
> the transition from application-specific fine-tuning toward in-context learning in language models.

The analogy may be imperfect, but the changed adaptation object is clear.

---

## S27.3 Demonstration video becomes the task representation

The prompt must convey:
- demonstrator intent;
- functional correspondences;
- object roles;
- ordering;
- progress;
- new atomic behavior.

The task is not a class ID.

It is a structured trajectory.

Therefore:

\`\`\`
task specification = label/language instruction
→ task specification = behavioral demonstration
\`\`\`

This is a deeper change than "video-conditioned VLA."

---

## S27.4 Long horizon makes ICL qualitatively harder

S1 emphasizes tasks up to around 10 minutes.

This introduces:
- dozens of manipulation stages;
- progress tracking;
- recovery;
- context-action correspondence across changing scenes.

So robotic ICL is not simply nearest-neighbor imitation from one clip.

The model must infer a persistent task program from context.

---

## S27.5 Company-reported scaling result changes the adaptation economics

Skild reports that one in-context demonstration on its tested unseen long-horizon tasks reaches a performance point requiring hundreds of post-training demonstrations for the comparison VLA.

Even if the exact ratio is setting-specific, the research object is important:

\`\`\`
adaptation curve over post-training data
vs
adaptation from context only
\`\`\`

This is more informative than one final success number.

---

## S27.6 Deployment pressure caused the research question

Skild's later deployment post explicitly argues that real commercial deployment exposed the problem:
- tasks/layouts change;
- repeated data collection/fine-tuning does not scale;
- demo quality is not deployment reliability.

This is an excellent industry→science pattern:

\`\`\`
deployment friction
→ question the assumed role of pretraining
→ redefine desired capability
\`\`\`

not:

\`\`\`
product wants feature X
→ build feature X.
\`\`\`

---

# S28 — Robotics adaptation is already splitting into several channels

Physical Intelligence provides an important contrast to S1.

The field should not collapse all fast adaptation into "ICL."

---

## S28.1 Multi-Scale Embodied Memory

MEM separates:
- short-term detailed visual memory;
- long-term abstract semantic/task memory.

The problem is that one fixed observation-history representation cannot simultaneously optimize:
- local occlusion recovery;
- multi-stage progress memory.

Primitive change:

\`\`\`
history = one context window
→ history = multiple memory timescales with different abstraction
\`\`\`

---

## S28.2 RL Token

RL Token targets a different adaptation mechanism.

The large VLA remains mostly frozen.

A compact learned representation is exposed as an RL token.

Small actor/critic components perform online RL on this bottleneck.

The key question is:

> **what information must a foundation model expose to make rapid control adaptation possible without updating the full model?**

This is not the same as:
- ICL;
- memory;
- LoRA fine-tuning.

---

## S28.3 π0.7 steerability

π0.7 explores another channel:
- language coaching;
- metadata/desired execution style;
- intermediate visual subgoals;
- cross-embodiment conditioning.

Here adaptation is:
> steering a fixed generalist policy through richer context/conditioning.

So current robotics has at least:

1. in-context task induction;
2. memory-based state adaptation;
3. online RL adaptation;
4. conditional policy steering;
5. weight fine-tuning.

"fast adaptation" is now scientifically under-specified.

---

# S29 — Negative-result preservation: startup technical reports can be more useful than final-model papers

Recent open technical reports increasingly state:

> we tried the obvious choice and it was worse.

This is extremely valuable for research taste.

ZONOS2 is a strong example.

---

# S29.1 ZONOS2: importing LLM MoE assumptions into audio breaks

ZONOS2 uses:
- autoregressive delayed RVQ audio tokens;
- sparse MoE;
- only ~900M active out of 8B total.

But the report openly says:
> expert balancing was substantially more unstable on delayed audio tokens than on text under comparable settings.

Router entropy could collapse.

They had to:
- make the first three layers dense;
- make the final layer dense;
- use top-2 on the last MoE block;
- manually adjust balancing/router learning rates.

The authors do not pretend they fully understand why.

They speculate about:
- noisy/difficult delayed DAC prediction;
- high-rate audio vs low-rate text alignment;
- other audio statistics.

### Research-taste value

A cross-domain architecture transfer creates a new failure.

The useful question is not:
> "MoE works for audio too."

It is:
> **which statistical property of the new token stream breaks an assumption learned from text?**

That is a much better scientific pressure.

---

# S29.2 GQA is faster but worse in early ZONOS2 ablations

The report says:
- MHA was significantly more stable and produced higher-quality outputs;
- GQA was still chosen for inference speed.

This is an unusually honest industrial design trade-off.

The selected architecture is not:
> best on one modeling metric.

It is:
> best acceptable point under production latency constraints.

Therefore reverse-engineering a product architecture as if each component were statistically optimal can be wrong.

Some choices are:
> Pareto compromises.

---

# S29.3 Speaker embedding: more information creates a shortcut

ZONOS2 uses a high-bandwidth speaker embedding for cloning.

But it also contains:
- duration;
- background/acoustic conditions;
- lexical content;
- pause timing.

During training, the model can exploit these target-specific cues.

The report observed failure modes including:
- silent output;
- glossolalia/babble.

So:

\`\`\`
richer conditioning representation
→ more desired speaker information
\`\`\`

also implies:

\`\`\`
richer conditioning representation
→ more shortcut leakage
\`\`\`

This is a classic information-bottleneck problem forced by deployment.

---

# S29.4 The repair is representation filtering + staged training

ZONOS2 uses:
- LDA to preserve between-speaker information while reducing within-speaker nuisance variation;
- random crop of target audio;
- loss masking over the crop;
- acoustic augmentation;
- two-stage annealing.

The key mechanism is not "LDA is good."

It is:

> **the conditioning channel contains both the causal variable we want and target-specific shortcuts we do not.**

The method attempts to reduce the shortcut bandwidth.

This pattern is highly transferable conceptually across modalities.

But it must not become:
> "apply LDA elsewhere."

---

# S29.5 Raw bytes beat phonemization only after scale changes the trade-off

ZONOS2 also reports another changed premise.

Phonemes give a useful early inductive bias.

But the G2P pipeline introduces silent failures:
- code-switching;
- proper nouns;
- low-resource languages;
- technical vocabulary.

At sufficient model/data scale, byte-level input catches up and surpasses the phoneme variant while eliminating the preprocessing failure class.

So:

\`\`\`
strong handcrafted inductive bias
is useful at low scale
but can become an error bottleneck at high scale.
\`\`\`

This is a very important architecture/data lesson:

> an inductive bias can move from advantage to liability as learner/data capacity changes.

---

# S30 — Orchestrator model vs self-modifying harness: two different answers to system complexity

Recent startup work can easily be flattened into:
> "multi-agent systems."

That hides a real disagreement.

---

## S30.1 Sakana Fugu: learn which external intelligence to activate

State being adapted:
- worker selection;
- topology;
- worker roles;
- decomposition.

The pool of models remains largely external.

Core operation:
> allocate computation across agents/models.

---

## S30.2 Prime / Continual Harness / RHI: learn the scaffold itself

State being adapted:
- prompts;
- skills;
- memory;
- subagent definitions;
- information flow.

Core operation:
> rewrite the persistent orchestration substrate.

---

## S30.3 MiniMax-style self-evolution: modify the machinery that creates future runs

State can include:
- scaffold code;
- evaluation/training scripts;
- experiment setup.

Core operation:
> outer-loop system modification.

---

## S30.4 These approaches differ in where learning lives

\`\`\`
weights
vs
router/orchestrator
vs
harness artifact
vs
outer-loop code
\`\`\`

The generic label "agent self-improvement" is now almost meaningless.

A serious paper must identify:
> which state is updated, what feedback updates it, how persistence works, and where failure/rollback occurs.

---

# S31 — Open model cards should preserve failure provenance

A new scan priority follows from ZONOS2 / Instella / Continual Harness / OpenWAM.

High-value artifacts do not only show:
> final winning recipe.

They expose:
- failed architecture choice;
- specialization regression;
- capability floor;
- scale boundary;
- train/inference mismatch;
- proxy failure.

This creates a new criterion.

---

## Failure-Provenance Value

For every model card / report, ask:

1. What obvious baseline failed?
2. At what scale did it fail?
3. What metric/trace exposed the failure?
4. Did the authors identify a mechanism or only patch it?
5. Does the failed checkpoint/config remain public?
6. Can the failure be reproduced cheaply?
7. Did the final method directly target it?

A paper with strong failure provenance can be a better source of research ideas than a larger final SOTA release.

---

# S32 — Current startup/open-lab source types are now visibly different

The startup/HF track should no longer be one bucket.

## Type A — Technical-thesis lab
Examples:
- Thinking Machines
- Sakana
- Kyutai
- InclusionAI

Value:
> clear structural hypothesis.

## Type B — Open training-stack lab
Examples:
- ZGCM
- AMD Instella
- OpenBMB
- Arcee

Value:
> staged artifacts, recipes, logs, code.

## Type C — Deployment-pressure startup
Examples:
- Skild
- Physical Intelligence
- H Company
- Poolside

Value:
> real-world constraints expose wrong academic assumptions.

## Type D — World/simulation startup
Examples:
- World Labs
- Runway
- General Intuition
- ACE Robotics

Value:
> new downstream contracts for generative models.

## Type E — Domain foundation-model lab
Examples:
- Zyphra audio/EEG
- EXAONE/Xiaomi tabular
- Tabby time series
- Cohere small specialist releases

Value:
> clean non-LLM basic-object changes.

Future scans should deliberately sample all five.

---

# S33 — Updated artifact-selection heuristic

A recent startup/HF artifact deserves deep reading when at least one is true:

### 1. It exposes a changed premise
Example:
> robot pretraining should produce ICL, not only a better fine-tuning initialization.

### 2. It publishes a failure and the repair
Example:
> IF-RL hurts reasoning → multi-teacher repair.
> speaker embedding leaks target information → bottleneck/staged conditioning.

### 3. It changes the unit of computation/state
Example:
> interface transition instead of code;
> tabular cell/feature interaction instead of early row compression;
> harness artifact instead of fixed scaffold.

### 4. It contains a cheap matched experiment
Example:
> sequential vs shuffled checkpoints;
> base/SFT/RL stages;
> precision pairs;
> tiny/large mechanism-faithful models.

### 5. Deployment introduces a variable absent from benchmarks
Example:
> adaptation latency;
> cache lifetime;
> persistent world state;
> real interaction timing.

If none of these is present and the model card is mainly:
- parameter count;
- leaderboard score;
- generic "agentic";
- generic 1M context;

it stays monitor-only.

---

# S34 — Current conclusion

The strongest pattern from this batch is not:
> startups are more creative than incumbents.

It is:

> **smaller/open research organizations often leave the conceptual seams visible.**

Large frontier systems hide many decisions inside one recipe bundle.

High-value startup/open artifacts often expose:
- the failed assumption;
- the intermediate checkpoint;
- the deployment constraint;
- the minimal repair;
- the lower-scale proxy.

That makes them unusually good for learning how research questions are formed.

The practical workflow becomes:

\`\`\`
frontier pressure
→ startup/open-lab thesis
→ public failure/artifact pair
→ academic genealogy
→ cheap diagnostic
→ only then decide whether training is necessary
\`\`\`

Still no formal candidate generation.
