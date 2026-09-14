# 2026-09-14 — Explore / Topic-Provenance Corpus

**Target:** ACL / EMNLP / NAACL Main  
**Round mode:** EXPLORE ONLY — search surface expansion before candidate generation  
**Candidate status:** **NO CANDIDATES GENERATED IN THIS DOCUMENT**  
**Repository baseline:** `main` at `048590b37585f7cf8c8164de2f6c0ad5d6cda596` when this Explore round began.

## 0. Round boundary

This round deliberately does **not** extend L32/L33/L34/L35/L36/L37 and does not reconstruct L08. L08's `MC-vs-generation / compression-readout / trajectory-mediation / state-carry / external-re-grounding` descendants remain closed.

Round-specific override: `Stable anomaly -> unresolved mechanism` is treated as one provenance class among many, **not** the highest-priority generator. No changes are made here to `RESEARCH_TOPIC_SEARCH.md` or `TOPIC_SEARCH_PLAYBOOK.md`.

The goal of this phase is narrower and earlier than Selection:

> reconstruct how strong research questions grow from prior scientific knowledge before asking what *we* should do.

No full owner assassination, E01 design, L-numbering, or candidate salvage belongs here.

---

# 1. Coverage

This Explore pass scanned **35+ strong papers/projects** and deeply reconstructed **16 provenance cases** across at least **9 distinct clusters**:

1. post-training / RL / alignment dynamics;
2. reasoning / test-time computation;
3. architecture / attention / generation;
4. transformer theory / learnability;
5. semantics / syntax / linguistic theory;
6. psycholinguistics / resource-rational memory;
7. classic empirical laws under foundation-model regimes;
8. interaction / multi-turn deployment mismatch;
9. open-ended population behavior / response diversity.

The scan was intentionally diversified once a vocabulary began repeating. In particular, it did not remain inside entropy, CoT, invariance, or representation/readout.

Primary calibration set included ACL 2024–2026 Best/Outstanding papers, EMNLP 2025 Outstanding papers, NAACL 2025 award papers, ICLR 2026, NeurIPS 2025, ICML 2026, and author/project lineages where the next paper can be traced to knowledge acquired in the previous one.

A useful meta-check comes from Chen, Zhao & Cohan (2026), *Measuring the Gap Between Human and LLM Research Ideas* (arXiv:2607.01233): LLM-generated ideas are disproportionately concentrated on bridge-like opportunities and synthesis relative to human papers. This is consistent with the repository's anti-bridge rule and is one reason this corpus emphasizes **inferential moves** rather than `A + B` combinations.

---

# 2. Topic Provenance Cases

Each case is reduced to: prior scientific state -> pressure -> focal inferential move -> who discovered the central phenomenon -> claim-matched observable -> consequence.

## P01 — The Flexibility Trap (ICML 2026 Outstanding)

**Prior state.** Arbitrary-order generation is treated as a defining advantage of diffusion LMs: the model can defer difficult/uncertain tokens and exploit non-left-to-right order. Separately, reasoning work increasingly treats broad solution support and high-entropy branching points as scientifically important.

**Pressure.** The mechanism advertised as a benefit — avoiding/defering uncertainty — may be the same mechanism that suppresses exploration at reasoning forks.

**Move.** Replace top-1 quality with a claim-matched quantity: solution-space support / Pass@k. Sweep a natural arbitrariness knob, localize the loss to high-entropy forking tokens, then derive a simpler RL recipe from the explanation.

**Phenomenon provenance.** The focal paper discovers the central failure mode; prior work supplies the incompatible premises, not the anomaly.

**Consequence.** A celebrated architectural freedom becomes a conditional benefit rather than an unconditional one. The paper changes both the scientific story and the need for diffusion-specific RL machinery.

**Discovery move:** `valued mechanism -> objective-dependent liability -> new consequential quantity -> gradient -> simplification`.

## P02 — Does RL Really Incentivize Reasoning Capacity Beyond the Base Model? (NeurIPS 2025 Runner-Up)

**Prior state.** RLVR visibly raises Pass@1 and is commonly described as expanding reasoning ability through exploration.

**Pressure.** Pass@1 cannot identify expansion of the model's reachable solution support. Better mode concentration and broader support are different scientific quantities.

**Move.** Replace small-k performance with large-k capability-boundary measurement; ask whether successful RL creates support or reallocates mass over support already present in the base model.

**Phenomenon provenance.** The focal paper designs the capacity test and discovers that current RLVR often redistributes rather than expands support, and can narrow large-k support.

**Consequence.** Reinterprets what a major post-training paradigm is doing.

**Discovery move:** `headline metric -> latent consequential quantity the headline metric cannot identify`.

## P03 — Characterizing the Expressivity of Local Attention (ACL 2026 Best)

**Prior state.** Local attention is an efficiency restriction, yet prior empirical work sometimes finds that it improves model quality. Li & Cotterell's previous theory exactly characterizes a restricted global-attention transformer in a temporal-logic language class.

**Pressure.** If local attention simply removes information access, why can a restriction improve quality?

**Move.** Translate an engineering architecture difference into a formal computational coordinate: local attention contributes a distinct temporal operator; global and local attention are complementary rather than ordered by simple containment.

**Phenomenon provenance.** Prior work owns the empirical puzzle; the focal paper supplies the explanatory theory.

**Observable.** Recognizable formal-language classes and length generalization, with natural-LM experiments as corroboration.

**Consequence.** Rewrites the design story from `efficiency versus expressivity` to `different attention patterns provide different computational operators`.

**Discovery move:** `engineering anomaly -> formal object -> complementary capability law`.

## P04 — Measuring CoT Faithfulness by Unlearning Reasoning Steps / FUR (EMNLP 2025 Outstanding)

**Prior state.** CoT faithfulness is a mature debate. Input/context perturbations can change reasoning traces, but they cannot cleanly distinguish whether the verbalized step reflects parametric computation because the model may reconstruct the missing information from its parameters.

**Pressure.** The main scientific question is older than the method, but existing evidence does not identify the desired causal statement.

**Move.** Change the intervention locus: remove the reasoning information from parameters rather than only from context, then measure downstream prediction change with specificity controls.

**Phenomenon provenance.** No new mother anomaly is needed. The contribution is an identifying operation for an existing debate.

**Consequence.** Raises the evidence standard for claims that verbalized reasoning is causally tied to a model's parametric beliefs.

**Discovery move:** `mature question -> old evidence cannot identify -> new causal operation changes what can be inferred`.

## P05 — Did Translation Models Get More Robust Without Anyone Even Noticing? (ACL 2025)

**Prior state.** Character-level noise fragility was a well-established NMT problem and motivated dedicated robustness methods.

**Pressure.** The training/model regime changed radically through multilingual pretraining and modern LMs. The old law may no longer have the same load-bearing cause or magnitude.

**Move.** Re-run the old scientific contrast under the modern regime and measure degradation as a function of corruption rather than only compare one noisy endpoint; then separate plausible causes such as scale, multilinguality, architecture, and training data.

**Phenomenon provenance.** The focal paper discovers the modern-regime robustness shift.

**Consequence.** Revises an old empirical law and questions whether an entire class of specialized fixes is still addressing the current bottleneck.

**Discovery move:** `old field-shaping failure -> changed computational regime -> matched retest -> revised law`.

## P06 — Mission: Impossible Language Models (ACL 2024 Best)

**Prior state.** Strong claims in the language-acquisition debate asserted that neural LMs should learn human-possible and human-impossible languages equally well, but direct experimental evidence for that strong statement was thin.

**Pressure.** The rhetoric/claim was much stronger than its identification.

**Move.** Construct an explicit continuum of impossible languages and study learning dynamics against English controls across training, rather than argue from existing benchmark competence.

**Phenomenon provenance.** The focal paper creates the decisive stress test and discovers the asymmetry itself.

**Consequence.** Converts a broad theoretical dispute into an empirically attackable scientific program.

**Discovery move:** `strong community/theoretical claim -> weak direct evidence -> decisive stress-test continuum`.

## P07 — Why Are Sensitive Functions Hard for Transformers? (ACL 2024 Best)

**Prior state.** Transformers display several apparently separate failures/biases: PARITY-like functions are difficult, low-sensitivity functions are easier, and length generalization is selective. Expressivity alone does not explain learnability.

**Pressure.** Multiple empirical observations point in the same direction but are not unified by a single computational quantity.

**Move.** Elevate sensitivity into the common object and connect it to optimization/loss-landscape geometry: sensitive functions correspond to difficult, isolated/sharp solutions.

**Phenomenon provenance.** Prior work supplies scattered phenomena; the focal paper unifies them.

**Consequence.** Shifts explanation from `can a transformer represent it?` to `what geometry does learning that function create?`.

**Discovery move:** `scattered failures -> common scientific object -> theoretical mechanism`.

## P08 — LLMs Get Lost In Multi-Turn Conversation (ICLR 2026 Best)

**Prior state.** Real users often specify tasks progressively, whereas evaluation overwhelmingly gives a fully specified single-turn instruction. Earlier multi-turn benchmarks often changed both task and interaction structure at once.

**Pressure.** Standard evaluation removes a deployment condition that is intrinsic to the interface.

**Move.** Hold the underlying task/information fixed and shard the same specification over turns. Then decompose the observed loss into aptitude versus unreliability instead of reporting only a 39% aggregate drop.

**Phenomenon provenance.** The focal paper discovers the large multi-turn degradation through the matched comparison.

**Consequence.** Establishes a distinct reliability problem: models can possess the aptitude yet repeatedly commit early and fail to recover.

**Discovery move:** `deployment/evaluation mismatch -> matched same-task contrast -> quantity decomposition`.

## P09 — Generative or Discriminative? Revisiting Text Classification in the Era of Transformers (EMNLP 2025 Outstanding)

**Prior state.** Classical statistics gives a famous two-regime law: generative classifiers tend to need fewer samples but have worse asymptotic error than discriminative classifiers under simple assumptions.

**Pressure.** Modern pretrained AR, MLM, diffusion, and encoder architectures violate many assumptions behind the classical comparison.

**Move.** Treat the classic law itself as the scientific object and trace learning curves/sample-efficiency/asymptotic behavior across modern paradigms; do not reduce the question to one benchmark winner.

**Phenomenon provenance.** The focal study discovers how the old two-regime story changes across transformer paradigms.

**Consequence.** Updates a long-lived law and gives a modern conditional account rather than `LLM X beats classifier Y`.

**Discovery move:** `classic law -> changed assumptions -> modern conditional law`.

## P10 — Gated Attention for Large Language Models (NeurIPS 2025 Best)

**Prior state.** Gates are common across recurrent, state-space, linear-attention, and other architectures, but the exact role and placement of gates inside modern softmax attention had not been isolated systematically.

**Pressure.** A ubiquitous structural choice is often treated as a method ingredient rather than a scientific variable.

**Move.** Factor the design space with controlled variants, identify the specific gate form/location that matters, then connect its effect to nonlinearity, query-dependent sparsity, and attention-sink behavior.

**Phenomenon provenance.** The focal paper discovers the stable design effect rather than inheriting a published anomaly.

**Consequence.** Produces a general architecture principle instead of a one-benchmark trick.

**Discovery move:** `default/underexamined structural axis -> controlled sweep -> stable law -> mechanism`.

## P11 — Language Models Resist Alignment: Evidence From Data Compression (ACL 2025 Best)

**Prior state.** Many papers had observed that aligned behavior can be undone by subsequent fine-tuning and that alignment can appear shallow, but the failures were scattered.

**Pressure.** `Alignment is fragile` is a collection of observations, not yet a dynamical object or quantitative law.

**Move.** Define **elasticity** as a shared dynamical quantity, derive a compression-theoretic account, and study trajectories as perturbation amount, model size, and pretraining data change.

**Phenomenon provenance.** Prior work supplies the scattered failures; the focal paper turns them into a common object and predicts gradients.

**Consequence.** Reframes alignment as a relatively shallow perturbation against a dominant pretraining distribution and predicts when rebound should be stronger.

**Discovery move:** `scattered failures -> named dynamical quantity -> theory -> natural gradients`.

## P12 — Causal Interventions Reveal Shared Structure Across English Filler–Gap Constructions (EMNLP 2025 Outstanding)

**Prior state.** Linguistic theory has long claimed that filler-gap constructions share abstract structure. Behavioral LM evidence can support or challenge this, but similar outputs do not establish a shared internal analysis.

**Pressure.** A mature theoretical question lacks identifying evidence at the computational level.

**Move.** Use distributed interchange interventions to test whether internal causal variables transfer across constructions; then use deviations from the shared analysis to expose frequency/filler/context factors relevant to linguistic theory.

**Phenomenon provenance.** The question is inherited; the evidence type is new.

**Consequence.** Mechanistic analysis becomes an instrument for theory revision rather than an interpretability add-on.

**Discovery move:** `old theoretical debate -> new causal evidence type -> theory-relevant residual structure`.

## P13 — Memory Efficiency and Resource-Rational Encoding in Sentence Processing (ACL 2026 Best)

**Prior state.** There is broad agreement that cognitive language models need working-memory limits, but earlier model constraints often instantiate memory as a fixed window, small network, retrieval limitation, or other ad hoc bottleneck. Resource-rational cognitive theory instead treats memory as limited precision strategically allocated.

**Pressure.** The field agrees memory is limited but has not identified what limited memory should do to the **quality and structure of representations**.

**Move.** Operationalize the cognitive theory as a tunable representation-precision budget; optimize language modeling under that budget and ask what representation emerges.

**Phenomenon provenance.** The theory/pressure precedes the experiment; the focal paper discovers categorical/compressed representation and improved human reading-time fit.

**Consequence.** Creates a concrete dissociation between memory encoding quality and retrieval mechanism.

**Discovery move:** `cognitive principle -> computational resource quantity -> emergent representation -> behavioral consequence`.

## P14 — Systematicity between Forms and Meanings across Languages Supports Efficient Communication (ACL 2026 Outstanding)

**Prior state.** Efficient-communication accounts explain language systems through simplicity–accuracy trade-offs, but common complexity measures treat forms too atomically to capture internal morphological systematicity. Language-evolution work independently shows systematic structure can emerge under communicative/learning pressures.

**Pressure.** The accepted theory is missing a structural dimension of the object it claims to explain.

**Move.** Redefine complexity in terms of **learnability of meaning-to-form mappings**, which makes internal form structure measurable and lets the efficiency theory discriminate attested from counterfactual systems better.

**Phenomenon provenance.** The focal paper does not merely connect two literatures; it creates a new common quantity that neither side previously supplied in this form.

**Consequence.** Extends what efficient-communication theory can explain.

**Discovery move:** `theory blind spot -> new estimand/quantity -> previously invisible regularity becomes testable`.

## P15 — Mind the (DH) Gap! (ACL 2026 Outstanding)

**Prior state.** Human decision science documents a description–experience gap and many framing/order effects. Existing LLM studies often test isolated biases or one model family.

**Pressure.** Reasoning-oriented post-training may move decision behavior into a different regime; asking only whether an LLM is `human-like` conflates several quantities.

**Move.** Compare description/history representations, reasoning/conversational families, human references, and rational-agent references to separate human-likeness, invariance, and utility-rationality.

**Phenomenon provenance.** The paper uses a classic human law as the external scientific coordinate and discovers a model-regime split.

**Consequence.** Shows that stronger reasoning can mean less human-like but more economically invariant behavior; suggests a formation-pressure question rather than a simple bias score.

**Discovery move:** `classic cognitive law -> model-regime shift -> multiple reference ideals instead of one accuracy notion`.

## P16 — Why Does Reinforcement Learning Generalize? (ACL 2026)

**Prior state.** RL post-training often transfers better than supervised fine-tuning, while SFT can specialize/forget. Output-level results alone do not say what the training objectives build internally.

**Pressure.** `RL generalizes better` is a behavioral difference, not a formation mechanism.

**Move.** Use matched base/data comparisons, track feature evolution through training, distinguish early specialized SFT features from restrained RL changes, and intervene on compact task-agnostic features that mediate broader transfer.

**Phenomenon provenance.** The behavioral gap is inherited; the paper's step is training-dynamics localization plus causal consequence.

**Consequence.** Moves the object from endpoint representation to **how training forms generalizable computation**.

**Discovery move:** `behavioral training gap -> matched formation dynamics -> causal mediator`.

---

# 3. Author-Lineage Mining

These lineages are more useful than isolated paper templates because they show how a research program converts knowledge from paper *n* into the pressure behind paper *n+1*.

## L-A — LeapLab / Yang Yue / Gao Huang: performance -> support -> self-generated support -> architectural collision

1. **Does RL Really Incentivize Reasoning Capacity...?** learns that reasoning progress cannot be inferred from top-1 success; reachable support / large-k behavior is a different scientific object.
2. **Absolute Zero** starts from a new bottleneck: even zero-style RL still inherits the support of human-curated problem sets. The next question becomes how a model can generate verifiable learning opportunities itself.
3. **The Flexibility Trap** reuses the support/exploration lens to interrogate a separate architectural belief: arbitrary-order diffusion decoding may improve immediate confidence while shrinking reasoning solution diversity.

The reusable program dynamic is:

> acquire a sharper scientific quantity in one project -> carry that quantity, not the method, into a different assumption where it changes the prediction.

This is much stronger than `apply previous method to new task`.

## L-B — Li & Cotterell: formal coordinate system -> explain an engineering puzzle

1. **Characterizing the Expressivity of Fixed-Precision Transformer LMs** (NeurIPS 2025) gives an exact temporal-logic characterization of a restricted global-attention transformer.
2. **Characterizing the Expressivity of Local Attention** (ACL 2026 Best) uses that formal coordinate system to ask why an apparent restriction can improve models; local attention contributes a complementary temporal operator.

Program dynamic:

> paper n builds a scientific language precise enough that paper n+1 can turn a vague empirical puzzle into a theorem-level question.

## L-C — Tutek / Belinkov: editing instrument -> identifying evidence for an old debate

1. **REVS** develops a precise unlearning/editing capability for factual information.
2. **FUR** does not make `use REVS on CoT` the contribution. It notices that CoT faithfulness is an old question whose main obstacle is intervention semantics, and parameter-level unlearning changes exactly that inference.

Program dynamic:

> method knowledge becomes valuable only when an independently important question has an identification hole that the method uniquely fills.

## L-D — Xu / Futrell: corpus interaction -> resource-rational principle -> neural representation

1. **Syntactic dependency length shaped by strategic memory allocation** (SIGTYP 2024) finds a cross-linguistic interaction predicted by preferential encoding of surprising antecedents.
2. **Strategic Resource Allocation in Memory Encoding** (JML 2026) develops the efficiency principle and evidence more explicitly: surprisal should govern precision allocation.
3. **Memory efficiency and resource-rational encoding** (ACL 2026 Best) instantiates this principle inside a neural LM and asks what representational structure the resource constraint creates.

Program dynamic:

> empirical interaction -> explanatory principle -> computational realization -> new representational consequence.

The next paper is not a narrower residual of the last table; the **level of explanation changes**.

## L-E — Potts / Mahowald and collaborators: LM behavior as linguistic evidence -> causal internals as linguistic evidence

1. **Mission: Impossible Language Models** directly stress-tests a strong linguistic claim through controlled learnability.
2. **CausalGym** develops the use of causal interpretability for linguistic tasks.
3. **Causal Interventions Reveal Shared Structure Across Filler–Gap Constructions** uses causal internals to revisit a mature syntactic-theory question and derives theory-relevant residual factors.

Program dynamic:

> once model behavior is accepted as a scientific instrument, the next pressure is whether the evidence identifies the abstract computation claimed by linguistic theory.

---

# 4. Pressure Landscape — NO RQs YET

The provenance corpus supports the following **independent pressure pools**. These are not candidate questions; they are places where existing knowledge is internally incomplete.

### Pool A — Old law, changed regime

Strong examples: MT noise fragility; generative-vs-discriminative two-regime law; description–experience gap. The key question-forming pressure is not `does the old benchmark still hold?`, but which load-bearing premise changed and whether a revised conditional law can preserve both old and new evidence.

### Pool B — Headline behavior does not identify the consequential quantity

Strong examples: Pass@1 vs reachable support under RL; aggregate multi-turn loss vs aptitude/unreliability. The provenance move is to locate the quantity that the field's headline metric cannot distinguish.

### Pool C — Strong claim, weak identification

Strong examples: impossible-language learnability claim; CoT faithfulness. The pressure exists before any anomaly: community language is stronger than the evidence chain.

### Pool D — Scattered phenomena need a common scientific object

Strong examples: alignment failures -> elasticity; transformer learnability failures -> sensitivity/loss geometry. This pool is healthy when the common object predicts gradients or boundaries, not merely gives several failures one name.

### Pool E — Mature debate, newly available identifying operation

Strong examples: parameter-level unlearning for faithfulness; interchange interventions for filler-gap theory. The operation must change what can be concluded, not just add a causal-looking figure.

### Pool F — Default structural choice as a scientific variable

Strong examples: local/global attention complementarity; attention gating. Healthy versions seek a general computational/design law; unhealthy versions are architecture-module shopping.

### Pool G — Theory is missing a dimension of the object

Strong example: efficient-communication complexity could not see internal form structure until learnability of the meaning-to-form mapping became the quantity. This is distinct from combining two literatures: the new quantity changes the older theory's predictions.

### Pool H — Training pressure as formation cause

Strong examples: RL-vs-SFT feature formation; reasoning-vs-conversational decision regimes. This pool requires genuine matched-stage leverage; model-family comparisons alone cannot support training causality.

### Pool I — Resource constraint -> representation, not merely performance

Strong example: strategic memory allocation and limited precision. The scientific object is how a natural resource constraint reshapes the representation/computation, with behavior used as consequence.

### Pool J — Evaluation/deployment condition mismatch

Strong example: same task split over multiple turns. This becomes Main-level when the same underlying object is genuinely held fixed and the mismatch exposes a new reliability/computation quantity, not when it becomes another benchmark audit.

### Pool K — Aggregate outcome -> contribution decomposition

Examples include aptitude vs unreliability and descriptive-vs-prescriptive accounts of response sampling. The important move is not `A or B`; it is quantifying how components contribute and what natural condition changes their weights.

### Pool L — Construct validity can precede mechanism

The 2026 *Imperfective Paradox* award paper and its August 2026 re-analysis are a cautionary pair: a strong semantic story can still collapse if the observable does not cleanly instantiate the semantic distinction. For semantic/pragmatic search, construct validity must be checked before treating a benchmark effect as a mother phenomenon.

---

# 5. What this corpus changes about the SEARCHER

This is **not** a rewrite of repository doctrine; it is an empirical observation from the strong-paper corpus.

1. The strongest papers often begin **one inferential level before an anomaly**. Prior work gives a law, claim, theory, default, or mismatch; the focal paper constructs the test and discovers the phenomenon.
2. Many Main/award papers add only **one main inferential move**, but it is consequential: `performance -> support`, `old law -> conditional law`, `behavior -> formation dynamics`, `atomic form ignored -> learnability-based complexity`, `correlational debate -> identifying intervention`.
3. The useful unit of transfer is a **scientific quantity or inferential move**, not a topic or method.
4. A+B is sometimes legitimate only when the collision creates a **third quantity that changes predictions**. The systematicity/efficient-communication paper is a good example: the bridge is valuable because it replaces the old complexity quantity with one that can see internal form structure.
5. Strong author lineages often move **levels of explanation** rather than shrink residual novelty: corpus interaction -> principle -> neural representation; theory language -> empirical architecture explanation; editing tool -> identification of a mature debate.
6. Natural continuous knobs are common but arise from the object: k/support, corruption amount, sample size, resource precision, training progress, perturbation volume. They are not added merely to make a mechanism plot.
7. The observable is often where the intellectual contribution begins. Pass@1, aggregate success, or atomic inventory size were inadequate because the claim concerned support, unreliability, or structural learnability.
8. The current repository failure mode — `one paper -> neighbor hook -> owner search -> narrower residual` — is nearly the opposite of these successful provenance patterns.

External research-selection material points in the same direction. Carlini's public idea log separates idea capture from later project choice; Marco Tulio Ribeiro advocates expanding the adjacent possible and evaluating a project's best-case reward rather than accepting the first good-enough project; Chris Olah's research-taste exercises emphasize practicing many cheap idea judgments because full projects make feedback too expensive. These are process corroboration, not new repository rules.

---

# 6. Explicit non-generation decision

**No rough RQ seeds are recorded in this Explore document.**

The next phase should first temporarily hide paper/topic names and operate on the pressure landscape above. Only then should it batch-generate roughly 25–40 rough seeds across multiple scientific objects, each with only:

- one-sentence question;
- scientific ancestry / pressure;
- why the answer is not autocomplete;
- claim-matched observable;
- best-case scientific consequence.

Deep owner search should remain off until after horizontal taste triage.

This separation is intentional: the point of this file is to prevent the first attractive paper in the corpus from becoming the anchor for the entire next search round.
