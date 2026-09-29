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

## 6. Second-pass ownership audit — 2026-09-29

A deeper search after the first workbench registration materially changed the shortlist. This section is intentionally preserved as an anti-premature-convergence record.

### 6.1 Model diffing comparative advantage — DEMOTED

Missed direct prior:

**Simple LLM Baselines are Competitive for Model Diffing** (Kempf et al., 2026)  
https://arxiv.org/abs/2602.10371

It already formalizes model-diff desiderata (generalization, interestingness, abstraction), performs a systematic simple-LLM vs SAE comparison, and finds simple LLM methods competitive / often more abstract.

Combined with:
- **Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences** (ICLR 2026);
- **Diff Mining** (Aug 2026);
- crosscoder sparsity-artifact work;

the previously registered broad question “when do internals add value beyond simple external/logit/activation baselines?” is too directly occupied.

Repository action: `workbench/model-diffing-measurement/` was demoted to a knowledge asset on 2026-09-29.

### 6.2 Generic MI metric validity — DEPRIORITIZE

New critical prior:

**Automated Interpretability Metrics Do Not Distinguish Trained and Random Transformers** (ICLR 2026)

Many SAE reconstruction / auto-interpretability-style metrics can score random transformers surprisingly similarly to trained ones. This strengthens the warning that a metric can validate properties of the analysis pipeline rather than learned computation.

But generic “better MI evaluation” is itself crowded by:
- MIB;
- SAEBench;
- Non-Linear Representation Dilemma;
- **Who Guards the Guardians?** (UAI 2026), which stress-tests representation-identifiability metrics under varying data-generating processes / encoder geometry;
- **Certified Interventional Fidelity** (UAI 2026), which formalizes causal intervention fidelity with statistical guarantees.

Conclusion: do not open a generic evaluation-metric workbench.

### 6.3 Intervention naturality / off-manifold steering — DIRECTLY OCCUPIED

2026 work already studies causal interventions pushing representations off the natural activation distribution, distinguishes benign from harmful divergence, and develops manifold-aware steering; another line proves steered states can be non-surjective / unreachable by natural prompts.

Conclusion: “steering is off-manifold” is not a fresh mother question.

### 6.4 Circuit stability / transportability / prompt specificity — HIGHLY ACTIVE

Relevant 2025–2026 work includes:
- **Circuit Stability Characterizes Language Model Generalization** (ACL 2025);
- **Towards Universality** (ICLR 2025);
- numerical-comparison circuit universality (ICLR 2026);
- **Many Circuits, One Mechanism** (TMLR 2026);
- **Finding Interpretable Prompt-Specific Circuits in Language Models** (NeurIPS 2026);
- 2026 work on circuit robustness under task-preserving distribution shift;
- ICML 2026 MI-workshop work on surrogate/open-model explanations failing to transfer cleanly to closed/target models.

Conclusion: transportability is important, but the generic form is too active to register without a new concrete scientific object.

### 6.5 Model-organism external validity — REAL PRESSURE, BUT ALREADY ACTIVE

Two especially important 2026 references:

**The Model Organism Lottery: Model Organism Interpretability Strongly Depends on Training Methodology** (ICML 2026 MI Workshop)

Across 54 OLMo2-1B / Gemma-3-1B organisms and seven training methodologies, apparent interpretability changes substantially with SFT/DPO/integrated-training construction, even when the intended hidden behavior is similar. More realistic integrated training is often harder to interpret.

**Pando: Do Interpretability Methods Work When Models Won’t Explain Themselves?** (2026)

A large model-organism suite explicitly varies whether models provide faithful, absent, or misleading verbal explanations and compares black-box/white-box interpretability methods.

Conclusion: “model organisms may be too easy / unrepresentative” is a genuine field pressure, but not an empty workbench.

### 6.6 Representation exists vs representation is functionally used — REAL PHENOMENON FAMILY, ACTIVE

Multiple 2026 works independently find versions of:

> pretraining creates a readable representation; later instruction/alignment training changes whether/how that representation controls output.

Examples:
- **Decoded but Unused: Instruction Tuning Routes Moral Framing into the Judgment Readout**;
- **Tool Calling is Linearly Readable and Steerable in Language Models**;
- **Instruction Tuning Changes How Upstream State Conditions Late Readout**;
- refusal work showing base models contain discrimination structure later transformed into a causal refusal gate.

This is scientifically richer than “probe says the model knows X”, but generic representation→use/readout is now an active lineage.

### 6.7 Training selects mechanisms — STRONG SCIENTIFIC OBJECT, NOT YET OUR WORKBENCH

**From Shortcut to Induction Head: How Data Diversity Shapes Algorithm Selection in Transformers** (NeurIPS 2025) proves in a controlled transformer setting that training-data diversity can select between a positional shortcut and a generalizable induction-head algorithm.

Related work studies:
- training/architecture biases selecting different circuit solutions;
- circuit evolution under fine-tuning;
- SFT vs RL circuit preservation and forgetting;
- objective transitions during post-training.

This establishes that **mechanism selection by training pressure is a real scientific object**, but a workbench must not simply scale the NeurIPS-2025 synthetic result to “modern LLMs”.

### 6.8 Capability precursors / developmental forecasting — DIRECT NEW PRIOR

A September 2026 preprint, **Capability Emergence Can Be Forecast**, already turns mechanistic precursors into a calibrated forecasting task:
- previous-token-head formation predicts induction emergence per seed;
- blind preregistration;
- manufactured negative controls;
- public Pythia / OLMo / OLMo-2 checkpoint evidence.

Thus “can mechanisms emerge before behavior and forecast capability?” is no longer an empty mother question.

### 6.9 Scaling / mechanism phase transitions — INTERESTING, BUT FIRST PRIOR ALREADY EXISTS

**Architecture, Not Scale: Circuit Localization in Large Language Models** (2026) reports architecture-dependent circuit concentration and a scale-linked factual-recall circuit phase transition inside Qwen2.5.

Older induction-head / grokking / repeated-data work also directly links training/scaling phase transitions to circuit formation.

Conclusion: promising model-science territory, but not enough ownership separation yet.

### 6.10 Current disposition

After the second-pass audit:

- **no new active interpretability workbench is authorized yet**;
- the prematurely opened model-diffing workbench is demoted;
- generic SAE reliability, circuit stability, intervention naturality, model-organism validity, representation→readout, and precursor forecasting are all too directly occupied in generic form;
- the most scientifically interesting remaining pressure is **how training pressure selects / reorganizes computation in realistic model-training flows**, but nearest-prior density is still high and the exact independent object has not yet crystallized.

This is a better state than forcing a survivor.

---

## 7. Library rule going forward

For any interpretability workbench:
1. state the **claim level** precisely: decodable / represented / causally manipulable / naturally used / algorithmically explanatory / actionable;
2. name the mediator and search procedure;
3. include negative controls;
4. distinguish in-distribution fit from held-out intervention generalization;
5. test simple black-box/logit/activation baselines;
6. require at least one external-validity rung beyond a single synthetic organism before candidate promotion.
