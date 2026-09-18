# Failed Topics — 2026-09-17 Round 4

**Status:** durable kill ledger. Read together with every other `FAILED_TOPICS*` file before generating new topics. These are negative/process evidence only, never positive research-taste exemplars.

This round reset after F99 and deliberately sampled CV/video, learning dynamics, algorithmic reasoning, circuit composition, architecture theory, cognitive event segmentation, gauge theory, and control/decision theory. The main discipline was to distinguish a genuinely new scientific object from a familiar parent made to look new by a mechanistic tool or cross-domain vocabulary.

---

## F100 — Do training examples teach content or reusable computation?

**Question.** When a model improves after training on a sample, did that sample mainly install/strengthen task content and surface associations, or did it change a reusable computation/algorithm that transfers across contents?

**Why it looked promising.** ICML 2026 Motion Attribution cleanly separates appearance from motion knowledge in video training influence, suggesting a stronger causal decomposition than generic data attribution. A language analogue could in principle distinguish examples that teach answers from examples that alter a reasoning operation.

**Nearest prior.** Modern reasoning learning-dynamics work already distinguishes memorization from generalizing reasoning behavior, while recent RFT/data-influence work explicitly attributes downstream reasoning changes to training trajectories/examples.

**Failure reason.** Without a new behavioral law, the project collapses into reasoning-data attribution or memorization-versus-generalization analysis. The measurement may improve, but the mother question is already occupied.

**Growth lesson.** Motion Attribution is valuable not because `appearance vs motion` should be copied into NLP, but because it first identifies two causally distinct things a sample can teach and then designs attribution to be selectively sensitive to one. Reuse that identification logic only when the two causal objects are themselves new.

---

## F101 — Representation quality versus computation depth as substitutable resources

**Question.** If a mapping must be produced with fewer downstream computational steps, must upstream representations become more linearly separable/disentangled/decision-ready, while deeper computation can tolerate more entangled intermediate states?

**Why it looked promising.** One-step image-generation work provides a concrete case where removing iterative refinement increases the burden on conditioning representations. The broader scientific hypothesis is a trade-off between representational maturity and remaining computation.

**Nearest prior.** Depth-separation theory already formalizes functions that become simpler with additional depth; controlled transformer/HMM work directly shows layer-wise progressive refinement of task-relevant representations, while broad LM literature measures increasing separability across depth.

**Failure reason.** The abstract parent `depth can trade off against representational complexity/refinement` is mature. A language instantiation would require a new behavior whose competing explanations make qualitatively different predictions, not merely another depth sweep.

**Growth lesson.** A cross-modal resource trade-off is useful only when it yields an identifying intervention on a specific computation. Otherwise it becomes a generic depth/representation observation.

---

## F102 — A causal internal state for “computation is complete”

**Question.** Does a model contain an internal state that represents whether the current computation is sufficiently mature to safely emit/stop, distinct from confidence in a particular answer?

**Why it looked promising.** If representation maturity and remaining computation are separable resources, a system that adaptively stops would need to distinguish `I have an answer candidate` from `further computation is no longer useful`.

**Nearest prior.** 2026 work on dynamic early exit, Thought Sufficiency, hidden-state convergence, confidence leaps, and overthinking already makes internal answer sufficiency/computation stopping a first-class object.

**Failure reason.** The parent is crowded and tends to become an efficiency/halting method paper. A new probe or stopping policy would not own a new scientific question.

**Growth lesson.** Resource-trade-off ideas can easily collapse into efficiency engineering. For the current search, prefer questions about why computation reorganizes, not when it can be truncated.

---

## F103 — State representation versus operator representation

**Question.** When a model learns a transformation, does it separately represent the current state (`what is there`) and the operator/update (`how it changes`), or is the transformation only implicit in a monolithic next-state computation?

**Why it looked promising.** Video work that separates appearance from dynamics suggests a general causal distinction between state and transformation knowledge, with potential implications for reusable computation.

**Nearest prior.** ICML 2025 *(How) Do Language Models Track State?* uses controlled permutation composition to identify concrete algorithms for state updating. Adjacent task-vector work studies the co-emergence of task/operator representations and conditional execution.

**Failure reason.** `state plus update/operator` is already an explicit algorithmic-learning parent. Porting the appearance/dynamics distinction to language would be cross-domain relabeling rather than a new mother question.

**Growth lesson.** The reusable lesson from motion/appearance work is not `state vs dynamics`; it is to identify two entangled causal objects and build interventions that selectively alter one while holding the other fixed.

---

## F104 — Higher-order computation from pairwise attention primitives

**Question.** Standard self-attention scores pairwise query-key relations, yet some tasks require irreducible three-way or higher-order interactions. How does an ordinary Transformer compose pairwise primitives into higher-order computation?

**Why it looked promising.** The pressure follows directly from the architecture rather than a reported anomaly, and yields natural possible worlds: cross-layer composition, conjunctive MLP codes, coordinated heads, or shortcut enumeration.

**Nearest prior.** NeurIPS 2024 work directly studies the sequential acquisition of higher-order token interactions during training. ICML 2025 theory characterizes limitations of pairwise self-attention and proposes HyperAttention for explicit multi-entity interactions.

**Failure reason.** Both the theoretical limitation and the learning of higher-order interactions are already explicit research objects.

**Growth lesson.** `Architecture primitive is only order-k while task requires order-(k+1)` is a strong generator, but theory and architecture literatures must be audited immediately because such gaps are obvious targets for new modules.

---

## F105 — Are learned skills/circuits genuinely composable?

**Question.** If a model separately knows computations A and B, does a novel A→B task causally reuse and compose the existing mechanisms, or invoke a separate joint shortcut/circuit?

**Why it looked promising.** Capability composition is only scientifically meaningful if the internal mechanisms are reusable; this naturally supports causal circuit interventions rather than score-only evaluation.

**Nearest prior.** ACL 2025 *Circuit Compositions* directly asks whether reusable circuits can be composed into complex capabilities and tests circuit-set composition. ICML 2024 work on compositional capabilities further separates capability selection from execution, associating attention and FFN roles with these stages.

**Failure reason.** Mechanistic compositionality of learned capabilities is already a named parent.

**Growth lesson.** The published lineage upgrades `can skills compose?` into `are modules reused faithfully?`, `does composition preserve causal function?`, and `does failure come from selecting a module or executing it?`. Those upgrades are reusable, but not this parent.

---

## F106 — Attention sinks as a workaround for missing no-op action

**Question.** Softmax attention must distribute total probability mass somewhere even when a head should retrieve nothing. Are attention sinks an architectural workaround that implements a null/no-op action by dumping mass into a harmless location?

**Why it looked promising.** This is a clean `architectural constraint -> seemingly impossible function -> workaround` question and fits the strongest Zhao-style requirement better than merely observing sink tokens.

**Nearest prior.** 2026 work on attention sinks proves that normalized softmax attention can require sink-like behavior on trigger/default tasks precisely because it lacks a genuine no-op; alternative non-normalized/gated attention removes the necessity. NeurIPS 2025 Gated Attention likewise addresses the inability to suppress attention globally.

**Failure reason.** The exact functional role, architecture-level necessity, minimal task, and constraint-removal validation have already been performed.

**Growth lesson.** This is an exemplary paper-growth pattern: `weird pattern -> functional role -> derive necessity from operator constraint -> construct minimal task -> remove the constraint and watch the mechanism disappear`. Preserve this as positive search methodology, not as a reusable topic.

---

## F107 — Latent event boundaries in continuous sequence processing

**Question.** Does a sequential model autonomously segment a continuous stream into latent episodes/states, and are those boundaries triggered by prediction error or latent-cause changes?

**Why it looked promising.** Event boundaries could provide a higher-level state update primitive without relying on linguistic segmentation categories.

**Nearest prior.** Event Segmentation Theory and latent-cause models are mature in cognitive science; ICCV 2025 online generic event-boundary detection explicitly uses prediction error to infer boundaries in video.

**Failure reason.** A language-model version would be classic event-segmentation theory transported into a new model family, with no new functional necessity.

**Revival condition.** A modern-model-specific boundary operation whose predictions cannot be reduced to prediction-error/latent-cause event segmentation.

---

## F108 — Gauge-invariant mechanistic explanation

**Question.** Neural networks admit large families of functionally equivalent invertible reparameterizations. Which mechanistic claims about directions, axes, subspaces, or circuits are invariant under these symmetries, and which are coordinate artifacts?

**Why it looked promising.** The question attacks a foundational assumption behind representation geometry and mechanistic interpretability: a true computation should survive changes of basis that leave the network function unchanged.

**Nearest prior.** 2025–2026 theory explicitly characterizes gauge symmetries of Transformer/neural representations and studies representation geometry modulo such transformations.

**Failure reason.** The scientific object shifts from `what computation does the model perform?` to `what properties should an interpretability method satisfy?`, making it primarily a methodology/invariance paper. The mathematical parent is also already active.

**Growth lesson.** A beautiful macro-variable or geometry is not enough; explanations need constrained alignment and causal predictions, otherwise reparameterization freedom can make many stories equally compatible with the same function.

---

## F109 — Dual-control / information-seeking actions in LLM agents

**Question.** When an action both changes the external world and changes what the agent will be able to observe, does an LLM agent represent task value and information value separately, choosing exploratory/probing actions when their future information gain outweighs immediate progress?

**Why it looked promising.** In control theory, action selection under partial observability is not just exploitation: actions can deliberately reduce uncertainty. This creates clean possible worlds and could be tested without a benchmark leaderboard.

**Nearest prior.** Active information gathering and clarification are mature agent/POMDP objects; ACL 2026 work already uses structured uncertainty and expected value of perfect information (EVPI) to decide when clarification/probing is worthwhile. Embodied and planning work explicitly discusses dual-control-style exploratory actions.

**Failure reason.** The reviewer-level parent is `active information gathering / value of information under partial observability`. Calling it dual control or applying it to another LLM agent environment is old question + new model/task.

**Growth lesson.** Control theory is useful when it provides a new identifying prediction, not merely a renamed objective. For a viable transfer, the LLM must face a structural conflict not already expressible as standard information-seeking/POMDP behavior.

---

## Round-level diagnosis

**Result: 0 survivor.**

This round generated many apparently fundamental topics, but most collapsed into mature parents once searched outside adjacent NLP. The most useful positive lessons came from covering papers rather than the seeds themselves:

- **Motion Attribution:** first separate two causally distinct things a sample can teach, then design attribution selectively sensitive to one.
- **Attention-sink necessity:** strange behavior becomes a mechanism paper only after identifying its functional role, deriving it from an architectural constraint, reproducing it in a minimal system, and making it disappear when the constraint is removed.
- **Heptapod/local-shortcut line:** ask which supervision can be satisfied without learning the intended structure, then intervene so shortcut and structure-learning worlds diverge.
- **Flexibility Trap:** an apparent architectural advantage can become a scientific question when the extra freedom lets the model systematically avoid the hardest/most globally decisive computation.

The generator also began to drift toward `fundamental-sounding property + mechanistic tool` (depth, operators, higher-order interactions, gauge invariance). Stop that generator here. The next round should begin from fresh strong-paper conflicts or constraints, especially outside representation geometry and attention mechanics.