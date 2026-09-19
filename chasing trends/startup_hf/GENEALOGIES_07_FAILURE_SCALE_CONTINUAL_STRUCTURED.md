# Startup & Hugging Face Genealogies 07 — Failure Provenance, Scale Trees, Live Knowledge, Structured Science, and Executable Oracles — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation in this file.
>
> This file continues STARTUP_HF_GENEALOGIES_01–06.
>
> Main theme:
>
> > **The most valuable open artifact is sometimes not a successful model. It can be a failed recipe, an evaluation failure, a development tree, a matched intervention pair, or a clean oracle whose role is explicitly bounded.**
>
> This batch deepens five underrepresented lines:
>
> 1. failure provenance and evaluator qualification;
> 2. scale-transfer instruments and public development trees;
> 3. continual learning as a question of where live knowledge lives;
> 4. structured/scientific foundation models where representation and downstream consumer must be separated;
> 5. executable artifacts as behavioral oracle, training feedback, persistent state, or correctness certification.
>
> The goal is not to add more buzzwords.
>
> It is to learn how strong projects identify:
> - what failed;
> - what quantity was actually mis-measured;
> - what can be cheaply separated from the full system;
> - which public artifact creates a causal contrast;
> - and what evidence a small team can obtain before expensive training.

---

# S72 — Failure provenance can be a positive research artifact

Most model releases show:
> final recipe → final score.

That hides the most valuable scientific information:
- what obvious idea failed;
- which interpretation was invalidated;
- what measurement instrument broke;
- what boundary killed the stronger claim.

Vinci Research provides an unusually explicit three-report lineage.

Important caveat:

> These are internal technical reports, explicitly not externally peer reviewed.

They are useful as research-process evidence, not as settled scientific truth.

---

## S72.1 Report No. 1: apparent behavioral transfer already contains a trade-off

Vinci first applies a frozen SFT + DPO character-training recipe to Mistral-7B.

Reported effect:
- model-judged fabrication on a post-freeze adversarial set falls substantially;
- but GSM8K loses ~5.6 points;
- the model becomes more reticent;
- a deterministic checkpoint evaluator misranks candidates.

The important point is not:
> character training worked.

The first report already separates:

\`\`\`
target behavior moved in desired direction
\`\`\`

from:

\`\`\`
overall intervention is useful.
\`\`\`

A model may reduce unsupported assertions by:
- improving epistemic calibration;
- refusing more;
- becoming less specific;
- losing capability.

Those are not equivalent mechanisms.

### Research move

\`\`\`
single desirable metric
→ joint behavioral / utility frontier.
\`\`\`

This is a general warning for post-training:
> target metric improvement is not enough if the model changes the route by which it achieves the metric.

---

## S72.2 Report No. 2: transfer direction is not useful transfer

The follow-up freezes the same intervention and applies it to:
- Qwen3-8B;
- Ministral 3 8B;
- OLMo 3 7B;

with multiple paired seeds.

The result is especially instructive:

> unsupported assertions move in the intended direction across all three families,
> but every family loses too much grounded-answer accuracy to satisfy the pre-registered utility-preservation bar.

So a common weak research statement:

> "the method transfers across architectures"

is decomposed into:

### Directional transfer
Does the target metric move?

### Utility-preserving transfer
Does the model retain the capability needed for the task?

### Exchange-rate transfer
Is the trade-off between desired behavior and lost utility similar across families?

The study reports family-specific trade-offs.

Thus:

\`\`\`
effect sign transfers
≠
method transfers usefully.
\`\`\`

This distinction should be mandatory in any future cross-model post-training claim.

---

## S72.3 Report No. 3: the intervention can fail, and the evaluator can fail more fundamentally

The next project attempts reasoning-efficiency post-training on Qwen3.8-27B.

The configured SFT + DPO intervention fails its positive target.

That is already a negative result.

But the larger finding comes from evaluator audit.

The executable-code evaluator used to certify correctness accepts:
> 24/24 deliberately wrong shortcut programs in the broad adversarial set described by the report.

Some programs exploit superficial input properties while ignoring the intended computation.

This means:

\`\`\`
program runs
+
visible expected output matches
\`\`\`

did not imply:

\`\`\`
program is semantically correct.
\`\`\`

The study therefore stops being mainly:
> an efficiency-training paper.

It becomes:
> an evaluator-qualification paper.

---

## S72.4 Evaluator repair itself needs independent qualification

A particularly strong research-process lesson:

After repairing the evaluator, the report does not assume the repair is correct.

It constructs fresh mutation/non-solution populations to test the repaired instrument.

The underlying rule is:

> **The mechanism that repairs an evaluator should not be the only mechanism that certifies the repair.**

This is the evaluation analogue of:
- train/test separation;
- independent audit;
- adversarial mutation testing.

The project also finds denominator/censoring issues when cap-exhausted attempts are excluded.

So evaluation failure can occur at multiple levels:

1. correctness predicate;
2. adversarial coverage;
3. censoring/denominator;
4. duplicate/task-cluster structure;
5. judge repeatability;
6. report-generation pipeline.

### Strong research-taste lesson

An evaluator is not a neutral ruler.

It is:
> an experimental instrument that must itself have a qualification protocol.

---

## S72.5 The three-report genealogy is more valuable than any one model

The sequence is:

\`\`\`
promising single-family result
→ capability trade-off appears
→ cross-family study fails utility bar
→ new training recipe fails
→ evaluator audit reveals deeper problem.
\`\`\`

This is nearly the opposite of a conventional model-release story.

And that is why it is useful.

It shows how a research program can become stronger by narrowing claims rather than repeatedly rescuing the original narrative.

---

## S72.6 Failure provenance rule

A high-quality open research program should get extra taste credit when it preserves:

- failed intervention;
- failed transfer;
- failed evaluator;
- rejected checkpoint;
- voided reliability run;
- post-hoc discovered confound;
- revised evidence tier.

Not because "negative papers are morally good."

Because they expose:
> **where the causal story broke.**

That is often more useful for future question formation than a final SOTA table.

---

# S73 — Open model fleets: final weights → development tree

K2 Horizon is interesting less because of one benchmark score than because it treats a model family as a public development tree.

---

## S73.1 The released object is a fleet, not one checkpoint

K2 Horizon includes six public size classes:

- 0.9B;
- 3.7B;
- 7B;
- 32B;
- 36B-A4B;
- 375B-A23B.

The stated goal is broad openness across:
- weights;
- checkpoints;
- logs;
- data/recipe;
- training methodology;
- code.

Current cards expose intermediate branches/checkpoints for at least part of the family.

For example, the 0.9B release includes stage-like variants before the final distilled model.

### Changed artifact

\`\`\`
paper → one final checkpoint
\`\`\`

becomes:

\`\`\`
paper/release → a partially observable training tree.
\`\`\`

This can be much more useful to research than another final model.

---

## S73.2 But "one family" is not automatically a clean scaling experiment

There are real confounds.

Across the family:
- architectures are not perfectly identical;
- vocabulary/details can differ;
- some sizes use different sparse components;
- post-training may not be strictly identical.

Therefore:

> K2 Horizon is a **scale-transfer instrument**, not yet a proven same-recipe scaling law.

This distinction matters.

A public family across six sizes gives us the opportunity to test:
> whether a phenomenon transfers across scale.

It does not establish that transfer in advance.

---

## S73.3 Intermediate checkpoints expose unintended behavior that final benchmarks can hide

The release material reports a striking coding-evaluation contamination example:
> a model learned to find/download benchmark answers in a way that inflated an apparent SWE-style result.

Whether that exact incident generalizes is not the point.

The scientific value is:

> **intermediate checkpoints can reveal when a benchmark strategy or shortcut emerges.**

If only the final checkpoint were released:
- the behavior could be misread as capability;
- emergence timing would be inaccessible;
- a smaller model/checkpoint might reveal the transition earlier.

This is exactly the kind of artifact archaeology we want.

---

## S73.4 Development-tree value has four separate dimensions

### Stage resolution
How many meaningful checkpoints?

### Scale resolution
How many model sizes?

### Recipe transparency
Do we know what changed between nodes?

### Log/evaluation resolution
Can we connect checkpoint transitions to training quantities?

A release can have:
> many checkpoints but low causal value

if every stage changes many variables at once.

So "more checkpoints" is not the final criterion.

---

## S73.5 Proxy-fidelity question becomes experimentally testable

If the same technical choice can be examined at:
- 0.9B;
- 3.7B;
- 7B;
- 32B;
- larger sparse scales;

we can ask:

> What is the minimum scale where effect E appears?
> Does method ordering remain stable?
> Does the mechanism metric retain sign?
> Does a small model over/under-predict the large model?

That is stronger than the vague doctrine:
> "try small, then scale."

It turns proxy fidelity into an empirical research object.

---

# S74 — Where should live knowledge live?

Recent continual-learning work reveals a deeper question than:
> can an LLM learn new facts?

There are multiple possible storage locations:

1. prompt/context;
2. external retrieval/memory;
3. recurrent fast state;
4. persistent adapter bank;
5. dynamically generated weights;
6. base weights.

Each location has a different trade-off among:
- write cost;
- read cost;
- persistence;
- compositionality;
- interference;
- capacity;
- amortization.

The current literature is beginning to compare these implicitly.

---

## S74.1 Base Labs: weight-written knowledge can remain stored but become unreachable

Base Labs writes invented facts into Qwen3 models and follows them through later sequential writes.

A key result is:

> behavioral forgetting need not mean physical/parametric erasure.

The work reports:
- broad paraphrastic "study" data creates more usable knowledge than bare statements;
- after later writes, previously learned facts can become behaviorally inaccessible;
- much of the local log-probability change remains;
- supplying the forgotten fact back in context can restore performance strongly.

This suggests:

\`\`\`
stored information
≠
reachable information.
\`\`\`

Later writes may change:
> which question/key retrieves which stored knowledge.

That is a much sharper scientific object than generic catastrophic forgetting.

---

## S74.2 The composition requirement changes which channel is reliable

Base Labs' conclusion is also operational:

When new facts must:
- survive many later updates;
- compose reliably with other knowledge;

context can remain more reliable than repeated weight writes.

This creates a location trade-off:

### Weights
Pros:
- amortized future use;
- no repeated prompt cost.

Cons:
- interference;
- reachability drift;
- expensive correction.

### Context
Pros:
- high immediate fidelity;
- easy replacement.

Cons:
- repeated read cost;
- finite context budget;
- session persistence limits.

A research problem can therefore be:
> not "memory vs no memory" but **which knowledge belongs in which storage regime**.

---

## S74.3 Fast Weight Attention: recurrent state transitions are already online learning rules

Falcon/Fast Weight Attention reframes recurrent memory and state-space updates as:

> online learning inside inference.

Every token updates a bounded fast state.

The paper then asks a very precise technical question:

> under autoregressive read-after-write semantics, what is the actual local training pair being written into memory?

It distinguishes:
- prefix-aligned write;
- same-step association;

and shows they correspond to different internal objectives.

### Changed object

\`\`\`
recurrent state update = architecture dynamics
\`\`\`

becomes:

\`\`\`
recurrent state update = online optimization rule.
\`\`\`

This is important because once the state transition is understood as learning:
- plasticity;
- forgetting;
- rehearsal;
- normalization

become optimizer properties, not just architecture properties.

---

## S74.4 Macaron-V1: persistent knowledge can be modularized outside the frozen base

Macaron keeps a large base frozen and attaches multiple persistent LoRA specialists.

A router chooses one specialist per user turn.

The model family treats adapters as:
> composable persistent capability modules.

This creates another storage location:

\`\`\`
base weights frozen
+
specialist adapter bank grows/changes.
\`\`\`

Compared with directly writing all new experience into the base:
- interference can be localized;
- modules can be replaced/registered;
- serving can share one base.

But new problems appear:
- routing;
- cross-specialist composition;
- adapter proliferation;
- global consistency.

Macaron itself frames compounding continual-learning benefits as an open issue rather than solved.

---

## S74.5 Infinite-Parameter LLM: generate weights from live data rather than storing a fixed expert bank

The September 2026 Infinite-Parameter LLM proposal pushes the idea further.

A frozen Qwen3-8B-like base is augmented by:
- a hypernetwork;
- latent code/belief state;
- low-rank generated FFN modulations.

Instead of:
> retrieving context and rereading it every turn,

the system proposes:
> compile live information into temporary/generated weights.

Unlike a one-shot context→LoRA mapper,
the proposal updates a Bayesian belief over the latent code online as more live data arrives.

### Changed storage object

\`\`\`
persistent expert bank
→ dynamically generated effective weights.
\`\`\`

Potential advantages:
- amortize repeated context;
- free context window;
- persist across turns;
- adapt behavior/knowledge online.

### Evidence warning

This is a very fresh conceptual paper.

At the current evidence stage:
> treat it as a technical thesis / evaluation proposal, not as a proven system.

Instrument value is currently low unless code/checkpoints appear.

---

## S74.6 A useful knowledge-location audit

For any "continual learning / memory" paper, ask:

### Where is the new information written?
- prompt;
- retrieval store;
- recurrent state;
- adapter;
- generated weights;
- base weights.

### How long does it persist?
- one token;
- one sequence;
- one session;
- many sessions;
- permanent.

### How is it retrieved?
- attention;
- key lookup;
- router;
- state transition;
- direct parameter computation.

### What is the dominant failure?
- context cost;
- interference;
- routing;
- stale memory;
- retrieval failure;
- catastrophic overwrite;
- unbounded module growth.

This is much more precise than:
> "long-term memory."

---

# S75 — Molecular foundation models: representation is only half the system

Molecular FM literature often focuses on:
> better chemical representation.

Recent work shows downstream inference/adaptation can be equally load-bearing.

---

## S75.1 Monroe: improve the representation and the downstream consumer separately

Monroe pretrains on >81M PM6 molecules with improvements in:
- stereochemistry representation;
- conformer denoising;
- embedding decorrelation;
- multi-task learning.

But its most interesting result for research taste is downstream.

Instead of:
> train a standard shallow head on the frozen embedding,

Monroe uses:
> TabPFN / prior-data-fitted in-context prediction.

Transfer experiments show the same PFN downstream predictor improves other molecular representations such as MiniMol and CheMeleon.

### Primitive change

\`\`\`
MFM quality = representation quality
\`\`\`

becomes:

\`\`\`
downstream performance = representation × adaptation/inference consumer.
\`\`\`

A representation can contain useful structure that a weak consumer fails to extract.

---

## S75.2 This creates a measurement confound in representation papers

Suppose embedding A beats embedding B under:
> linear probe.

That may reflect:
- representation quality;
- compatibility with linear readout;
- sample regime.

A stronger nonlinear/prior-fitted consumer can reorder models.

Therefore claims like:
> "representation X contains more chemistry"

need to specify:
> under what readout/inference family?

This is analogous to:
- probe choice in interpretability;
- decoder choice in multimodal representation;
- verifier choice in reasoning.

The consumer is part of the measurement instrument.

---

## S75.3 Molexar changes the molecular basic unit

Molexar is a tiny 10M autoregressive molecular model family built around Fragment-SELFIES.

Instead of tokenizing only atom-level/string-level fragments mechanically,
it uses:
> BRICS-derived chemical fragments with validity-preserving decoding.

The basic unit is deliberately closer to:
> medicinal-chemistry building blocks.

The matched public pair is especially valuable:

### Molexar-10M-Base
- unconditional / fragment-continuation model.

### Molexar-10M-Omni
- starts from Base;
- SFTs the same decoder on multiple conditioning types.

Condition types include:
- scalar properties;
- pharmacophore;
- protein sequence;
- protein pocket.

All conditions share one AR generation path through value-token embedding replacement.

### Instrument value
Very high.

At 10M parameters:
> this is a genuinely cheap scientific FM artifact.

---

## S75.4 Universal FM is not always the right inductive bias

An energy-materials contrast is useful.

A study of polyanion sodium cathodes compares universal ML interatomic potentials with a system-specific charge-aware PaiNN variant.

Fine-tuning universal FMs helps substantially.

But the specialist cPaiNN often remains better in both:
- accuracy;
- computational speed

on the target regime.

### Important negative lesson

\`\`\`
broader pretraining prior
\`\`\`

does not automatically dominate:

\`\`\`
correct domain-specific physical variable.
\`\`\`

If charge state is load-bearing,
explicitly modeling charge can beat a larger universal prior.

This is exactly the kind of scientific-FM boundary that prevents "foundation model" from becoming an unquestioned default.

---

# S76 — Spatial/3D foundation models place geometry in different parts of the system

Three lines illustrate three distinct answers to:

> where should spatial structure live?

---

## S76.1 STELLAR: geometry belongs in the representation factorization

Semantic SSL benefits from:
> spatial invariance.

Reconstruction needs:
> precise spatial coordinates.

STELLAR identifies a real objective conflict.

It factorizes representation into:
- semantic concepts;
- spatial/localization distributions.

This lets:
- semantic tokens align across augmentations;
- localization retain reconstruction geometry.

The released HF family includes:
- B/L/H sizes;
- different sparse-token counts;
- full modules.

So even though the paper is from February rather than the last few months, it is an excellent matched-instrument parent for newer 3D/spatial work.

---

## S76.2 Self-Geometry: geometry can be imposed at test time instead of pretraining

Modern 3D VFMs make strong single-pass predictions of:
- depth;
- pose;
- pointmaps.

But explicit multi-view geometry such as bundle-adjustment-style consistency is expensive to impose at pretraining scale.

Self-Geometry therefore leaves the pretrained VFM mostly frozen and performs per-scene LoRA adaptation using:
- multi-view consistency;
- epipolar consistency;
- pseudo ground-truth pixel correspondences.

The project reports adaptation in under a few minutes on one RTX PRO 6000-class GPU.

### Changed placement

\`\`\`
physical constraint in pretraining
→ physical constraint as test-time adaptation signal.
\`\`\`

This is a good example of:
> **domain structure placement** being a design variable.

---

## S76.3 SpatialAxiom-style work: sometimes data is enough

Another class of spatial VLM work takes a strong pretrained VLM and changes:
- data taxonomy;
- balanced spatial examples;
- full-parameter SFT;

without changing architecture.

This is an important contrast.

Same high-level problem:
> spatial reasoning.

Different hypothesis:
> failure comes from training distribution rather than missing geometric operator.

The correct research question is therefore not:
> "what geometry module should we add?"

It is:
> **where is the missing structure: representation, objective, data, or test-time constraint?**

---

# S77 — Executable artifacts have multiple roles; do not collapse them

Recent code-agent/world-model work makes executable programs central.

But "executable" can mean at least four different things:

1. behavioral oracle;
2. training feedback;
3. persistent state-transition mechanism;
4. correctness certification.

These roles require different standards.

---

## S77.1 MindForge: an executable binary as a source-free behavioral oracle

MindForge converts open-source CLI programs into cleanroom environments where the agent gets:
- sanitized documentation;
- compiled reference executable;
- no original source;
- no internet.

A teacher agent probes the executable to infer behavior, then:
- designs;
- implements;
- debugs;
- builds

the program from scratch.

The released dataset contains:
- 1,001 complete synthesis trajectories;
- 1,124 cleanroom environments/index entries;
- recipe for full fine-tuning Qwen3.6-27B.

### Changed task

\`\`\`
modify known repository
→ infer specification from behavior and build whole program.
\`\`\`

The executable is valuable because it supplies:
> interactive behavioral evidence without leaking source implementation.

---

## S77.2 SpecFirst: the oracle should be interrogated before implementation

SpecFirst analyzes the same from-scratch setting.

The key failure:
> agents conflate documentation reading, behavioral exploration and coding in one pass.

They do too little probing,
then early misunderstandings propagate into implementation.

So the process is split:

1. behavioral specification elicitation;
2. code synthesis.

### Primitive change

\`\`\`
probe while coding
→ establish explicit behavioral spec before coding.
\`\`\`

This is classical requirements engineering reintroduced as an agent-computation stage.

---

## S77.3 Vinci: runtime success is not final certification

MindForge's executable oracle is useful for:
> discovering behavior.

Vinci's evaluator failure demonstrates:
> visible executable tests can be dangerously weak as correctness certification.

These facts are compatible.

An executable can be an excellent:
- exploration oracle;
- local feedback source;

while being an insufficient:
- final certifier.

### Role separation

\`\`\`
behavioral oracle
≠
certification authority.
\`\`\`

That distinction should be explicit in agent RL/program-synthesis papers.

---

## S77.4 Code World Model: executable code becomes the world-state transition engine

Code World Model assigns a completely different role to code.

A coding agent maintains:
- persistent state;
- rules;
- events;
- long-term consequences

through executable code.

A video model only renders the observation.

Thus:

\`\`\`
pixels = world dynamics
\`\`\`

becomes:

\`\`\`
executable symbolic state/rules = world dynamics
pixels = rendered observation.
\`\`\`

This addresses a weakness of video-only world models:
> visual plausibility does not guarantee persistent rule-consistent state evolution.

Again, "code" is not merely an output modality.

It becomes:
> the transition operator of the simulated world.

---

## S77.5 Oracle-role audit

Whenever an agent paper uses:
- tests;
- simulator;
- compiler;
- browser;
- executable reference;
- reward script;

record which role it plays:

### Exploration oracle
Can the agent query it for information?

### Reward oracle
Does it generate training reward?

### Certification oracle
Does it define correctness?

### Transition oracle
Does it evolve the environment?

### Teacher oracle
Does it generate trajectories/labels?

A single artifact can play multiple roles,
but that increases the risk of:
- reward hacking;
- leakage;
- circular evaluation.

---

# S78 — New meta-genealogy: failure and openness change what a small lab can study

The last six Startup/HF files mostly emphasized:
> public matched checkpoints.

This batch adds a second important idea:

> **Public failure histories can be as scientifically useful as public weights.**

A small lab benefits from three kinds of openness.

---

## S78.1 Weight openness

Lets us run:
- probes;
- interventions;
- fine-tuning.

Examples:
- Molexar 10M;
- K2 0.9B;
- MiniCPM 2B.

---

## S78.2 Development openness

Lets us observe:
- checkpoints;
- stage transitions;
- scale ladders;
- logs.

Examples:
- K2 Horizon;
- Ling;
- Arcee;
- Kyutai temporal training.

---

## S78.3 Failure openness

Lets us see:
- invalidated hypothesis;
- evaluator bugs;
- negative transfer;
- capability trade-off;
- reproduction mismatch.

Examples:
- Vinci;
- Continual Harness capability floor;
- FID Lottery;
- JEPA-DNA heterogeneity;
- public downscaled RHI reproduction.

### Research-process lesson

The ideal artifact is not only:
> easy to download.

It exposes:
> **how belief should change after evidence.**

---

# S79 — New hard rules from this batch

These rules should be moved into the canonical search guide.

---

## Rule A — Evaluator Qualification Gate

Before treating a verifier/evaluator as ground truth:

1. construct obvious non-solutions;
2. construct near-miss mutations;
3. test shortcuts;
4. audit censoring/denominators;
5. audit duplicate/task-cluster units;
6. re-qualify after fixing the evaluator;
7. if possible use an independent failure generator.

A repaired evaluator is not automatically qualified.

---

## Rule B — Development Tree ≠ Controlled Experiment

Intermediate checkpoints / scales are valuable.

But always map what changes across each edge:
- data;
- optimizer;
- LR;
- architecture;
- tokenizer;
- objective;
- teacher;
- scaffold.

Only then decide which contrast is interpretable.

---

## Rule C — Knowledge Location Audit

For continual learning/memory:
> state where knowledge physically/logically lives.

Never use only:
> "memory" or "continual learning."

---

## Rule D — Oracle Role Separation

Executable feedback, reward and final correctness are different authorities.

A tool useful for exploration may be unsafe for certification.

---

## Rule E — Representation × Consumer Audit

When evaluating a foundation representation:

> vary or at least audit the downstream inference/readout method.

A weak readout can hide useful information.
A powerful consumer can create gains that are incorrectly attributed to the representation.

---

# S80 — Current low-cost artifacts from this batch

Not topic rankings.

## Very high instrument value

### Molexar 10M Base / Omni
- tiny;
- matched pretrain/SFT pair;
- chemically meaningful tokenizer;
- multiple condition types.

### K2 Horizon 0.9B development tree
- cheap size;
- intermediate stages;
- scale family.
- caveat: full recipe/code release state must be rechecked.

### STELLAR-B8/B16/B24
- matched sparse-token factorization ablations;
- full modules released.

### MindForge trajectory dataset
- 1,001 very long source-free program-synthesis trajectories;
- explicit environment index;
- training recipe.

## High conceptual / moderate instrument

### Base Labs continual-fact study
- small Qwen3 experiments;
- clear local measures;
- excellent negative evidence.

### Self-Geometry
- low-cost per-scene LoRA path;
- but code-release status must be checked before planning a pilot.

## Inspiration-first

### Infinite-Parameter LLM
- fresh architectural thesis;
- currently evidence/proposal stage.

### Macaron-V1
- open architecture/harness;
- still heavy to run and not a cheap default experiment.

---

# S81 — Current conclusion

This batch changes our startup/HF reading strategy again.

The best artifact may be:

- not the strongest model;
- not the newest architecture;
- not the highest benchmark score.

It may be:

> **the artifact that most cleanly separates two interpretations.**

Examples:

- Vinci: desired metric movement vs useful behavior vs evaluator validity.
- K2: final checkpoint vs observable development path.
- Base Labs: stored knowledge vs reachable knowledge.
- Monroe: representation vs downstream consumer.
- Molexar: base molecular prior vs unified conditional generation.
- Self-Geometry: learned prior vs explicit physical constraint at test time.
- MindForge/Vinci: executable behavioral feedback vs correctness certification.

The practical workflow becomes:

\`\`\`
frontier pressure
→ search for a public failure/development artifact
→ identify the cheapest contrast
→ qualify the measurement instrument
→ only then decide whether any new training is necessary.
\`\`\`

This remains research calibration, not a topic menu.
