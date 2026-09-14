# 2026-09-14 — Wall-Problem Immersion I

**Mode:** LONGITUDINAL SCIENTIFIC IMMERSION  
**Input:** `2026-09-14_STANDING_IMPORTANT_PROBLEMS_STATE.md` + `2026-09-14_STANDING_PROBLEM_TASTE_SELECTION.md`  
**Candidate generation:** **OFF**  
**L-series / K-series:** **NO CHANGES IN THIS DOCUMENT**  
**Goal:** understand how beliefs inside WALL-A/B/C/D actually changed over multiple years, and identify live disagreements before generating any paper idea.

---

# 0. Evidence labels

Every source is treated as evidence about a standing problem, not as an anchor for a successor paper.

- **SUPPORTS** — strengthens a belief already in the wall state.
- **CONTRADICTS** — makes two currently plausible beliefs hard to hold simultaneously.
- **IDENTIFIES** — introduces an operation/quantity that changes what can be inferred.
- **REFINES** — changes the level or unit of explanation without resolving the problem.
- **IRRELEVANT** — excellent work that does not materially update this wall problem.

The point of the exercise is to become comfortable with **IRRELEVANT**. Reading a strong paper creates no obligation to create a project.

---

# 1. WALL-A — Reusable abstractions

> **What would make us believe the same abstract computation is actually reused across different linguistic realizations?**

## 1.1 Historical belief trajectory

### Stage A1 — behavioral evidence can reveal latent linguistic state

**Futrell et al., NAACL 2019 — _Neural language models as psycholinguistic subjects: Representations of syntactic state_.**  
https://aclanthology.org/N19-1004/

The paper uses controlled psycholinguistic experiments to ask whether recurrent LMs behave as if they maintain incremental syntactic states. It finds evidence for basic syntactic-state representations and shows that lexical cues can update those states.

**Update:** behavioral contrasts can provide evidence that a model tracks an abstract linguistic state rather than only local surface statistics.

**But the unresolved inference is already visible:** several internal computations could generate the same behavioral interaction. “Behavior is consistent with representation X” is not yet “the model implements X.”

**Label:** SUPPORTS the existence of meaningful abstract-state hypotheses, but exposes an identification gap.

---

### Stage A2 — decodability/local correlation is not enough; require counterfactual implementation

**Geiger, Potts & Icard, 2023 — _Causal Abstraction for Faithful Model Interpretation_.**  
https://arxiv.org/abs/2301.04709

This line formalizes a much stronger claim: a high-level causal model is a faithful abstraction of a neural network only if interventions on the hypothesized high-level variables correspond to interventions in the low-level neural system in the right counterfactual way.

This changes the evidence standard. A representation can be decodable, localized, or predictive without playing the causal role assigned by the theory.

**Update:** the object moves from “information is present” to “the network implements a high-level causal model.”

**Label:** IDENTIFIES — gives a formal operation for testing implementation rather than correlation.

---

### Stage A3 — the high-level variable itself may be distributed and basis-dependent

**Geiger et al., CLeaR 2024 — _Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations_.**  
https://proceedings.mlr.press/v236/geiger24a.html

Earlier causal-abstraction methods often assumed high-level variables map to disjoint neurons or easily enumerable alignments. Distributed Alignment Search removes both restrictions: variables may live in distributed subspaces and individual neurons may participate in multiple roles.

**Update:** failure to find a neuron/component corresponding to a theory variable does not imply the variable is absent. The correct alignment itself is an empirical object.

**Label:** REFINES the unit of representation; prevents false rejection of distributed abstractions.

---

### Stage A4 — linguistic mechanisms are not necessarily learned gradually

**Arora, Jurafsky & Potts, ACL 2024 Outstanding — _CausalGym_.**  
https://aclanthology.org/2024.acl-long.785/

CausalGym explicitly contrasts behavioral psycholinguistic evidence with causal mechanism evidence and benchmarks interventional methods on linguistic tasks. In Pythia training trajectories, NPI licensing and filler–gap mechanisms emerge in discrete stages rather than as a smooth strengthening of the same mechanism.

**Update:** endpoint abstraction and formation history are distinct objects. A behavior can improve smoothly while the underlying mechanism changes qualitatively.

**Label:** IDENTIFIES/REFINES — adds training time as an axis on which computational implementation can change.

---

### Stage A5 — systematic computation can emerge after a heuristic phase

**Wu, Geiger & Millière, ICML 2025 — _How Do Transformers Learn Variable Binding in Symbolic Programs?_**  
https://proceedings.mlr.press/v267/wu25j.html

The model passes through random prediction, a shallow early-assignment heuristic, and finally a systematic mechanism in which the residual stream functions as an addressable memory and attention heads route bound values. The model acquires a classical-looking computational primitive despite lacking an explicit binding module.

**Update:** a network can move between qualitatively different algorithms while solving the same nominal task; the existence of a systematic abstraction is therefore a developmental claim, not just an endpoint claim.

**Label:** SUPPORTS + REFINES.

---

### Stage A6 — causal reuse across constructions can inform linguistic theory

**Boguraev, Potts & Mahowald, EMNLP 2025 Outstanding — _Causal Interventions Reveal Shared Structure Across English Filler–Gap Constructions_.**  
https://aclanthology.org/2025.emnlp-main.1271/

Distributed interchange interventions provide evidence that multiple filler–gap constructions converge on similar abstract internal analyses. Crucially, the analysis also exposes frequency, filler-type, and contextual factors that complicate standard linguistic theory.

This is a much stronger use of interpretability than “find the circuit”: the high-level hypothesis is independently supplied by linguistic theory; causal transfer tests shared implementation; residual failures become theory-relevant.

**Update:** internal causal evidence can adjudicate *sharing* claims, not just localization claims.

**Label:** IDENTIFIES.

---

### Stage A7 — one high-level causal model may still be the wrong explanatory unit

**Pîslar, Magliacane & Geiger, CLeaR 2025 — _Combining Causal Models for More Accurate Abstractions of Neural Networks_.**  
https://proceedings.mlr.press/v275/pislar25a.html

The authors begin from a practical limitation of causal abstraction: one proposed high-level algorithm often only partially captures a network’s reasoning. Combining multiple simple high-level causal models and allowing the network to occupy different computational states gives more faithful explanations on toy tasks.

This is not a minor method patch. It destabilizes a tacit assumption in many mechanistic narratives:

> there exists one compact abstraction that the model “really implements” across all relevant inputs.

**Update:** the correct scientific explanation may be a state-dependent family of abstractions rather than one universal mechanism.

**Label:** CONTRADICTS the strongest single-abstraction reading; REFINES the standing problem.

---

## 1.2 What the history has actually taught us

The field-level trajectory is:

> behavioral signature  
> → representational hypothesis  
> → causal implementation criterion  
> → distributed alignment  
> → developmental mechanism change  
> → cross-construction causal reuse  
> → possibility of multiple computational states.

The unresolved problem has therefore **moved**. It is no longer simply:

> “Does the model represent abstract variable X?”

A more mature wall state is:

> **When is a high-level variable stable enough across inputs, lexical items, constructions, and training stages that it deserves to be called a reusable abstraction, and when is the apparent unity only a local approximation to several computations?**

This is still a standing problem, not a paper RQ.

## 1.3 Live internal disagreements / frictions

### A-F1 — universality vs computational states

Cross-construction transfer supports shared variables, while combined-causal-model work says a single abstraction may only partially explain a network. Both can be true only under a **conditional notion of reuse**.

### A-F2 — high-level theory selection

Causal abstraction can test a specified high-level model, but it does not by itself tell us **which high-level theory is scientifically privileged**. A powerful alignment optimizer can find a representation compatible with a convenient theory; independent theory constraints remain essential.

### A-F3 — causal mediation vs systematic reuse

A variable may causally mediate one local behavior without supporting productive transfer. “Causal” and “systematic” are not synonyms.

### A-F4 — endpoint reuse vs acquired reuse

A shared mechanism at the final checkpoint might have emerged from several heuristics or might later be replaced. Formation history is evidence about abstraction, not merely a training detail.

### A-F5 — behavioral OOD generalization and internal reuse need not coincide

A model can sometimes generalize behaviorally via a new heuristic; conversely a genuine reusable primitive may be present but not selected by the response policy. Linking the two remains nontrivial.

## 1.4 Things that should now be marked IRRELEVANT to WALL-A

- generic neuron/feature localization;
- probe accuracy;
- patching a representation without an independently specified causal variable;
- another phenomenon where behavior merely “suggests abstraction”;
- mechanistic work that cannot distinguish local mediation from cross-context reuse.

## 1.5 Wall-state update

**WALL-A remains PRIMARY.**

But the target has become sharper:

> not “find abstract representations,” but understand the **conditions of causal reuse and explanatory stability** of high-level variables.

No candidate generated.

---

# 2. WALL-B — Formation of inductive bias

> **Why does learning prefer one generalization over another when both fit the observed evidence?**

## 2.1 Historical belief trajectory

### Stage B1 — manipulate the language, not just the learner

**Ravfogel, Goldberg & Linzen, NAACL 2019 — synthetic variations of natural languages.**

A central methodological move in this lineage is to create controlled versions of natural-language structure so that properties normally entangled in corpora become separately testable.

**Update:** inductive bias can be studied experimentally by holding training setup fixed while changing the structural regularities available to the learner.

**Label:** IDENTIFIES, historically.

---

### Stage B2 — parameter count is not the bias; architecture and input distribution matter differently

**Mueller & Linzen, ACL 2023 — _How to Plant Trees in Language Models_.**  
https://aclanthology.org/2023.acl-long.629/

The paper diagnoses preference for hierarchical rather than linear generalizations after pretraining. Number of parameters alone does not explain hierarchical generalization; depth matters more than width. Child-directed speech can induce hierarchical bias with roughly an order of magnitude less data than web/Wikipedia-style corpora.

**Update:** “bigger model / more data” is not a satisfactory account of structural bias. The *form* of architecture and data distribution matters.

**Label:** CONTRADICTS crude scale explanations; SUPPORTS interactional formation accounts.

---

### Stage B3 — bias can be deliberately acquired before natural-language learning

**Papadimitriou & Jurafsky, EMNLP Findings 2023 — _Injecting structural hints_.**  
https://aclanthology.org/2023.findings-emnlp.563/

Synthetic pretraining is used to alter the learner’s structural prior before training on English, Japanese, and Basque. Different artificial structures lead to different downstream learning outcomes.

**Update:** a model’s “inductive bias” need not be a fixed property of architecture. It can be an **acquired prior** produced by earlier learning.

**Label:** IDENTIFIES a formation operation; REFINES the meaning of inductive bias.

---

### Stage B4 — strong claims about human-possible bias need learning-trajectory evidence

**Kallini et al., ACL 2024 Best — _Mission: Impossible Language Models_.**  
https://aclanthology.org/2024.acl-long.787/

Rather than ask only whether a model can eventually fit a language, the study compares learning trajectories across English and systematically constructed impossible languages. GPT-2 learns the impossible languages less readily, challenging the strongest “equally learnable” claim.

**Update:** endpoint capacity and **relative learnability / trajectory** are different evidence about bias.

**Label:** IDENTIFIES a more relevant observable for the theoretical claim.

---

### Stage B5 — acquired bias can transfer through internal machinery

**Hu et al., ACL 2025 Outstanding — _Between Circuits and Chomsky_.**  
https://aclanthology.org/2025.acl-long.478/

Formal-language pre-pretraining improves natural-language acquisition particularly when the formal language captures dependency structure and fits the model’s computational limitations. The work further reports that attention heads acquired in formal pre-pretraining remain important for later syntactic evaluations.

**Update:** prior learning does not merely alter scalar sample efficiency; it can leave reusable computational machinery that changes later acquisition.

**Label:** IDENTIFIES/REFINES the route from experience to bias.

---

### Stage B6 — move from global bias to the exact indirect evidence supporting a grammatical exception

**Leong & Linzen, Journal of Memory and Language 2026 — passivization constraint learning.**  
https://doi.org/10.1016/j.jml.2026.104751

The object is a classic acquisition problem: productive grammatical rules have lexical exceptions, and direct negative evidence is limited. The authors manipulate LM training data to identify sources of indirect evidence that allow learners to infer which verbs resist passivization.

**Update:** “the learner has a structural bias” is too coarse. A mature acquisition account must identify **which evidence supports which generalization or exception**.

**Label:** IDENTIFIES.

---

### Stage B7 — possible/impossible LM experiments are explicitly becoming a program, not a one-off benchmark

**Kallini & Potts, Behavioral and Brain Sciences 2026 — _Language models as tools for investigating the distinction between possible and impossible natural languages_.**  
https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/language-models-as-tools-for-investigating-the-distinction-between-possible-and-impossible-natural-languages/4746025E15F0817E081DE4C3803A8FF3

The article explicitly argues for LMs as tools for uncovering inductive biases relevant to human language learning.

**Update:** the open scientific object is not “do transformers have bias?” but how to build a linking theory from controlled model learning to human-possible language.

**Label:** SUPPORTS the standing problem and raises the evidence bar.

---

## 2.2 What the history has actually taught us

The concept of **inductive bias** has changed underneath the field.

A naive view is:

> architecture has a fixed bias; data reveals it.

The accumulated lineage instead suggests:

> **effective bias at time t = architecture × optimizer × prior learning × current evidence × developmental trajectory.**

The important conceptual update is that **the prior is itself learned**. In modern foundation models, asking “what is the transformer’s inductive bias?” without specifying its learning history may be badly posed.

That is a standing insight, not yet a candidate.

## 2.3 Live internal disagreements / frictions

### B-F1 — intrinsic vs acquired bias

Possible/impossible learning differences can be read as architecture-level preference, but formal pre-pretraining demonstrates that prior experience can install transferable biases. How much of a mature model’s “bias” is intrinsic to architecture versus acquired from earlier learning remains unresolved.

### B-F2 — ability vs preference vs sample efficiency

A model may eventually learn both generalizations while strongly preferring one early. Capacity, final accuracy, learning speed, and data efficiency are distinct quantities.

### B-F3 — natural evidence vs experimental identification

Naturalistic corpora preserve the acquisition object but contain many correlated cues. Synthetic transformations isolate causal factors but can create a learner/environment unlike natural acquisition. This is a **fundamental design tension**, not a nuisance control issue.

### B-F4 — mechanism of transfer

A pretraining experience can alter later learning, but whether transfer occurs via reusable circuits, representational geometry, optimization initialization, or simpler statistical priors is not generally settled.

### B-F5 — model bias vs human bias

Even a clean bias in LMs is not automatically evidence about humans. The linking hypothesis is part of the theory, not an optional discussion section.

## 2.4 Things that should now be IRRELEVANT to WALL-B

- arbitrary curriculum/data-order sweeps;
- “model A generalizes more hierarchically than B” without a formation account;
- more impossible-language variants as inventory expansion;
- parameter-count correlations;
- base-vs-instruct or pretrain-vs-post-train comparisons without genuine competing generalizations.

## 2.5 Wall-state update

**WALL-B remains PRIMARY**, but its mature form is now:

> **How is a preference among compatible generalizations formed over learning history, and which evidence / mechanisms make that preference persist or change?**

No candidate generated.

---

# 3. WALL-C — Expressivity → learnability → learned algorithm

> **Why does optimization discover one computation rather than another that the architecture could also implement?**

## 3.1 Historical belief trajectory

### Stage C1 — formal expressivity is useful, but it is only a prerequisite

**Strobl et al., TACL 2024 — _What Formal Languages Can Transformers Express? A Survey_.**  
https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00663/120983/

The survey explicitly separates expressivity from trainability: expressivity asks what a transformer can represent; trainability asks what it can learn from examples. Theoretical transformer results also depend strongly on idealization assumptions.

**Update:** capacity results cannot by themselves explain empirical learning.

**Label:** SUPPORTS the wall distinction.

---

### Stage C2 — optimization itself creates a reduced effective hypothesis class

**Merrill et al., EMNLP 2021 — _Effects of Parameter Norm Growth During Transformer Training_.**  
https://aclanthology.org/2021.emnlp-main.133/

The paper studies inductive bias produced by gradient descent and parameter-norm growth. As parameters grow, the network approaches a saturated regime with reduced effective capacity, linkable to formal-language/automata classes.

**Update:** the trained model’s effective computational class can be much narrower than the raw architecture’s representational family because of optimization dynamics.

**Label:** IDENTIFIES a concrete training-induced restriction.

---

### Stage C3 — formal expressivity can systematically over/underpredict realistic learnability

**Hahn & Rofin, ACL 2024 — _Why are Sensitive Functions Hard for Transformers?_**  
https://aclanthology.org/2024.acl-long.800/

The paper starts from scattered empirical learnability failures such as PARITY and low-degree bias and explicitly notes that existing expressiveness theory can overpredict or underpredict realistic learning. It connects input-space sensitivity to loss-landscape geometry: highly sensitive functions occupy isolated parameter-space solutions and are harder for transformers to learn/generalize.

**Update:** a property of the *function + loss geometry*, not representability alone, can predict what optimization selects.

**Label:** IDENTIFIES a candidate selection-law quantity.

---

### Stage C4 — empirical learnability needs quantities defined on the target distribution itself

**Borenstein et al., ACL 2024 — _What Languages are Easy to Language-Model?_**  
https://aclanthology.org/2024.acl-long.807/

Instead of treating LMs as classifiers of unweighted formal languages, this work studies probabilistic languages — the actual type of object a language model represents. RLM rank and expected sampled-string length significantly predict empirical learnability across RNN and Transformer LMs, with some architecture-specific patterns.

**Update:** learnability can depend on graded distributional complexity that is invisible to a binary language-recognition class.

**Label:** REFINES the scientific object and SUPPORTS a quantitative learnability theory.

---

### Stage C5 — architecture restrictions can add a computational operator instead of only removing capacity

**Li & Cotterell, ACL 2026 Best — _Characterizing the Expressivity of Local Attention in Transformers_.**  
https://aclanthology.org/2026.acl-long.1739/

Under the analyzed idealization, local attention contributes a second temporal operator and is expressively complementary to global attention; neither simply subsumes the other. Hybrid local/global attention has the richest fragment and the theory is corroborated by formal and natural-language experiments.

**Update:** intuitive monotonic stories such as “global sees more, therefore is strictly more capable” can be wrong. Architectural restrictions change the **kind** of computation available.

**Label:** CONTRADICTS naive capacity monotonicity; SUPPORTS operator-level theories.

---

### Stage C6 — representational succinctness still does not guarantee gradient discovery

**Bergsträßer, Cotterell & Lin, ICLR 2026 — _Transformers are Inherently Succinct_.**  
https://proceedings.iclr.cc/paper_files/paper/2026/hash/5f7804e8855efe5554025217abc49315-Abstract-Conference.html

This theory introduces succinctness as expressive efficiency: transformers can represent some formal languages exponentially more compactly than standard representations.

**Zhao, Findings ACL 2026 — _Do Transformers Grok Succinct Algorithms?_**  
https://aclanthology.org/2026.findings-acl.1301/

The immediate empirical question is whether gradient-trained transformers actually converge to the predicted succinct circuits rather than heuristics. The work reports a grokking-like transition and a counting circuit consistent with the theoretical prediction in its synthetic setting.

**Update:** even a sharp theorem about an architecture predicts only an available solution; one still needs a theory of **algorithm selection by training**.

**Label:** IDENTIFIES the missing layer, but this exact parent is already occupied and must not be used as our seed.

---

## 3.2 What the history has actually taught us

The wall can be written as four nested sets that should not be conflated:

1. **Representable:** there exist parameters implementing computation X.
2. **Learnable:** realistic optimization/data can reach some good implementation of X.
3. **Preferred:** among many fitting solutions, training reliably selects X rather than Y.
4. **Stable/generalizing:** the selected computation continues to operate under length, distribution, or structural shifts.

Most theory establishes (1). A growing literature reaches toward (2). Much less is known about the general laws governing (3) and (4).

This is the deepest reason WALL-C remains alive.

## 3.3 Live internal disagreements / frictions

### C-F1 — no single complexity notion yet predicts algorithm selection across regimes

Sensitivity, rank, expected length, succinctness, symmetry, circuit complexity, norm/implicit regularization and other quantities each explain pieces. It is unclear whether they reduce to a common selection principle or genuinely govern different regimes.

### C-F2 — formal simplification vs natural relevance

The cleaner the formal task, the stronger the identification of a learned algorithm; the more natural the task, the harder it becomes to define the competing algorithms precisely. This is the central experimental tradeoff.

### C-F3 — optimization may change the effective architecture

Parameter growth, saturation, grokking, and learned routing can make the trained system computationally unlike the naïve architecture class used in an expressivity theorem.

### C-F4 — restrictions can improve both inductive bias and expressivity in different senses

Local attention shows that “restriction” is not a one-dimensional reduction. We need to stop treating architectural capacity as a scalar.

### C-F5 — mechanistic circuit recovery is evidence about one trained solution, not yet a general learning law

A discovered counting or binding circuit does not explain why another initialization/task/model should discover the same algorithm.

## 3.4 Things that should now be IRRELEVANT to WALL-C

- another formal-language benchmark with no candidate algorithm competition;
- another expressivity theorem with no learnability consequence;
- another grokking curve without a scientific selection variable;
- another architecture leaderboard;
- the already-owned “does GD find the succinct circuit?” parent.

## 3.5 Wall-state update

**WALL-C is upgraded from STRETCH to PRIMARY-THEORY WATCH.**

The genuinely open scientific layer is:

> **a selection theory over representable computations.**

But our future entry point must preserve natural-language relevance; toy formal tasks are evidence, not automatically the project.

No candidate generated.

---

# 4. WALL-D — Structure from resource constraints

> **What useful representation/computation emerges specifically because a natural resource is limited?**

## 4.1 Historical belief trajectory

### Stage D1 — memory and expectation need not be rival explanations

**Futrell, Gibson & Levy, Cognitive Science 2020 — _Lossy-Context Surprisal_.**  
https://doi.org/10.1111/cogs.12814

Sentence-processing theories often separated expectation-based difficulty (surprisal) from memory-based difficulty (e.g. dependency locality). Lossy-context surprisal computes expectations from an imperfect memory representation and thereby unifies major predictions from both traditions. It also derives information locality as a more general principle.

**Update:** resource limitations alter the *information state from which prediction is performed*, rather than simply adding an independent penalty after prediction.

**Label:** REFINES / UNIFIES.

---

### Stage D2 — specify which information should be forgotten by optimizing memory itself

**Hahn, Futrell, Levy & Gibson, PNAS 2022 — _A resource-rational model of human processing of recursive linguistic structure_.**  
https://pmc.ncbi.nlm.nih.gov/articles/PMC9618130/

Lossy-context theory left a major gap: which aspects of context are lost? The resource-rational model learns retention probabilities to minimize downstream processing effort under a memory-resource constraint. It predicts patterns in recursive sentence processing that neither expectation-only nor traditional memory-only accounts predict.

**Update:** memory loss is not arbitrary noise. The representation can be **optimized under a resource budget**.

**Label:** IDENTIFIES a formation principle.

---

### Stage D3 — resource allocation should be strategic at encoding time

**Xu & Futrell, Journal of Memory and Language 2026 — _Strategic resource allocation in memory encoding_.**  
https://doi.org/10.1016/j.jml.2025.104706

The theory predicts that unexpected information receives higher encoding precision because allocating scarce memory to informative content is efficient. The paper derives this as a resource-rational solution and reports reduced locality effects for high-surprisal material.

**Update:** limited memory does not imply uniform degradation. It predicts **content-dependent precision allocation**.

**Label:** IDENTIFIES / REFINES.

---

### Stage D4 — constraints can reshape the geometry/quality of neural representations

**Xu, Dillon & Futrell, ACL 2026 Best — _Memory efficiency and resource-rational encoding in sentence processing_.**  
https://aclanthology.org/2026.acl-long.1550/

Transformer hidden representations are trained under an explicit total encoding-precision constraint. The constrained models better predict human reading times and, crucially, their context representations become more compressed and categorical.

**Update:** a resource constraint is a **formation cause of representational structure**, not merely a source of performance degradation.

**Label:** IDENTIFIES the wall’s central phenomenon.

---

### Stage D5 — sequential information bottlenecks may shape language itself

**Futrell & Hahn, Nature Human Behaviour 2026 — _Linguistic structure from a bottleneck on sequential information processing_.**  
https://www.nature.com/articles/s41562-025-02336-w

Natural-language-like systematic structure emerges in codes constrained by predictive information / excess entropy.

**Update:** resource constraints may operate one level above online processing: they can help explain why communication systems evolve/learn structured forms in the first place.

**Label:** SUPPORTS a formation-cause view at a different explanatory scale.

---

### Stage D6 — limited computation can explain approximate inference, not just memory representation

**Clark et al., EMNLP 2025 — _Resource-Rational Noisy-Channel Language Processing_.**  
https://aclanthology.org/2025.emnlp-main.1207/

Sequential Monte Carlo under bounded computation trades computational resources against human-like noisy-channel inferences.

**Update:** “resource” is not one thing. Memory precision, retrieval, search/inference compute, and communication bandwidth can each impose different optimal algorithms.

**Label:** REFINES and warns against a generic bottleneck story.

---

### Stage D7 — representation and retrieval are separable hypotheses

**Yoshida et al., ACL 2025 — _If Attention Serves as a Cognitive Model of Human Memory Retrieval, What is the Plausible Memory Representation?_**  
https://aclanthology.org/2025.acl-long.483/

This line asks whether attention can instantiate a retrieval algorithm over token-level versus syntax-structured memory representations, reporting independent predictive contributions.

Together with ACL 2026 memory-efficiency work, it exposes an important decomposition:

> **what is encoded** and **how it is retrieved** are different scientific objects.

**Label:** REFINES; creates an explicit construct-separation requirement.

---

## 4.2 What the history has actually taught us

The mature program is no longer:

> memory is limited, therefore humans make errors.

It is:

> **a resource budget defines an optimization problem; the solution changes what information is encoded, at what precision, in what structure, and sometimes what communication system emerges.**

This is a strong scientific shape because the constraint makes **positive structural predictions**, not just deficits.

## 4.3 Live internal disagreements / frictions

### D-F1 — which resource is actually load-bearing?

Memory precision, retention probability, retrieval competition, inference samples, predictive information, time, and communication complexity are not interchangeable. Different resource theories may fit the same behavior for different reasons.

### D-F2 — encoding vs retrieval

A human-like memory effect may arise because the stored representation is compressed, because retrieval is noisy/competitive, or both. ACL 2026 explicitly argues that encoding quality and retrieval mechanism can dissociate.

### D-F3 — normative optimum vs descriptive human mechanism

A resource-rational solution says what an optimal bounded agent should do under a specified objective; it does not automatically establish that humans or trained LMs implement that solution for the same reason.

### D-F4 — imposed constraint vs naturally occurring pressure

Adding a bottleneck can make structure emerge, but this is scientifically strongest when the constraint corresponds to a real resource and its magnitude/structure is independently justified.

### D-F5 — same resource, different explanatory scale

A sequential-information bottleneck can be used to explain online sentence processing, learned neural representation, or population-level language structure. It is not obvious that the same optimization objective should operate identically across those scales.

## 4.4 Things that should now be IRRELEVANT to WALL-D

- arbitrary context truncation;
- generic compression/pruning/quantization;
- “smaller model generalizes better”;
- injecting noise without deriving what should be preserved;
- fitting a resource-rational story after observing an effect;
- treating every bottleneck as the same resource.

## 4.5 Wall-state update

**WALL-D is upgraded from SECONDARY to SERIOUS IMMERSION.**

It has unusually good question provenance because the theory predicts positive representational consequences of a constraint. Our current weakness is not scientific quality but intimacy with the exact resource-rational assumptions and linking hypotheses.

No candidate generated.

---

# 5. Cross-wall synthesis — without generating a paper

The purpose of cross-wall comparison here is **not** to combine WALL-A+B or WALL-C+D into a project. It is to identify the different scientific levels so we stop confusing them.

## 5.1 Four different “why” questions

### WALL-A — implementation

> Once a behavior exists, **what abstract computation is actually being reused?**

### WALL-B — formation of preference

> During learning, **why is one compatible generalization preferred over another?**

### WALL-C — algorithm selection

> Given many representable computations, **why does optimization converge to this algorithm?**

### WALL-D — objective/constraint-induced structure

> Given a natural resource limit, **what representation or algorithm should emerge because it is efficient under that constraint?**

These are related but not synonyms. Conflating them was one reason earlier ideas became bloated.

---

# 6. The strongest new meta-beliefs after immersion

These are **updates to our internal research state**, not candidate claims.

## MB1 — “Inductive bias” in foundation models is often acquired, not fixed

Pre-pretraining and training-data interventions show that prior experience can install biases that shape later learning. Therefore mature-model behavior should not be casually attributed to “the transformer architecture.”

**Confidence:** HIGH.

## MB2 — Causal representation is not enough; explanatory stability is the real abstraction problem

Causal abstraction raises the evidence standard beyond probing, but multi-state causal models show that a single abstraction can still be only locally faithful. Reuse across contexts/training regimes must be part of the claim.

**Confidence:** HIGH.

## MB3 — Expressivity is only level 1 of a four-level theory

Representable → learnable → preferred → stable/generalizing are distinct. Formal and empirical work increasingly attacks the middle levels, but there is no general selection law.

**Confidence:** HIGH.

## MB4 — Resource constraints can be constructive causes

The strongest resource-rational work predicts categorical/compressed representation and systematic linguistic structure as *solutions* to constraints, not merely damage from constraints.

**Confidence:** HIGH.

## MB5 — the most promising standing problems have changed level of explanation over time

Good lineages repeatedly move:

- behavior → causal implementation;
- architecture → learned prior;
- representability → optimization selection;
- performance cost → representational formation.

This is a stronger signal of a mature research program than a growing list of benchmark cells.

---

# 7. Revised immersion priority

After the first longitudinal pass:

| priority | wall | status | reason |
|---|---|---|---|
| **1** | **WALL-A — reusable abstractions** | **PRIMARY** | Strong theory ancestry + modern identifying operations + live dispute over universal vs state-dependent abstraction. |
| **2** | **WALL-B — formation of inductive bias** | **PRIMARY** | Deep language-science relevance; modern pretraining makes “prior” itself acquired; natural/synthetic identification tension remains real. |
| **3** | **WALL-D — structure from resource constraints** | **SERIOUS IMMERSION** | Exceptionally coherent multi-year lineage; constraints generate positive structure; need more intimacy with theory. |
| **4** | **WALL-C — algorithm selection** | **PRIMARY-THEORY WATCH** | Potentially deepest theoretical reward, but highest risk of drifting into toy formal-language work. |

This is not a candidate ranking.

---

# 8. What NOT to do next

Do **not** now generate:

- “shared abstraction under condition X”;
- “pretraining changes bias Y”;
- “which algorithm does model Z learn?”;
- “bottleneck X induces structure Y.”

Those are autocomplete descendants of the wall state.

The next immersion pass must instead search for **persistent disagreements / failed predictions / awkward empirical facts inside these lineages** — the equivalent of Ribeiro’s “failures I don’t understand.”

Specifically:

### WALL-A
Look for cases where two studies both claim a faithful abstraction but require different high-level variables; cases where causal variables fail to transfer across superficially same phenomena; and known limitations of causal abstraction as scientific evidence.

### WALL-B
Look for controlled cases where the same architecture/data regime develops different generalizations; biases that reverse with learning history; human/LM learning trajectories that disagree despite endpoint similarity; and evidence that current “inductive bias” explanations fail.

### WALL-C
Look for explicit gaps between theoretical representability predictions and experimentally learned algorithms; cases where different optimizers/regularizers select qualitatively different computations despite equal task fit; and candidate quantities that failed to generalize as learnability laws.

### WALL-D
Look for resource-rational predictions that fail, competing resource theories that explain the same phenomenon differently, and cases where an imposed constraint creates structure unlike humans/natural language.

Only **after collecting real frictions** should candidate generation be reconsidered.

---

# 9. Current decision

**No RQ seeds. No new L-series. No new kill IDs. No pilot.**

This pass has increased research intimacy and changed the standing state, which is the intended output.

The next artifact should be an **UNEXPLAINED FRICTIONS dossier**, not a candidate list.