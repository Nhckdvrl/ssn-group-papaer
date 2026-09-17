# Failed Topics — 2026-09-17 Round 3

**Status:** durable kill ledger. Read together with every other `FAILED_TOPICS*` file before generating new topics. These are negative/process evidence only, never positive research-taste exemplars.

This round deliberately expanded provenance beyond adjacent NLP: speech/full-duplex interaction, control and neuroscience, masked/diffusion generation, CV/VLA, statistics, information theory, representation learning, and general ML. A recurring discipline in this round was: when a seed collided with a paper, first extract how the published work grew from a naive idea into a Main-level scientific question, then kill the seed itself.

---

## F80 — Backchannel versus interruption as multimodal turn-control computation

**Question.** When the same short expression (e.g. “yeah”) can be either a backchannel or a genuine attempt to take the floor, how does a speech-language model combine lexical content, prosody, timing, and dialogue state into the decision to yield, continue, or interrupt?

**Why it looked promising.** The lexical sequence can be identical while the required conversational action differs, giving a clean cue-integration problem with natural competing computations and possible causal interventions.

**Nearest prior.** Full-duplex speech work already makes interruption versus backchannel a first-class object; recent systems such as DuplexSLA explicitly introduce semantic-driven turn-taking control in unified speech-language interaction.

**Failure reason.** The reviewer-level parent is already `how multimodal conversational cues determine turn-taking / interruption / backchannel behavior`. Matched-prosody interventions plus hidden-state analysis would be mechanistic deepening of an occupied parent.

**Growth lesson.** A strong speech mechanism paper must identify a computation beyond cue integration itself; “same words, different prosody/timing” is now a standard identification pattern rather than an under-owned mother question.

---

## F81 — State similarity versus transformation similarity across independently trained models

**Question.** If hidden representations from two independently trained models can be linearly aligned, do the models actually implement the same layer-to-layer transformation/computation, or can similar states arise from functionally different operators?

**Why it looked promising.** This follows the Zhao-style emphasis on `h_l -> h_{l+1}` rather than probing `h_l`, and could distinguish representational similarity from computational equivalence.

**Nearest prior.** General-ML representation-comparison work already distinguishes representational from functional alignment; model-stitching work shows that apparently compatible representations can still give misleading conclusions about computation. Cross-model concept/subspace transfer is also active in LLMs.

**Failure reason.** Without an independently motivated behavior whose explanations diverge, replacing state similarity by transformation similarity becomes a new comparison/measurement layer, easily reviewer-compressible to `better representation similarity / functional alignment analysis`.

**Revival condition.** A concrete behavior for which two models are state-aligned yet make opposite causal predictions under a transformation-level intervention, such that the scientific object is the behavior/computation rather than the similarity measure.

---

## F82 — Prerequisite structure versus exposure order in capability acquisition

**Question.** If capability B logically depends on capability A, can a model learn B first when B examples are more frequent or earlier, or does acquisition order remain constrained by the prerequisite computation?

**Why it looked promising.** This separates data exposure order from computational dependency order and offers direct interventions on prerequisite availability.

**Nearest prior.** NeurIPS 2023 Spotlight *Skill-It!* explicitly models interdependent skills with a skill-dependency graph and shows that training prerequisite skills can improve the sample efficiency of advanced skills.

**Failure reason.** The parent `LM skills have directed prerequisite dependencies that should shape curriculum/acquisition` is already owned. Re-running the idea with new skills or larger LMs would be an exact-cell extension.

**Growth lesson.** The way a naive “what is learned first?” idea becomes scientific is to turn temporal co-occurrence into a directed dependency and causally intervene on prerequisite exposure. That growth lesson is reusable; this parent is not.

---

## F83 — Global scalar preference versus conditional/cyclic preference computation

**Question.** Pairwise preference training is often represented by one scalar utility. If real preferences are context-dependent or cyclic, does post-training learn a global ranking or a conditional/local policy that cannot be reduced to one scalar?

**Why it looked promising.** This is distinct from the killed ordinal-versus-cardinal question: it challenges the single-order representation assumption itself.

**Nearest prior.** ICML work on general preference models explicitly targets Bradley–Terry expressivity failures and intransitive preferences; 2026 work such as *Transitivity Meets Cyclicity* decomposes preference into transitive/scalar and cyclic components.

**Failure reason.** Non-transitive/cyclic preference representation is already a named modern alignment parent. Mechanistic analysis of a trained reward/policy model would be follow-up rather than an independent mother question.

---

## F84 — Transient developmental scaffolds during training

**Question.** Can an intermediate representation/solution that disappears by the final checkpoint nevertheless be causally necessary for the later emergence of the final capability? In other words, can the learning path contain temporary computational scaffolds that final-state analysis cannot reveal?

**Why it looked promising.** This asks a developmental question unavailable from endpoint interpretability: a feature may have no final causal role yet have changed which later features became learnable.

**Nearest prior.** Modern grokking theory already gives a closely related mechanism: an early temporary memorization solution can reshape the backpropagated signal and enable hidden layers to acquire a later generalizing representation. ACL 2026 work additionally tracks feature emergence, maintenance, and discontinuation over training.

**Failure reason.** The general parent `temporary training states can causally scaffold later representations` is already emerging in learning-dynamics theory. An LLM checkpoint-tracking version risks becoming grokking/developmental-learning plus feature tracking.

**Growth lesson.** Do not ask only where a final feature came from. A stronger developmental mechanism asks whether an intermediate state changes the future gradient field / learnable subspace. But that general move is no longer empty territory.

---

## F85 — Model-generated speech versus actually-heard speech in full-duplex self-history

**Question.** In streaming speech interaction, should an agent’s internal self-history contain what its model generated or only what was actually played to and heard by the user before interruption?

**Why it looked promising.** Asynchronous TTS/playback creates a structural mismatch between internal generation and the external conversational world; the same generated content may never become common conversational history.

**Nearest prior.** 2026 *LoopSpeech* directly names this mismatch the anchoring gap and feeds actually played audio back into the model’s self-history.

**Failure reason.** Exact parent and solution logic are already owned.

**Growth lesson.** A strong interaction paper can emerge from distinguishing internal action issuance from externally realized action. But this exact realization-vs-generation gap is no longer open in speech.

---

## F86 — Future plan in an output-null state before becoming output-potent

**Question.** Can an autoregressive LM represent a future decision before it should affect the current token, keeping the plan causally silent until the appropriate time and then making it output-potent?

**Why it looked promising.** The identification logic comes from motor neuroscience: preparatory activity can encode a movement in an output-null subspace and later rotate into an output-potent subspace. The scientific pressure is how a system can prepare future information without leaking it prematurely.

**Nearest prior.** ICLR 2026 *Latent Planning Emerges with Scale* already demands more than future-token probing: the latent plan must causally control the future output and shape earlier generation in ways that prepare for its execution. Follow-up 2026 work localizes planning sites.

**Failure reason.** The parent `causal latent future planning before explicit generation` is already directly occupied. Output-null language would mostly redescribe a mechanistic subcase.

**Growth lesson.** “Future content is decodable” is a weak initial idea. A Main-level planning claim becomes much stronger when the latent plan both changes the future decision and changes pre-execution behavior to make that future realizable.

---

## F87 — Locally valid masked conditionals versus one coherent global joint

**Question.** Can all of a masked language model’s apparently sensible local conditional distributions be simultaneously derived from one coherent joint distribution, or are they mutually incompatible?

**Why it looked promising.** This comes from a hard mathematical consistency requirement rather than a guessed anomaly. Local correctness need not imply global integrability.

**Nearest prior.** *Inconsistencies in Masked Language Models* (2022) directly proves and measures incompatibility of conditionals from different masking patterns. AISTATS 2025 work develops path/autoregressive/swap consistency conditions and characterizes when a joint distribution exists.

**Failure reason.** The exact mathematical parent is mature and explicitly named.

**Growth lesson.** Mathematical-consistency generators are high-value because they force a phenomenon instead of gambling on one, but the first audit must ask whether the constraint has already been formalized and named.

---

## F88 — Common-cause decision before multimodal fusion

**Question.** Before combining two individually credible modalities, does a multimodal model first decide whether they refer to the same object/event/cause, or does semantic similarity trigger fusion even when the evidence should remain separate?

**Why it looked promising.** Multisensory causal inference distinguishes `integrate` from `segregate` based on common-cause inference; this yields cleaner predictions than generic modality weighting.

**Nearest prior.** Causal-inference models of multisensory integration are a mature cognitive/neuroscience parent, and neural systems have already been explicitly trained/evaluated on integrate-versus-separate causal inference.

**Failure reason.** A VLM version risks becoming a classic cognitive-science question transported to a new model family. The transferable generator is valuable, but the exact question lacks parent-level novelty.

**Growth lesson.** Preserve the structural question `should these sources be merged at all?`, but seek a modern-model-specific object for which the merge decision is newly necessary rather than re-running multisensory causal inference.

---

## F89 — How multi-component circuits bootstrap themselves during learning

**Question.** If a computation only becomes useful after several subcomponents are assembled, how can gradient training learn the individually weak/useless intermediate pieces? Does component A create the learning signal for B, B create it for A, or do they cross a joint threshold?

**Why it looked promising.** This is a circuit-formation/credit-assignment problem rather than endpoint localization, and it naturally supports training-time causal interventions.

**Nearest prior.** ICML 2024 *What needs to go right for an induction head?* uses training-time activation clamping and identifies interacting subcircuits whose coordinated formation drives the induction-head phase change.

**Failure reason.** The general training-mechanism pattern `interacting subcircuits bootstrap a circuit and can be causally perturbed during formation` is already exemplified very strongly. A new circuit would need an independently important computation, not circuit-formation novelty alone.

**Growth lesson.** Checkpoint curves are insufficient. The stronger design is `final circuit -> candidate developmental subcircuits -> intervene on one subcircuit during training -> test whether another subcircuit/capability still forms`.

---

## F90 — Redundant/backup circuits make single ablations understate mechanism

**Question.** Can a Transformer implement one computation through multiple substitutable pathways such that ablating any one component appears harmless because the intervention itself induces compensatory routing?

**Why it looked promising.** Biological degeneracy shows why lesion-based causal inference can fail even when a function is mechanistically real.

**Nearest prior.** Backup Name Mover Heads already demonstrate self-repair in GPT-style circuits; 2026 *Conditional Co-Ablation* directly makes hidden redundancy and intervention-induced compensation a central interpretability problem.

**Failure reason.** Redundancy/self-repair under ablation is already an explicit mechanistic parent.

**Growth lesson.** A surprisingly weak lesion should trigger re-measurement of the post-intervention system, not the conclusion that the component was irrelevant. The mechanism itself may reconfigure after intervention.

---

## F91 — Relation as attention routing signal versus downstream relational representation

**Question.** Query-key interaction can decide *which* token to retrieve, but attention writes primarily value/content information into the residual stream. How does a standard Transformer turn a pairwise relation used for routing into a relation representation that downstream layers can explicitly compute with?

**Why it looked promising.** The pressure follows from the attention operator plus strong relational capabilities; ICML 2025 *Dual Attention Transformer* motivates explicit relational values partly from this architectural gap.

**Nearest prior.** ACL 2026 Main work on cell-based relational binding identifies relation-binding subspaces and uses activation patching to causally alter relational predictions.

**Failure reason.** Even if the exact score-to-value workaround is not spelled out identically, a reviewer can compress the project to a finer mechanistic analysis of an already owned relational-binding representation parent.

**Revival condition.** A concrete relational behavior whose outcome distinguishes `routing-only relation`, `explicit relation state`, and another computation in a way existing relational-binding work cannot absorb.

---

## F92 — Chaotic training trajectories versus convergent representations

**Question.** How can optimization be highly sensitive to tiny initialization/stochastic differences while independently trained models nevertheless converge toward highly similar/“Platonic” representations? Which level is path-dependent and which level behaves like an attractor?

**Why it looked promising.** Two mature empirical observations appear contradictory, inviting one lower-level dynamical law rather than a new representation-similarity metric.

**Nearest prior.** Recent theory already studies representation convergence under SGD stochasticity, symmetry breaking, entropic forces, and bias toward common solutions despite many parameter minima.

**Failure reason.** The contradiction is already being resolved theoretically at the correct abstraction level; another seed sweep would mainly be empirical confirmation.

**Growth lesson.** When two literatures report apparently incompatible laws, the best upgrade is not to choose which is right but to identify a lower-level quantity whose different projections produce both observations.

---

## F93 — Understanding invariance versus generation detail preservation

**Question.** Recognition/understanding benefits from invariance to nuisance variation, while generation/reconstruction must preserve those same fine-grained variations. How can one shared representation support both objectives?

**Why it looked promising.** Two mature objectives impose opposing representation requirements, creating natural possible worlds: subspace factorization, layer-wise compression, pathway separation, or only superficial parameter sharing.

**Nearest prior.** CVPR 2025 *Janus* explicitly argues that understanding and generation require different information granularity and decouples visual encoding. CVPR 2026 *Unified Latent Space via Semantic Auto-encoder* explicitly characterizes semantic abstraction versus fine-grained geometry as a representation trade-off.

**Failure reason.** The mother conflict is already directly owned in unified vision models.

**Growth lesson.** The reusable paper-growth pattern is: `two tasks conflict -> identify the conflicting representation requirements -> distinguish subspace/layer/pathway resolutions -> causally validate`. Do not reduce it to two benchmark tables.

---

## F94 — Superposition versus precise variable binding

**Question.** If large models rely on superposition to compress many features into limited dimensions, how do they temporarily separate role/entity variables well enough for precise binding without cross-talk? Do relevant variables dynamically de-mix, orthogonalize, or receive temporary addresses?

**Why it looked promising.** This is a structural conflict between a capacity-efficient representation strategy and a computation that appears to require clean variable separation.

**Nearest prior.** Binding-ID work already makes distances between binding vectors determine distinguishability/capacity; 2026 *Slot Machines* studies multiple entity bindings and orthogonal slots, including failures when one token must carry several bindings. Classic VSA/HRR work explicitly uses binding to make superposed representations recoverable, and MIMONets gives interference bounds for superposition channels.

**Failure reason.** The reviewer-level compression is `binding capacity/interference under superposed distributed representation`, a long-standing parent now directly connected to Transformer binding mechanisms.

**Growth lesson.** The binding lineage has already grown from existence -> binding IDs -> low-dimensional binding subspaces -> distance/capacity -> multi-entity orthogonal slots -> load limits. A new capacity topic must ask whether computation qualitatively changes near a boundary, not merely how many items fit.

---

## F95 — Capacity-efficient superposition versus robustness allocation

**Question.** Does a model reserve cleaner/more separated/redundant encoding for behaviorally critical features while compressing low-value features more aggressively in superposition? Who determines the capacity-versus-robustness allocation?

**Why it looked promising.** This reframes representational capacity as resource allocation rather than a uniform property and predicts a link between causal importance and geometry.

**Nearest prior.** Superposition is already analyzed as lossy compression; recent work explicitly connects robustness and superposition, including mechanisms by which robust training removes non-robust features and reduces superposition. Toy superposition models also make allocation depend on feature importance/frequency.

**Failure reason.** This is a natural subproblem of an actively developing superposition-allocation/robustness literature rather than a new mother question.

---

## F96 — Softmax averaging versus exact multiplicity/counting

**Question.** Softmax attention produces normalized weighted averages; duplicating identical inputs does not trivially scale their contribution linearly. How can a standard Transformer nevertheless recover exact multiplicity/count information?

**Why it looked promising.** The contradiction follows from the operator itself and suggests distinct workaround algorithms rather than an empirical anomaly.

**Nearest prior.** ICML 2025 *Counting in Small Transformers* identifies relation-based and inventory-based learned counting strategies and analyzes the roles of softmax, BOS, attention, and MLPs. ICLR 2026 *The Counting Power of Transformers* further develops the expressivity theory.

**Failure reason.** The exact architecture-capability tension and learned strategy space are already occupied.

**Growth lesson.** Architecture constraints can be productive generators when they force qualitatively different workaround algorithms. But obvious constraints such as normalized averaging versus counting are now well mined.

---

## F97 — Mixed selectivity versus monosemantic/disentangled representation

**Question.** Is representational entanglement merely interference/capacity pressure, or do some flexible computations actively benefit from nonlinear mixed selectivity that would be lost under monosemantic factorization?

**Why it looked promising.** Neuroscience treats mixed selectivity as a computational resource because it expands downstream linear readout flexibility, whereas mechanistic interpretability often treats disentanglement as an explanatory ideal.

**Nearest prior.** Mixed-selectivity neuroscience already makes the functional-benefit case explicitly; modern superposition theory likewise treats overlapping representations as functionally useful rather than merely a defect.

**Failure reason.** `Entanglement: bug or feature?` is now a synthesis of two mature viewpoints, not a sufficiently specific under-owned scientific question.

**Revival condition.** A concrete task where mixed and factorized representations make opposite causal predictions under a controlled intervention, beyond generic capacity or flexibility benefits.

---

## F98 — Why approximately linear feature geometry emerges in nonlinear networks

**Question.** Given enormous nonlinear encoding freedom, why do concepts/tasks so often become approximately linearly decodable and linearly steerable? Is linearity induced by the final linear readout, residual/additive communication, superposition geometry, compositionality, or training dynamics?

**Why it looked promising.** Much of Zhao/Cho-style interpretability relies on linear/low-rank geometry; explaining why this representational primitive exists would be more fundamental than finding another linear direction.

**Nearest prior.** The Linear Representation Hypothesis has been mathematically formalized; 2026 work directly asks how linear representations are learned, and theory connects linear/orthogonal representations to compositional generalization and feature capacity.

**Failure reason.** This fundamental parent is already active at theory level. A new empirical case would not own the question.

---

## F99 — Pretrained-manifold alignment as a law of downstream learnability

**Question.** Neuroscience shows new mappings within an existing neural manifold can be learned much faster than mappings requiring activity outside that manifold. Does an analogous law govern foundation-model adaptation: are new capabilities easy or hard according to geometric alignment with existing pretrained representational/computational subspaces?

**Why it looked promising.** This makes a quantitative prediction about *learnability*, not merely whether pretrained features can be reused. A matched intervention could construct equally complex target functions aligned with or orthogonal to existing task geometry and compare adaptation speed/data requirements.

**Nearest prior.** ACL 2021 Outstanding Paper *Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning* already makes low-dimensional adaptation central. ACL 2023 measures task alignment of pretrained text representations. 2025 NTPS work measures overlap between autoregressive and downstream feature subspaces and predicts linear-probe and LoRA gains. Most directly, a 2026-09 paper titled *Teacher Geometry Shapes Learnability in Teacher-Student Networks* formalizes how teacher geometry determines optimization learnability.

**Failure reason.** The neuroscience analogy yields a clean experiment, but the reviewer-level parent is already `representation/task geometry determines transfer/fine-tuning learnability`. This would be a cleaner causal instantiation rather than a new scientific object.

**Growth lesson.** A neuroscience law is not automatically new when transferred to foundation models. The key audit is whether modern transfer-learning theory already owns the same abstract relation between geometry and learning difficulty.

---

## Active re-audit — UID online regulation remains NOT PILOT-AUTHORIZED

The control-theoretic re-audit produced a potentially stronger identification idea but not yet a sufficient one.

**Candidate distinguishing prediction.** A genuine online information-rate controller should not merely produce negative autocorrelation after a surprisal spike; it should maintain an internal *signed regulation state* (e.g. deviation from an information-rate target) whose intervention causally changes later entropy in the compensatory direction. Passive discourse/conditional-distribution effects need not have the same state variable.

**Why this is still not enough.** Generic feedback control does not require an integral/cumulative-error state in every setting. Language-generation control theory also already offers alternatives to UID in which production is an incremental policy under information-processing constraints. Unless we can derive a controller-specific prediction that is necessary under a clearly stated class of online-regulation hypotheses and impossible under conditional narrowing / ordinary autoregressive policy, the latent-state proposal risks becoming `probe for a quantity we chose to call error`.

**Status unchanged:** SERIOUS SEED / NOT PILOT-AUTHORIZED.

---

## Round-level growth lessons

1. **Prefer structural paradoxes to reported anomalies.** The strongest examples in this round came from constraints such as local conditionals needing a global joint, attention normalization versus counting, or two tasks imposing opposing representational requirements. These generate predictions before observing a benchmark failure.
2. **But obvious architecture paradoxes are heavily mined.** Softmax subtraction, counting, relational values, future planning, and binding capacity already have direct owners. Architecture-derived pressure is a generator, not a novelty guarantee.
3. **Cross-domain transfer should preserve identification logic, not terminology.** Output-null/potent, within/outside-manifold learning, common-cause inference, degeneracy, and mixed selectivity are useful because they suggest interventions. Directly asking whether LLMs exhibit the same named phenomenon is usually old-question-new-model.
4. **When a covering paper appears, study its growth.** Recurrent successful growth patterns were: probe -> causal behavioral consequence; state similarity -> transformation; anomaly -> functional role; endpoint circuit -> developmental subcircuits; two conflicting objectives -> representation requirement conflict -> mechanism of resolution.
5. **Zhao-style remains a second-stage structure.** Representation -> computation -> component -> intervention is useful only after an under-owned mother question exists. This round repeatedly killed attractive mechanisms whose parent question was already mature.

**Result so far: 0 new survivor.**
