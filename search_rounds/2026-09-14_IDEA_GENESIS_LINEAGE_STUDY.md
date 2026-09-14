# 2026-09-14 — Idea-Genesis Lineage Study

**Target:** ACL / EMNLP / NAACL Main research-question search  
**Mode:** META-RESEARCH / LINEAGE RECONSTRUCTION ONLY  
**Candidate generation:** **FORBIDDEN IN THIS DOCUMENT**  
**Purpose:** learn how strong human researchers actually arrive at important questions before returning to our own question generation.

---

# 0. Why this document exists

The previous provenance corpus was useful but still too paper-centric. It reconstructed many excellent papers and then quickly compressed them into abstract moves such as `old law -> conditional law`, `metric -> consequential quantity`, or `mature debate -> new causal operation`. Those descriptions are true, but they are not yet a good model of **how a researcher came to notice the question in the first place**.

That distinction matters because an LLM can imitate the *shape* of a successful paper after seeing it, while still failing to generate the kind of question a strong human researcher would have selected before the answer was known.

This is not merely an intuition. Chen, Zhao & Cohan (2026), *Measuring the Gap Between Human and LLM Research Ideas* (arXiv:2607.01233), reverse-engineer local prior-work contexts for 11,683 human papers and ask LLMs to ideate from comparable contexts. Their main finding is a systematic taste gap: LLM ideas are disproportionately concentrated around **bridge-like opportunities and synthesis**, while human papers occupy a substantially broader distribution of problem framings and contribution types. More context does not automatically remove this gap. This is uncomfortably consistent with the repository's repeated failure mode: `paper A + paper B`, neighboring successors, and small novelty residuals.

Therefore this pass studies **research programs and researcher self-reports**, not isolated papers.

For each lineage, we distinguish:

- **DIRECT** — the researcher explicitly described how the idea arose;
- **DOCUMENTED-LINEAGE** — the sequence of papers and their claims is observable, but the causal story between papers is partly inferred;
- **INFERRED** — a plausible program dynamic inferred from publications, used cautiously.

The goal is not to produce another taxonomy. The goal is to preserve enough historical detail that we can see what the researcher was *paying attention to* before the paper existed.

---

# 1. Meta-evidence: how strong researchers say they choose problems

## M1 — Marco Tulio Ribeiro: important-problem filters + unexplained annoyances

**Evidence quality: DIRECT.**  
Source: https://medium.com/@marcotcr/coming-up-with-research-ideas-3032682e5852  
Companion: https://medium.com/@marcotcr/organizing-and-evaluating-research-ideas-e137637b599e

Ribeiro's advice is much more specific than “read papers and find gaps.” His first precondition is to expand one's **adjacent possible**: broad enough exposure that new information can connect to a rich internal map. He recommends keeping a mental/listed set of important problems so that new knowledge is filtered through questions one already cares about.

His most informative example is his own PhD trajectory. During a Google internship, he had a model with good cross-validation accuracy that performed badly in the wild. What bothered him was not merely the accuracy drop. The persistent annoyance was that it took a great deal of manual work — collecting data, perturbing inputs, inspecting predictions — to understand **what the model was actually doing**. When asked to present the internship, he spoke mostly about this annoyance and a rough vision of understanding arbitrary ML model behavior, not about the nominal internship project. His advisor asked whether he wanted to work on that problem; they switched topics, producing the line that became his PhD trajectory.

This is an important distinction:

> The seed was not `paper X lacks interpretability`; it was prolonged contact with an important capability failure whose cause he could not see.

Ribeiro explicitly recommends maintaining a list of **failures I don't understand**. Crucially, the failure is fertile only after trying to understand *why* it occurs. A workaround is not the research result; the unexplained failure is a pressure source.

His analogy heuristic is also easily misread by LLMs. The path to SEARs was not “adversarial examples + NLP.” While working on explanations, he noticed that text models were unexpectedly brittle to changes that should preserve meaning. The decisive analogy was that the relevant counterpart of small pixel-space distance was **small semantic distance**, not small edit distance. That scientific invariant constrained the transfer. Later, universal adversarial rules looked to Scott Lundberg like software unit tests, which prompted the broader CheckList project. Again, the analogy worked because the existing object already behaved like a test, not because two literatures had never been combined.

His second essay contains an equally useful negative example. After roughly six weeks on an internship project, a senior researcher convinced him that the **problem itself was bad**, making his technical solution irrelevant. Later he wasted months on a vague project mixing “unifying interpretability,” cool experiments, and new techniques with no crisp problem. These experiences led him to explicitly evaluate projects by: what changes in the world if this succeeds, why that change matters, how success is known, and what uncertainties could falsify the value of the project.

He also warns against accepting the first “good enough” project because generating alternatives takes weeks whereas projects consume months. One of his strongest filters is effectively a **best-case reward upper bound**: if the most successful imaginable result is still unimportant, reject the project before polishing the method.

### What this teaches us

The transferable object is **not** “find anomalies.” It is:

1. keep important problems active before reading;
2. notice persistent failures/annoyances encountered while genuinely trying to do something;
3. understand the failure well enough to name the violated invariant;
4. only then use analogy or technique transfer;
5. evaluate the *best imaginable answer* before evaluating implementation novelty.

This is almost the reverse of `new paper -> missing experiment -> owner search`.

---

## M2 — Nicholas Carlini: separate idea capture from project selection; preserve the problem even when the solution guess is wrong

**Evidence quality: DIRECT.**  
Source: https://nicholas.carlini.com/writing/2024/my-research-logfile.html

Carlini published his raw `ideas.txt` log from 2016–2019, which is unusually valuable because it exposes pre-publication thinking rather than a polished retrospective narrative.

Three observations matter for our searcher.

### 1. Idea generation and project selection are temporally separated

Carlini appends ideas that seem plausibly good, then revisits the log only a few times per year when choosing what to work on. The time separation acts as a filter: an idea must feel compelling at generation time and again later when attachment has faded. Many ideas become obsolete, get solved by others, or simply no longer look important.

This is directly opposed to our recent pattern:

> generate seed -> immediately novelty-search -> immediately salvage/kill.

That workflow encourages attachment to whatever was generated first and confounds **idea quality** with **current ownership status**.

### 2. His logs visibly evolve from solution-first to problem-first

Carlini explicitly notes that his early entries often prescribed how to solve something; he later decided this was unwise and shifted toward writing down **problems worth solving**.

The log provides an especially strong example. He wrote that current black-box adversarial attacks were awful and proposed a complicated surrogate/uncertainty approach. He later judged that his *solution idea was wrong* but the **question was right**. ZOO and other query-based methods found a much simpler route and changed black-box attacks. If he had evaluated the research question by whether his first mechanism worked, the good question would have been incorrectly discarded.

This is highly relevant to our repeated “E01 failed -> therefore the parent question was bad” confusion. Sometimes a failed instrument kills the question; sometimes it only kills the proposed identification. These must not be conflated.

### 3. Field intimacy made simple problem statements scientifically loaded

Entries such as “Lots of systems to detect adversarial examples, can we break them?” look almost embarrassingly simple in hindsight. One became a highly cited paper. Another entry reframed model stealing as a cryptographic query problem and later became the foundation for two papers. These were not generated from a generic template. Their value came from deep enough field intimacy to know that the simple sentence pointed at a load-bearing assumption.

Carlini's own hindsight also documents failures of taste: he sometimes wrote down ideas that later became important fields but did not pursue them because he underestimated their importance. This demonstrates that **novelty was not the bottleneck**; importance judgment was.

### What this teaches us

- Preserve a strong question independently from a guessed solution.
- Do not force every idea into an experiment at generation time.
- Let time / comparative ranking filter ideas instead of immediately defending them.
- “Simple” questions can be deep when backed by research intimacy; elaborate wording is not evidence of depth.

---

## M3 — Chris Olah: research taste is trained by many cheap judgments, not by executing a few expensive projects

**Evidence quality: DIRECT.**  
Source: https://colah.github.io/notes/taste/

Olah frames research taste as the ability to choose good problems. The central difficulty is feedback scarcity: fully executing an idea can take months, so a researcher gets only a few high-quality feedback signals per year.

His exercises therefore deliberately increase the number of **cheap taste judgments**:

- write many ideas and ask a respected mentor to rate them;
- study disagreements rather than merely accepting scores;
- watch what happens when other groups independently execute ideas you had;
- interview strong researchers about why they work on their problems and what their big-picture model is;
- study history of science and ask why some researchers focused on directions their contemporaries ignored;
- compare the taste of neighboring research schools;
- periodically ask what you would work on if starting from scratch.

Two details are especially important for this repository.

First, Olah explicitly calls **lack of research intimacy** a taste failure mode. Theoretical knowledge is table stakes; one cannot develop taste “in a vacuum.” Helping with a real project or doing short exploratory work can create the contact needed to notice real problems.

Second, he highlights a failure mode suggested by Andy Matuschak: running to execute an idea as soon as it becomes tractable. Sitting with the idea can reveal a deeper variant. This describes our current behavior almost exactly: once an E01-shaped design appears, we become eager to instantiate it, even when the question has not matured.

### What this teaches us

The right use of a research-search agent is not to manufacture one polished proposal. It should create **many opportunities for taste feedback**, especially by comparing its judgments with the historical choices of strong researchers.

---

## M4 — John Schulman: goal-driven programs create differentiated questions; literature-following creates correlated ideas

**Evidence quality: DIRECT essay; historical examples documented.**  
Original essay: *An Opinionated Guide to ML Research* (John Schulman, 2020; original site currently intermittently unavailable, widely mirrored).  
A faithful excerpt/copy is indexed at multiple research-advice archives.

Schulman distinguishes:

- **idea-driven research**: follow a literature, see X, think of a way to improve X;
- **goal-driven research**: choose a concrete capability/goal and solve whatever scientific/technical bottlenecks prevent it.

His central criticism of idea-driven research is exactly our current failure: researchers worldwide read the same papers, so they generate correlated follow-up ideas and face high scoop/duplication risk. Goal-driven work supplies an independent coordinate system for deciding what matters.

His own RL trajectory is the canonical example. The standing goal was robust continuous-control / humanoid locomotion, not “improve whichever RL algorithm is newest.” When the field surged toward DQN/Atari, his experience with the target problem made Q-learning look poorly matched to the goal. He stayed with policy-gradient style methods and developed a sequence including TRPO, GAE, and later PPO. The program's continuity came from the **goal**, not from allegiance to one method.

This does not mean our NLP work should be capability-engineering. The scientific analogue is to maintain a stable **important scientific object/question family** that supplies an external criterion for relevance. New papers are then evidence that bears on the problem, rather than anchors whose nearest unoccupied neighbor becomes the next project.

### What this teaches us

A strong searcher needs a few persistent scientific goals / important problems that are *not defined by the current paper frontier*. Without those, literature search inevitably becomes successor generation.

---

# 2. Longitudinal research lineages

## L1 — Ribeiro / Singh / Guestrin: `real-world opacity -> local explanations -> semantic brittleness -> behavioral tests`

**Evidence quality: DIRECT for idea genesis + DOCUMENTED-LINEAGE for papers.**

Key works:

- Ribeiro, Singh & Guestrin (KDD 2016), *Why Should I Trust You? Explaining the Predictions of Any Classifier* — LIME.
- Ribeiro, Singh & Guestrin (AAAI 2018), *Anchors: High-Precision Model-Agnostic Explanations*.
- Ribeiro, Singh & Guestrin (ACL 2018), *Semantically Equivalent Adversarial Rules for Debugging NLP Models*.
- Ribeiro et al. (ACL 2020 Best Overall), *Beyond Accuracy: Behavioral Testing of NLP Models with CheckList*.

### What the program was actually trying to understand

The persistent problem was not “interpretability” as a paper category. It was practical epistemology:

> How can a person know enough about a learned model's behavior to decide whether to trust/deploy/debug it?

LIME attacked this via local explanation. Anchors made the local sufficient conditions more explicit and high precision. While working with explanation methods on NLP models, Ribeiro encountered a different but related nuisance: tiny meaning-preserving changes could radically change predictions. The right invariant was not character/edit distance but semantic equivalence. That produced SEAs/SEARs.

Then a collaborator recognized the universal adversarial rules as analogous to software unit tests. CheckList enlarged the unit from *an adversarial rule that breaks a model* to a **systematic behavioral testing methodology** organized by linguistic capability and test type. The accepted community metric — held-out accuracy — was now seen as insufficient not because the authors brainstormed “metric bad,” but because years of trying to understand actual model behavior repeatedly exposed unmeasured failure modes.

### The human conceptual moves

1. **Persistent problem stays fixed; operational object changes.** Explanation, semantic invariance, and behavioral tests are different instruments around the same real problem.
2. **A side-effect in one project becomes central only because it bears on the persistent problem.** The brittleness observation was not mined from Related Work; it was encountered while trying to use explanations.
3. **Analogy is constrained by the object.** `small L2` becomes `small semantic change`, not `vision adversarial method + NLP`.
4. **The best paper comes after a sequence of partial tools.** CheckList's idea looks simple partly because the group had accumulated the right empirical pain.

### What an LLM imitation would get wrong

An LLM seeing only SEARs and CheckList might generate “apply software testing technique Y to LLMs.” That misses the provenance. The real bridge became useful only after semantic invariance rules had already emerged from an independent debugging problem.

---

## L2 — Julie Kallini / Potts / Futrell / Mahowald: `sweeping field claim -> is the decisive evidence actually there? -> research program`

**Evidence quality: DIRECT origin story + DOCUMENTED-LINEAGE.**

Sources:

- Quanta (2025), *Can AI Models Show Us How People Learn? Impossible Languages Point a Way.*
- Kallini et al. (ACL 2024 Best), *Mission: Impossible Language Models*.
- Kallini & Potts (Behavioral and Brain Sciences 2026), *Language models as tools for investigating the distinction between possible and impossible natural languages*.

### The origin

This lineage is an unusually clean counterexample to “find a literature gap.” Kallini had just started graduate school in August 2023. Chomsky's critique of LLMs was repeatedly discussed around her: language models were claimed to be too unconstrained, able to learn possible and impossible languages equally, and therefore uninformative about human language acquisition.

Kallini looked at the literature and did not start from “Mitchell & Bowers left transformer X untested.” Her dissatisfaction was that a **sweeping theoretical claim** was being used in a major debate despite very little direct empirical evidence, and the existing evidence involved older neural architectures. According to the Quanta account, the mission felt obvious to her: actually test the claim on modern transformers. Potts initially considered the proposed study too ambitious for a first graduate project; she persisted.

The ACL 2024 paper then built a continuum of impossible languages and compared learnability throughout training. The result challenged the strongest claim. More importantly, the 2026 BBS article explicitly turns the result into a **phased research program**: iteratively refine model architectures and impossible-language tests to probe inductive biases and eventually build linking hypotheses to human cognition.

### Why this is not “classic human debate + LLM” in the weak sense

The key was not that nobody had “tested Chomsky on GPT-2.” The claim itself was load-bearing: it was being used to dismiss an entire class of computational models as evidence for language acquisition. A decisive experiment had high reward whichever direction it went.

The model regime mattered because the universal claim was explicitly about modern LMs, while empirical support lagged behind the rhetoric.

### The human conceptual moves

1. Notice when **community rhetoric outruns direct evidence**.
2. Ask whether the strong version of the claim has ever received the experiment it logically requires.
3. Build a continuum/stress test that makes degrees of failure informative instead of one benchmark score.
4. Use the first result to open a research program, not to claim the nearest residual novelty.

### What an LLM imitation would get wrong

“Take another classic linguistic controversy and test it on LLMs” is not the lesson. The hard filter is: **is the old claim currently load-bearing in a modern scientific argument, and is the missing experiment decisive for that claim?** Most classic debates fail this test.

---

## L3 — LeapLab / Yang Yue / Gao Huang collaborators: `reasoning score -> reachable support -> sources of exploration -> architectural assumption`

**Evidence quality: DOCUMENTED-LINEAGE; causal relation between projects is partly inferred.**

Key works:

- Yue et al. (NeurIPS 2025), *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*
- Zhao et al. (NeurIPS 2025), *Absolute Zero: Reinforced Self-play Reasoning with Zero Data*.
- Ni et al. (ICML 2026 Outstanding), *The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models*.

### The deeper program object

The obvious topic labels differ: RLVR, self-play data generation, diffusion LMs. The repeated scientific object is closer to:

> What actually enlarges the set of reasoning trajectories/solutions a model can reach, rather than merely concentrating probability on already reachable behavior?

The RLVR paper attacks a widely repeated belief that reinforcement learning creates novel reasoning capacity. The key move is not merely “use pass@k.” It notices that Pass@1 cannot identify the claimed object. Large-k behavior probes the **reachable support/boundary**. Under that measurement, current RLVR often looks like probability redistribution rather than support expansion.

Absolute Zero attacks a different bottleneck in the same broad aspiration toward open-ended reasoning improvement. Even “zero” RL still consumes human-curated task distributions. If the goal is self-improvement beyond the frontier of human supplied examples, the task source itself becomes the bottleneck. The project therefore makes the model propose verifiable tasks that maximize learning progress.

The Flexibility Trap then interrogates a celebrated architectural assumption in diffusion LMs: arbitrary token order is supposed to make the solution space more flexible. The paper asks whether the mechanism actually expands reasoning exploration. It finds the opposite under current generation: uncertainty-avoiding order lets the model skip high-uncertainty forking tokens, shrinking solution diversity. ICML's award citation specifically praises the work for challenging a dominant assumption and exposing a non-obvious failure mode.

### The human program move

The important continuity is not “reuse pass@k” or “apply exploration analysis to dLLMs.” It is that the group has a **standing scientific quantity — reachable reasoning support/exploration — against which new training regimes and architectures can be judged**.

That makes papers from unrelated hot topics bear on the same internal question.

### What an LLM imitation would get wrong

An LLM would likely turn this into “find another method and measure support.” That is precisely the wrong transfer. The transferable habit is to acquire a **scientific coordinate system** that can expose when headline performance answers a different question from the one the field claims to be discussing.

---

## L4 — Li & Cotterell: `build a formal coordinate system -> later use it to explain an empirical architecture puzzle`

**Evidence quality: DOCUMENTED-LINEAGE.**

Key works:

- Li & Cotterell (NeurIPS 2025), *Characterizing the Expressivity of Fixed-Precision Transformer Language Models*.
- Li & Cotterell (ACL 2026 Best), *Characterizing the Expressivity of Local Attention in Transformers*.

### What paper n contributed to paper n+1

The 2025 work characterizes a restricted fixed-precision causal transformer exactly in terms of a fragment of linear temporal logic with a past operator, connecting the architecture to formal-language, automata, and algebraic classes. This is not just one theorem; it supplies a **language for saying what temporal computations a restricted transformer can express**.

The 2026 work starts from an empirical puzzle: local attention is usually described as an efficiency restriction, yet it can improve model quality. If “local” merely means less information access, improvement is conceptually awkward.

The prior formal coordinate system changes the question. Rather than asking “why does this regularizer help?” in generic optimization language, they can ask what temporal operators local attention adds or removes. The result is a complementary expressivity account: local attention introduces a second temporal operator; local and global attention are not ordered by simple containment; a hybrid can be strictly richer.

### The human conceptual move

A strong earlier paper can create **new scientific vocabulary** that makes a later empirical puzzle askable at a much sharper level.

This is a lineage pattern we have underused. We search primarily for “facts that collide.” But mature research programs often first spend effort creating a representational/formal coordinate system, and only later does that language reveal that a familiar engineering distinction was scientifically misdescribed.

### What an LLM imitation would get wrong

“Use formal-language theory to analyze module X” is not the lesson. The prior theory must make a previously vague empirical puzzle **change form**. If the formalism does not change the question, it is decorative theory.

---

## L5 — Xu / Futrell / Dillon: `cross-linguistic interaction -> efficiency principle -> resource variable -> emergent representation`

**Evidence quality: DOCUMENTED-LINEAGE.**

Key works:

- Xu & Futrell (SIGTYP 2024), *Syntactic dependency length shaped by strategic memory allocation*.
- Xu & Futrell (Journal of Memory and Language 2026), *Strategic resource allocation in memory encoding: An efficiency principle shaping language processing*.
- Xu, Dillon & Futrell (ACL 2026 Best), *Memory efficiency and resource-rational encoding in sentence processing*.

### The lineage does not shrink the same experiment

The 2024 paper studies a cross-linguistic interaction: dependency-locality pressure is modulated by antecedent surprisal. Unexpected antecedents appear capable of sustaining longer dependencies, consistent with preferential memory encoding.

The JML paper elevates the empirical interaction into **Strategic Resource Allocation**: a resource-rational principle under which high-surprisal inputs receive greater encoding precision because limited working memory should allocate resources strategically.

The ACL 2026 Best Paper changes level again. Rather than looking for another corpus interaction, it operationalizes memory as a **precision budget over internal representations** in a neural LM and asks what representation emerges when prediction is optimized under this resource constraint. The striking consequence is not just better reading-time fit; representations become more compressed and categorical, producing a dissociation between memory encoding quality and retrieval mechanism.

### The human conceptual move

Each paper asks at a different explanatory level:

1. is there an empirical interaction?
2. what efficiency principle would predict it?
3. if that principle is implemented computationally, what representation should emerge?

This is a genuine program progression. It does not repeatedly mine residuals from the previous experiment.

### What an LLM imitation would get wrong

“Apply resource rationality to phenomenon Y” is too shallow. The strong move is to locate a **natural resource quantity** that the scientific theory says should be optimized, then ask what representation or law follows from imposing it.

---

## L6 — Potts / Mahowald / collaborators: `LM behavior as linguistic evidence -> causal internals as a stronger evidence type`

**Evidence quality: DOCUMENTED-LINEAGE.**

Key works:

- long-running behavioral LM/psycholinguistic work on filler–gap dependencies and related constructions;
- Arora, Jurafsky & Potts (ACL 2024 Outstanding), *CausalGym: Benchmarking causal interpretability methods on linguistic tasks*;
- Boguraev, Potts & Mahowald (EMNLP 2025 Outstanding), *Causal Interventions Reveal Shared Structure Across English Filler–Gap Constructions*.

### The pressure existed before the method

Linguistic theory already made a substantive claim: superficially different filler–gap constructions share abstract syntactic structure. Behavioral LM studies could show similar surprisal signatures, island sensitivity, and so on, but **similar behavior does not identify a shared internal computation**. Separately learned heuristics can produce similar output patterns.

CausalGym is method-facing, but its scientific motivation is precisely this evidence gap: psycholinguistic LM work had overwhelmingly relied on behavior, while causal interpretability could potentially test abstract mechanisms. It benchmarks which interventions can causally manipulate linguistic behavior and studies how mechanisms form during training.

The 2025 Outstanding paper then asks the theory-facing question directly. Distributed interchange interventions test whether a causal variable learned for one filler–gap construction transfers to others. The important output is not just “we found a circuit.” The shared abstraction supports part of linguistic theory, while residual effects of frequency, filler type, and context identify where the standard theory may need revision.

### Why this is different from generic activation patching

The latent variable was **not invented after inspecting activations**. Linguistic theory independently asserts a shared abstraction. Cross-construction interchange therefore has a pre-specified semantics: if the same abstract computation is reused, the intervention should transfer in a particular way.

This is the standard any future mechanistic-linguistic idea must meet. “Behavior paper exists, so now do mechanism” is not sufficient.

---

## L7 — Tutek / Belinkov collaborators: `local technical capability -> only valuable when it fills an independent identification hole`

**Evidence quality: DOCUMENTED-LINEAGE; motivational bridge partly inferred.**

Key works:

- Ashuach, Tutek & Belinkov (2024/2025), *REVS: Unlearning Sensitive Information in Language Models via Rank Editing in the Vocabulary Space*.
- Tutek et al. (EMNLP 2025 Outstanding), *Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps*.

### The weak story would be method-first

A superficial provenance story is “the group had an unlearning method, so they applied it to CoT.” That would be exactly the sort of method-neighbor search we want to avoid.

The scientifically stronger story is visible from the estimand. The CoT-faithfulness literature asks whether verbalized reasoning corresponds to the model's **parametric beliefs/computation**. Context perturbations can show that text matters to subsequent text, but they cannot cleanly establish dependence on the parametric information represented by a reasoning step. The desired counterfactual therefore lives in parameters.

REVS supplied unusually precise local experience with erasing information from model parameters. FUR makes parameter-level removal the intervention and asks how the prediction changes. The prior method becomes valuable because an independently important mature question has an **intervention-semantics hole** that parameter-level unlearning fits.

### The human conceptual move

Do not search for applications of your method. Search for important questions whose desired causal estimand logically demands an operation you happen to know how to perform.

That difference is small linguistically but enormous scientifically.

---

## L8 — Ji / Yang / PKU alignment program: `many attack/failure observations -> stop inventing stronger attacks -> identify a common dynamical variable`

**Evidence quality: DOCUMENTED-LINEAGE / INFERRED program dynamics.**

Key focal work:

- Ji et al. (ACL 2025 Best), *Language Models Resist Alignment: Evidence From Data Compression*.

The alignment/safety literature already contained many ways to make aligned behavior disappear: malicious fine-tuning, benign fine-tuning, task adaptation, and other perturbations. A low-level successor search would naturally propose another stronger attack or another defense.

The ACL Best Paper instead asks whether these scattered observations point to a **general dynamical property of post-alignment models**. It names and measures *elasticity*: after further fine-tuning, behavior tends to rebound toward the distribution established by much larger-scale pretraining. Compression theory then predicts why a small alignment dataset is structurally weak relative to the information encoded through pretraining, and natural gradients — model scale, pretraining data, perturbation amount — test the account.

### The human conceptual move

When a mature group has seen many variants of “the same thing breaks,” the next high-reward question may not be another break. It may be:

> What state variable / dynamical law would make these failures manifestations of one phenomenon?

This move requires **enough accumulated contact with failures to see recurrence**. An LLM reading one attack paper is unlikely to know that the right next step is abstraction rather than extension.

---

## L9 — Lesci / Meister / Hofmann / Vlachos / Pimentel: `let the scientific definition dictate the method`

**Evidence quality: DOCUMENTED focal provenance.**

Key work:

- Lesci et al. (ACL 2024 Best), *Causal Estimation of Memorisation Profiles*.

This paper illustrates a different origin pattern. Prior work already defines memorization causally: the effect of including a training instance on the model's ability to predict that instance. The definition itself contains a counterfactual — what would the same model have done had that instance not appeared in training?

The methodological problem follows **from the construct**, not from a desire to import econometrics into NLP. Existing methods either approximate the counterfactual expensively or estimate architecture-level tendencies rather than a particular trained model instance. Difference-in-differences is brought in because the scientific quantity requires counterfactual identification from observable training trajectories.

Once the estimand is measured, the paper can characterize memorization profiles over training and reveal laws involving model scale, data order, and learning rate.

### The human conceptual move

Start from the strongest semantic definition of the object. Ask what observation would actually identify that definition. If existing measurements do not satisfy the definition, the **measurement problem itself** can be the important research question.

This is much stricter than “proxy bad.” The definition logically entails a missing counterfactual.

---

## L10 — Translation researchers around Yafu Li / Yue Zhang / collaborators: `deep domain immersion -> stage-localization rather than another quality improvement`

**Evidence quality: DOCUMENTED paper; longer causal lineage partly inferred from authors' sustained MT work.**

Key focal work:

- Li et al. (ACL 2025), *Lost in Literalism: How Supervised Training Shapes Translationese in LLMs*.

Translationese is old. Literal/unidiomatic output is old. What changes in the LLM regime is a sharp pressure: pretrained LMs have consumed enormous amounts of natural target-language text and demonstrate fluent target-language generation, yet **translation mode still reintroduces systematic unnatural literalism**.

A method-first project would propose another decoding trick or translation objective. The stronger question is a formation question:

> If the base model already has natural target-language competence, at what training stage is the translationese behavior introduced?

The paper localizes the bias to supervised fine-tuning and then uses that diagnosis to motivate interventions on references/training instances.

### Why domain intimacy matters

The pressure only looks obvious once one knows both sides of the pipeline: what pretraining gives the model as a target-language generator and what supervised MT data teaches it in translation mode. A generic LLM searcher may see “translationese persists” and produce a benchmark or mitigation method. A domain-immersed researcher sees a **formation-stage contradiction**.

### The human conceptual move

When a mature capability pipeline has multiple stages, ask whether an observed property is inherited, created, amplified, or merely revealed at each stage. This becomes scientific when the stages imply competing causal stories, not when it is a generic ablation grid.

---

## L11 — Schulman's continuous-control program: `stable external goal prevents literature mode-collapse`

**Evidence quality: DIRECT retrospective + DOCUMENTED technical lineage.**

The point of including this ML lineage in an NLP-search document is not to propose robotics work. It is a control case for how a long-running goal changes idea generation.

Schulman's stated goal was to make reinforcement learning work for difficult continuous-control behaviors such as 3D locomotion. That goal forced repeated confrontation with stability, sample efficiency, policy updates, advantage estimation, and benchmarking. When Atari/DQN became the field's gravitational center, the target problem supplied independent evidence that value-based/Q-learning approaches were not the right local path. The program therefore continued through policy-gradient/trust-region methods rather than following the hottest literature neighborhood.

### The human conceptual move

A stable external problem creates **private evidence**. After enough attempts, the group knows failure modes and desiderata that are not visible from paper abstracts. This differentiated information is what makes its questions less correlated with everyone reading the same literature.

For our scientific-question search, the analogue is not necessarily a capability goal. It can be a stable scientific obsession such as “what changes a model's reachable support?” or “what computational evidence can distinguish two linguistic theories?” The key is that the research object persists longer than any current paper trend.

---

# 3. Cross-lineage conclusions — what humans are doing that our searcher was not

The lineages above suggest several recurring facts. These should be treated as observations, not as another rigid idea-template catalog.

## 3.1 Strong questions are usually anchored outside the focal paper

Examples:

- Ribeiro had a persistent deployment/debugging problem before SEARs and CheckList.
- Kallini had a field-level theoretical claim whose evidential support bothered her.
- Schulman had a concrete control goal independent of Atari fashion.
- Potts/Mahowald had a linguistic-theory claim independent of causal interpretability.
- Xu/Futrell had an efficiency theory of memory independent of one LM benchmark.

This anchor gives the researcher a reason to ignore 95% of plausible novelty gaps.

**Our failure:** the focal paper itself often became the anchor.

---

## 3.2 Research intimacy produces pressures that abstracts do not contain

Several important ideas came from information available only after trying to make something work:

- Ribeiro's model looked good under cross-validation but was inscrutable and bad in the wild.
- Text explanation work exposed semantic brittleness as a side failure.
- Continuous-control experience gave Schulman's group a different view of fashionable RL methods.
- Translation expertise makes “fluent base LM, literal translation LM” a stage-level contradiction rather than a generic quality complaint.

This is why simply reading 100 more abstracts may have diminishing returns. Some scientific pressure is generated by **contact with the object**, not literature coverage.

For us, short cheap reproductions can therefore have a legitimate *search* role — not to test a prewritten candidate, but to manufacture/observe failures before a question is fixed. This is distinct from phenomenon gambling because the search experiment is explicitly disposable and no paper story depends on its sign.

---

## 3.3 The initial method guess is allowed to be wrong

Carlini's black-box attack log is the clearest example: the question was right, his proposed solution was wrong, and later work found the simple solution.

Therefore the searcher must maintain two separate confidence variables:

- **Q-confidence:** is the scientific question important and well-posed?
- **I-confidence:** do we currently have an identifying instrument / feasible attack?

A failed I does not automatically set Q to zero. Conversely, a clever I does not rescue a low-Q question.

Our previous candidate documents often coupled these too tightly.

---

## 3.4 Great follow-ups often change explanatory level rather than shrink residual novelty

Xu/Futrell is the cleanest lineage:

`corpus interaction -> efficiency principle -> computational constraint -> emergent representation`.

Li/Cotterell:

`formal coordinate system -> empirical architecture puzzle -> complementary operator law`.

Ribeiro:

`local explanation -> invariant-breaking behavior -> reusable behavioral testing framework`.

These are follow-ups, but they are not “paper n did behavior, paper n+1 does mechanism” by default. The next project inherits a **problem/object**, then moves to the explanatory level that has become newly justified.

---

## 3.5 A new method becomes a strong idea only when the question dictates its semantics

FUR and filler-gap interventions are important calibration examples.

Weak pattern:

> We have unlearning / activation patching; where can we apply it?

Strong pattern:

> The scientific claim is explicitly parametric/shared-causal; existing evidence cannot identify that; therefore a parameter-level/cross-construction intervention is logically required.

This is the threshold for Direction A (“mature theory + genuinely new identifying operation”).

---

## 3.6 “Challenge an assumption” is downstream of understanding why the assumption existed

Both Ribeiro's Chesterton's-fence advice and the Flexibility Trap support this.

The Flexibility Trap is not strong merely because it says “arbitrary order is bad.” The original belief is highly reasonable: arbitrary generation order appears to weakly enlarge available trajectories and lets a dLLM defer uncertain tokens. The paper identifies the exact condition under which the virtue becomes a liability: deferring uncertainty bypasses the high-entropy branching tokens needed for exploration.

The good question therefore comes from understanding the **load-bearing mechanism of the status quo** well enough to identify where it changes sign.

Our searcher often began with “find an assumption to overturn,” which invites fake contrarianism.

---

## 3.7 Measurement innovations are strongest when the community claim semantically entails the quantity

Three examples:

- RLVR claims to expand reasoning *capacity* -> top-1 success cannot identify reachable support -> large-k boundary becomes necessary.
- Memorization is defined as an inclusion counterfactual -> observational accuracy cannot identify it -> causal estimation becomes necessary.
- Shared syntactic abstraction is a claim about reused computation -> similar output behavior cannot identify it -> cross-construction causal interchange becomes necessary.

The quantity is not chosen because it is novel. It is forced by the noun in the scientific claim.

This is a much stronger filter than generic `metric/proxy bad` ideation.

---

## 3.8 Strong researchers carry a small number of important problems for years

Ribeiro explicitly recommends keeping 10–20 important problems / personal filters, echoing Hamming. Schulman recommends goal-driven programs. Olah recommends interviewing researchers about their “big picture.” Carlini's log shows repeated revisiting of long-lived adversarial-ML questions.

This may be the largest structural difference between human and LLM ideation.

An LLM begins each search turn with a broad semantic prior over papers. A strong researcher begins with a **highly non-uniform private prior** built by years of obsession, failures, and judgments.

If we do not simulate that persistent problem state, more web search simply gives the model more opportunities to produce plausible bridges.

---

# 4. What the 2026 human-vs-LLM ideation study changes for our process

Chen, Zhao & Cohan (2026) matters because it gives external evidence that our observed failure mode is not idiosyncratic.

Their setup is unusually relevant: for high-quality human papers, they reconstruct nearby prior work likely to have inspired the paper, then give comparable prior-work context to LLMs and ask for ideas. Even with this controlled local context, LLM idea distributions remain systematically shifted toward **Bridge Opportunity** framing and **Synthesis/Unification** methods.

That means the fix cannot simply be:

- read more Related Work;
- use a stronger reasoning model;
- provide more neighboring papers;
- ask for more novelty.

Those interventions can leave the same framing prior intact.

Our countermeasure must operate **before generation** by changing what the searcher conditions on:

1. persistent important scientific problems;
2. raw failure/annoyance logs from real research contact;
3. longitudinal author/group histories;
4. explicit field claims whose evidence chain is weak;
5. scientific definitions/estimands that force a particular observation;
6. researcher self-reports of why a project was selected over plausible alternatives.

In other words, lineage reconstruction is not decorative background reading. It is an attempt to change the prior over what counts as an opportunity.

---

# 5. Concrete correction to our search behavior — without generating topics yet

This is not a rewrite of `RESEARCH_TOPIC_SEARCH.md`. It is a temporary discipline for the next ideation phase.

## Before reading new frontier papers

Maintain three separate ledgers:

### A. Important-problem ledger

Not paper titles. Questions/objects we would care about even if no 2026 paper existed. Each entry needs:

- why the object matters scientifically;
- which accepted beliefs depend on it;
- what would change if the answer went either way.

### B. Unexplained-friction ledger

Things observed during experiments, reproductions, model use, or close reading that violated an expectation and whose cause we genuinely do not understand.

No paper claim is attached at capture time.

### C. Instrument/knowledge ledger

Methods, formal tools, datasets, or experimental abilities we understand unusually well. These do **not** generate projects by themselves. They are only matched later against identification holes in A/B.

This separation is directly motivated by Ribeiro, Carlini, FUR, and the causal-linguistics lineage.

---

## When reading a strong paper

Do not ask “what did they leave undone?”

Record only:

1. **Which standing problem caused the authors to care?**
2. **What did they know from earlier work that a newcomer would not know?**
3. **What private/public friction made the current framing salient?**
4. **Which part of the final idea was present before the method?**
5. **Was their first attempted solution likely the final one?**
6. **What scientific object persisted across their previous papers?**
7. **Why did they choose this question instead of ten equally novel neighbors?**

If these cannot be answered from papers, search talks, interviews, blogs, author pages, thesis introductions, and project histories. If still unknown, label the provenance **unknown** rather than hallucinating a neat template.

---

## Before novelty search

For each future rough question, evaluate **taste without ownership** first.

Pretend a famous group published the result tomorrow. Would we be genuinely excited to read it? If not, direct ownership is irrelevant; kill it for reward, not novelty.

Only after a question survives that test should owner assassination begin.

This follows Olah's suggested taste exercise and Ribeiro's best-case reward logic.

---

# 6. Non-generation decision

**No new research questions, L-series entries, Kills, pilots, or candidate directories are produced by this document.**

The important output of this pass is a corrected model of human idea genesis:

> Strong researchers usually do not traverse the literature graph looking for empty neighboring nodes. They carry important problems, accumulate friction through research intimacy, build private scientific coordinates, and notice when new knowledge changes what can be inferred about those standing problems.

The next ideation phase should therefore begin from a deliberately constructed set of **standing scientific problems / unresolved frictions**, not from the latest papers themselves.

The frontier literature should then serve as evidence that updates those problems — not as the generator of the problems.

---

# 7. Core sources

Research-taste / self-report:

- Marco Tulio Ribeiro, *Coming up with research ideas*: https://medium.com/@marcotcr/coming-up-with-research-ideas-3032682e5852
- Marco Tulio Ribeiro, *Organizing and evaluating research ideas*: https://medium.com/@marcotcr/organizing-and-evaluating-research-ideas-e137637b599e
- Nicholas Carlini, *My research idea logfile, 2016–2019*: https://nicholas.carlini.com/writing/2024/my-research-logfile.html
- Chris Olah, *Research Taste Exercises*: https://colah.github.io/notes/taste/
- John Schulman, *An Opinionated Guide to ML Research* (2020; original essay widely mirrored).
- Ziyu Chen, Yilun Zhao, Arman Cohan, *Measuring the Gap Between Human and LLM Research Ideas*, arXiv:2607.01233.

Strong-paper / lineage anchors:

- Ribeiro et al., KDD 2016, LIME.
- Ribeiro et al., ACL 2018, SEARs: https://aclanthology.org/P18-1079/
- Ribeiro et al., ACL 2020 Best Overall, CheckList: https://aclanthology.org/2020.acl-main.442/
- Kallini et al., ACL 2024 Best, Mission Impossible: https://aclanthology.org/2024.acl-long.787/
- Kallini & Potts, BBS 2026, impossible-language research program.
- Quanta 2025 profile of Kallini's project genesis: https://www.quantamagazine.org/can-ai-models-show-us-how-people-learn-impossible-languages-point-a-way-20250113/
- Yue et al., NeurIPS 2025, RLVR reasoning capacity.
- Zhao et al., NeurIPS 2025, Absolute Zero: arXiv:2505.03335.
- Ni et al., ICML 2026 Outstanding, Flexibility Trap: arXiv:2601.15165.
- Li & Cotterell, NeurIPS 2025, fixed-precision transformer expressivity.
- Li & Cotterell, ACL 2026 Best, local attention: https://aclanthology.org/2026.acl-long.1739/
- Xu & Futrell, SIGTYP 2024: https://aclanthology.org/2024.sigtyp-1.1/
- Xu & Futrell, JML 2026, Strategic Resource Allocation.
- Xu, Dillon & Futrell, ACL 2026 Best: https://aclanthology.org/2026.acl-long.1550/
- Arora et al., ACL 2024 Outstanding, CausalGym: https://aclanthology.org/2024.acl-long.785/
- Boguraev et al., EMNLP 2025 Outstanding: https://aclanthology.org/2025.emnlp-main.1271/
- Ashuach et al., REVS: arXiv:2406.09325.
- Tutek et al., EMNLP 2025 Outstanding, FUR: https://aclanthology.org/2025.emnlp-main.504/
- Ji et al., ACL 2025 Best, alignment elasticity: https://aclanthology.org/2025.acl-long.1141/
- Lesci et al., ACL 2024 Best, causal memorization: https://aclanthology.org/2024.acl-long.834/
- Li et al., ACL 2025, translationese formation: https://aclanthology.org/2025.acl-long.630/
