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

## 7. Research-space map after field-first reading — 2026-09-29

This section deliberately records **research spaces**, not paper ideas or literature gaps.

A paper existing inside a space is positive evidence that the space has real objects, baselines, and pressure. Do not kill an entire space because one local question has been studied.

### SPACE-A — Developmental / population-level mechanistic science

**Core object**

> How does computation form during training, and which aspects of the resulting mechanism are forced by the task/training regime versus contingent on stochastic training history?

This is broader than “track feature X over checkpoints” and broader than “do different seeds learn the same head”.

**Strong parents / substrate**
- **PolyPythias** (ICLR 2025): 50 pretraining runs, 5 scales, about 7k checkpoints; its paper explicitly leaves circuit formation × training-state-transition relations for future interventional study.
- **Crosscoding Through Time** (ACL 2026): aligns features across checkpoints and tracks emergence / maintenance / discontinuation plus causal importance.
- developmental-attention / rLLC work: head differentiation and specialization through training.
- cross-seed/generalizability work: e.g. 1-back heads show strong developmental but weaker positional correspondence.
- **From Shortcut to Induction Head** (NeurIPS 2025): controlled evidence that training-data diversity can select different algorithms.
- **Mechanistic Data Attribution** (ICML 2026 Oral): specific training samples can causally accelerate/delay interpretable mechanism formation.
- **Influence Dynamics and Stagewise Data Attribution** (ICLR 2026): sample influence itself changes across learning stages.

**Why this is a field space rather than a gap**

Existing work supplies different axes but does not collapse them into one answer:
- checkpoint time;
- random seed;
- model scale;
- initialization vs data ordering;
- training-data influence;
- feature/circuit causal importance.

The broad scientific object is the **developmental causality of learned computation**.

A useful conceptual graph is:

```
data / initialization / ordering / stage
                 ↓
       training-state transition
                 ↓
      mechanism formation / choice
                 ↓
      behavior / generalization
```

**Available baseline**
- Pythia / PolyPythias checkpoints;
- decoupled 160M data-seed vs weight-seed variants, subject to artifact verification;
- Crosscoding Through Time implementation;
- induction-head / previous-token-head score datasets;
- TransformerLens / patching / intervention stack.

**Important artifact warning**
A 2026 issue reports possible inconsistency between some published `pythia-160m-weight-seed{1,2}` step-0 initializations and later checkpoints. Any attempt to use the clean initialization-vs-data-order decomposition must independently verify checkpoint provenance first.

**What exploration should look like**
Not a preregistered “seed instability” hypothesis. First build a mechanism population map:
- which functional mechanisms appear across runs;
- when they appear;
- whether the same function appears in the same components or only in functionally equivalent implementations;
- whether runs bifurcate and later reconverge;
- whether data-order or initialization perturbations predict the branch;
- whether mechanism trajectory predicts robustness/generalization beyond endpoint performance.

**Top-conference ceiling**
Potentially high: a result can change how mechanistic claims generalize across model instances and how training science thinks about algorithm selection.

**Main risk**
Small models and familiar mechanisms (1-back / induction / IOI) can make the work look like another toy circuit paper. The workbench must eventually reach a broader principle than one circuit and should use causal/function-level equivalence rather than raw head overlap.

**Status:** STRONG RESEARCH SPACE. Not yet a workbench.

---

### SPACE-B — Mechanism provenance / developmental data causality

**Core object**

> Which data, and at which training stage, create or reshape a computation inside the model?

This sits at the intersection of mechanistic interpretability, training-data attribution, and learning dynamics.

**Strong parents**
- **Mechanistic Data Attribution**: influence-function attribution from training samples to interpretable heads, with causal data addition/removal interventions.
- **Influence Dynamics and Stagewise Data Attribution**: influence is non-stationary and can peak or change sign around developmental transitions.
- **Concept Influence** / related 2026 work: attribution to internal concepts/features rather than only outputs.
- developmental interpretability supplies the mechanism trajectory to be explained.

**Why this is larger than “find induction-head training examples”**
Current papers establish that:
1. data influence can be stage-dependent;
2. data can causally change mechanism formation;
3. mechanisms themselves change over training.

The broader open scientific territory is how these three objects interact.

**Baseline-first exploration**
A future workbench should start from already-known mechanisms and already-trained multi-checkpoint runs, then ask whether attribution predicts *changes in mechanism trajectory*, not invent a new behavior and search for influential documents.

**Top-conference ceiling**
High if it reveals a transferable law relating data structure / learning stage / mechanism formation / generalization, or leads to a principled training intervention.

**Main risk**
Becoming ordinary data selection or influence-function engineering. The mechanism trajectory must remain the scientific object.

**Status:** STRONG RESEARCH SPACE; closely coupled to SPACE-A.

---

### SPACE-C — Stateful / adaptive computation interpretability

**Core object**

> What computation is implemented when model state itself changes during inference?

Traditional MI usually assumes fixed parameters and analyzes one forward computation. TTT, fast-weight memory, learned recurrent state, and test-time adaptation weaken that assumption.

**Strong parents / baselines**
- **End-to-End TTT**: next-token-prediction updates compress context into weights; public 125M/1B/3B checkpoints.
- **In-Place TTT** (ICLR 2026 Oral): pretrained LLM MLP projections used as fast weights; public Qwen/Llama stack.
- **TTT-NTP**: asks explicitly what each test-time write should store; multiple open 0.6B–8B backbones.
- **GradMem** (ICML 2026): explicit WRITE / READ meta-learned memory.
- **TTT with KV Binding Is Secretly Linear Attention** (ICML 2026): a broad KVB class that looked like online learning can be rewritten as learned linear attention.
- **Test-Time Regression** (JMLR 2026): unifies attention, SSMs, fast-weight programmers, and online learners as associative-regression designs.

**Central field pressure**

The phrase “test-time learning” currently covers computationally different objects.

At one extreme, gradient syntax can merely implement a fixed recurrent/attention-like operator. At another, end-to-end or task-coupled updates may implement genuine online specialization.

The research space is therefore not “look at fast-weight update norms”, but understanding the **functional regimes of mutable inference-time state**.

**Natural axes**
- fixed operator vs genuinely update-dependent computation;
- write objective;
- update order / direction sensitivity;
- read/write compatibility;
- addressability;
- persistence/interference;
- task specialization;
- whether equivalent fixed-state operators can reproduce the behavior.

**Top-conference ceiling**
High because it can change the conceptual understanding of an emerging architecture family, not merely interpret one model.

**Main risks**
Very fast-moving; strong unifying theory already exists. A workbench must empirically expose a functional boundary not already implied by Test-Time Regression / MIRAS / KVB equivalence.

**Status:** STRONG HOLD / RESEARCH SPACE. Do not register yet.

---

### SPACE-D — Global / compositional mechanisms

**Core object**

> Are model capabilities assembled from reusable computational primitives, and at what abstraction level can such primitives be meaningfully identified?

**Strong parents**
- **Towards Global-level Mechanistic Interpretability / ModCirc** (ICML 2025): proposes reusable task-agnostic modular-circuit vocabulary.
- **How Much Do Circuits Tell Us?** (2026): component-level circuits are highly consistent and causally important but often not task-specific; much of the overlap is generic MLP infrastructure / attention sinks.
- instruction-vector / selector work suggests reusable representations may control which circuits execute.
- modular reasoning papers find analogous but non-identical subcircuits across tasks/models.

**Real tension**
“Reuse” at coarse component level may mean:
1. true reusable computational primitive; or
2. generic shared infrastructure that every task needs.

Those are scientifically different.

**What a healthy workbench would do**
Start from multiple existing tasks and strong circuit baselines, then ask which decomposition predicts:
- transfer to unseen tasks;
- compositional reuse;
- targeted intervention;
- functional interchangeability.

Do not merely optimize circuit overlap or invent another extraction score.

**Top-conference ceiling**
High if the work reveals the correct abstraction level for global model computation.

**Main risk**
The experimental object is less crisp than SPACE-A. It can easily become a circuit-method paper.

**Status:** PROMISING RESEARCH SPACE / HOLD.

---

### SPACE-E — Interpretability-guided learning and intervention

**Core object**

> When does knowledge of internal computation provide a better intervention target than ordinary optimization signals?

This is the most method-friendly space.

**Strong parents**
- **Towards Understanding Fine-Tuning Mechanisms via Circuit Analysis** (ICML 2025): circuit dynamics → circuit-aware LoRA.
- **Mechanistic Unlearning** (ICML 2025): high-level mechanism localization → more robust editing/unlearning.
- **From Insight to Action** (ACL 2026): causal SAE task features → feature-resonant data selection.
- **Where CoT Reasoning Commits** (ACL Findings 2026): process-level head dynamics → selective head fine-tuning.

**Changed premise**
Interpretability is not only descriptive. Internal structure can be used as a control signal for:
- where to update;
- what data to select;
- what to edit/unlearn;
- which components to freeze;
- what to intervene on at inference.

**The important research pressure**
The scientific bar is not “MI-guided method beats random selection”.

A strong project must establish why the internal signal has **incremental intervention value** over:
- gradient magnitude;
- loss / uncertainty;
- influence functions;
- Fisher / curvature;
- activation magnitude;
- simple parameter sensitivity;
- standard data-selection or PEFT heuristics.

The desired paper shape is:

```
real optimization failure
→ internal-mechanism analysis
→ bottleneck / controllable target
→ minimal intervention
→ benchmark + ablation + mechanism validation
```

**Top-conference ceiling**
High and especially compatible with method + analysis papers.

**Main risk**
Degenerating into an interpretability-score heuristic zoo.

**Status:** STRONG RESEARCH SPACE; needs a real baseline failure before workbench registration.

---

### SPACE-F — Intrinsic interpretability

**Core object**

> Can useful computation be made interpretable by construction rather than recovered post hoc?

**Strong parents**
- intrinsic-interpretability survey (ACL 2026);
- **Prototype Transformer** (ICML 2026);
- CB-LLM / concept-bottleneck families;
- interpretable recurrent / modular architecture work.

**Pressure**
Post-hoc decompositions suffer from non-identifiability and multiplicity. Intrinsic models attempt to make the computational interface itself human-legible.

**Top-conference ceiling**
Potentially very high.

**Main risks**
Training-heavy; architecture novelty is crowded; readable bottlenecks can still leak information or coexist with opaque computation.

**Status:** WATCHLIST, not preferred immediate workbench under current resource/process constraints.

---

## 6A. Deep genealogy notes — how strong interpretability papers actually grow

**Added after a process correction on 2026-09-29.**

A nearby paper is **not** a reason to kill a territory. Mature top-conference work nearly always grows inside a dense lineage. The useful question is:

> what pressure did the parent leave unresolved, what premise changed, and what new scientific object became measurable?

The lineages below are recorded to train research navigation, not to nominate paper ideas.

### GENEALOGY-1 — Induction heads → function vectors → mechanism competition → mechanism selection

#### Parent state 1: circuits establish a concrete computational mechanism
- Elhage et al., **A Mathematical Framework for Transformer Circuits** (2021)
- Olsson et al., **In-context Learning and Induction Heads** (2022)

The important move was not merely “an attention head correlates with copying”. Induction heads were connected to a concrete algorithmic pattern and their formation during training coincided with a sharp improvement in an ICL-related token-loss measure.

At this stage a reasonable field belief became:

> induction heads are an important mechanism behind in-context learning.

#### Pressure 1: a different mechanism explains the same high-level capability
- Hendel et al., **In-Context Learning Creates Task Vectors** (2023)
- Todd et al., **Function Vectors in Large Language Models** (ICLR 2024)  
  https://proceedings.iclr.cc/paper_files/paper/2024/hash/4ae163cb8788970e53b4fd9578141139-Abstract-Conference.html

Function-vector work did not treat induction-head papers as “the territory is occupied”. It changed the mediator and the functional question: can a compact task representation be causally transported and reused outside the original demonstrations?

The strong evidence was intervention: adding the task vector can recover/trigger task behavior in zero-shot or unrelated contexts.

#### Pressure 2: two plausible mechanisms now conflict
- Yin & Steinhardt, **Which Attention Heads Matter for In-Context Learning?** (ICML 2025)  
  https://proceedings.mlr.press/v267/yin25e.html

This paper is an especially important search-process exemplar.

**Reconstructed genesis:** once induction heads and FV heads both had credible causal evidence for “ICL”, the next good question was not to invent a third head type. It was to put the two mechanisms in the *same experimental frame*.

The paper first verifies that the two head sets are actually distinct, then uses matched ablations across 12 models / 45 tasks. It finds FV heads matter much more for ordinary few-shot ICL, especially at scale.

Crucially, it does **not** simply declare the older work wrong. It reconstructs why the literature diverged:
1. Olsson-style “ICL score” (late-token vs early-token loss) and ordinary few-shot ICL accuracy are different outcomes;
2. induction and FV scores are correlated, so naive ablation is confounded;
3. scale changes the relative importance of the mechanisms.

Then training trajectories reveal that some FV heads begin as induction heads and later transition.

**Reusable research move:**

> two mature explanations coexist → align definitions/metrics → control confounds → compare causally → trajectory resolves apparent contradiction.

This is exactly why “paper X exists” is not a kill criterion.

#### Pressure 3: if multiple algorithms are possible, what selects one?
- Kawata et al., **From Shortcut to Induction Head: How Data Diversity Shapes Algorithm Selection in Transformers** (NeurIPS 2025)  
  https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html

This paper changes the question again. The object is no longer “what mechanism exists?” but:

> why does training select a generalizable induction algorithm rather than a positional shortcut that fits the same training task?

The pressure comes from shortcut/generalization literature plus induction-head theory. The changed premise is that task success does not identify the learned algorithm.

The revealing controlled experiment/theory varies **data diversity** while the task remains solvable by both mechanisms. Increased diversity weakens positional shortcuts and selects induction.

**Reusable move:**

> known mechanism + competing solution + matched training success → manipulate training pressure → study algorithm selection.

This is a much stronger template for future model science than “find behavior anomaly, then explain it”.

#### What this lineage teaches search

The lineage did not close after Olsson 2022. It became *more scientifically productive* because each parent made the next distinction possible:

mechanism existence → alternative mechanism → causal competition → developmental relation → training pressure selecting mechanisms

When searching a mature area, ask what the newest parent **made measurable**, not merely what keyword it already contains.

---

### GENEALOGY-2 — Superposition → SAEs → scaling → benchmark/construct validity → feature semantics

#### Parent state: neurons are often polysemantic
- Elhage et al., **Toy Models of Superposition** (2022)

The pressure was representational: if many concepts are superposed in fewer dimensions, neurons are a poor semantic unit.

#### Changed representation: sparse dictionary learning
- Bricken et al., **Towards Monosemanticity** (2023)
- Templeton et al., **Scaling Monosemanticity** (2024)

These works did not originate from “SAE is fashionable”. The scientific premise was that sparse latent features might be a better decomposition than neurons.

**Documented genesis in Towards Monosemanticity:** the authors considered sparse architectures and ordinary dictionary-learning-style approaches, encountered practical/interpretive problems, and developed SAE-style decomposition as an existence proof.

Scaling work then asks whether the decomposition survives at frontier scale.

#### Pressure: SAE-method zoo outruns evaluation
- Karvonen et al., **SAEBench** (ICML 2025)  
  https://proceedings.mlr.press/v267/karvonen25a.html

By 2024–25 many SAE variants improved sparsity/reconstruction tradeoffs. SAEBench changes the premise:

> a better unsupervised proxy is not automatically a better interpretability tool.

It compares 200+ SAEs over multiple architectures and evaluation axes, finding proxy gains do not consistently predict downstream interpretability/application gains.

**Reusable move:**

> successful method family → method zoo → strong common benchmark → discover which apparent improvements are real.

This is analogous to EDM / ResNet-Strikes-Back style research navigation.

#### New pressure: what kind of object does an SAE recover?
2026 work then branches rather than ending the field:
- **Sparse Autoencoders Trained on the Same Data Learn Different Features** (ICLR 2026): seed changes produce substantially different dictionaries.
- **Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs** (ACL 2026): consistency becomes an explicit evaluation axis.
- **Automated Interpretability Metrics Do Not Distinguish Trained and Random Transformers** (ICLR 2026): some popular metrics have weak construct validity.
- **Do Sparse Autoencoders Identify Reasoning Features?** (ICML 2026): falsification-oriented tests expose lexical/confounding explanations for candidate reasoning features.
- **Sparse Autoencoders are Topic Models** (ICML 2026): reframes what the SAE objective naturally extracts.
- **PolySAE** (ICML 2026): relaxes the linear additive decoder assumption to model feature interactions.

The correct conclusion is **not “SAEs are solved / killed.”**

The lineage is differentiating several scientific questions:
- canonical recovery vs useful basis;
- semantic labeling vs causal role;
- linear atoms vs compositional interactions;
- reconstruction vs intervention utility;
- local feature interpretation vs trajectory/model comparison.

For topic search, the danger is entering at the wrong abstraction level (“another SAE architecture”) rather than finding a scientific pressure that makes a new axis load-bearing.

---

### GENEALOGY-3 — Sparse circuits → automated discovery → stability/reuse → abstraction-level crisis

#### Parent state
Manual reverse engineering establishes sparse computational graphs for specific tasks.

Automation follows:
- ACDC and related automated circuit-discovery methods;
- MIB later standardizes circuit-localization evaluation.

#### Pressure: task-specific circuits do not answer global questions

Two different papers push out from the local-circuit paradigm:

- Sun, **Circuit Stability Characterizes Language Model Generalization** (ACL 2025)  
  https://aclanthology.org/2025.acl-long.442/
- He et al., **Towards Global-level Mechanistic Interpretability: Modular Circuits** (ICML 2025)  
  https://proceedings.mlr.press/v267/he25x.html

Circuit Stability changes the use of circuits: the circuit is no longer only an explanation of one behavior; stability/equivalence across subtasks becomes a possible signal of generalization.

ModCirc asks whether task-specific circuits can be replaced by a reusable vocabulary of task-agnostic computational modules.

These are **new scientific objects created by a mature baseline**, not “gaps in circuit extraction”.

#### New pressure: structural reuse may not mean functional modularity

- Li & Subramani, **How Much Do Circuits Tell Us? Measuring the Consistency and Specificity of Language Model Circuits** (2026)  
  https://arxiv.org/abs/2605.08348

Component-level circuits are highly consistent but often nonspecific across tasks; much shared structure consists of MLP blocks / generic attention-sink infrastructure. Neuron-level circuits become more specific but less consistent.

This creates a real abstraction problem:

> coarse units are reproducible but generic; fine units are specific but unstable.

#### Further pressure: structural difference may not imply mechanistic difference

- Bayat Makou et al., **Many Circuits, One Mechanism** (TMLR 2026)  
  https://arxiv.org/abs/2606.06267

Input statistics can yield structurally different circuits that transfer across conditions and appear functionally interchangeable. A common core recovers almost all performance.

So the lineage develops:

find sparse graph → automate extraction → ask stability/generalization → seek reusable modules → discover specificity–consistency tension → discover functional equivalence classes

**Search lesson:** the promising object is often the *level of abstraction at which a mechanism becomes stable and predictive*, not “another circuit extraction method”. But the exact paper question still has to be found experimentally.

---

### GENEALOGY-4 — Final-checkpoint interpretation → developmental interpretability

#### Parent state
Most MI work studies a frozen final checkpoint. Separate training-dynamics work tracks:
- behavioral curves;
- parameter movement;
- activation similarity;
- knowledge acquisition.

Those two literatures leave a mismatch:
- MI can make fine-grained conceptual/causal claims, but usually at one time;
- training-dynamics work sees trajectories, but often at coarse behavioral/representation level.

#### Crystallization
- Bayazit et al., **Crosscoding Through Time** (ACL 2026)  
  https://aclanthology.org/2026.acl-long.60/

The paper explicitly builds from this mismatch.

Crosscoders solve a technical obstacle: separate SAEs at different checkpoints live in incomparable feature spaces. A joint feature space makes feature emergence / persistence / disappearance traceable. RelIE then asks when a feature becomes causally important.

The paper deliberately compares checkpoints from the **same training run** to avoid tokenizer/data/objective confounds, and validates across Pythia, BLOOM, and OLMo.

Important limitations from the paper itself:
- checkpoint selection affects conclusions;
- early checkpoints are hard to interpret;
- benchmark concepts may not reflect real-world variation;
- attribution is not a strict causal guarantee;
- human-readable feature aliasing remains a risk;
- crosscoder cost grows with model/checkpoint count.

**Reusable move:**

> two mature literatures expose complementary blind spots → import an existing instrument (crosscoder) to make a new longitudinal scientific object measurable.

This is the kind of growth we should imitate. The novelty is not “crosscoder + checkpoints” syntactically; it is making *representation development* experimentally addressable.

---

### GENEALOGY-5 — Big functional hypothesis → converging mechanistic tests

Anthropic, **A Global Workspace in Language Models** (2026)  
https://www.anthropic.com/research/global-workspace

This is useful as a contrasting research style.

The work does **not** start from an odd benchmark failure. Its starting point is a broad functional distinction from cognitive science:

> some information is reportable, deliberately controllable, flexibly reusable and involved in deliberate reasoning, while much computation remains automatic.

The Jacobian lens is developed to operationalize one key property: representations positioned to influence what the model *could say*.

Crucially, the work then stacks multiple tests rather than treating readout as explanation:
- reportability;
- voluntary modulation;
- causal swap/intervention;
- silent multi-step reasoning;
- flexible reuse of one representation by different downstream tasks;
- selective ablation separating higher-order from automatic behavior;
- post-training changes;
- training interventions that alter internal workspace content and behavior.

**Reusable move:**

> natural high-level functional hypothesis → operationalize several independent predictions → invent/use tools only as needed → demand converging causal evidence.

This is closer to field-shaping scale than “feature X correlates with behavior Y”.

The paper also leaves a genuine research program (e.g. what controls workspace entry), but those statements should **not** be copied as ready-made topics. The useful asset is the question-forming process.

---

### Meta-lesson from the genealogies

Do **not** use this rule:

> nearby paper exists → territory dead.

Use this rule instead:

1. What was the **parent capability / method / scientific belief**?
2. What did the new paper make newly measurable or newly questionable?
3. Is the next question merely “same thing on another model”, or does the parent create a **new experimental object**?
4. Can we enter through a strong baseline and let experiments choose among multiple plausible stories?
5. If the first expected outcome fails, does the lineage still have informative branches?

A dense lineage can be *better* than an empty literature cell because it gives:
- trustworthy baselines;
- reusable artifacts;
- agreed phenomena;
- multiple competing explanations;
- clear experimental pressure.

The search goal is therefore not to find an untouched keyword. It is to find a **live scientific object whose parent lineage has become mature enough to support discovery, but whose next important distinction is not yet crystallized**.

---

### Current field-level comparison

Do **not** interpret this as a ranking of paper ideas. It is a map of where baseline residency currently looks most informative.

| Space | Scientific object | Baseline/artifact maturity | Experiment-first discoverability | Main danger |
|---|---|---:|---:|---|
| A Developmental/population mechanisms | how computation forms and varies across training histories | very high | very high | small-model / one-circuit trap |
| B Mechanism provenance | which data/stage causes mechanisms to form | high | high | becoming data-attribution engineering |
| C Stateful/adaptive computation | what mutable test-time state actually computes | high | high | fast-moving / theory catches up |
| D Global/compositional mechanisms | reusable computational primitives | medium-high | medium | circuit-method abstraction drift |
| E MI-guided intervention | when internals give better control targets | high | high once a real failure exists | heuristic zoo |
| F Intrinsic interpretability | interpretable computation by construction | medium-high | medium-low | training cost / architecture zoo |

### Current search policy

The next workbench should emerge from **baseline residency in one of these spaces**, not from a paper-title gap.

Most promising exploration strategy at this point:

1. **SPACE-A/B as one connected developmental-science territory**: exploit multi-seed/dense-checkpoint public models to understand how stochastic training and data influence mechanism formation.
2. **SPACE-C as an independent architecture/model-science territory**: understand functional regimes of adaptive inference-time state.
3. Keep **SPACE-E** as the preferred route if exploration in A/B/C exposes a controllable bottleneck; it is a paper-shape, not the initial question.

No new interpretability workbench is authorized by this map alone.

---

## 7. Library rule going forward

For any interpretability workbench:
1. state the **claim level** precisely: decodable / represented / causally manipulable / naturally used / algorithmically explanatory / actionable;
2. name the mediator and search procedure;
3. include negative controls;
4. distinguish in-distribution fit from held-out intervention generalization;
5. test simple black-box/logit/activation baselines;
6. require at least one external-validity rung beyond a single synthetic organism before candidate promotion.
