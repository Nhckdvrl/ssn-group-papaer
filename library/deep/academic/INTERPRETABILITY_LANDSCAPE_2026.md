# Interpretability Landscape 2025–2026

**Last verified:** 2026-09-29  
**Role:** academic genealogy / field map. This is not a candidate list.

## 0. Why this map exists

The repository has already learned a costly lesson: starting from a guessed behavioral anomaly, constructing a toy setting, and then applying probes / DAS / SAE / circuit tools is a poor default research process. The behavior may not survive; the synthetic endpoint may be seed-unstable; the interpretation may be identified only conditional on a convenient instrument; and mature mechanistic-interpretability literature may already own the phenomenon.

For current search, interpretability methods are therefore treated as **measurement instruments**, not idea generators.

The central 2025–2026 field movement is:

> neuron/head hunting → learned features/circuits → causal abstractions → evaluation, identifiability, actionability, dynamics, and model comparison.

The important scientific question is increasingly not merely *“can we produce an interpretation?”* but:

> **what evidence warrants a mechanistic claim, under which mediator, intervention, distribution, and analysis choices?**

---

## 1. Surveys / foundations worth starting from

### S1 — Open Problems in Mechanistic Interpretability (TMLR 2025)
Sharkey et al.  
https://arxiv.org/abs/2501.16496

**Parent state:** a rapidly growing collection of circuit, feature, patching, probing, and dictionary-learning tools.

**Pressure:** deeper model understanding still lacks agreed units, scalable validation, and clear connection to concrete scientific/engineering goals.

**Reusable move:** treat MI as a science with unresolved measurement and abstraction problems, rather than a bag of visualization methods.

### S2 — Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability (JMLR 2025)
Geiger et al.  
https://www.jmlr.org/papers/v26/23-0058.html

Unifies activation/path patching, mediation, causal tracing, circuit analysis, SAE-style features, DAS, steering, etc. under causal abstraction.

**Changed premise:** mechanistic explanation should be an explicit high-level causal model related to the low-level network through intervention-preserving maps; correlation/readability alone is not enough.

### S3 — The Quest for the Right Mediator (Computational Linguistics 2026)
Mueller et al.  
https://aclanthology.org/2026.cl-1.10/

The most useful current NLP-centered map. It organizes methods by **causal mediator** and search procedure rather than surface tool names.

**Key pressure:** the field has little unity; evaluations are often ad hoc; papers often say “mechanism” without explicitly defining the causal units.

**Research-search lesson:** mediator choice is itself a scientific assumption.

### S4 — Towards Intrinsic Interpretability of Large Language Models (ACL 2026)
Gao et al.  
https://aclanthology.org/2026.acl-long.1605/

Five design families: functional transparency, concept alignment, representational decomposability, explicit modularization, latent sparsity induction.

**Why keep:** reminds us that post-hoc MI is not the only route. A future territory may change the architecture/training objective so that useful abstractions are easier to identify.

### S5 — Locate, Steer, and Improve (Findings ACL 2026)
Zhang et al.  
https://aclanthology.org/2026.findings-acl.502/

Organizes actionable MI as localization → intervention/steering → improvement.

**Warning:** “we can steer a direction” still does not by itself prove that the direction is the naturally used mechanism.

### S6 — Position: Interpretability Can Be Actionable (ICML 2026)
Orgad et al.  
https://arxiv.org/abs/2605.11161

Argues that the missing ingredient is often evaluation, not another method. Defines actionability through concreteness and validation.

**Strong search pressure:** does an interpretation provide comparative advantage for an external decision/intervention over cheaper black-box, logit, or activation baselines?

---

## 2. Method families and what they actually assume

### 2.1 Component / circuit localization

Typical instruments:
- activation patching / path patching;
- causal tracing;
- attribution patching;
- automated circuit discovery.

Assumption under stress:
> a sparse subgraph selected by one perturbation/evaluation procedure corresponds to a stable mechanism.

Current pressure:
- first-order attribution approximations can fail under downstream nonlinearity;
- different discovery/evaluation choices can return very different structures;
- structurally different circuits may still implement the same computation.

Important references:
- **MIB** (ICML 2025): https://proceedings.mlr.press/v267/mueller25a.html
- **When Attribution Patching Lies** (2026 preprint): https://arxiv.org/abs/2606.09899
- **Many Circuits, One Mechanism** (TMLR 2026 Featured): https://arxiv.org/abs/2606.06267
- **Explanation Multiplicity** (Aug 2026 preprint): https://arxiv.org/abs/2608.13754

**Current boundary:** another circuit for another behavior is usually too weak. Circuit *evidence standards* remain scientifically live.

### 2.2 Distributed causal variables / DAS / causal abstraction

Typical instruments:
- interchange interventions;
- DAS / Boundless DAS;
- subspace alignment;
- causal abstraction metrics.

Core appeal:
> test whether a hypothesized high-level variable can be causally exchanged in the model.

Fundamental 2025 pressure:
**The Non-Linear Representation Dilemma** (NeurIPS 2025)  
https://proceedings.neurips.cc/paper_files/paper/2025/hash/dbb98528c9870377f3f0d133aae6050b-Abstract-Conference.html

Unrestricted nonlinear alignment can map essentially any network to any algorithm; random LMs can achieve perfect/near-perfect IIA. Thus causal abstraction becomes vacuous without assumptions about the encoding map.

2026 follow-ups / collisions:
- **Validating Causal Abstraction Metrics on Simulated Complex Systems**: https://arxiv.org/abs/2607.00267
- **Bucketing the Good Apples**: https://arxiv.org/abs/2605.02234
- **When Does Linear Causal Abstraction Work? Mapping the Boundary on the Grassmannian** (Zenodo/preprint): https://zenodo.org/records/21325349

**Open pressure:** how should mediator expressivity, held-out interventions, negative controls, mapping complexity, and representation assumptions jointly constrain a mechanistic claim?

### 2.3 Sparse autoencoders / dictionary learning

Parent belief:
> superposition makes neurons poor units; learned sparse features may recover a more natural basis.

Field movement:
- monosemanticity → scalable SAE training → benchmark/evaluation → consistency / identifiability.

Key references:
- **SAEBench** (ICML 2025): https://proceedings.mlr.press/v267/karvonen25a.html
- **Sparse Autoencoders Trained on the Same Data Learn Different Features** (ICLR 2026): https://proceedings.iclr.cc/paper_files/paper/2026/hash/3c1fe56b043848b211030c202764c6a7-Abstract-Conference.html
- **Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs** (ACL 2026): https://aclanthology.org/2026.acl-long.99/

Current facts that matter:
- proxy/reconstruction metrics do not reliably imply practical interpretability utility;
- identical model+data with different SAE seeds can yield markedly different dictionaries;
- “SAE feature = true model feature” is therefore too strong; an SAE is better treated as a useful decomposition unless stronger evidence is supplied.

**Saturation warning:** generic “SAE stability/consistency” is already an active owned line.

### 2.4 Crosscoders / model diffing

Scientific object:
> what changed between two models after training, fine-tuning, or architecture/model updates?

Key lineage:
- Anthropic crosscoder model diffing (2024–2025);
- **Overcoming Sparsity Artifacts in Crosscoders to Interpret Chat-Tuning** (NeurIPS 2025): https://papers.nips.cc/paper_files/paper/2025/hash/9902a53031ebbbab73898028073d4790-Abstract-Conference.html
- **Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences** (ICLR 2026): https://proceedings.iclr.cc/paper_files/paper/2026/hash/3b939edfdf9c1211fb764a888078f13d-Abstract-Conference.html
- **Cross-Architecture Model Diffing with Crosscoders** (2026 preprint / Anthropic Fellows): https://arxiv.org/abs/2602.11729
- **Delta-Crosscoder** (2026): https://arxiv.org/abs/2603.04426
- **Diff Mining: Logit Differences Reveal Finetuning Objectives** (Aug 2026): https://arxiv.org/abs/2608.26462

Crucial pressures:
1. L1 crosscoder artifacts can falsely label shared concepts as fine-tune-specific.
2. Narrow model organisms can leave trivially readable activation traces; they may be poor proxies for realistic broad post-training.
3. A very cheap **output-logit-difference** method now outperforms state-of-the-art model-diffing methods on some finetune-objective discovery evaluations.

This makes model diffing unusually attractive as a **measurement-science workbench**:
> when do internal diffing tools reveal something behavior/logit baselines cannot, and when are they merely an expensive decomposition of an already-visible delta?

Do not turn this into “another crosscoder architecture” before running strong baselines.

### 2.5 Temporal / developmental interpretability

Key reference:
**Crosscoding Through Time** (ACL 2026)  
https://aclanthology.org/2026.acl-long.60/

Tracks feature emergence, maintenance, discontinuation and causal importance across checkpoints.

**Opportunity:** training trajectory as object.

**Risk:** training dynamics / checkpoint biography is already crowded. Avoid “feature X appears at step Y” unless it changes a broader scientific inference.

### 2.6 Long-horizon / autoregressive interpretability

2026 is moving from static single-forward-pass analyses toward multi-token reasoning traces and dynamic causal influence.

Examples:
- FlashTrace / long-horizon interpretability;
- sequential activation patching;
- dynamic causal interpretability for reasoning.

**Status:** fast-moving and increasingly crowded. Not currently the default workbench recommendation.

### 2.7 Natural-language / automated explanations

Anthropic **Natural Language Autoencoders** (May 2026) turn internal activations into text descriptions:
https://www.anthropic.com/research/natural-language-autoencoders

This sits alongside auto-interpretation agents, Neuronpedia explanations, and attribution-graph summaries.

**Core unresolved issue:** fluency/readability of an explanation is not the same as causal faithfulness or unique identification.

### 2.8 Intrinsic interpretability

Instead of explaining an opaque model after training, modify architecture/objective so computation is more decomposable.

**Status for this repo:** intellectually important but potentially training-heavy. Keep as a long-horizon territory rather than immediate execution unless a strong public baseline makes intervention cheap.

---

## 3. The 2026 reliability pressures that matter most

### P1 — Mediator identifiability
A successful probe/DAS/SAE fit may reflect a flexible coordinate system rather than a model-intrinsic variable.

### P2 — Explanation multiplicity
Different seeds, datasets, hyperparameters, patching choices, or circuit objectives can yield different explanations.

### P3 — Functional equivalence vs structural difference
Different circuits can implement the same mechanism. Structural overlap alone is the wrong target.

### P4 — Intervention validity
A causal intervention can push the model off the natural activation manifold or activate dormant pathways; causal effect is not automatically evidence of natural use.

### P5 — Proxy metric mismatch
Reconstruction, sparsity, IIA, attribution score, and interpretability-agent judgments each validate different things.

### P6 — Comparative advantage / actionability
If a simple behavior/logit/activation-difference baseline finds the same actionable change more cheaply, an internal interpretation needs a stronger justification.

### P7 — External validity of model organisms
Narrow fine-tunes and synthetic tasks are useful ground-truth instruments, but can create unrealistically salient traces. They should be one rung of an evidence ladder, not the final scientific object.

---

## 4. What current top-conference work teaches about scale

Strong 2025–2026 interpretability papers tend not to be:
> “we found feature X for behavior Y.”

They more often change the **measurement object or evidential premise**:

- **MIB (ICML 2025):** method progress needs standardized causal-variable/circuit evaluation.
- **SAEBench (ICML 2025):** better proxy metrics do not guarantee practical interpretability.
- **Non-Linear Representation Dilemma (NeurIPS 2025):** unconstrained causal alignment can be vacuous.
- **SAE seed instability (ICLR 2026):** learned feature dictionaries are not canonical by default.
- **Narrow Finetuning / ADL (ICLR 2026):** a strong simple baseline changes what model-diffing results mean.
- **Feature Consistency (ACL 2026):** reproducibility itself becomes an evaluation axis.
- **Crosscoding Through Time (ACL 2026):** a method opens a new scientific object—representation development—not just a prettier visualization.
- **Interpretability Can Be Actionable (ICML 2026):** explanation quality should be tied to external decisions/interventions.

Reusable research move:

> **interpretability instrument → stress-test its scientific claim → locate what evidence survives → only then improve the instrument or use it to answer a new question.**

---

## 5. Explicit no-go patterns for this repository

Do not default to:

1. guess a surprising LLM behavior → construct dataset → probe/SAE/DAS → call it mechanism;
2. find a linear direction → say the model “knows/recognizes” the concept;
3. find a causal steering effect → infer the direction is naturally used;
4. train one SAE → interpret its dictionary as the canonical feature inventory;
5. discover two different circuits → infer two different mechanisms;
6. invent a new interpretability metric without strong negative controls;
7. use only one toy/model-organism setting and claim a general interpretability law;
8. use a more expressive mediator solely because it improves IIA;
9. interpret narrow fine-tuning artifacts as evidence about broad post-training;
10. build another tool when a simple black-box/logit/activation baseline has not been exhausted.

The repository's archived procedural-history line is especially relevant: unstable endpoints + conditional mechanistic analysis + survivor bias are a reason to stop, not a reason to switch from DAS to SAE/probes and keep rescuing the same mother problem.

---

## 6. Current territory shortlist after ownership audit

### T-MI-A — Mechanistic evidence / mediator identifiability
**Status:** WORKBENCH-WORTHY, but broad and collision-sensitive.

Parent:
- causal abstraction + MIB.

Pressure:
- nonlinear alignment can be vacuous;
- SAE/circuit explanations can be non-unique;
- interventions can be OOD;
- metrics can validate the wrong object.

Natural workbench question:
> under what constraints does a discovered causal mediator provide evidence about the model rather than evidence about the flexibility of our analysis pipeline?

Do not start with a new metric or nonlinear method. Start from existing baselines + negative controls + held-out interventions.

Nearest-prior risk is high: Non-Linear Dilemma, CAE, Grassmannian preprint, circuit multiplicity. The workbench must compare and compose these pressures rather than re-prove one of them.

### T-MI-B — Model diffing as a measurement instrument
**Status:** WORKBENCH-WORTHY and currently more execution-friendly.

Parent:
- crosscoders / BatchTopK crosscoders / ADL / DFC / Delta-Crosscoder.

New pressure:
- crosscoder sparsity artifacts;
- unrealistic narrow-finetune traces;
- simple activation differences can be extremely strong;
- Aug-2026 **Diff Mining** shows output logit differences can beat SOTA internal diffing on finetune-objective discovery.

Natural workbench question:
> what kinds of model changes actually require access to internals to discover or explain, and what kinds are already recoverable from output/logit deltas?

Strong artifact:
https://github.com/science-of-finetuning/diffing-toolkit

This is attractive because it supports strong-baseline residency before method invention.

### HOLD — Intrinsic interpretability
Large scientific upside, but training-heavy and broad. Revisit when there is a concrete public baseline and a pressure that can be explored within local compute.

### DEPRIORITIZE — Generic SAE consistency, generic circuit stability, generic long-horizon reasoning tracing
Important topics, but 2026 nearest-prior density is already high enough that a generic workbench risks starting inside someone else's active paper.

---

## 7. Library rule going forward

For any interpretability workbench:
1. state the **claim level** precisely: decodable / represented / causally manipulable / naturally used / algorithmically explanatory / actionable;
2. name the mediator and search procedure;
3. include negative controls;
4. distinguish in-distribution fit from held-out intervention generalization;
5. test simple black-box/logit/activation baselines;
6. require at least one external-validity rung beyond a single synthetic organism before candidate promotion.
