# Industry Frontier Genealogies 02 — 2026-09-19

> **Status: industrial literature / research-taste calibration only.**
>
> Window: mainly June–September 2026.
>
> This file continues `GENEALOGIES_01.md`.
>
> No CT candidates are generated here.

---

# INDUSTRY GENEALOGY I7 — Static capability → environment learning → experience internalization

This lineage is important because “agent learning” is often used ambiguously.

Recent industry research separates at least three different abilities:

1. **perform from pretrained capability;**
2. **improve while interacting with an environment;**
3. **internalize that experience so improvement persists outside the context.**

These are not the same problem.

---

## I7.1 Static benchmarks measure what the model already knows

Most benchmarks ask:

> Given a fixed task instance, how capable is the model now?

Even interactive agent benchmarks often remain short enough that success is mostly:
- retrieval;
- planning;
- tool execution;
- repeated attempts.

They do not necessarily measure:
> systematic learning across hours of feedback.

---

## I7.2 EdgeBench changes the time scale enough for learning dynamics to become visible [DIRECT]

**ByteDance Seed — EdgeBench, July 2026**

Primary evidence:
- ~38,000 total agent-hours;
- 134 real-world tasks;
- each task supports ≥12h continuous work;
- some extended runs go to 72h;
- recorded human expert effort averages ~57.2h per task.

The benchmark deliberately creates **two feedback loops**:

### Fast inner loop
- compiler/tester/simulator/local data;
- agent can explore repeatedly.

### Slow outer loop
- hidden test;
- expert-style rubric;
- authoritative judge feedback.

The sequence is endogenous:
> the agent's actions determine what feedback it sees next.

This makes the object:
```
score on task
→ trajectory of improvement under feedback
```

---

## I7.3 The headline scaling law is less interesting than the changed quantity

EdgeBench reports:
> aggregate performance follows a log-sigmoid curve as a function of environment interaction time, with very high fitted R² across models/task families.

It also reports:
- early ~6.5h curves forecast later 12h aggregate performance well;
- learning speed across frontier model generations rises quickly;
- progress is not explained only by submission frequency or independent restarts;
- accumulated experience matters.

### Why this is a new industrial/scientific object

Pretraining scaling:
> capability as a function of training data/compute before deployment.

EdgeBench:
> **improvement as a function of post-deployment interaction time.**

This is not ordinary test-time scaling.

The agent is:
- probing;
- receiving feedback;
- editing artifacts;
- preserving/using discoveries.

So the time axis contains **learning**, not just additional samples.

---

## I7.4 The feedback structure matters

The benchmark authors emphasize:

> realistic feedback is necessary to measure learning.

A task with only final binary reward can support repeated search but may not reveal:
- diagnostic interpretation;
- strategy revision;
- incremental improvement.

This suggests a distinction:

```
interaction count
vs
information gained per interaction
```

The environment is not only a source of reward.

It is:
> a teacher with a structured feedback channel.

---

## I7.5 EdgeBench itself is almost maximally expensive for us

Replicating:
- 38k agent hours;
- 134 expert-built tasks;
- 57h mean expert effort/task;
- frontier closed models

is completely unrealistic.

So:
> **EdgeBench is an A-level inspiration / F-level replication source.**

This is exactly why industry reading must separate the two.

---

## I7.6 Sample-Efficient Learning from Agent Experience asks the next, cheaper question [FIELD]

**ByteDance/Monash collaboration, July 23 2026**

Once environment interaction is recognized as expensive, a second problem becomes visible:

> after the agent learns something during a long interaction, how can that knowledge persist after the context is gone?

In-context learning from interaction history is sample-efficient:
- no parameter update;
- rich trial-and-error experience.

But its gain is transient:
> remove the history, remove the gain.

Direct SFT on trajectories may fail to preserve the useful relation.

The paper frames:
> **Experience Distillation**

as a separate operation:
```
experience acquisition
→ in-context improvement
→ internalize useful experience into weights
```

Reported:
- ≥64.8% of ICL gains retained in their tested domains;
- direct SFT ~3.8%;
- at least 9.6× fewer environment samples than classical RL baselines.

---

## I7.7 What changed between EdgeBench and Experience Distillation

This is a [FIELD]/[RECONSTRUCTED] relation, not a claim of direct inspiration.

EdgeBench makes:
> **learning from an environment**

a measurable capability.

Experience Distillation separates:
> **acquiring experience** from **internalizing experience**.

This is a useful research decomposition:

```
Can the agent exploit feedback now?
≠
Can the agent retain what feedback taught it?
```

This relation resembles:
- ICL vs parametric learning;
- working memory vs long-term learning;
- online adaptation vs consolidation.

But those analogies are not the topic.

---

## I7.8 Microsoft Fara → Echoverse provides a parallel environment-learning genealogy [CROSS-COMPANY]

### Fara-1.5
The main bottleneck is:
> collecting computer-use demonstrations is expensive.

Solution stack:
- synthetic/live environments;
- solvers;
- user simulator;
- correctness/efficiency/critical-point verifiers;
- iterative data balancing toward model deficiencies.

### Echoverse
Once scalable environment generation exists, a new observation emerges:
> more shallow environments are not necessarily better.

Environment **behavioral depth**, weakness-targeting, and co-evolution become the object.

So another progression is:

```
scarce demonstrations
→ scalable synthetic environment production
→ environment quantity no longer enough
→ learner-relative environment depth/fidelity
```

---

## I7.9 Qwen-AgentWorld creates a third branch: internalize the environment model itself

Qwen-AgentWorld learns:
> next environment observation conditioned on agent action/history

from >10M interaction trajectories.

It can act as:
- external simulator;
- world-model warm-up for the policy itself.

This splits “environment scaling” into:
1. build executable worlds;
2. evolve synthetic worlds;
3. learn a generative world model.

These should not be collapsed into:
> “synthetic environment is hot.”

The scientific questions are different:
- fidelity;
- controllability;
- transition error;
- transfer;
- learner pressure.

---

## I7.10 What this industrial lineage teaches

The word “experience” itself decomposes:

```
environment interaction
→ feedback
→ transient context learning
→ persistent parameter learning
→ environment/world modeling
```

A future academic question must specify:
> which transfer across these boundaries is being studied.

“Agents learn from experience” is too vague to carry novelty.

---

# INDUSTRY GENEALOGY I8 — Deployment constraint → representation/training objective

Industry is particularly valuable when a physical constraint forces a model-design question.

Three recent examples:
- on-device robotics;
- low-precision agent models;
- embodiment-invariant navigation.

---

## I8.1 Gemini Robotics On-Device 2: adaptation speed becomes the capability [DIRECT]

The July 2026 model card emphasizes:
- local/on-device VLA inference;
- multiple robot types;
- post-training adaptation to novel platforms.

The model card reports much stronger data-scaling curves than the prior On-Device version when adapting to novel embodiments.

Example reported success curves:
- SO101: v2 reaches ~53.3% vs v1 ~6.7%;
- Dexmate: v2 ~75.6% vs v1 ~33.3% at larger adaptation budgets.

### Changed object

Classic robotics model comparison:
> final success on known embodiment.

Frontier deployment requirement:
> **how quickly can the policy adapt to a new embodiment with limited on-robot data?**

So capability becomes a curve:
```
success = f(adaptation data / hours)
```

not one number.

---

## I8.2 This is a deployment-driven changed premise

A cloud model can assume:
- stable hardware;
- centralized inference;
- one interface.

A deployable robot foundation model faces:
- embodiment differences;
- local compute;
- actuator/sensor differences;
- safety controllers.

Therefore the scientific object is not only:
> universal policy representation.

It is:
> **transfer under embodiment shift plus adaptation efficiency.**

This is a real industrial pressure because physical data collection is expensive.

---

## I8.3 Mistral Robostral: representation can factor out embodiment differences [FIELD/CROSS-COMPANY]

Robostral Navigate uses:
- monocular RGB;
- waypoint/image-space pointing.

Rather than predicting:
- robot-specific joint commands;
- depth-dependent map coordinates;

the high-level policy points in image space.

### Representation move

```
robot-specific action/coordinate output
→ embodiment-light perceptual waypoint representation
```

The policy intentionally leaves low-level embodiment conversion downstream.

This is a strong example of:
> **representation choice as a transfer mechanism.**

---

## I8.4 Episode serialization also becomes a training-cost object

Robostral packs whole episodes into training sequences and uses masking to prevent leakage from future/ground-truth actions.

Reported:
> ~22× fewer training tokens.

Again:
> sequence serialization is not merely dataset formatting.

It changes:
- repeated prefix cost;
- what history is visible;
- causal validity.

This echoes:
- OpenAI prefix caching;
- agent context layout;
- packed trajectory training.

---

## I8.5 NVIDIA QAD: low precision becomes a learning problem, not only numerical compression [DIRECT]

Nemotron 3.5 Lightning targets an execution role:
- 30B total / ~3B active;
- long-running agent workloads.

Aggressive NVFP4 quantization introduces quality loss.

NVIDIA's QAD pipeline:
1. creates a quantized student via PTQ;
2. freezes BF16 teacher;
3. uses logit KL distillation to adapt the constrained student.

### Changed abstraction

Traditional quantization:
> approximate weights/activations while preserving output.

QAD:
> **quantization creates a constrained student distribution that can be trained toward a full-precision teacher.**

So a deployment constraint becomes:
> a teacher–student learning problem.

---

## I8.6 The commonality is not “edge AI”

These examples do not share one method.

They share a process:

```
deployment constraint
→ identify what representation/parameterization cannot remain unchanged
→ rewrite the learning target around the constrained system
```

- robot embodiment → portable output representation/adaptation curve;
- low precision → constrained-student distillation;
- on-device compute → local model family.

### Warning

This is **not** a generator:
> find hardware constraint → make paper.

Only constraints that alter the statistical/causal structure of learning are interesting to our taste.

---

# INDUSTRY GENEALOGY I9 — Product usage → evaluation abstraction → training loop

Recent ByteDance/OpenAI/DeepSeek materials converge on a less-discussed point:

> deployment is becoming upstream of evaluation and training.

---

## I9.1 Old linear model-development picture

```
dataset
→ train
→ benchmark
→ deploy
```

Real industrial frontier increasingly looks:

```
deploy
→ observe workflows/failures
→ abstract evaluations
→ reconstruct tasks/environments
→ train/post-train
→ redeploy
```

This changes what an “evaluation” is for.

It is not only:
> compare models.

It is:
> **compress observed product failure into a reproducible training/evaluation object.**

---

## I9.2 Seed2.0: start from user needs, then abstract benchmarks [DIRECT]

Seed2.0 model-card framing explicitly says its process begins with:
- identifying genuine user needs;
- constructing forward-looking evaluation from realistic complex scenarios;
- targeting long-tail knowledge and instruction reliability.

This is product-driven evaluation design.

The scientific rigor of individual abstractions still needs audit.

But the process direction is notable:

```
real workflow
→ abstraction into eval
→ optimization target
```

rather than:
> available benchmark → optimize.

---

## I9.3 Seed2.1 makes the loop explicit [DIRECT]

Seed says:
- internal/external user/developer feedback continuously calibrates optimization;
- real workflows are prioritized alongside static benchmarks;
- Seed2.1 itself participates in:
  - evaluation-system development;
  - capability diagnosis;
  - SFT data synthesis;
  - RL framework optimization.

This creates a recursive production loop:
> the current model helps build the measurement/training infrastructure for the next model.

This parallels OpenAI/Anthropic internal R&D automation observations.

---

## I9.4 DeepSeek converts failures directly into executable environments [CROSS-COMPANY]

V4.1's post-training pipeline reconstructs:
- real interfaces;
- tool context;
- failure conditions;
- difficult coding sessions.

The industrial asset is not only:
> user feedback.

It is the machinery that converts vague feedback into:
> **verified executable tasks.**

That conversion step is under-studied academically because it sits between:
- dataset creation;
- evaluation;
- environment engineering;
- post-training.

---

## I9.5 Microsoft Echoverse closes the loop on environment quality

If environments are generated from model failures, the next question is:
> do generated worlds preserve the property that made the original failure informative?

Echoverse's co-evolution concept effectively treats:
> environment quality as learner-relative.

This creates a full loop:

```
failure
→ environment
→ training
→ new failure distribution
→ environment update
```

---

## I9.6 Why this matters for academic question formation

Many academic studies assume:
> the task distribution is fixed before the model is trained.

Industrial post-training increasingly violates this.

The distribution is:
- adaptive;
- model-relative;
- deployment-derived.

Therefore research objects such as:
- data difficulty;
- benchmark representativeness;
- curriculum;
- synthetic data quality

may need to be defined relative to:
> **a moving policy/model state.**

This connects to academic SFT/distillation genealogy, where supervision quality also became learner-relative.

---

# INDUSTRY GENEALOGY I10 — More interaction time → predictable improvement, but not all time is equivalent

EdgeBench's headline could easily be misread as:

> give agents more hours.

That is not the full finding.

---

## I10.1 Environment-time is not ordinary inference-time compute

Test-time scaling:
> more samples/search at fixed task knowledge.

Environment learning:
> each action changes what the agent knows.

So:
```
more tokens / samples
≠
more informative interaction time
```

Two agents can spend the same 12h and acquire different reusable knowledge.

---

## I10.2 Two-loop feedback creates different information rates

Fast local loop:
- cheap;
- frequent;
- possibly overfittable.

Slow hidden/judge loop:
- authoritative;
- sparse;
- less exploitable.

The combined trajectory resembles:
> exploration under multi-fidelity feedback.

This structure matters to the scaling curve.

A future small scientific study would need to distinguish:
- wall time;
- number of attempts;
- number of submissions;
- feedback entropy/information;
- accumulated reusable state.

---

## I10.3 EdgeBench already observes harness-level differences

The paper reports harness ablations and notes:
> weak scaffolding can make a capable model stop progressing,
while stronger mechanisms keep it actively improving.

This means measured “learning speed” is not purely model-intrinsic.

Again:
```
model × environment × harness
```
defines the learning curve.

That echoes industry genealogy I3.

---

## I10.4 The most interesting academic abstraction may be learning efficiency, not benchmark score

If post-deployment learning follows structured trajectories, a new quantity becomes relevant:

> **how much durable improvement is extracted from a unit of feedback?**

That could be measured in:
- score gain / authoritative feedback;
- reusable discovery / environment interaction;
- retained gain after context removal;
- transfer to new task after experience.

This is conceptually richer than:
> success@12h.

But it is not yet a candidate.

---

# 11. Cross-genealogy convergence after I7–I10

Recent industry work independently pushes several “relations” to the foreground.

---

## Relation 1 — capability vs adaptation

On-device robotics:
> final success ≠ adaptation efficiency.

EdgeBench:
> initial score ≠ learning speed.

Distillation:
> temporary in-context gain ≠ retained capability.

So deployed intelligence increasingly has:
> **a dynamic axis.**

---

## Relation 2 — information availability vs information internalization

Agent context:
> contains experience.

But:
- can model use it?
- can model compress it?
- can it persist?
- does parameter learning preserve it?

This relation appears in:
- experience distillation;
- context compaction;
- memory/state management;
- long-running research agents.

---

## Relation 3 — realistic environment vs useful learning environment

Qwen-AgentWorld / Echoverse / DeepSeek:
> realism alone does not define training value.

Useful environments must:
- expose relevant failure;
- provide valid feedback;
- avoid shortcut contamination;
- target current learner weaknesses.

---

## Relation 4 — deployment constraint vs learning target

Low precision / embodiment / on-device compute:
> constraint changes what representation/objective is useful.

This is stronger than:
> “make model smaller.”

---

# 12. Current industry-reading warning

Industrial reports make one temptation stronger:

> everything appears to become an agent problem.

That is an artifact of current product investment.

Do not let this bias the academic search.

Use these sources to learn:
- changed regimes;
- hidden variables;
- real bottlenecks.

Then return to the full academic genealogy library before generating any seed.

