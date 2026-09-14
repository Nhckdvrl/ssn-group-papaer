# 2026-09-14 — Standing Important Problems / Unexplained Frictions State

**Target:** ACL / EMNLP / NAACL Main scientific-question search  
**Mode:** LONG-TERM RESEARCH STATE — **NOT candidate generation**  
**L-series generation:** FORBIDDEN IN THIS document  
**Owner assassination:** FORBIDDEN at this layer unless needed to mark an entire standing problem as currently saturated  
**Purpose:** construct the persistent scientific state that strong human researchers appear to carry *before* reading the next frontier paper.

---

# 0. Why this is not another pressure-pool document

The repository has already built broad pressure taxonomies. Those were useful but still allowed a failure mode:

> read paper -> classify its provenance -> instantiate the same provenance pattern elsewhere -> generate a neighboring question.

This file instead stores **problems we would still care about if no paper from 2025–2026 existed**.

A standing problem is admitted only if:

1. it survives removal of the newest paper that reminded us of it;
2. it is scientifically meaningful before specifying a method;
3. it has a long intellectual ancestry or a repeatedly encountered real friction;
4. both major answer directions would change understanding;
5. it is broader than one benchmark, architecture, language, model family, or intervention;
6. a new frontier paper may **update** the problem state but may not create the problem ex nihilo.

The intended workflow is Hamming/Schulman/Ribeiro-style:

> keep important problems active -> learn something new -> ask whether it bears on one of them.

It is explicitly **not**:

> learn something new -> ask what paper can be written next to it.

The state is separated into:

- **ACTIVE** — important, scientifically rich, and not ruled out as a source of future questions;
- **WATCH** — important, but currently high-density / difficult to identify cleanly; keep the problem, suppress idea generation unless genuinely new leverage appears;
- **DORMANT** — important in principle but our recent search has repeatedly collapsed into crowded or low-reward formulations. New papers do not reopen it automatically.

No item below is a candidate. No L-number should be created from this file without a later independent question-generation and selection pass.

---

# 1. ACTIVE standing problems

## IP01 — What makes an internal representation a **reusable abstraction**, rather than a decodable correlate?

### Standing question

When a model behaves as though it knows an abstract linguistic or semantic variable — syntactic role, scope relation, event structure, discourse relation, logical variable, constructional dependency — what would justify saying that the model actually **implements and reuses** that abstraction across surface forms?

### Why this problem exists independently of current papers

Linguistics and cognitive science routinely posit abstract variables shared across superficially different expressions. Neural models can reproduce the behavior without making clear whether they use the same abstraction, multiple context-specific heuristics, or a distributed mixture whose apparent unity exists only at the output level.

This is a classical representation/implementation problem, not an interpretability fashion. The question is older than transformers: when does a physical/computational system implement a high-level computation rather than merely correlate with its outputs?

### Long-lineage anchors

- linguistic theories that posit shared syntactic/semantic structure across constructions;
- causal-abstraction work (Geiger, Icard, Potts, Goodman and collaborators, 2021–2025) asking when a neural system faithfully implements a high-level causal model;
- causal intervention work on filler–gap constructions (Boguraev, Potts & Mahowald, EMNLP 2025 Outstanding) using transfer of internal causal variables as evidence for shared structure.

### Persistent friction

- **Decodability is too weak:** almost any useful variable can often be decoded somewhere.
- **Localization is too weak:** finding a direction/component does not establish that the model treats it as the same variable across contexts.
- **Behavioral equivalence is too weak:** different algorithms can produce the same judgments.
- **Patching is not automatically identifying:** intervention semantics must be independently justified.

The core scientific friction is therefore:

> What invariances and counterfactual transfers distinguish a genuinely reused causal variable from multiple correlated, context-specific representations?

### Why we care

A clean answer changes what it means to say that a neural model has learned linguistic structure. It also decides whether internal model evidence can adjudicate theories that differ precisely in whether two phenomena share an abstraction.

### Cheap versions that are NOT this problem

- “Can feature X be linearly probed?”
- “Where in the model is X?”
- “Activation patching improves behavior, therefore X is causal.”
- “Two constructions have similar hidden states.”
- “They tested syntax; we test semantics.”

### State

**ACTIVE — HIGH VALUE, HIGH IDENTIFICATION BAR.**

A future paper bears on IP01 only if it supplies an independently meaningful high-level variable and a counterfactual test of **reuse/implementation**, not merely another probe.

---

## IP02 — Where do language-model **inductive biases** actually come from?

### Standing question

When a learner prefers one generalization over another under incomplete evidence, what creates that preference: architecture, optimization, training distribution, objective, curriculum, parameterization, scale, or interactions among them?

### Why this problem exists independently of current papers

The language-acquisition debate has always depended on what can be learned from experience and which biases must be supplied by the learner. Neural language models make this empirically attackable, but good benchmark performance does not reveal the source of the bias.

Tal Linzen and collaborators have pursued this question for years through synthetic language variants, controlled architecture/data manipulations, hierarchical generalization, child-directed input, formal-language pre-pretraining, and explicit manipulation of training evidence. Kallini and collaborators attack a related question through possible vs impossible language learnability.

The persistent scientific object is not “does an LM know syntax?” but:

> **What constraints on generalization emerge from which properties of the learning system?**

### Persistent friction

- Similar endpoint behavior can arise from different formation histories.
- Parameter count is repeatedly an inadequate explanation for structural generalization.
- Architecture and data can interact rather than contribute independently.
- Natural data contain many correlated cues, making attribution of a learned bias difficult.
- A model may eventually learn a pattern even if its **sample efficiency / developmental trajectory** strongly disfavors it.

### Why we care

This bears directly on both language-learning theory and model design. A theory that says “transformers can learn X” is much weaker than a theory predicting **when X becomes the preferred generalization**.

### Cheap versions that are NOT this problem

- another architecture leaderboard;
- another “base vs instruct” comparison;
- arbitrary data-order effects;
- synthetic task with no relation to a real competing generalization;
- “more data helps.”

### State

**ACTIVE — LONG-HORIZON.**

Recent data-order / curriculum parents are saturated, but the broader formation question remains fundamental. A future project must isolate a real competing generalization, not shop over training knobs.

---

## IP03 — What is the relationship between **expressivity, learnability, and learned algorithm**?

### Standing question

A model class may be able to represent a computation without gradient-based learning reliably finding it. Conversely, empirical models sometimes learn useful restrictions or algorithms not captured by coarse expressivity comparisons. What properties determine the gap between:

1. what a model can represent;
2. what it can learn from realistic evidence;
3. what optimization tends to select;
4. what it continues to use out of distribution?

### Long-lineage anchors

Ryan Cotterell / William Merrill / collaborators have built a program connecting neural LMs to formal automata, probabilistic formal languages, temporal logic, and precise architecture-level expressivity. Tal Linzen and collaborators have built a complementary program around empirical acquisition and structural generalization.

These are not two ingredients to combine for novelty. They expose a standing theoretical gap in machine learning itself: **capacity is not a learning theory**.

### Persistent friction

- Formal expressivity often predicts possibility but not preference.
- Optimization can strongly privilege a small subset of representable solutions.
- Restrictions can sometimes improve empirical modeling rather than simply reduce capacity.
- Length/generalization failures often reveal learned algorithm choice rather than lack of representational capacity.
- “The transformer can implement X” is routinely mistaken for an explanation of why trained transformers should learn X.

### Why we care

A satisfactory account could turn architecture folklore into conditional computational laws. It also gives a principled bridge between formal-language theory and empirical model behavior without requiring an application benchmark.

### Cheap versions that are NOT this problem

- proving another upper/lower bound with no empirical implication;
- measuring one formal language because it is convenient;
- observing grokking and calling it a theory;
- “architecture A gets higher accuracy than B.”

### State

**ACTIVE — VERY HIGH VALUE, THEORY-HEAVY.**

The strongest future questions should identify a quantity that predicts *which representable computation learning selects*.

---

## IP04 — How do **resource constraints reshape representations and algorithms**, rather than merely degrade performance?

### Standing question

When memory, computation, precision, context, communication bandwidth, or another natural resource is limited, how does an intelligent system reorganize what it represents and how it computes?

### Why this problem exists independently of current papers

Resource-rational cognitive science treats bounded resources as causes of structured behavior rather than nuisance limitations. Futrell, Levy, Gibson, Hahn and collaborators have spent years asking how memory and information-processing constraints shape sentence processing and even language structure.

Recent neural work strengthens rather than creates the standing question: explicit limits on memory precision can induce more categorical/compressed representations rather than simply lowering accuracy.

### Persistent friction

Typical ML scaling stories treat resources monotonically:

> more context / memory / parameters / computation = better.

But biological and engineered systems often develop **qualitatively different representations** under constraints. A restriction may improve generalization, robustness, human alignment, or compositional structure because the system is forced to discard or compress the right information.

The unresolved object is therefore not “does limiting X hurt performance?” but:

> **What representation/computation is optimal under a given resource constraint, and what qualitative structure should emerge?**

### Why we care

This can produce genuine scientific laws linking resource budgets to representation, and it naturally connects language processing, architecture, and learning without being benchmark-first.

### Cheap versions that are NOT this problem

- context-window ablation;
- pruning/quantization because efficiency is useful;
- “small models behave differently”;
- adding noise without a resource-rational prediction;
- fitting a post-hoc compression story to an arbitrary bottleneck.

### State

**ACTIVE — HIGH VALUE.**

Require a natural resource and a theory of optimal allocation/representation before designing the intervention.

---

## IP05 — What makes linguistic generalization **systematic**, and what are its true units of recombination?

### Standing question

Humans can use familiar pieces in novel structural combinations. Neural LMs often show impressive generalization but also sharp context-, frequency-, and formulation-dependence. What internal organization makes a generalization genuinely systematic rather than a dense patchwork of locally successful continuations?

### Why this problem exists independently of current papers

Systematicity/compositionality has been central to cognitive science and connectionism for decades. Modern LMs make old binary debates less useful: the empirical question is increasingly **which dimensions of systematicity emerge, under what learning conditions, and what computational units support them**.

### Persistent friction

- held-out accuracy can look compositional even when transfer collapses under a new recombination;
- syntactic and semantic generalizations can show different sensitivity to depth, frequency, or pretraining;
- the correct unit may be neither symbolic rule nor token association;
- models can possess abstract-looking variables while failing to reuse them in the exact counterfactual way a theory predicts.

### Why we care

This is a central scientific question about what kind of learner a language model is. It remains important even if every current compositional-generalization benchmark disappeared.

### Cheap versions that are NOT this problem

- another SCAN-like benchmark;
- new split engineering;
- “model X generalizes better”;
- treating any OOD drop as failure of compositionality;
- using mechanistic interpretability without first specifying what systematic reuse predicts.

### State

**ACTIVE, but must be theory-first.**

This problem is closely related to IP01–IP03; future generation should avoid duplicating them unless the scientific estimand is clearly distinct.

---

## IP06 — Which properties of human language arise from **efficiency / processing pressures**, and which require other explanations?

### Standing question

Natural languages exhibit recurring structural regularities across word order, morphology, dependency length, predictability, systematicity, and information distribution. To what extent are these structures solutions to communication and processing problems, and what exact constraints/objectives are required to derive them?

### Long-lineage anchors

Futrell, Gibson, Levy, Hahn and collaborators have developed a long program treating language as an efficient code under information-processing and memory constraints. The program is attractive because it tries to explain **why language has the structure it does**, not merely predict annotations.

### Persistent friction

- “efficiency” is not one quantity: memory, prediction, learnability, communicative accuracy, coding complexity, robustness and production costs can trade off.
- a model may fit one typological law while failing another because the assumed objective is incomplete.
- the same surface regularity can admit multiple efficiency explanations.
- many theories are evaluated by aggregate corpus correlation rather than decisive contrasts among objectives.

### Why we care

A successful result changes a scientific explanation of language form. It naturally supports law-like claims and counterfactual predictions.

### Cheap versions that are NOT this problem

- another correlation between surprisal and property Y;
- “languages are efficient” with a new metric;
- adding an LLM estimator to a typology paper;
- mining more languages without an explanatory competition;
- inventing a complexity quantity only because it improves classification.

### State

**ACTIVE — SCIENTIFICALLY ATTRACTIVE, HIGH CONSTRUCT-VALIDITY BAR.**

The right project must make two plausible explanatory accounts disagree on a natural quantity.

---

## IP07 — When can a language model serve as a **scientific model system** for human language, and what is the required linking hypothesis?

### Standing question

LMs can provide controlled learners, exact training histories, interventions impossible in humans, and large-scale behavioral predictions. But similarity between model and human behavior does not by itself establish that the same mechanism or learning pressure is responsible. When does evidence from an LM genuinely bear on a theory of human language learning/processing?

### Why this problem exists independently of current papers

This is now an explicit debate in linguistics and psycholinguistics. Futrell & Mahowald argue that LMs can be productive model systems without replacing linguistic theory; Kallini & Potts frame possible/impossible-language experiments as a phased program toward linking hypotheses; older work already treated neural LMs as psycholinguistic subjects.

### Persistent friction

- same behavior, different resource regime;
- same preference, different training history;
- high predictive accuracy on one human measure but not another;
- model intervention may reveal a computational possibility, not a human mechanism;
- human cognitive constraints can sometimes be imposed on models, but that risks building the answer into the model.

### Why we care

Without a linking theory, the rapidly growing “LLMs as cognitive models” literature risks oscillating between overclaiming and dismissiveness. A principled answer changes what evidence counts in computational cognitive science.

### Cheap versions that are NOT this problem

- “humans vs LLMs on phenomenon X”;
- another correlation with reading times;
- “LLMs are/aren’t human-like” as a scalar judgment;
- copying a classic psycholinguistic paradigm onto a new model;
- matching one human effect and inferring shared mechanism.

### State

**ACTIVE AS A META-SCIENTIFIC OBJECT.**

Future questions should target a concrete linking claim, not generic human-model similarity.

---

## IP08 — How are **semantic content, context, and pragmatic goals** combined into a decision about what an utterance means?

### Standing question

Language interpretation requires more than literal sentence meaning: listeners integrate alternatives, speaker intentions, discourse state, world knowledge, expectations about relevance, and uncertainty. Which parts are represented compositionally, which are inferred online, and when do pragmatic goals alter or override semantic defaults?

### Why this problem exists independently of current papers

This is a core semantics/pragmatics problem, not an LLM benchmark topic. Computational pragmatics, probabilistic models of language use, formal semantics, experimental pragmatics, and modern LMs all address pieces of it.

### Persistent friction

- behavioral success often underdetermines whether the model represented the semantic distinction or learned a pragmatic shortcut;
- prompts conflate semantic content with task instructions and conversational incentives;
- classic phenomena are often explained by multiple theories that agree on ordinary examples;
- modern instruction-following introduces an unusually strong policy layer between linguistic representation and response.

### Why we care

A decisive study can clarify what linguistic competence exists independently of response policy and how interpretation is assembled.

### Cheap versions that are NOT this problem

Recent repository search has already killed generic presupposition, free-choice, scalar/pragmatic competence, ambiguity maintenance, pedagogical selection and many neighboring “does the LLM know phenomenon X?” parents.

Therefore IP08 must **not** generate another phenomenon inventory. A future project needs a mature rival-account question plus a genuinely identifying operation or a broken premise introduced by the modern model regime.

### State

**ACTIVE PROBLEM / SUPPRESSED GENERATOR.**

Important enough to keep on the wall; dangerous enough that no new seed should be generated without unusually strong leverage.

---

# 2. WATCH problems

## IP09 — How does training produce **generalizable computation** rather than task-local behavior?

### Standing question

Different objectives and training stages can reach similar endpoint accuracy while differing in transfer, forgetting, robustness, or internal computation. What aspects of the learning trajectory create representations that remain reusable outside the training distribution?

### Why it remains important

Endpoint behavior does not identify formation mechanism. The scientific object is how optimization pressure shapes reusable computation over time.

### Why only WATCH

The repository has already searched post-training/RL/SFT/distillation/weak-to-strong/reasoning formation extremely heavily. 2025–2026 work is dense, and this object easily degenerates into `SFT vs RL on metric Y` or feature-probe stories.

### Reopen condition

Only if a **new natural quantity of formation** or a genuine stage-specific intervention makes previously inseparable causal accounts disagree.

**State: WATCH — IMPORTANT, HIGH OWNER DENSITY.**

---

## IP10 — What is the relationship between latent competence and **reliable use over time / interaction**?

### Standing question

A system may possess information or skill yet fail to use it consistently when tasks unfold over multiple turns, when commitments must be revised, or when earlier errors must be recovered from. What computational state distinguishes possessing a capability from reliably deploying it?

### Persistent friction

Single-turn evaluation often collapses aptitude and reliability. Extended interaction introduces path dependence, premature commitment, recovery, inhibition, and context management.

### Why only WATCH

The agent/multi-turn/social-cognition literature is already dense, and our previous searches repeatedly collapsed into benchmark or interface questions.

### Reopen condition

A matched interaction manipulation that holds underlying task information fixed and exposes a **new state variable or law**, not another multi-turn score.

**State: WATCH.**

---

## IP11 — How should we describe a model’s **reachable behavioral support**, not just its modal answer?

### Standing question

Top-1 performance can improve while the set/diversity/geometry of reachable successful behaviors shrinks; conversely, a model may contain low-probability capabilities invisible to ordinary evaluation. What is the right scientific object for the space of behaviors a generative model can produce?

### Why important

Generative systems define distributions, yet most evaluation compresses them to one or a few samples. For reasoning, creativity, safety, translation, and interaction, the support and its structure can matter more than the mode.

### Why only WATCH

RLVR capacity/support, diversity, entropy, stochastic generation, and related parents are now highly active. The repository has already killed several nearby formulations.

### Reopen condition

A new object must change a substantive scientific conclusion; “use pass@k instead of pass@1” is no longer enough.

**State: WATCH.**

---

## IP12 — What is a model’s **computational explanation** when behavior switches among multiple strategies?

### Standing question

Mechanistic work often searches for one compact high-level algorithm. Real models may use different strategies across inputs, training stages, or regimes. When is a single abstraction appropriate, and when is a mixture/state-dependent family of abstractions the real explanation?

### Persistent friction

Causal-abstraction theory makes “implements algorithm A” precise, but later work already shows that combining high-level causal models can better approximate networks in different computational states.

### Why only WATCH

This is theoretically important but easy to turn into interpretability-method development. The user-facing scientific reward is high only when the competing algorithms correspond to an independently important NLP/linguistic theory.

**State: WATCH — METHOD MUST FOLLOW SCIENCE.**

---

# 3. DORMANT standing problems

These remain intellectually important but should currently **not generate new questions**. They exist here to prevent a newly seen paper from creating false excitement.

## IP13 — Model uncertainty / confidence / verbalized belief

Important real problem: how probability, uncertainty, confidence language, and decision policy relate.

Current state: **DORMANT / SATURATED.** Rank calibration, semantic uncertainty, verbal uncertainty, calibration tuning, forecasting consistency, confidence semantics, and decision effects are already dense. The repository has killed many adjacent parents. Do not reopen because of a new elicitation format or intervention.

---

## IP14 — Factual memory localization / retrieval / readout

Important real problem: how factual knowledge is stored, accessed, suppressed, and expressed.

Current state: **DORMANT / SATURATED.** Knowledge neurons, MLP-as-memory, attention-vs-MLP, causal tracing, editing, architecture-dependent recall, geometric recall, promote/suppress dynamics, multilingual sharing, and readout-vs-representation have formed an active program. New architecture/model family does not reopen the parent.

---

## IP15 — Generic cognitive-bias replication in LLMs

Important real problem: what kinds of bounded-rational behavior emerge in trained models and why.

Current state: **DORMANT AS A GENERATOR.** “Classic human bias X in LLM Y” is now a mature research program. Only a modern model regime that breaks a load-bearing premise of an old law, or a new identifying operation unavailable in humans, can reactivate a concrete descendant.

---

## IP16 — Generic preprocessing / tokenization / packing / loss-masking effects

Important engineering problem: training conventions can alter what a model learns.

Current state: **DORMANT AS SCIENTIFIC-QUESTION GENERATOR.** Recent repository kills K234–K236 and surrounding literature show dense ownership. Do not mistake an under-documented engineering axis for an important scientific object.

---

## IP17 — Generic “knowledge vs use / representation vs readout”

Important distinction, but **DORMANT IN GENERIC FORM**. The repository repeatedly generated versions where different estimands were rhetorically collapsed into one “importance/access/use” story. Reactivation requires a domain theory that independently defines the two processes and a manipulation that separates them.

---

# 4. Unexplained-friction log

These are not questions. They are recurring facts/tensions worth keeping in working memory because strong projects often begin when one friction bears on a standing problem.

## F01 — Similar outputs do not identify shared computation

Modern models can reproduce linguistic generalizations while internal causal analyses reveal either shared abstractions or important context/frequency residuals. This keeps IP01/IP05 alive.

## F02 — Formal capacity routinely overpredicts what optimization learns

Transformers can represent computations they fail to learn or fail to extrapolate. Restrictions can sometimes improve behavior. This keeps IP03 alive.

## F03 — More parameters are not a sufficient explanation of better structural generalization

Depth, input distribution, structural experience, and task structure can matter independently of raw parameter count. This bears on IP02/IP03.

## F04 — Naturalistic input contains too many correlated cues for easy causal stories about acquisition

A learner may exploit multiple indirect cues. Controlled interventions are needed, but overly synthetic worlds can destroy the linguistic object. This is the central experimental tension for IP02.

## F05 — Resource limits can create structure

Memory/processing restrictions need not simply cause errors; they can induce categorical/compressed representations and may help explain language structure. This bears on IP04/IP06.

## F06 — Human-model correspondence is dependent-variable-specific

A model that improves on one neural/behavioral human measure may fail to improve on another. “More human-like” is not a scalar property. This bears on IP07.

## F07 — Community rhetoric is sometimes substantially stronger than direct evidence

The possible/impossible-language debate is a clean historical example. This is a search heuristic, not itself a topic: whenever an important claim is repeated, ask what decisive experiment actually supports the exact claim.

## F08 — Generative-model quality is frequently summarized by quantities that ignore the distribution of possible behavior

This bears on IP11 but the obvious metrics are already occupied; future leverage requires a new scientific consequence, not metric substitution.

## F09 — The same broad capability can arise from distinct training histories

Endpoint evaluation therefore cannot by itself explain acquisition or formation. This bears on IP02/IP09.

## F10 — Instruction/policy layers can separate what the model can represent from what it is incentivized to say

This creates a genuine complication for semantic, pragmatic, uncertainty, safety, and cognitive interpretation. Generic “readout” formulations are saturated; useful descendants need object-specific theory.

## F11 — Model internals may be best explained at multiple levels

Neuron, direction, distributed subspace, circuit, and high-level causal variable are not interchangeable units. A good explanation depends on the scientific claim. This bears on IP01/IP12.

## F12 — Strong research programs repeatedly change level of explanation

Examples from the lineage study include behavior -> invariant -> testing methodology; corpus interaction -> efficiency principle -> representational consequence; formal characterization -> explanation of architecture behavior. The next valuable question is often **not a narrower residual at the same level**.

---

# 5. Our scientific-interest filter

The standing state above is intentionally narrower than “all important NLP problems.” For this repository, high-value future questions should preferentially have the following shape:

- a natural scientific object, not a dataset;
- mechanism/explanation/law rather than benchmark superiority;
- an independently motivated quantity;
- a real rival account or incomplete law;
- decisive evidence even when the sign/result goes the opposite way;
- a reason the modern model/training/inference regime changes what can be inferred;
- enough conceptual reward to support an ACL/EMNLP/NAACL Main abstract without method inflation.

Strong dislikes remain:

- RAG as the scientific object;
- benchmark construction as the main contribution;
- data collection as the intellectual center;
- “first to test X on LLMs”;
- application A × method B;
- generic activation patching;
- owner collision followed by narrower salvage;
- phenomenon gambling.

---

# 6. How future reading updates this state

For every strong paper / talk / blog encountered later, the searcher must first answer:

1. **Which standing problem, if any, does this bear on?**
2. **What belief inside that problem state should update?**
3. **Does it remove an uncertainty, create a new contradiction, or supply a genuinely new identifying operation?**
4. **Would we still care about the resulting question if this focal paper were deleted from history?**

If the answer to (1) is “none,” the paper may simply be interesting. Do not force a project from it.

If the answer to (4) is “no,” it is probably a successor/gap idea and should not enter candidate generation.

A frontier paper is therefore evidence, not a question generator.

---

# 7. How future candidate generation must start

Candidate generation is still **OFF** after this document.

Before turning it on, do one additional pass over this state and choose a **small subset of standing problems we genuinely want to think about for months**, independent of current novelty. That choice is a taste decision, not a literature-coverage decision.

Only after that should we expose fresh papers/observations and ask:

> Does this new knowledge bear on one of our standing problems in a way that changes the question we can ask or the inference we can make?

The first candidate batch should therefore be generated **standing-problem first**, not paper first:

> standing problem -> unresolved internal friction -> new leverage -> question

never:

> new paper -> missing neighbor -> question.

---

# 8. Calibration sources / lineages used to construct this state

This is not an exhaustive bibliography; it records the research programs that shaped the standing state.

### Research-taste / idea-genesis evidence

- Marco Tulio Ribeiro, *Coming up with research ideas* and *Organizing and evaluating research ideas* (2022): important-problem filters, unexplained annoyances, adjacent possible, best-case reward.
- Nicholas Carlini, *My research idea logfile, 2016–2019* (2024): persistent idea log, separation of problem from guessed solution, later reevaluation.
- Chris Olah, *Research Taste Exercises* (2021): taste learned through many cheap judgments, historical comparison, research intimacy.
- John Schulman, *An Opinionated Guide to ML Research* (2020): goal-driven vs literature/idea-driven research.
- Chen, Zhao & Cohan, *Measuring the Gap Between Human and LLM Research Ideas* (2026): LLM idea generation overconcentrates on bridge/synthesis opportunity patterns relative to human papers.

### Language learning / inductive bias

- Ravfogel, Goldberg & Linzen (NAACL 2019), synthetic variations of natural languages.
- Mueller & Linzen (ACL 2023), data/architecture sources of hierarchical inductive bias.
- Petty et al. (NAACL 2024), depth and compositional generalization.
- Kallini et al. (ACL 2024 Best), possible vs impossible language learnability.
- Hu et al. (ACL 2025 Outstanding), formal-language pre-pretraining and linguistic inductive bias.
- Kallini & Potts (BBS 2026), phased possible/impossible-language research program.
- Leong & Linzen (JML 2026), manipulating LM training evidence to study syntactic constraint learning.

### Formal characterization / learnability

- Svete & Cotterell (EMNLP 2023), RNN LMs as probabilistic finite-state automata.
- Borenstein et al. (ACL 2024), empirical learnability of probabilistic regular languages.
- Merrill/Cotterell formal-language and transformer expressivity line.
- Li & Cotterell (ACL 2026 Best), local attention as a complementary computational operator.

### Causal abstraction / linguistic theory

- Geiger et al. (NeurIPS 2021; ICML 2022; CLeaR 2024; JMLR 2025), causal abstraction and distributed alignments.
- Arora, Jurafsky & Potts (ACL 2024 Outstanding), CausalGym.
- Boguraev, Potts & Mahowald (EMNLP 2025 Outstanding), shared filler–gap structure through causal interventions.

### Resource-rational language / efficiency

- Futrell, Gibson & Levy and related long-running work on memory, surprisal, dependency locality and efficient communication.
- Xu & Futrell (JML 2026), strategic resource allocation in memory encoding.
- Xu, Dillon & Futrell (ACL 2026 Best), resource-rational memory constraints reshape representations.
- Futrell & Hahn (Nature Human Behaviour 2026), linguistic structure from sequential-information bottlenecks.

### Language models as scientific model systems

- Futrell et al. (NAACL 2019), neural LMs as psycholinguistic subjects.
- Linzen & Baroni (Annual Review of Linguistics 2021), syntactic structure from deep learning and implications for acquisition.
- Futrell & Mahowald (BBS 2026), LMs as productive model systems for language science without replacing linguistic theory.

---

# 9. Current decision

**No candidate generated. No L-series change. No pilot authorization.**

The main achievement of this pass is the creation of a persistent research state that is independent of the next paper we read.

Current priority for the next pass:

> perform **taste selection over standing problems**, not novelty selection over candidate ideas.

Specifically, rank the ACTIVE problems by:

1. would we personally still care after six months?;
2. is there a plausible Main-level scientific consequence?;
3. do we have enough research intimacy to notice real frictions rather than invent them?;
4. is the object currently so saturated that a new question is unlikely to survive?;
5. can modern models provide a genuinely different inference rather than merely a new test subject?

Only after that ranking should question generation resume.