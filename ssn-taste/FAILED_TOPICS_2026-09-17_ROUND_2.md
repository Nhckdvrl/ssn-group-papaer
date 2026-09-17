# Failed Topics — 2026-09-17 Round 2

**Status:** durable kill ledger. Read together with every other `FAILED_TOPICS*` file before generating new topics. These are negative/process evidence only, never positive research-taste exemplars.

This round was freshly recalibrated against Sasano's real Slack judgments and recent ACL/EMNLP/ICLR/ICML/CV work. The search deliberately moved away from the already overused memory/uncertainty/trajectory/architecture-puzzle generators.

---

## F75 — Independent corroboration ≠ repeated evidence

**Question.** When several statements agree, does an LLM treat them as genuinely independent corroborating evidence, or merely accumulate repeated surface support even when the statements share one upstream source? More generally, can the model distinguish evidence count from effective independent-source count?

**Why it looked promising.** The scientific pressure comes from statistical evidence aggregation rather than from a recent LLM anomaly: duplicated/correlated observations should not carry the same evidential weight as independent observations. The contrast is simple, broadly understandable, and admits matched interventions that hold proposition content and nominal support count fixed while varying source dependence.

**Nearest prior.** Lin et al. (2026), *Beyond Memory Majority: Latent-Source Reasoning for Multi-Agent Memory Arbitration*, explicitly identifies correlated memories that inherit the same upstream source as a false-majority problem and estimates the effective number of independent evidence sources. Wang et al. (2026), *GraphEcho: Structural Redundancy and Evidence Provenance in LLM Graph Agents*, directly varies path count versus evidential origin while holding evidence content fixed to test whether repeated encounters are mistaken for additional corroboration.

**Failure reason.** The load-bearing statistical distinction — nominal multiplicity versus independent evidential origin — is already the explicit parent of two very recent works. Moving the same contrast from multi-agent memory/graphs to plain-context reasoning would be a cleaner or simpler cell, not a new mother question.

**Growth lesson.** Cross-domain statistical ideas are valuable when they create a new identification logic, but provenance/correlation is now colliding rapidly with agent-memory and graph-reasoning work. Parent audit must happen before designing a context-only version.

**Revival condition.** A different dependence structure whose qualitative prediction cannot be reduced to source correlation / false-majority / provenance-aware evidence aggregation.

---

## F76 — Goal-conditioned causal relevance of the same feature

**Question.** How can the same represented feature be causally active for one instructed task but causally silent for another, while remaining available in both? Does the model gate a preserved representation, rotate it into/out of a decision-relevant subspace, or route computation through task-specific pathways?

**Why it looked promising.** This is a natural multi-task computation rather than a probe question: flexible behavior requires information to change computational role as the goal changes without necessarily erasing the information itself. It also supports a Zhao-style chain from representation to transformation to component to causal intervention.

**Nearest prior.** Bigoulaeva et al. (ACL 2026), *Patches of Nonlinearity: Instruction Vectors in Large Language Models*, studies how instruction-specific representations are constructed and used, and finds that early task representations select different later information pathways — explicitly describing instruction vectors as **circuit selectors**. Broad multi-task and conditional-computation work already treats task-conditioned gating/routing of shared features as a core mechanism.

**Failure reason.** Once honestly compressed, the proposed mother question becomes `task representation conditionally selects which information pathway/feature contributes to the output`, which is already directly owned at Main level. Choosing one particular feature and showing active-vs-silent use would be a controlled mechanistic subcase, not parent-level novelty.

**Growth lesson.** The useful lesson from the Zhao/Cho chain is not to search for a feature whose causal coefficient changes with task. Recent Main work has already moved from `task vector exists` to `task representation selects downstream computation`; a new mechanistic topic needs a different higher-level computation, not finer localization of routing.

**Revival condition.** A goal-dependent transformation that makes a qualitative prediction impossible under circuit selection/gating/routing accounts.

---

## F77 — Cross-entropy as an endogenous self-reweighting curriculum

**Question.** As training progresses and easy/predictable examples acquire low loss, does ordinary cross-entropy automatically move gradient mass toward residual hard/rare examples, creating an implicit self-generated curriculum even under stationary random sampling? If so, what determines whether late training refines generalizable structure or starts memorizing noise/exceptions?

**Why it looked promising.** The pressure follows directly from the objective rather than from an anomaly: per-example gradient signal changes as the model learns. This suggests a dynamical law in which the effective training distribution can differ strongly from the nominal data distribution over time.

**Nearest prior.** The general deep-learning literature already studies memorization dynamics in which easy/shared-pattern examples are learned early and hard/atypical examples later; gradient-starvation work formalizes how learning one feature removes gradient signal for alternatives. Ravikumar et al. (ICLR 2026), *Memorization Through the Lens of Sample Gradients*, directly links when examples are learned and cumulative sample gradients to memorization. Liu et al. (2026), *What do Language Models Learn and When? The Implicit Curriculum Hypothesis*, explicitly frames pretraining as a structured implicit curriculum, while current LLM curriculum-learning papers analyze easy/hard ordering and gradient-noise dynamics.

**Failure reason.** The exact wording `gradient mass migrates as loss falls` is sharper than some adjacent work, but the reviewer-level parent is already crowded by easy-to-hard learning dynamics, sample-gradient memorization, gradient starvation, and implicit curriculum. Without a new qualitative law that makes these accounts disagree, this would be synthesis/measurement of a mature phenomenon.

**Growth lesson.** A strong training-dynamics topic needs more than an endogenous weighting story. It should expose a non-obvious regime change or conserved/controlling quantity that existing memorization/curriculum accounts do not already predict.

**Revival condition.** A concrete intervention producing opposite predictions between `residual-error reweighting`, `feature competition/starvation`, and existing implicit-curriculum accounts, rather than merely measuring their relative contributions.

---

## F78 — Rule application versus exception override as an internal computation

**Question.** When a model knows a general rule and an applicable exception, does it first activate the default conclusion and then suppress/override it, gate the default before it is computed, or store exception-specific behavior separately?

**Why it looked promising.** `General rule + exception` is a ubiquitous computation, easy to explain, and naturally produces competing mechanistic worlds. It does not require fine-grained formal semantics, and a controlled synthetic task could support representation dynamics plus causal intervention.

**Nearest prior.** Default/defeasible reasoning with exceptions is a long-standing cognitive and AI parent. Modern LM work directly evaluates default rules and exceptions, including Kirkpatrick & Sterken (2025), *Generics and Default Reasoning in Large Language Models*, and Leong & Linzen (2023), *Language Models Can Learn Exceptions to Syntactic Rules*. 2026 work additionally studies how supervised fine-tuning changes LLM exception handling in decision-making contexts.

**Failure reason.** The behavioral parent `how neural/language models learn and apply defeasible rules with exceptions` is already mature. Adding hidden-state dynamics and causal patching would amount to mechanistic deepening of an old mother question. That violates the current parent-level novelty requirement even though the computation itself is clean.

**Growth lesson.** `Old cognitive question + modern causal mechanism tools` is still an old question unless the mechanism analysis is forced by a genuinely new explanatory contradiction. Mechanistic tractability does not create mother-question novelty.

**Revival condition.** A non-default-reasoning setting in which override is only one manifestation of a broader under-owned computational primitive, with an identifying intervention that existing exception/default accounts cannot explain.

---

## F79 — Inter-token dependency propagation during diffusion-language denoising

**Question.** When one masked position becomes resolved during diffusion-language generation, how does that local commitment propagate to unresolved positions: are token predictions effectively independent conditioned on visible context, or does the denoiser construct and update an explicit dependency structure across positions?

**Why it looked promising.** Unlike autoregressive generation, masked diffusion predicts many positions in parallel, making cross-token coordination a genuine functional requirement. The question comes from the generative factorization itself and could in principle separate independent local denoising from dependency-mediated refinement.

**Nearest prior.** Deng et al. (ACL 2026), *Beyond Fully Random Masking: Attention-Guided Denoising and Optimization for Diffusion Language Models*, already studies attention-derived token dependencies and uses them to guide denoising. Zhou et al. (Findings ACL 2026), *DOS: Dependency-Oriented Sampler for Masked Diffusion Language Models*, explicitly uses inter-token dependencies for token-update order. Most decisively, Ji et al. (arXiv 2026-09-14), *DA-DLM: Explicitly Modeling Token Dependencies in Diffusion Language Models*, states that standard DLM parallel predictions discard inter-token dependencies and introduces an evolving DAG in which earlier resolved tokens anchor remaining positions.

**Failure reason.** The structural pressure and the obvious competing explanation are now directly occupied, including by a paper released only days before this search. A mechanism study of an existing DLM would be an immediate follow-up in a very fast-moving lane.

**Growth lesson.** Fast-moving new architectures are not automatically good novelty surfaces. When the scientific pressure follows directly from an obvious factorization limitation, multiple groups may already be converging on it; current-date collision search is mandatory before investing in mechanism design.

**Revival condition.** A denoising computation not reducible to dependency-aware token ordering/coordination or semantic coarse-to-fine convergence.

---

## Round-level process diagnosis

**Result: 0 survivor.** This is intentional rather than a search failure.

The generator began to drift toward a repeated pattern: identify a clean necessary computation (`independence`, `gating`, `curriculum`, `override`, `dependency propagation`) and then imagine a Zhao-style mechanistic analysis. Parent audits showed that each computation already has a mature or rapidly forming research owner. Continuing would therefore manufacture exact-cell novelty.

The next round should not keep polishing these five seeds. It should reset the search surface and look for a scientific pressure whose **mother question itself** is under-owned before asking whether a representation/computation/circuit analysis is possible.
