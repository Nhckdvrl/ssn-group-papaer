# Industry Frontier Genealogies 03 — 2026-09-19

> **Status: industry literature / research-taste calibration only.**
>
> Recent-window focus: May–September 2026, with older parents only where they explain a changed industrial regime.
>
> This file does not generate CT candidates.
>
> Main question:
>
> > **What training objects become visible only when frontier models are trained/deployed as long-horizon, multi-effort, multi-scaffold systems?**

---

# INDUSTRY GENEALOGY I11 — Reasoning effort: from inference knob to trained conditional policy

A recurring 2026 product surface is:

> low / high / max / extended reasoning effort.

It would be easy to treat this as an API feature.

Kimi K3 shows that, at least in one frontier open model, effort is deeply entangled with post-training.

---

## I11.1 Previous abstraction: inference-time compute is chosen outside the policy [FIELD]

Academic test-time scaling often starts from a trained model and varies:
- number of samples;
- generated reasoning length;
- search depth;
- token budget.

The model is relatively fixed.

The controller chooses:
> how much compute to spend.

Even when the model responds to budget prompts, effort can appear like an external decoding control.

---

## I11.2 Kimi K3 makes effort a training dimension [DIRECT]

**Kimi K3: Open Frontier Intelligence (July 2026)**

K3 explicitly trains RL experts across:

### Three domains
1. general tasks;
2. general agents;
3. coding agents.

### Three effort levels
- low;
- high;
- max.

This yields:
> nine domain × effort expert policies.

The final unified model is then obtained through:
> Multi-Teacher On-Policy Distillation (MOPD).

### Changed object

```
effort = external inference budget
→ effort = policy-conditioned behavior learned during RL
```

This is much stronger than:
> “prompt the model to think less.”

---

## I11.3 Effort is trained relative to each problem, not a universal token count [DIRECT]

K3 does not impose one fixed low/high/max length.

For each problem (x), it estimates an initial budget:
> (b_0(x)) from the cold-start model.

A trajectory receives reward −1 when total token use exceeds:
> (	au cdot b_0(x)).

Training proceeds curriculum-style:
- first relatively generous max effort;
- then reduce (	au);
- obtain high- and low-effort experts.

### Important scientific distinction

```
absolute token budget
vs
problem-relative compute budget
```

Low effort on an intrinsically hard problem need not equal low effort on an easy one in absolute tokens.

This makes:
> **effort a conditional resource policy.**

---

## I11.4 The final model is not one expert with a knob; it is a distilled composition [DIRECT]

The nine specialized experts produce trajectories at different effort levels.

MOPD samples:
- domain (d);
- effort (e);

and guides the unified student with the corresponding teacher.

So the model's effort control is formed by:
> **consolidating separately optimized policies.**

This raises a useful general question for research taste:

> when one model exposes a continuous/discrete control knob, is the underlying capability actually one policy smoothly conditioned on the knob, or a consolidation of qualitatively different specialists?

This is not a candidate.
It is an interpretation audit for future model cards.

---

## I11.5 Effort also enters the serialization contract [DIRECT]

K3's chat template includes reasoning effort as a global option message before input messages.

The report says:
- tool declaration and effort are global session options;
- changing them invalidates the KV cache anyway;
- one-shot request options are placed later so they do not invalidate reusable history.

So effort has three simultaneous roles:

1. **training target**
2. **generation constraint**
3. **cache/layout variable**

This is a textbook example of model/system co-design.

Academic work may study only role 1 or 2.

Production must respect all three.

---

## I11.6 Cross-company convergence, but mechanism remains opaque [CROSS-COMPANY]

Other 2026 frontier systems also expose effort:
- Anthropic effort controls;
- Gemini Flash effort;
- OpenAI reasoning/model tiers;
- Tencent Hy3 no-think/low/high;
- Grok-style reasoning levels.

Independent convergence tells us:
> effort is operationally valuable.

It does **not** tell us:
> all companies implement effort the same way.

K3 is valuable precisely because its report exposes one concrete training construction.

---

## I11.7 What not to infer

Wrong:
> low/high/max is a universal latent scalar.

Wrong:
> token count is the scientific quantity.

Wrong:
> effort-control research is open because products expose a knob.

The literature is already crowded.

The industrial lesson is:
> **resource-control semantics can be trained, distilled, serialized, and served as one coordinated object.**

---

# INDUSTRY GENEALOGY I12 — Long-horizon RL changes the meaning of an “iteration”

Classic RL training diagrams quietly assume:

> rollout batch is generated → batch completes → optimize → next iteration.

Frontier agent trajectories break this temporal assumption.

---

## I12.1 Kimi K3: ultra-long trajectories create stragglers [DIRECT]

K3's agentic environments may involve:
- hundreds/thousands of tool calls;
- millions of accumulated context tokens.

Waiting for every trajectory in a rollout batch creates:
> severe long-tail latency.

So K3 uses **partial rollouts**.

Generation pauses once only a fraction of trajectories finish.

Policy optimization proceeds.

Unfinished trajectories are:
- preserved;
- resumed at the next iteration.

### Changed training object

```
trajectory belongs to one policy iteration
→ one trajectory can span multiple policy iterations
```

This creates intentional policy staleness.

---

## I12.2 Stale data stops being an accident and becomes a designed regime [DIRECT]

K3 explicitly notes:
> partial rollout makes individual long-horizon trajectories span multiple iterations, introducing highly stale data.

Instead of eliminating this stale data, their optimization is designed to tolerate it using per-token regularization that constrains updates to a localized neighborhood.

### Important conceptual change

Academic RL often treats off-policy/stale rollout as:
> deviation from ideal on-policy optimization.

Here:
> **staleness is the price paid to make the target task distribution computationally feasible.**

The optimization algorithm must be robust to the systems decision.

This reverses the usual causal order:
```
algorithm defines data regime
```
becomes:
```
real trajectory-time distribution forces a new optimization regime
```

---

## I12.3 Persistent model state requires persistent environment state [DIRECT]

A paused rollout cannot be resumed with model tokens alone.

K3 preserves:
- external KV state;
- sandbox state;
- microVM state;
- tool/environment context.

For 1M-context rollouts, a prefix miss is extremely expensive.

The system therefore maintains an external KV pool and resumable sandboxes.

### New compound state object

```
RL state
= policy text history
+ model KV state
+ external environment/sandbox state
```

Long-horizon agent RL is not merely:
> token sequence RL.

Its state is distributed across model and environment infrastructure.

---

## I12.4 MiniMax Forge encounters the same long-tail problem, but solves a different boundary [CROSS-COMPANY]

**MiniMax M2 Series (May 2026, direct parent to current M2.7)**

Forge reports trajectory completion times ranging:
> seconds → hours.

Two naive schedulers create opposite pathologies:

### Strict FIFO
Pros:
- preserves generation order / distributional consistency.

Cons:
- head-of-line blocking;
- cluster idle time.

### Greedy “use anything completed”
Pros:
- high throughput.

Cons:
- short/easy trajectories are disproportionately consumed early;
- training distribution becomes biased.

MiniMax's **Windowed FIFO** permits reordering only inside a sliding queue window.

So the scheduler interpolates between:
- throughput;
- distributional fidelity.

### Changed object

```
scheduler = systems throughput policy
→ scheduler = training-distribution policy
```

This is a high-value industrial lesson.

---

## I12.5 Kimi and MiniMax reveal two different forms of “asynchrony”

Kimi:
> unfinished trajectory persists across policy updates.

MiniMax:
> completed trajectory consumption order is selectively reordered.

Both arise from long-tail rollout time.

But the statistical consequences differ:

### Kimi
- policy staleness;
- off-policy trajectory continuation.

### MiniMax
- sample-order / difficulty bias.

Therefore generic:
> “async RL”

is scientifically under-specified.

A real question must say:
> what temporal mismatch is introduced and what distribution/objective it changes.

---

## I12.6 Prefix-tree merging: long-horizon RL has a repeated-prefix training structure [DIRECT]

MiniMax observes:
> multiple completions in the same rollout group share long prefixes.

Independent training redundantly recomputes them.

Prefix-tree merging computes the shared prefix once, branches for completion-specific suffixes, then recovers per-sample losses.

The report claims:
> exact equivalence to independent forward computation and up to ~40× training acceleration in its setting.

### Research-taste lesson

The trajectory data distribution itself contains exploitable computation structure.

This is not:
> approximate compression.

It is:
> exact computation factorization induced by shared causal history.

The same “shared prefix” structure appears in inference caching, but the training operation is different.

---

## I12.7 Long-horizon training creates a three-way optimization problem

Frontier systems must jointly manage:

1. **statistical fidelity**
   - freshness;
   - sample order;
   - on/off policy.

2. **trajectory completeness**
   - long tasks cannot be cut arbitrarily.

3. **hardware utilization**
   - stragglers waste accelerators.

This is not well captured by standard:
> RL algorithm comparisons at fixed rollout infrastructure.

Again:
> systems choices can alter the actual training distribution.

---

# INDUSTRY GENEALOGY I13 — Agent data moves from answer supervision to executable artifact supervision

Kimi, MiniMax, DeepSeek, Tencent and Microsoft repeatedly converge here.

The common change is not simply:
> “agent data is harder.”

It is:
> **the target of supervision becomes an executable artifact/workflow rather than a textual answer.**

---

## I13.1 MiniMax: artifact-aligned reward [DIRECT]

MiniMax M2 data pipelines create training tasks with:
- executable workspaces;
- verifiable outputs;
- artifact-aligned rewards.

For knowledge-worker office tasks, the pipeline:
- constructs real supporting documents;
- defines expected deliverables;
- uses multi-axis rubrics;
- cleans fabricated references/entities;
- grounds synthetic tasks in realistic professional artifacts.

### Changed target

```
response text quality
→ artifact correctness under an executable workspace
```

This changes what training data must contain.

---

## I13.2 Kimi K3: professional output and long workflow are first-class RL domains [DIRECT]

K3's training environments explicitly include:
- professional knowledge work;
- office deliverables;
- software engineering;
- kernel optimization;
- web development;
- vision-in-the-loop tools;
- persistent assistant workflows.

Their agentic reward model follows a mandatory protocol:
1. inspect outcome/product/text;
2. generate a rubric;
3. score candidates against the rubric;
4. record scores.

It additionally imposes output-budget controls to limit verbosity reward hacking.

### Changed evaluator role

The evaluator no longer scores:
> one answer string.

It must understand:
> a produced artifact / workflow outcome.

---

## I13.3 Tencent Hy3 closes the loop with product teams [CROSS-COMPANY]

Tencent Hy3 reports:
- feedback from 50+ products after the April preview;
- scaled post-training with higher-quality data;
- specific fixes for tool-call/output reliability;
- hallucination/fact-conflation;
- multi-turn intent retention.

It also evaluates scaffold robustness across:
- CodeBuddy;
- Cline;
- KiloCode;

reporting a relatively small variance on SWE-Bench Verified.

### Why this matters

The product complaint is often not:
> “benchmark score too low.”

It is:
- tool call breaks;
- output format violates contract;
- long intent drifts;
- evidence is fabricated.

These properties are **interface/workflow correctness**.

So post-training targets production failure modes that may be underweighted in academic benchmark averages.

---

## I13.4 Data pipeline increasingly mirrors production task structure

The sequence becomes:

```
real workflow
→ executable workspace
→ artifact specification
→ agent trajectory
→ verifier/rubric
→ post-training
```

This is a richer object than:
> instruction + answer pair.

It makes the verifier/environment part of the data schema.

---

## I13.5 But this is a huge engineering trap for academia

A small team can easily decide:
> “Let's build realistic office/coding environments.”

Then spend months on:
- data synthesis;
- containerization;
- verifiers;
- rubric bugs;
- UI/tool wrappers.

The industrial material is useful as pressure evidence.

A viable academic question must isolate one relationship without recreating the whole pipeline.

---

# INDUSTRY GENEALOGY I14 — From “general multimodal understanding” to action-centric world understanding

Tencent Hy-Embodied provides a useful contrast to generic VLM scaling.

---

## I14.1 Generic VLM taxonomy is observation-centric [FIELD]

Standard multimodal benchmarks emphasize:
- object recognition;
- OCR;
- spatial relation;
- chart/document understanding;
- visual QA.

For embodied agents, that taxonomy may not match the downstream action loop.

A robot needs to know:
- what state matters for action;
- what an action changes;
- what to do next after the world changes.

---

## I14.2 Hy-Embodied explicitly reorganizes capability around action [DIRECT]

**Hy-Embodied-VLM-1.0 (July 2026)**

Tencent defines three progressive capability classes:

1. **Action-Relevant State Understanding**
   - what state is relevant to acting?

2. **Action–Transition Reasoning**
   - what action should happen, and what will it change?

3. **Sequential and Adaptive Reasoning**
   - long-horizon planning, reflection, repair, recovery.

The taxonomy then drives:
- data mixture;
- pretraining;
- post-training;
- evaluation.

### Changed object

```
vision-language understanding
→ state / action / transition / adaptation
```

This is not only “add robotics data.”

It changes what counts as useful visual knowledge.

---

## I14.3 Deployment efficiency is co-equal with physical reasoning [DIRECT]

The model:
- ~30B total;
- ~3B active/token;
- is designed for latency-sensitive physical-world deployment.

Compared with the previous generation with much more active computation, it targets similar/stronger embodied performance with much lower activation.

This reflects a physical-system constraint:
> a robot cannot treat cloud-scale latency as incidental.

So capability taxonomy and compute architecture are developed together.

---

## I14.4 Self-evolving post-training introduces multiple reward semantics [DIRECT]

Tencent describes:
- RL + rejection-sampling fine-tuning loop;
- a final reward-specialized stage;
- continuous-reward and discrete-reward RL policies trained separately then fused.

The stated motivation includes both:
- geometric precision;
- decision/planning/reflection quality.

### Research-taste observation

Physical action mixes:
> continuous geometric quality
and
> discrete task/decision success.

A single reward representation may not naturally serve both.

This is a domain-grounded reason to separate reward semantics.

Not:
> “multi-reward is better.”

---

## I14.5 Comparison with generic VLMs

Hy-Embodied reports some generic/embodied benchmarks where general VLMs remain strong and others where embodied specialization helps.

That prevents a simplistic story:
> generic vision-language understanding is useless for robotics.

The pressure is more specific:
> **which visual-semantic knowledge needs action-conditioned structure?**

Again, this is an academic question family, not a candidate.

---

# INDUSTRY GENEALOGY I15 — Frontier models optimize across multiple sparsity axes

The industrial attention around “small active parameters” is not just cost marketing.

Recent reports reveal a repeated co-design pattern.

---

## I15.1 Kimi K3: sparsity across sequence, depth, and width [DIRECT]

K3 describes architecture in terms of scaling information flow across:
- sequence length;
- network depth;
- model width.

Concrete components:
- KDA + periodic Gated MLA for sequence mixing;
- AttnRes for selective access across depth;
- Stable LatentMoE for sparse width/expert activation.

### Important abstraction

Different bottlenecks are assigned to different sparsity/mixing mechanisms.

This is not one global:
> “make attention sparse.”

---

## I15.2 Stable LatentMoE pushes width sparsity extremely far [DIRECT]

K3:
- 896 routed experts;
- 16 selected per token;
- plus shared experts;
- 104B active out of 2.8T total.

At this regime, routing stability/load balancing are not side issues.

Moonshot adds:
- latent expert space;
- normalization;
- Quantile Balancing;
- systems-level expert parallelism.

### Industrial lesson

Once sparsity becomes extreme:
> **the router and balance mechanism become part of training stability, not only conditional-compute design.**

---

## I15.3 MiniMax chooses a different point: small activated compute as deployment thesis [FIELD]

M2:
- ~229.9B total;
- ~9.8B active/token.

The report's central product/research thesis is:
> small activation footprint + agent-specific data/RL can produce strong real-world intelligence.

This is an alternative frontier strategy:
> scale representational capacity without paying dense per-step compute.

---

## I15.4 Tencent Hy3 / Hy-Embodied repeat active-compute emphasis [CROSS-COMPANY]

Hy3:
- 295B total;
- 21B active.

Hy-Embodied:
- ~30B total;
- ~3B active.

Across companies, “active parameters” is becoming a more operational deployment quantity than total parameter count.

### But caution

Active parameters alone still do not define:
- memory;
- communication;
- routing overhead;
- KV;
- latency.

It is one resource proxy, not the full cost.

---

## I15.5 Academic translation

A paper comparing models only by:
> total parameter count

may now be scientifically misleading.

Depending on claim, relevant scale axes may include:
- total capacity;
- activated parameters;
- memory bandwidth;
- communication;
- context cost;
- expert count/routing entropy.

Again:
> model scale is becoming multidimensional.

---

# INDUSTRY GENEALOGY I16 — Self-evolution: from model-generated data to model-modified training machinery

MiniMax M2.7 provides a concrete recent example of a phrase that is otherwise very easy to hype.

---

## I16.1 Weak meaning of self-evolution

Many releases can call:
- synthetic data generation;
- self-play;
- self-critique

“self-improvement.”

These still leave:
> the training scaffold fixed by humans.

---

## I16.2 MiniMax operationalizes a stronger version [DIRECT]

M2.7 is reported to:
- triage failed training runs on internal infrastructure;
- edit its own agent scaffold;
- run experiments;
- evaluate changes.

One reported internal scaffold-optimization cycle:
- 100 autonomous rounds;
- analyze failures;
- modify code;
- evaluate;
- discover mechanisms/parameters;
- ~30% performance gain on their internal target.

On MLE Bench Lite, their self-evolution scaffold runs:
- 22 competitions;
- 24h per competition;
- repeated trials.

### Changed object

```
model generates training examples
→ model modifies the machinery that produces/uses those examples
```

That is a qualitatively stronger feedback loop.

---

## I16.3 But “self-evolution” still depends on a designed meta-environment

The model does not magically improve itself.

Humans still define:
- experiment sandbox;
- metrics;
- permissions;
- evaluators;
- review points;
- budget.

So the relevant research object is:
> **the outer-loop environment that makes autonomous improvement possible.**

This resembles AutoML / program synthesis / research agents more than biological self-evolution.

---

## I16.4 Relation to OpenAI/Anthropic internal R&D agents [CROSS-COMPANY]

OpenAI and Anthropic report growing agent use in:
- code;
- experiments;
- debugging;
- analysis.

MiniMax goes one step more operationally specific:
> model changes its own agent scaffold and training-related code under evaluation.

Cross-company convergence:
> AI is moving upstream into AI-development infrastructure.

### Small-team warning

This may make implementation-heavy research even faster for industrial labs.

It reinforces our need to compete on:
- question selection;
- sharp identification;
- cheap experiments;
not on:
- sheer number of variants.

---

# 17. Cross-company comparison: effort, scale, and state are all becoming multidimensional

After K3/MiniMax/Tencent, three old scalar abstractions look increasingly weak.

---

## 17.1 “Compute”

Not one scalar:
- pretraining FLOPs;
- activated parameters;
- reasoning effort;
- agent steps;
- tool calls;
- prefill;
- decode;
- persistent context;
- parallel agents.

---

## 17.2 “Trajectory”

Not one immutable sample:
- can span policy versions;
- can share prefixes;
- can include environment/sandbox state;
- can be partially resumed;
- can be judged as artifact/workflow;
- can be distilled across effort teachers.

---

## 17.3 “Model”

Not one policy:
- domain experts;
- effort experts;
- unified distilled student;
- router;
- scaffold;
- specialized execution model;
- live controller + deep backend.

### Taste lesson

Whenever an academic paper speaks of:
> “the model,” “the trajectory,” or “the compute budget,”

we should ask:
> is this scalar abstraction still load-bearing in the regime being studied?

But this remains a reading question, not a search generator.

---

# 18. Resource-transfer audit for this batch

## Kimi K3
Inspiration: **A**
Direct reproduction: **F**

Possible cheap sub-observations:
- effort control on open smaller models;
- stale rollout statistics in small RL;
- harness serialization/cache effects;
- partial rollout simulation.

But all require independent novelty audit.

## MiniMax M2.7
Inspiration: **A**
Direct reproduction: **F**

Transferable parts:
- windowed scheduling bias;
- prefix-tree shared-compute structure;
- scaffold robustness.

Self-evolution loop itself is expensive.

## Tencent Hy3
Inspiration: **B+/A-**
Transferability: **B/C**

Open weights make:
- scaffold sensitivity;
- effort modes;
- multi-turn behavior

more inspectable.

## Hy-Embodied
Inspiration: **A-**
Transferability: **C/D**

Model is open enough for inference,
but full training/data reproduction is large.

---

# 19. Current conclusion

The deepest industrial signal from this batch is not:
> bigger models, bigger RL.

It is:

> **frontier training is increasingly conditional on multiple control variables — effort, domain, scaffold, trajectory age, environment state, deployment precision, embodiment — and the infrastructure is deliberately allowed to change the statistical training object.**

That is exactly why blindly importing an industrial recipe into an academic project is dangerous.

Industrial teams can make the entire stack co-adapt.

Academic research needs to:
> isolate one relation at a time and prove that it survives when stripped from the proprietary stack.
