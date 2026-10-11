# Startup & Hugging Face Genealogies 08 — Scientific Experience, Native Structure, Predictive State, and Discovery Systems — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues Startup/HF Genealogies 01–07.
>
> Recent-window focus:
> - ScienceIDE — Sep 16/17 2026
> - ScienceBuddy — Sep 15/16 2026
> - JEPA-Anything — Sep 17/18 2026
> plus recent BioMatrix / SciReasoner artifacts as structural contrasts.
>
> Core observation:
>
> > **"Scientific foundation model" is no longer one coherent technical category.**
>
> Recent systems place scientific structure in radically different locations:
>
> - executable environment and verifier;
> - mutable research/harness state;
> - latent predictive world state;
> - unified discrete token space;
> - addressable native structural evidence.
>
> The interesting research question is therefore not:
>
> > "How do we make a scientific foundation model?"
>
> but:
>
> > **What is the correct state / evidence / interaction unit for the scientific process being modeled?**

---

# S82 — Scientific code → executable experience

ScienceIDE is one of the freshest and clearest attempts to turn scientific software into a reusable learning substrate.

---

## S82.1 Scientific repositories contain knowledge, but not automatically trainable experience

A scientific codebase contains:
- equations;
- solvers;
- implementation conventions;
- numerical tolerances;
- domain-specific assumptions;
- regression tests;
- examples.

But a repository alone does not define:
- a task;
- a valid action space;
- partial progress;
- scientific correctness;
- an RL reward.

ScienceIDE names this:
> the scientific experience bottleneck.

The bottleneck is not:
> lack of scientific code.

It is:
> converting implicit scientific practice into an executable training contract.

---

## S82.2 The construction unit is a scientific responsibility, not a file/repository

ScienceIDE decomposes a codebase into modules defined by:
> coherent scientific responsibility + executable coverage.

This is a strong design decision.

The basic unit is not:
- file;
- function;
- repository;
- benchmark problem.

It is:
> a scientific module whose behavior can be externally checked.

That unit then supports many task types:
- repair;
- implementation;
- reproduction;
- calibration;
- integration;
- acceleration;
- discovery-oriented tasks.

### Primitive change

repository as training environment
→ scientific responsibility + acceptance contract as reusable environment.

---

## S82.3 Correctness is numerical/physical equivalence, not diff matching

The agent edits source.

The verifier:
- rebuilds code;
- runs physical/numerical cases;
- compares scientific observables under calibrated tolerances/invariants.

The reward is not:
> did the patch match the reference diff?

It is:
> did the repaired code recover scientifically acceptable behavior?

This is a much stronger contract than ordinary repository editing.

---

## S82.4 Known nuisance variation is explicitly removed from the correctness definition

ScienceIDE makes a distinction between:

### Scientific observable
- conserved quantity;
- physical field;
- numerical result;
- distribution;
- invariant.

### Implementation nuisance
- storage order;
- adaptive step count;
- timing;
- rank layout;
- eigenvector phase;
- random draw identity.

A good evaluator should not fail a scientifically correct implementation because of nuisance representation differences.

This is the scientific-code version of:
> domain structure placement.

The known invariance belongs in:
> the evaluation contract.

---

## S82.5 Tolerances are empirical scientific objects, not arbitrary epsilons

The project distinguishes:
- pointwise tolerances;
- invariant-based checks.

It uses:
- nominal runs;
- variant initial conditions;
- alternative builds where available;

to measure numerical variation before fixing acceptance criteria.

### Research-taste lesson

A verifier should not simply choose:
> 1e-5 because it is conventional.

The tolerance itself is part of:
> scientific identification.

This is an excellent contrast to the executable-evaluator failure in Vinci.

---

## S82.6 Task validity is established before task difficulty

ScienceIDE separates:

### Validity
- official fix passes;
- defective baseline leaves reward headroom;
- task is observable;
- no answer leakage;
- infrastructure works.

### Difficulty
- measured relative to a named model/harness/budget/date.

This is important.

A task is not intrinsically:
> hard.

Difficulty is relational.

This mirrors:
- student-relative supervision;
- model-relative data difficulty;
- harness-conditioned agent ability.

---

## S82.7 Public model pairs create a low-cost scientific-experience instrument

ScienceIDE currently releases:
- PhAI-IDE-4B;
- PhAI-IDE-9B;
- PhAI-IDE-72B.

The 4B and 9B releases are compared against matched Qwen3.5 bases on held-out scientific-code repair.

Training uses verified interaction trajectories and LoRA-style SFT.

For a small lab, the 4B pair is especially valuable:

\`\`\`
same base family
→ scientific-experience SFT
\`\`\`

This can support cheap analyses of:
- tool behavior;
- code repair;
- scientific/numerical reasoning transfer;
- specialization side effects.

---

## S82.8 ScienceIDE also exposes the negative side of transfer

The paper reports:
> gains are not uniform.

Some public benchmarks improve;
at least one reported code benchmark declines for one scale.

This is useful.

The story is not:
> scientific data universally improves general intelligence.

It is:
> verified scientific interaction creates a distinctive training distribution whose transfer pattern must be measured.

That makes the release more useful scientifically.

---

## S82.9 RL reintroduces the industrial async-rollout problem

Scientific episodes can:
- rebuild Fortran/C++;
- run expensive simulations;
- take tens of turns;
- have highly variable duration.

A synchronous RL loop would wait for the slowest episode.

ScienceIDE therefore uses asynchronous rollout/training with bounded staleness and truncated importance correction.

This connects two genealogies:

### Scientific environment
creates long, expensive, heterogeneous episodes.

### RL systems
must tolerate asynchronous model versions.

So once again:

> task semantics reshape the statistical training regime.

---

# S83 — Scientific interaction → dual adaptation of harness and model

ScienceBuddy sits one layer above ScienceIDE.

Its key question is not:
> how to train a scientific task model?

It is:
> what should change when repeated scientist–agent interaction reveals a better way to work?

---

## S83.1 Research collaboration produces two kinds of reusable signal

A scientist's feedback may imply:

### Procedural lesson
"Use this analysis tool first."
"Preserve this intermediate result."
"Check this database before proposing hypotheses."

This belongs in:
> harness/workflow.

### Capability lesson
"The model repeatedly fails this class of reasoning."

This may belong in:
> weights.

Most systems collapse these.

ScienceBuddy explicitly separates them.

---

## S83.2 Inner recursion: improve the harness with model fixed

Given interactions and feedback:
- propose Python harness variants;
- evaluate candidates against a parent;
- select the better procedure.

This is a search over:
> working procedure / information flow.

The model stays fixed.

---

## S83.3 Outer recursion: improve the model under the selected harness

Then:
- collect fresh on-policy attempts;
- score with a verifier;
- apply GRPO;
- export updated model.

The improved model returns to the next harness-improvement cycle.

So:

\`\`\`
harness changes model's experience
→ model changes what harness adaptation is useful
\`\`\`

The two learning processes co-evolve.

---

## S83.4 This is stronger than generic self-improving harness

Earlier RHI / Continual Harness usually emphasize:
> update the scaffold.

ScienceBuddy explicitly creates:

\`\`\`
harness optimization
↔
weight optimization
\`\`\`

as alternating recursions.

That is a new coordination problem.

But it also inherits the same risks:
- unstable outer loops;
- evaluator overfitting;
- model capability floor;
- expensive interaction;
- hard attribution.

---

## S83.5 The open artifact is more constrained than the product narrative

The public experiment is deliberately simplified:
- Qwen3.5-4B;
- fixed train/val/test release;
- bounded harness proposals;
- three harness/RL cycles;
- finite GRPO updates.

The full hosted product is not completely open.

This distinction is good practice.

### Artifact lesson

Do not infer:
> production-scale self-improving scientist

from:
> a bounded reproducible double-recursion experiment.

Keep evidence tiers separate.

---

# S84 — Scientific codebases can become environments in different ways

MindForge and ScienceIDE share a high-level pattern:
> repository → agent environment.

But the scientific/engineering contract is almost opposite.

---

## S84.1 MindForge removes source to force specification discovery

Agent sees:
- docs;
- executable reference.

Goal:
> reconstruct the whole program.

The executable is an oracle for:
> what the program should do.

The scientific object:
> behavioral specification elicitation.

---

## S84.2 ScienceIDE preserves source and hides scientific certification

Agent sees:
- actual scientific code;
- defect/implementation objective.

Goal:
> restore scientifically correct behavior.

Private verifier checks:
- numerical/physical equivalence.

The scientific object:
> operating correctly inside an inherited scientific codebase.

---

## S84.3 Same "executable environment", different information boundary

MindForge:
> implementation hidden; behavior visible.

ScienceIDE:
> implementation visible; certification hidden.

These boundaries create different learning problems.

### MindForge
- infer spec;
- synthesize architecture;
- reconstruct behavior.

### ScienceIDE
- understand code;
- locate scientific responsibility;
- repair/implement under numerical contract.

Therefore:
> "turn repositories into environments"

has no scientific specificity until the information boundary is defined.

---

# S85 — Scientific world model: unify the predictive principle, not necessarily the raw modality

JEPA-Anything is important because it offers a different interpretation of "unified scientific model" from BioMatrix.

---

## S85.1 The question is cross-domain predictive structure

Domains:
- vision;
- single-cell biology;
- clinical trajectories;
- control;
- molecular dynamics;
- PDE fields;
- weather.

They do not share:
- observation geometry;
- encoder;
- semantics;
- time scale.

The project does not force one raw tokenization across all domains.

Instead it shares:
> a context→target predictive interface.

---

## S85.2 OPF: monolithic target embedding may create internal competition

A standard JEPA predicts:
> one target embedding through one prediction pathway.

JEPA-Anything argues complex target states often contain multiple predictable modes:
- local/global change;
- multiple entities;
- identity vs response;
- physical modes at different rates.

A single pathway can allow:
- high-variance/easy modes to dominate;
- redundant latent directions;
- conflicting gradients.

Orthogonal Predictive Factorization therefore:
- decomposes target representation into factors;
- gives factors dedicated predictive pathways;
- encourages complementary subspaces;
- recombines them into full latent state.

### Primitive change

one predictive state vector
→ structured complementary predictive factors.

---

## S85.3 Cross-domain unification happens at the operator level

This is the key point.

BioMatrix-style unification:
> common discrete token vocabulary + NTP.

JEPA-Anything-style unification:
> domain-specific adapters + common predictive factorization/operator.

Thus:

\`\`\`
unify representation
\`\`\`

and:

\`\`\`
unify learning principle
\`\`\`

are different research theses.

The latter preserves domain-specific input geometry.

---

## S85.4 Public checkpoints make cross-domain mechanism testing unusually possible

The HF release includes paired:
- standard JEPA;
- JEPA-Anything/OPF

checkpoints across multiple domains.

The model card explicitly exposes branch-based matched inference.

This gives high instrument value:
> the central method is compared against a matched parent across heterogeneous tasks.

That is much stronger than a final all-domain leaderboard.

---

## S85.5 One method across domains needs a stricter generality test

Cross-domain success can mean two things.

### Weak generality
Same method name applied with extensive per-domain tuning.

### Stronger generality
Same underlying operator solves the same identifiable failure across domains.

For OPF, the claimed shared failure is:
> multiple predictive modes compete in one target pathway.

A proper audit should test:
- factor redundancy;
- gradient conflict;
- mode coverage;
- long-horizon error;
- intervention compositionality;

rather than only downstream performance.

---

# S86 — Unified token space vs native structural evidence

BioMatrix and SciReasoner provide a useful near-sibling contrast.

Both want:
> one scientific model spanning multiple biological/chemical structures.

But they make different bets about the role of structure.

---

## S86.1 BioMatrix: make every modality generatable under one NTP interface

BioMatrix maps:
- molecule 1D;
- molecule 3D;
- protein 1D;
- protein 3D;
- natural language

into one discrete vocabulary.

Everything is:
> consumed and generated under next-token prediction.

No external modality-specific output head is required.

### Thesis

> **uniform generation interface can itself create cross-modal capability.**

This is the scientific analogue of native multimodal LLM design.

---

## S86.2 BioMatrix's own limitation reveals where unification stops

The model card explicitly notes:
> molecular and protein 3D structures are tokenized in disjoint geometric reference frames.

Therefore the model cannot natively represent:
> cross-entity complex geometry such as docking poses.

This is very valuable.

The success of unified tokens exposes a new missing relation:

\`\`\`
within-entity structure
→ supported
\`\`\`

but:

\`\`\`
cross-entity relative geometry
→ not natively represented.
\`\`\`

### Research-taste lesson

Every "unified representation" should be audited for:
> **which relations become impossible to express after unification.**

---

## S86.3 BioMatrix also creates clean open pairs

Public:
- 1.7B CPT;
- 1.7B SFT;
- 4B CPT;
- 4B SFT;
- SFT data;
- molecular 3D tokenizer code/checkpoint.

This has high instrument value.

Possible studies can start with:
> inference-stage comparisons rather than 304B-token re-pretraining.

---

## S86.4 SciReasoner: structure should be addressable evidence, not only another modality

SciReasoner starts from a different pressure.

Scientific prediction is not enough if:
> the model cannot explain which structural evidence supports the prediction.

It encodes:
- Foldseek 3Di;
- ConfSeq;
- SLICES;
- sequence/formula/text

as structure-aware evidence units.

The reasoning trace can explicitly refer to:
- residues;
- fragments;
- conformers;
- space groups;
- bonding patterns;
- coordination environments.

### Thesis

\`\`\`
structure as input modality
→ structure as addressable reasoning evidence.
\`\`\`

This changes what "interpretability" means.

It is not:
> post-hoc probe hidden states.

It is:
> expose native structural evidence as the substrate of the task reasoning.

---

## S86.5 But SciReasoner currently has weaker artifact value

At the checked repository state:
- model/evaluation releases are still marked coming soon in parts of the project.

Therefore:
> thesis value high,
> immediate pilot value lower than BioMatrix.

Again:
> paper quality and artifact value are independent.

---

# S87 — Discovery Foundation Models: agenda vs validated object

The September DFM report is extremely broad.

It defines seven capabilities:
- problem discovery;
- formulation;
- representation construction;
- hypothesis formation;
- intervention;
- evidence-grounded revision;
- continual discovery improvement.

This is conceptually useful.

But a research agenda is not a validated model class.

---

## S87.1 The correct way to read a manifesto-style technical report

Do not ask:
> "Is Discovery Intelligence the next paradigm?"

Ask:
> Which child projects create falsifiable units?

Current public branches include:
- ScienceBuddy;
- ScienceIDE;
- JEPA-Anything.

Each makes a different part executable.

Thus the parent report should be treated as:
> **research-map evidence**, not mechanism evidence.

---

## S87.2 Research state is a proposed basic object

A DFM operates over:
> revisable research state.

That state includes:
- hypotheses;
- evidence;
- interventions;
- representations;
- skills;
- verification outcomes.

This is more structured than:
> conversation history.

But the value of such a state representation must be demonstrated through child systems.

---

## S87.3 A strong research agenda should decompose into independent failure modes

The current child projects suggest at least three:

### Scientific experience bottleneck
ScienceIDE:
> code/experiments are not automatically trainable environments.

### Scientist–agent adaptation bottleneck
ScienceBuddy:
> collaboration improves procedure and model on different time scales.

### Predictive-state bottleneck
JEPA-Anything:
> world states contain multiple predictive factors that may interfere.

These are independently testable.

That is much stronger than treating:
> "discovery"

as one benchmark score.

---

# S88 — New scientific-FM taxonomy: where does the domain's causal structure enter?

Combining files 06–08 yields a more complete placement map.

---

## 1. Token / representation unit

Examples:
- Carbon hybrid DNA tokenizer;
- Molexar chemical fragments;
- BioMatrix structure tokens;
- SciReasoner structural evidence units.

Question:
> what should count as one scientific symbol?

---

## 2. Objective

Examples:
- JEPA-DNA latent segment prediction;
- JEPA-Anything factorized predictive objective;
- Carbon FNS restoring nucleotide-level supervision.

Question:
> what information should training force the model to predict?

---

## 3. Explicit context / known nuisance

Examples:
- lunar acquisition geometry;
- intervention/action variable;
- scientific initial/boundary conditions.

Question:
> what is known externally and should not be re-inferred?

---

## 4. Architecture / state decomposition

Examples:
- STELLAR semantic vs localization state;
- JEPA-Anything predictive factors;
- genomic SSMs.

Question:
> what quantities require separate state channels because their invariances differ?

---

## 5. Executable environment / verifier

Examples:
- ScienceIDE;
- MindForge.

Question:
> what real-world behavior turns scientific knowledge into feedback?

---

## 6. Research process / harness

Examples:
- ScienceBuddy.

Question:
> what procedural knowledge should persist outside model weights?

---

## 7. Downstream consumer

Examples:
- Monroe + TabPFN.

Question:
> is the representation weak, or is the inference/readout mechanism weak?

---

# S89 — A new warning: "unification" can happen at different layers

Recent scientific systems all say some version of:
> unified.

But:

### BioMatrix
unifies raw modalities into one token space.

### SciReasoner
unifies structure types into addressable evidence for reasoning.

### JEPA-Anything
unifies the predictive operator, not the raw input representation.

### ScienceIDE
unifies environment interface/reward contract across heterogeneous codes.

### ScienceBuddy
unifies interaction feedback into two adaptation loops.

These are not substitutes.

Therefore:

> **"unified scientific foundation model" has nearly zero technical specificity.**

A paper must say:
> what exactly is shared, and what remains domain-specific.

---

# S90 — Research-instrument audit for this batch

## ScienceIDE — HIGH
Public:
- 4B/9B/72B models;
- 15 full environments currently exposed in main repo;
- 30/85 hard tasks exposed in preview repo;
- SFT recipe;
- RL recipe;
- matched base→SFT comparisons;
- environment verifier logic.

Caveat:
- complete environment/task registry remains partially held out / work in progress.

## ScienceBuddy — HIGH/MEDIUM
Public:
- simplified experiment code;
- Qwen3.5-4B setting;
- fixed splits;
- bounded harness/RL cycles.

Caveat:
- production workspace source not fully open.

## JEPA-Anything — HIGH
Public:
- reusable core;
- paired baseline/method checkpoints across multiple domains on HF;
- inference commands;
- task-design tooling.

Caveat:
- repo/HF release is actively evolving;
- domain-specific datasets and evidence must be audited per experiment.

## BioMatrix — HIGH
Public:
- 1.7B/4B CPT and SFT;
- SFT data;
- structure tokenizer implementations;
- explicit known limitations.

## SciReasoner — CURRENTLY MEDIUM/LOW
Public:
- paper/project/code skeleton;
- detailed task/result tables.

Caveat:
- weights/evaluation artifacts were still marked forthcoming in checked repo.

---

# S91 — Current conclusion

The scientific/HF frontier suggests a new workflow for reading domain foundation models:

Do not start from:
> model architecture.

Start from:

1. **What is the scientific state?**
2. **What relation/intervention changes it?**
3. **What part of the state is observed vs latent?**
4. **What is known nuisance/context?**
5. **What evidence certifies a prediction?**
6. **What part should be represented, predicted, generated, or executed?**
7. **What is the public matched artifact that lets us test that choice cheaply?**

Only after this should we care about:
> whether the backbone is Transformer, SSM, JEPA, MoE, diffusion, or autoregressive.

This remains literature calibration, not a topic menu.
