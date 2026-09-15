# Search Round VI — 2026-09-15

## Status

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  
**Result:** **0 NEW SURVIVOR**  
**New pilot authorization:** **NONE**  
**L42:** unchanged — `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

This was another **deep-zero round**, not a shallow hook-generation round. The search moved across multiple independent scientific objects and repeatedly recalibrated against fresh 2026 strong papers rather than refining a single failed generator.

Two questions remain worth keeping in long-term memory as **WATCH / IMPORTANT**, but neither currently has a sufficiently clean identifying instrument to justify an L-series candidate or pilot.

---

# 1. Main search lesson

The dominant failure mode in this round was no longer `bad question -> kill`.

A surprising number of the questions generated were genuinely low-description-length, consequential, and easy to motivate — but **2025–2026 strong work has already asked them very directly**.

The practical bottleneck therefore shifted again:

> not merely finding an important question,
> but finding an important question whose **answer has only recently become identifiable** and whose strongest modern leverage has not already been claimed.

This matters because repeatedly shrinking a good but owned mother question into a finer internal distinction is exactly how the searcher falls back into successor-paper search.

---

# 2. Recalibration heartbeats

## Heartbeat A — strong papers can be old questions with modern leverage

Fresh ACL / ICML / ICLR work reinforced that a strong paper need not invent a new architecture or benchmark.

Examples used for calibration included:

- **Evolutionary Guided Decoding**: a classical off-policy distribution mismatch becomes load-bearing for LLM value-guided decoding; the solution evolves the training distribution with the guided policy.
- **Flexibility Trap**: challenge the supposed advantage itself, not merely a downstream failure mode.
- **To Grok Grokking**: move the explanation level downward; a simple model can be scientifically stronger than a deeper mechanistic story.
- 2026 work on Transformer training dynamics and succinct algorithms: formal architecture claims become interesting when connected to what SGD actually selects.

Lesson:

> `old concept + LLM` is strong only when the modern regime makes a previously theoretical distinction operationally decisive.

## Heartbeat B — do not turn “classic law modernized” into another template

Several attractive classical laws were already modernized almost exactly in 2025–2026:

- softmax / LM-head bottlenecks;
- edge-of-stability at billion-scale;
- dropout / weight decay in single-pass pretraining;
- neural collapse in contextual language modeling;
- finite-precision Transformer expressivity;
- kernel/lazy vs feature learning;
- benign overfitting in attention models.

Lesson:

> once a provenance class produces several consecutive ideas, stop. The source-field move itself has become the autocomplete.

## Heartbeat C — award-level taste is broader than mechanism detail

ICML 2026 award material again emphasized longevity, cross-area interest, and nontrivial insight. This was used as a correction when several questions began degenerating into:

> existing scientific question + better causal probe.

The round therefore rejected multiple technically feasible mechanism follow-ups whose **paper identity would have been created by the instrument rather than by the question**.

---

# 3. Dead walls — do not resurrect cosmetically

## V1 — Reasoning failure: wrong computation vs correct latent state / wrong readout

Question:

> When a reasoning model fails, did the internal computation itself go wrong, or is the error already diagnostically visible while the model fails to use that information?

Why it died:

- 2026 work directly reports **hidden error awareness** that is strongly diagnostic but not causally rescuable by steering, self-correction, or activation patching;
- ACL 2026 work already uses hidden-state trajectories as reasoning verifiers.

The remaining variants (`which layer first knows`, `latent correct answer`, `readout failure`) are successor questions.

**Verdict:** direct causal owner.

---

## V2 — What does SwiGLU / gated FFN actually change?

Question:

> Are modern multiplicative gated FFNs merely easier to optimize, or do they change how computation / feature specialization is organized?

Why it died:

- 2026 controlled matched-pretraining work isolates premature upper-layer attention specialization in GPT-style blocks and traces the important difference to the **multiplicative gated FFN**, rather than RMSNorm or the activation choice.

**Verdict:** mechanism owner already exists.

---

## V3 — Why does SGD select particular simple algorithms?

Mother question:

> When many algorithms fit the training set, what implicit bias determines which algorithm a Transformer learns?

Why it died in actionable form:

- optimizer-dependent simplicity bias is already an active theory object;
- modern work connects Muon / optimization geometry to simplicity bias;
- recent length-generalization theory explicitly studies when gradient descent selects generalizing / relative solutions rather than memorizing / absolute ones.

A broad `simplicity bias in LLMs` paper is too vague; a narrow toy instance is too owned / predictable.

**Verdict:** important mother problem, no available independent paper found.

---

## V4 — Softmax bottleneck in the modern LLM regime

Old-law question:

> Does the classical low-rank softmax bottleneck still create a real capability limit in modern LLMs, or has deep representation learning made it only a formal statement?

Why it died:

- 2026 **Lost in Backpropagation: The LM Head is a Gradient Bottleneck** modernizes the problem more strongly than a simple expressivity revisit: the LM head is argued to suppress roughly 95–99% of gradient norm / feedback and controlled pretraining is used to test the consequence.

**Verdict:** modern old-law revival already executed.

---

## V5 — Training plateaus / emergence: hidden gradual learning or sudden computation?

Question:

> When capability looks abrupt, did the underlying computation suddenly appear, or was it gradually present and only became behaviorally visible after a final readout / composition event?

Why it died:

- **Quiet Feature Learning** already shows important prerequisite feature learning during apparently flat periods with causal ablation;
- 2026 work on emergent capabilities in Pythia checkpoints identifies sparse attention-pattern changes and can patch post-emergence patterns into earlier checkpoints to recover capability.

**Verdict:** the causal version is already being directly studied.

---

## V6 — Why does low-rank adaptation work?

Question:

> Does downstream adaptation genuinely live in a low-dimensional functional subspace, or are low-rank parameter updates only one redundant realization in an overparameterized network?

Why it died:

- recent theory already studies LoRA expressivity / asymmetry;
- 2026 **Pretraining Induces a Reusable Spectral Basis for Downstream Task Adaptation** argues that pretraining establishes a stable spectral coordinate system reused across downstream tasks.

**Verdict:** strong current owner; do not shrink to another LoRA geometry probe.

---

## V7 — In-context learning vs weight learning: same computation?

Question:

> If the same task is learned from examples in context or from weight updates, does the model execute the same internal algorithm?

Why it died:

- prior work already compares ICL and SFT on the same task and finds substantially different internal representation landscapes;
- ICLR 2025 theory studies the emergence of in-context vs in-weight predictors;
- circuit-shift / task-vector work further crowds the mechanism space.

**Verdict:** direct scientific owner; a stronger patching instrument is not enough to create a new parent question.

---

## V8 — How is instruction hierarchy represented?

Question:

> Why does identical content acquire different control authority when labeled system / user / assistant?

Why it died:

- hierarchy training is already a major alignment line;
- AAAI 2026 work probes distinct subspaces for system–user conflict and social-authority conflict and performs steering;
- ACL 2026 work adds reasoning-based hierarchy enforcement.

**Verdict:** active mechanism line.

---

## V9 — Source identity as epistemic evidence

Broader question:

> Why does the same proposition receive different epistemic weight depending on whether it comes from a system message, user, tool, retrieved text, report, or the model itself?

Why it died:

- 2026 **Trust, but Don’t Verify: Epistemic Blind Spots in LLM Source Evaluation** directly studies source/methodological appearance versus actual validity using probing / tracing / component attribution;
- ACL 2026 work also studies evidential / epistemic framing and prior-vs-context weighting.

Expanding to more source types would become a context/model-zoo paper.

**Verdict:** direct pressure owner + taste mismatch for larger version.

---

## V10 — Process reward vs outcome reward: same optimum, different algorithm?

This reached **SERIOUS-LOOK A**.

Sharpened question:

> If a process reward is potential-based / policy-invariant with respect to the same terminal objective, can the different feedback path systematically make neural training converge to a different internal computation despite the same optimal policy set?

Why the question is real:

- classical reward shaping says potential-based shaping preserves optimal policies;
- ICML 2025 theory shows advantage can be an optimal process reward under rollout/verifier access;
- ICLR 2026-style process supervision work explicitly exploits policy-invariant shaping.

Why it did **not** pass identification:

- on natural reasoning tasks there is no accepted ground-truth notion of `same policy, different algorithm`;
- if behavioral policies are not tightly matched, representation differences are uninterpretable;
- if moved to a fully analyzable toy task, the likely result compresses to ordinary nonconvex implicit bias / optimization-path dependence, lowering the reward upper bound.

**Status:** `WATCH / IMPORTANT — IDENTIFICATION HOLD`.

Revive only if a natural task supplies a strong algorithmic equivalence class or an intervention identifies computation independently of raw representation geometry.

---

## V11 — Effective depth of Transformer computation

Question:

> Does nominal layer count correspond to actual sequential computational depth, and when does a model recruit more layers?

Why it died:

- recent work directly defines and measures effective depth across scale and tasks;
- findings already include stable relative effective-depth fractions and weak dependence on ordinary task difficulty;
- 2026 causal layer-skipping work on agent trajectories shows multi-turn execution can recruit deeper computation over time.

The apparent static-task vs agent difference is not a same-regime contradiction.

**Verdict:** active explicit research object.

---

## V12 — Lazy / kernel learning vs feature learning in foundation models

Question:

> Is scaling mostly fitting on a fixed feature kernel or continuously reshaping feature geometry?

Why it died:

- ICLR 2025 theory already connects feature learning to altered scaling behavior;
- prior language-model fine-tuning work demonstrates genuine kernel-regime behavior in some settings;
- 2026 work applies empirical NTK analysis to RL post-training and develops spectral accounts of feature-learning scaling.

**Verdict:** mature theory bridge; applying the same lens again is not enough.

---

## V13 — Why can self-training improve a model that generated its own data?

Question:

> If the learner cannot create information that was absent from itself, where does self-improvement come from?

Why it died:

- **Self-Improvement in Language Models: The Sharpening Mechanism** asks essentially this exact question and formalizes filtering / reweighting / amortization via a generation–verification gap;
- **Mind the Gap** further formalizes and measures generator–verifier asymmetry;
- later work studies residual failure modes of self-distillation.

**Verdict:** exact theory owner.

---

## V14 — Numerical precision as a computational resource

Question:

> Does BF16/FP8/INT8 merely add noise, or can reducing numeric precision qualitatively remove algorithms that depend on high-precision internal state?

Why it died:

- NeurIPS 2025 work formally characterizes fixed-precision Transformer expressivity;
- 2026 **Every Bit Counts** shows single-bit precision changes can cross expressivity thresholds for exact computations;
- precision-aware scaling laws already study the empirical regime.

**Verdict:** formal theory already claims the strongest version; natural-LLM validation would be an obvious sequel.

---

## V15 — Classical regularization laws in single-pass pretraining

The search tested whether dropout / weight decay / early-stopping-style intuition had fundamentally changed under web-scale single-pass training.

Why the generator was stopped:

- Stanford 2025 work already shows conventional dropout can hurt single-epoch language-model pretraining;
- ICML 2026 work shows carefully designed layer dropout can still improve compute efficiency at multi-billion-parameter scale;
- 2026 weight-decay work shows a conditional law: worse base loss can coexist with better downstream plasticity.

**Verdict:** multiple modern conditional laws already exist. Do not generate a third `regularizer X in modern LM regime` topic.

---

## V16 — Neural collapse vs contextual diversity

Question:

> Next-token prediction is a huge classification problem, but the same token must preserve strongly context-dependent meaning. Can language models ever exhibit classical neural collapse?

Why it died:

- NeurIPS 2024 **Linguistic Collapse** already establishes the language-model analogue;
- 2026 work studies semantic structure before collapse;
- **Neural Collapse Is Forbidden: Information Floors in Language Models** proves contextual information imposes a nonzero floor on within-token dispersion.

**Verdict:** the revised-law paper already exists.

---

## V17 — Benign overfitting / interpolation in language modeling

Why it was rejected:

- Transformer benign-overfitting theory already exists for supervised/attention settings;
- more importantly, the classical interpolation object maps poorly to natural next-token pretraining because long contexts are often unique, so `memorize noisy label yet generalize` is not cleanly defined.

**Verdict:** bad A+B bridge; scientific object becomes less precise after transfer.

---

## V18 — Unified value-of-computation for thinking, tools, and answering

This reached **SERIOUS-LOOK B**.

Initial question:

> Has a modern agent learned a common internal value-of-computation signal that decides whether to continue thinking, call an external tool, or answer now?

Why it was attractive:

- classical rational metareasoning gives a clean normative object: expected benefit of further computation minus cost;
- NeurIPS 2024 **Rational Metareasoning for LLMs** already applies VoC to deciding whether to continue reasoning;
- ACL 2025 **Adaptive Tool Use with Meta-Cognition Trigger** finds hidden signals predictive of whether external tool use is needed.

Sharpened question:

> Are internal reasoning and external tool use priced in a **shared learned currency / state**, or are they controlled by unrelated heuristics?

Owner audit:

- recent agent theory already proposes internal reasoning and external actions as equivalent epistemic tools under a unified meta-controller;
- 2026 verified-agent / value-of-information work allocates resources across search, sampling and verification;
- recent work separately studies when models should stop thinking, when dual-mode systems should invoke tools, and when extended reasoning reaches a deterministic horizon where delegation becomes necessary.

No exact paper was found that proves a single latent scalar/subspace is shared across `continue reasoning / tool / answer` actions.

However, remaining novelty compressed toward:

> several already-studied meta-decisions share a hidden representation.

That risks making the interpretability instrument create the paper identity.

Identification issue:

- a natural test would need the **same real prefix** with forced branches `continue reasoning / call tool / answer`, followed by counterfactual rollout utility estimates;
- creating an artificial `THINK` tool would contaminate the construct;
- probe-only evidence is inadequate; causal cross-action transfer would be required.

**Status:** `WATCH / IMPORTANT — NO PILOT`.

Revive only if a natural model/task exposes all action classes without synthetic interface engineering and supports a decisive common-currency test.

---

## V19 — Model-based vs model-free control in LLM agents

Question:

> Does successful long-horizon behavior come from prospective prediction with an internal world model or from cached policy / heuristic mapping?

Why it died:

- the distinction is classically identifiable with reward revaluation, transition revaluation, detour and shortcut tests;
- NeurIPS 2023 **CogEval** already transferred essentially these diagnostics to LLMs / cognitive-map behavior.

Adding activation patching would be `existing scientific question + new instrument`, and likely benchmark-heavy.

**Verdict:** owned scientific object.

---

## V20 — Why can one foundation model learn so many heterogeneous tasks without catastrophic gradient interference?

Question:

> Is scale helping simply because high-dimensional task gradients become naturally separable, or because the model learns routing / superposition that actively protects task-specific features?

Why it died:

- 2026 **Why Larger Models Learn More: Effects of Capacity, Interference, and Rare-Task Retention** asks almost exactly this, moving from controlled mixtures to OLMo pretraining across roughly 4M–4B scale and tracing larger-model gains to reduced overwrite of rare-task features;
- newer work further compares multi-task interference geometry under SFT and RL.

**Verdict:** exact modern owner.

---

## V21 — What substrate must exist before RL can create reasoning?

Cross-paper pressure:

- mid-training may alter most parameters while later RL changes relatively few;
- RL updates can look directionally similar from different starting points yet only capable starting points improve;
- feature-level analyses often portray RL as recruiting / reweighting a prepared representation substrate.

Question:

> Is RL learnability determined by an identifiable pre-RL computational substrate?

Why it died:

- ICLR 2026 **RA3** provides a theory in which mid-training creates useful action abstractions, shrinking effective action space and planning horizon for later RL;
- ICML 2026 **On the Interplay of Pre-Training, Mid-Training, and RL** isolates exploration coverage / edge-of-competence / primitive seeds as conditions for RL success;
- ExpRL and related work explicitly treats base-policy coverage as the sparse-RL bottleneck.

The remaining `find the internal substrate proxy` version is too close to the old L11-style `task gradient / learning pressure` family.

**Verdict:** `KILL — ANTI-RESURRECTION`.

---

## V22 — Correlated rollouts and effective sample size in test-time scaling

Cross-field idea:

> Parallel test-time scaling should be governed by the effective number of independent rollouts, not nominal sample count N. Correlated generations should obey an effective-sample-size law.

Why it died:

- 2026 **When More Sampling Hurts: The Modal Ceiling and Correlation Ceiling of Test-Time Scaling** develops essentially this exact account and uses the classical correlated-sample form
  `n_eff = n / [1 + (n-1) rho]`;
- diversity-aware / correlated sampling in test-time compute is already an active line.

**Verdict:** exact cross-field transfer already executed.

---

# 4. Surviving WATCH items — not candidates

## WATCH-A — Policy-equivalent rewards, different learned computation?

Question:

> When reward shaping preserves the optimal policy set, can different feedback localization systematically select different neural algorithms?

Why worth remembering:

- clean bridge between classical reward-shaping invariance and neural implicit bias;
- both outcomes matter: either policy invariance extends surprisingly far into learned computation, or internal mechanism is path-dependent even when optimal behavior is invariant.

Why not actionable:

- no clean natural algorithm ground truth;
- behavior matching is difficult;
- toy settings lower the paper’s scientific upper bound.

Needed leverage:

> a natural task with several behaviorally equivalent but mechanistically distinguishable algorithms and an intervention that identifies algorithm without relying on arbitrary representation similarity.

---

## WATCH-B — A common learned currency for metareasoning actions?

Question:

> Does a model compare `think more`, `use a tool`, and `answer now` using a common internal value-of-computation state?

Why worth remembering:

- links classical metareasoning to modern adaptive inference / tool use;
- current work separately supports metacognitive signals for reasoning and tools;
- normative unified-controller theories exist, but direct evidence for a shared learned currency was not found.

Why not actionable:

- the natural action space is difficult to hold fixed;
- artificial THINK actions pollute the construct;
- remaining novelty risks collapsing to common-subspace interpretability.

Needed leverage:

> an existing model/environment where all three actions occur naturally and counterfactual action utilities can be estimated from the same prefix.

---

# 5. Searcher updates after Round VI

## A. The generator quality improved, but 2026 owner density is extremely high

Many generated questions were not bad questions. They failed because recent strong groups had independently identified the same mother question.

This is useful evidence: the searcher is closer to good taste, but the **timing / leverage window** is now the limiting factor.

## B. Stop shrinking owned questions

If the direct mother question is already owned, do not rescue it by saying:

- `but they did not use activation patching`;
- `but they did not test a larger model`;
- `but they did not include one more action/source/task`;
- `but they did not measure the exact latent subspace`.

Those are usually successor papers unless the new operation changes the scientific statement itself.

## C. Cross-field transfer must improve precision, not reduce it

Good transfer this round:

- reward-shaping invariance created a precise policy-equivalence condition;
- value-of-computation created a precise normative quantity;
- effective sample size created a precise TTS prediction — but that one was already owned.

Bad transfer:

- benign-overfitting language became less well-defined after mapping to natural LM contexts.

Rule:

> if importing field A makes the LLM scientific object fuzzier, the bridge is probably bad.

## D. Strongest next-session target

Do **not** immediately continue WATCH-A or WATCH-B.

The next session should again open new standing-problem pools and search specifically for:

> **important old question + new identifying leverage that appeared only very recently, where the leverage has not yet been used to answer the question.**

Favor situations where a new model family / training regime / intervention changes what can be inferred, rather than merely increasing benchmark performance.

Potential source pools to inspect without precommitting to a topic:

- optimization / control concepts not already covered by reward shaping, VoC, edge-of-stability or SGD simplicity;
- information-theoretic laws whose assumptions genuinely change under autoregressive interactive deployment;
- architecture-level scientific questions arising from genuinely new 2026 model families, but only where the question predates the architecture;
- natural post-training phenomena where current papers agree on behavior but make incompatible predictions about the same causal quantity;
- simple language-science questions only if the first sentence is obvious to a broad ML reader and modern models create a new identifying experiment.

---

# 6. Portfolio after Round VI

### Mainline

**NONE**.

### L42 — Does Scale Reward Syntax?

`PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.

Unchanged. Do not use Round VI to reinterpret or extend it.

### New L-series

**NONE**.

### New pilot authorization

**NONE**.

### WATCH

- policy-equivalent process/terminal rewards -> same or different learned computation;
- common internal value-of-computation across reasoning/tool/answer actions;
- previous standing WATCH: test-time-compute compilability;
- previous standing WATCH: autoregressive learnability of equivalent computations.

The first two are not ready for Selection or compute.

---

# 7. Final verdict

Round VI returns **0 new survivor**.

This zero is accepted because the search covered genuinely independent scientific objects and repeatedly changed provenance instead of shrinking failed ideas. The strongest failures were generally caused by recent exact owners or by identification that could not support the size of the claim.

The next search should not lower standards or revisit these walls cosmetically. It should target the remaining scarce configuration:

> **a question that was important before our method existed + a genuinely new leverage that makes it answerable now + no direct owner has already used that leverage to answer it.**
