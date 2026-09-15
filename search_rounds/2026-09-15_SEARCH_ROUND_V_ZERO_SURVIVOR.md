# Search Round V — 2026-09-15

## Status

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  
**Result of this round:** **0 NEW SURVIVOR**  
**L42:** unchanged — `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`  
**New pilot authorization:** **NONE**

This is a **real zero**, not a shallow-search zero. The round deliberately moved across multiple independent scientific objects instead of repeatedly repairing one generator. Most of the high-upside questions failed because a strong owner already asks essentially the same scientific question; several remaining openings failed because the best-case paper identity or identification quality was too weak for Main.

The purpose of this document is to prevent the next session from re-searching the same attractive-but-owned mother questions under slightly different wording.

---

# 1. Search discipline used in this round

The round followed the current doctrine:

> **Question first → scientific pressure → lineage → modern leverage → identification.**

It explicitly avoided treating any one successful research move as a template. In particular, the search repeatedly switched provenance after a few dead walls:

- reasoning / test-time computation;
- post-training / RLVR;
- architecture / inductive bias;
- mechanistic interpretability;
- classical optimization / training dynamics;
- computational mechanics / predictive-state theory;
- tokenizer / interface choices;
- memorization vs algorithmic generalization;
- efficient-attention architecture.

A candidate was not kept merely because exact prior work was absent. It also had to pass the **reward-upper-bound**, **prediction-entropy**, **belief-change-both-ways**, and **credible identifying attack** tests.

---

# 2. Recalibration heartbeats

## Heartbeat A — strong papers are not one research template

Fresh strong papers were used to break the tendency to overfit to one move:

- **ICLR 2026 Outstanding — _Transformers are Inherently Succinct_**: a theoretical comparison quantity can redefine what architecture comparison means.
- **ICLR 2026 Outstanding — _LLMs Get Lost In Multi-Turn Conversation_**: a training/deployment mismatch can itself be the main scientific object.
- **ACL 2026 Best — _Characterizing the Expressivity of Local Attention in Transformers_**: formal architecture characterization can explain a practical design surprise.
- **ACL 2026 Best — _Memory Efficiency and Resource-Rational Encoding in Sentence Processing_**: mature old theory plus a simple controllable constraint can make a new representation prediction.
- **NeurIPS 2025 — _Gated Attention_**: a very simple architecture change can matter when industrial-scale evidence and a real mechanism support it.
- **NeurIPS 2025 — _Superposition Yields Robust Neural Scaling_**: controlled toy mechanism → concrete prediction → real-model validation.

Main lesson:

> A strong paper can come from theory, mismatch, de-mystification, architecture, or a revised law. Do **not** convert any one of these into the next autocomplete grammar.

## Heartbeat B — de-mystification and question-before-method

- **ICML 2026 — _To Grok Grokking_**: a phenomenon that looked like a deep-network phase transition can be scientifically valuable precisely because a simple ridge-regression account explains it.
- **EMNLP 2025 Outstanding — _Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps_**: the scientific question exists before the intervention; unlearning is used because it makes the question answerable.

Main lesson:

> A mechanism paper is strongest when it changes the **explanatory level**, not when it merely adds a finer internal measurement.

## Heartbeat C — scientific-object validity matters

- **ACL 2026 Best — _The Imperfective Paradox in Large Language Models_** was followed by a 2026 critique arguing that part of the claimed failure comes from benchmark / construct mis-specification.

Main lesson:

> A clean effect plus a beautiful representation story is still weak if the scientific object itself is not identified correctly.

This reinforces construct audits, but **does not authorize generic “metric is wrong” papers**.

---

# 3. Fully audited dead walls

The following are **do-not-resurrect in cosmetic form** for the next round.

## W1 — Extra reasoning tokens: time vs writable memory

Mother question:

> Do filler / reasoning tokens help because they buy more sequential computation, or because they create additional writable state?

Why it looked good:

- low description length;
- directly bears on what test-time compute buys;
- both answers matter.

Why it died:

- recent theory already separates memory budget from computation budget in sequential reasoning;
- CoT / pause-token expressivity theory has already made this a formal object;
- a natural-model experiment would mostly validate a live theory line rather than create a new scientific object.

**Verdict:** important, but owned / successor-prone.

---

## W2 — Does post-training create new computation or select existing computation?

Mother question:

> Is SFT/RL/RLVR genuinely learning new algorithms, or primarily changing when pre-existing computation is selected?

Why it died:

- RLVR pattern-selection work already directly argues for redistribution over reasoning patterns;
- complementary theory shows RLVR can acquire behavior such as backtracking from on-policy dead ends;
- ACL 2026 work directly asks whether RLVR extends reasoning capability boundaries.

This is now a **contested active mother problem**, not a clean empty slot.

**Anti-resurrection:** do not revive L09/L11 as “feature creation vs feature selection,” “capability vs elicitation,” or a renamed circuit version.

---

## W3 — SFT hurts later RL: exploration/support vs optimization plasticity

Why it looked good:

> SFT sometimes improves the starting policy but harms later RL. Is the damage merely reduced action support / entropy, or has the optimization landscape itself become less plastic?

Why it died:

- entropy / support / exploration explanations are already heavily occupied by ICLR/ACL 2026 post-training work;
- the plasticity version is difficult to identify without collapsing into checkpoint/optimizer diagnostics;
- likely contribution compresses to a mechanistic refinement of an already active SFT→RL literature.

**Verdict:** crowded; no clean Main identity found.

---

## W4 — MoE routing: expert identity vs hidden-state geometry

Mother question:

> Does routing reveal semantically / functionally specialized experts, or mostly reflect geometry of the hidden state and redundant conditional computation?

Why it died:

- current literature already contains both domain/task-expert claims and geometry-based routing explanations;
- counterfactual routing, causal expert control, and modularity interventions are now being used directly.

**Verdict:** important but actively owned.

---

## W5 — Recurrent/shared depth vs copied depth

Mother question:

> Given the same number of sequential applications, does repeatedly applying one shared Transformer block learn a different kind of algorithm from using distinct parameters at every depth?

Why it died:

- Universal Transformer already framed recurrence as an algorithmic inductive bias;
- ICLR 2024 _Looped Transformers Are Better at Learning Learning Algorithms_ is an exact owner;
- modern shared-depth work continues this line.

**Verdict:** exact lineage owner.

---

## W6 — Parallel vs sequential test-time compute

Mother question:

> At equal inference budget, does serial refinement/search yield capabilities that parallel sampling cannot, or is it mainly a more efficient way to search the same base distribution?

Why it died:

- parallel/sequential/aggregation TTC is already a rapidly growing explicit research object;
- recent code, agent, and translation work directly compare sequential refinement to parallel sampling and analyze ceilings.

**Verdict:** core question, but already a field rather than an opening.

---

## W7 — Critical periods / irreversible training order

Mother question:

> If final data and total compute are identical, does seeing a structure early vs late irreversibly change what the model can learn?

Why it died:

- TACL has directly studied critical-period effects in language models using exposure age;
- 2026 pretraining data-order / curriculum papers make data organization an explicit variable;
- it would also pull the project toward a data-centric surface the current search de-prioritizes.

**Verdict:** owner + taste mismatch.

---

## W8 — Reasoning SFT as imitation-learning state-distribution shift

Mother question:

> Is the core limitation of teacher-forced reasoning SFT that training sees gold intermediate states while deployment runs on the model’s own states?

Why it died:

- 2026 work already explicitly frames post-training as **states, not tokens**;
- on-policy distillation / reasoning work directly treats learner-prefix distribution mismatch as the central problem.

**Verdict:** direct owner.

---

## W9 — Hybrid SSM/attention role split

Tempting formulation:

> Does an SSM provide compressed state while attention supplies exact retrieval, and is this why hybrids work?

Why it died:

- this functional split is already a live theoretical and empirical explanation for hybrid architectures;
- a new experiment would likely be “validate the proposed role split on another model.”

**Verdict:** successor paper risk.

---

## W10 — Do circuits persist across scale/training?

Mother question:

> Is a circuit found in a small model / early checkpoint the same computation used after scaling and training, or does the model replace the algorithm?

Why it died:

- cross-scale and cross-training circuit studies already find a nuanced answer: individual components can change while higher-level algorithms remain stable;
- 2026 work explicitly studies circuit universality / stability.

**Verdict:** direct owner.

---

## W11 — Why next-token prediction learns future-useful state

Mother question:

> The objective is called next-token prediction. Why do earlier hidden states learn variables useful only many tokens later?

Why it looked excellent:

- very low description length;
- foundational consequence;
- naturally invites a causal gradient decomposition.

Why it died:

- ICLR 2026 _Seemingly Useless Features_ already decomposes gradients into direct / pre-caching / circuit-sharing effects;
- its “myopic training” stop-gradient intervention is essentially the decisive experiment we would have proposed.

**Verdict:** exact owner. Strong example of why “fresh strong paper → obvious unresolved why?” becomes successor search.

---

## W12 — Global planning vs local/myopic reasoning

This one reached **SERIOUS-LOOK** before dying.

Question:

> Does a reasoning model form a plan that causally constrains distant future computation, or mostly make local step-by-step decisions?

Why it passed initial taste:

- central question about what CoT is;
- easy to state;
- both outcomes change belief;
- natural distinction between “future is decodable” and “future causally controls computation.”

Owner audit:

- ICML 2026 _How Far Ahead Do LLMs Plan?_ already argues for mostly myopic behavior using future-token / answer / length probes;
- 2026 _Extracting Search Trees from LLM Reasoning Traces Reveals Myopic Planning_ includes causal deletion/pruning of reasoning structure;
- 2026 _Where’s the Plan?_ explicitly contrasts probe decodability with activation patching and finds future information can be decodable without being causal.

**Verdict:** `KILL — exact causal owner`. Do not revive as “probe is not causal.”

---

## W13 — Optimizer changes what is learned, not just speed

Question:

> Do AdamW / Muon / SGD-like optimizers select qualitatively different representations / capacity allocation even when loss and compute are matched?

Why it died:

- optimizer-dependent scaling and spectral/capacity analyses are already explicit 2026 topics;
- the broad phenomenon is not novel enough, and a narrower “feature X under optimizer Y” version has low scientific consequence.

**Verdict:** active theory/optimization line.

---

## W14 — Batch size / SGD-noise implicit bias in modern pretraining

Why it died:

- ICML 2024 already showed that classical small-batch generalization advantages change substantially in single-pass/online language-model training;
- later work systematizes critical batch-size scaling.

**Verdict:** old-law→new-regime move already executed.

---

## W15 — Independent seeds: same behavior, same computation?

Question:

> If two independently trained models solve the same task, do they converge to the same internal algorithm up to symmetry, or can behaviorally identical models implement genuinely different computations?

Why it died:

- ICML 2023 toy universality;
- “universal neurons” across GPT-2 seeds;
- ICLR 2025 Transformer↔Mamba mechanistic similarity;
- 2026 cross-seed representation/circuit alignment.

**Verdict:** established universality research line.

---

## W16 — Depth vs width: efficiency or algorithmic inductive bias?

Question:

> At matched parameter/compute budgets, does extra depth merely improve efficiency, or does it select qualitatively different algorithms/generalization?

Why it died:

- NAACL 2024 already reports controlled depth effects on compositional generalization;
- 2026 architecture-conditioned scaling and variable-width/depth work occupy the broader law.

**Verdict:** no clean unowned Main question found.

---

## W17 — Does the autoregressive / next-token objective itself select algorithms?

Question:

> If different sequence objectives have the same information and Bayes-optimal target, do they learn different internal algorithms because of the factorization/objective?

Why it died in broad form:

- TACL 2025 directly finds language-modeling objective choice changes hierarchical generalization;
- AR-vs-diffusion/masked modeling has become a major controlled comparison line;
- ICLR 2026 any-order AR work further crowds “generation factorization as inductive bias.”

**Verdict:** mother problem real, available paper not found.

---

## W18 — Why are high-level concepts linearly represented?

Question:

> Why should semantic / latent variables become approximately linearly accessible in hidden states at all?

Why it died:

- ICML 2024 _On the Origins of Linear Representations in Large Language Models_ directly studies this using latent-variable next-token models and implicit bias;
- contemporaneous work formalizes the linear representation / steering geometry;
- 2026 COLT work separates representation from linear accessibility and gives capacity results.

**Verdict:** exact theoretical owner.

---

## W19 — Normalization as computational rather than optimization structure

Question:

> Is LayerNorm/RMSNorm merely an optimization stabilizer, or does it determine where/how a learned program is implemented?

Why it looked strong:

- challenges a ubiquitous “training trick” interpretation;
- could change how we interpret effective depth and circuits.

Why it died:

- 2026 controlled SUBLEQ work directly shows normalization placement changes the layer where computation is localized;
- 2026 Post-Norm rank-collapse work provides another mechanism-level analysis.

**Verdict:** exact modern owner.

---

## W20 — “Decodable but not causal” as a general interpretability paper

Why it died:

- this is already an established methodological caution;
- ACL 2026 work such as _Patches of Nonlinearity_ shows linearly separable instruction vectors can interact nonlinearly / act as circuit selectors;
- multiple recent works directly compare probing with causal interventions.

**Verdict:** do not write another generic probe-vs-causality paper. Need a scientific question that exists before the instrument.

---

## W21 — Can test-time sequential computation be compiled into parameters?

Status after audit: **WATCH / IMPORTANT — NOT CANDIDATE**.

Question:

> Which computations genuinely require instance-specific sequential test-time work, and which can be internalized into weights so that a model answers directly?

Why it remains important:

- connects CoT, distillation, latent reasoning, and inference scaling;
- asks what TTC fundamentally buys rather than which method wins;
- a clean boundary law would be high consequence.

Why it is not a candidate now:

- 2024 explicit→implicit CoT work already studies internalization;
- 2026 _Transformers Provably Learn to Internalize Chain-of-Thought_ proves internalization on particular computations;
- CoT expressivity / circuit-complexity work supplies lower-bound regimes where extra sequential tokens genuinely increase computational power.

What would revive it:

> a **natural, task-independent quantity** that predicts compilability and is not already equivalent to known depth/horizon/complexity notions, plus a decisive test on more than a hand-built algorithmic toy.

Do **not** generate another shortest-path / parity / DP variant just to instantiate it.

---

## W22 — Predictive-state / sufficient-statistic view of hidden state

Tempting cross-field move:

> Control/statistics defines state as an equivalence class of histories that induce the same distribution over all futures. Are Transformer “world states” actually predictive states / minimal sufficient statistics?

Why it died:

This transfer has already happened:

- **NeurIPS 2024 — _Transformers Represent Belief State Geometry in their Residual Stream_** connects computational mechanics / optimal prediction to Transformer activations and explicitly finds information about the entire future;
- **ICML 2025 — _Constrained Belief Updates Explain Geometric Structures in Transformer Representations_** predicts attention, OV, embedding, and representation geometry from constrained Bayesian belief updating;
- **2026 — _Grid-World Representations in Transformers Reflect Predictive Geometry_** continues this lineage with analytically known sufficient predictive vectors.

**Verdict:** direct cross-field owner. Do not rescue via “minimality” or “future-irrelevant information”; that risks reverting to `quantity X is too coarse → invent Y`.

---

## W23 — Do learned circuits compose when tasks compose?

Question:

> If A and B are composable functions, does a Transformer solve A∘B by causally reusing/composing the mechanisms for A and B, or can behavioral compositionality emerge from a separate monolithic circuit?

Why it looked strong:

- compositionality is a real old scientific problem;
- both answers matter for mechanistic abstraction;
- natural causal test exists.

Why it died:

- **ACL 2025 Main — _Circuit Compositions: Exploring Modular Structures in Transformer-Based Language Models_** asks essentially this question and demonstrates circuit reuse/composition on compositional string-edit operations;
- **ICML 2025 — _Towards Understanding Fine-Tuning Mechanisms of LLMs via Circuit Analysis_** also combines subtask circuits in compositional tasks.

**Verdict:** exact owner; do not scale it up and call that novelty.

---

## W24 — Are training “developmental stages” causally necessary?

Question:

> When a capability appears after a sequence of earlier circuit milestones, are those earlier stages true prerequisites or merely one commonly observed route?

Why it died:

- **ICML 2024 — _What Needs to Go Right for an Induction Head?_** already uses optogenetics-inspired interventions that clamp activations throughout training to identify subcircuits required for induction-head formation;
- ICML 2025 and 2026 work maps multi-phase emergence and formalizes induction-head training dynamics.

**Verdict:** direct causal developmental lineage.

---

## W25 — Is verification intrinsically easier than generation?

Question:

> Why does verifier-guided search work? Is the generator–verifier gap a genuine computational asymmetry in LMs, or mostly a consequence of task and answer representation?

Why it looked very strong:

- central premise behind best-of-N, reward models, verifier-guided search, self-improvement;
- low description length;
- both outcomes matter.

Why it died:

- **ICLR 2025 — _Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models_** formally defines the generation–verification gap, studies scaling, cross-verification, iterative self-improvement, and task dependence;
- 2026 factual-GV work traces when verification is learned relative to generation and how it survives continual learning.

**Verdict:** major standing problem, but already a named active research object.

---

## W26 — Is tokenization an efficiency detail or an inductive bias?

Question:

> If two tokenizers preserve exactly the same underlying text, does tokenization merely change efficiency, or does it change learned generalization/computation even under controlled training?

Why it died:

- NAACL 2024 trains 24 controlled 2.6B models across tokenizer choices;
- TokSuite trains fourteen otherwise-identical 1B models varying tokenizer;
- 2026 work directly studies tokenization invariance under alternate valid segmentations.

**Verdict:** controlled science already underway. A mechanistic sequel would need a much stronger independent question.

---

## W27 — Input/output weight tying as hidden inductive bias

Question:

> Sharing the input embedding and output classifier is usually treated as parameter efficiency. Does tying distort the learned representation because the two interfaces receive fundamentally different gradients?

Why it died:

- EACL 2017 already analyzed different update dynamics under tying;
- **ACL 2026 Findings — _Weight Tying Biases Token Embeddings Towards the Output Space_** directly shows output-gradient dominance, unembedding bias, and causal effects on early-layer computation.

**Verdict:** exact mechanism owner.

---

## W28 — Memorization vs algorithmic compression

Mother question:

> Given enough capacity to memorize training examples, what makes a Transformer learn a reusable algorithm instead of a lookup table?

Why it is important:

- foundational to generalization;
- connects scaling, abstractions, grokking, and reasoning.

Why no candidate was extracted:

- ICML 2026 _How Much Do Language Models Memorize?_ gives a formal information-theoretic split between intended generalization and unintended memorization and estimates capacity;
- ICLR 2024 / PNAS 2025 controlled algorithmic work already separates memorizing vs generalizing representations and studies data-diversity transitions;
- EMNLP 2025 work claims neuron-level differentiation and causal steering of memorization vs generalization;
- any new “natural control variable” found in this round reduced to capacity/data-diversity/regularization, which would push the project toward data-centric sweeps or phenomenon gambling.

**Verdict:** important mother problem; no Main-ready attack found.

---

## W29 — GQA/MQA sharing: efficiency constraint or algorithmic bias?

Question:

> When query heads must share K/V projections, does the model learn a qualitatively different retrieval algorithm, or is GQA merely a lower-memory approximation to MHA?

Why not promoted despite weaker ownership:

- existing GQA/MQA literature already studies grouping/quality tradeoffs and learned/asymmetric grouping;
- a credible algorithmic claim would require matched pretraining of MHA/GQA models at serious scale;
- best-case reviewer compression remains “why an inference optimization loses/changes quality,” which has lower reward upper bound than the stronger questions above.

**Verdict:** unclean opening; insufficient consequence/identification for Main.

---

## W30 — Why do attention heads specialize at all?

Question:

> Multi-head attention starts from exchangeable heads. Why does training produce heterogeneous functional specialization rather than equivalent redundant heads? Is specialization task-required symmetry breaking or an accidental basis choice in an overparameterized model?

Why it looked strong:

- architecture question exists independently of interpretability tooling;
- directly connects head pruning, redundancy, GQA, and circuit universality;
- natural bridge to spontaneous symmetry breaking.

Why it died:

- **2026 — _Specialization of Softmax Attention Heads: Insights from the High-Dimensional Single-Location Model_** explicitly derives an unspecialized phase followed by multi-stage head specialization under SGD while allowing redundant heads;
- **2026 — _Symmetry Breaking in Transformers for Efficient and Interpretable Training_** explicitly manipulates Transformer symmetries and studies optimization / semantic specialization;
- 2025–26 statistical-mechanics work also directly labels attention-head specialization as spontaneous symmetry breaking, including an NLP extension.

**Verdict:** exact theoretical owner.

---

# 4. Portfolio after this round

## New survivors

**NONE.**

No new candidate receives `SERIOUS`, `PILOT-AUTHORIZED`, or a new L-number from this round.

## Existing active item

### L42 — Does Scale Reward Syntax?

Status unchanged:

> **`PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`**

Do not expand open-ended search around L42 unless a new direct collision appears.

## WATCH / IMPORTANT

### A. Compilability of test-time computation

Question:

> What property determines whether sequential reasoning can be absorbed into parameters versus requiring genuine instance-specific test-time computation?

Keep only at standing-problem level. Current local/horizon/depth/parity/DP instantiations are too crowded.

### B. Autoregressive learnability of equivalent computations

Existing WATCH remains. Do not generate another shortest-path / DP / local-predictability variant without a new natural phenomenon or theorem.

---

# 5. What the searcher learned in this round

## 5.1 “Low description length” is working — but strong groups see those questions too

The most attractive questions in this round were not bad ideas. In fact, many were **so natural that they already had exact 2024–26 owners**:

- why NTP stores future-useful features;
- whether reasoning plans globally;
- whether circuits compose;
- whether verification is easier than generation;
- why attention heads specialize;
- whether hidden states match optimal predictive states.

Therefore an exact owner is not evidence that the searcher generated nonsense. It is often evidence that **problem taste improved**.

The remaining challenge is timing / leverage:

> Find the natural question **before** the literature has already built the decisive instrument.

## 5.2 Fresh strong papers are dangerous if immediately used as parents

The cleanest dead wall was W11:

> strong paper says models represent future-useful variables → ask why → independently rediscover owner’s own pre-caching/myopic intervention.

This is the successor-paper trap in its purest form.

After reading a strong paper, prefer extracting:

- what kind of evidence changed belief;
- what older standing problem it connected to;
- what made the attack newly possible;

rather than asking “what remains unexplained in this paper?”

## 5.3 Cross-field transfer only works when the source theory makes a new prediction

Predictive-state / computational-mechanics work is a positive calibration example even though it is already owned.

The good transfer was not:

> causal states are a cool concept; use them to describe LLMs.

It was:

> source theory specifies an exact belief-state geometry / update rule **before looking at activations**, then the model is tested against that prediction.

Future cross-field search should demand this standard.

## 5.4 “No exact owner” is far below the acceptance bar

GQA algorithmic bias survived owner search more than most questions, but still failed because:

- best-case consequence was weaker;
- a decisive matched experiment is expensive;
- the reviewer can compress the identity to an efficiency-architecture explanation.

This is important: avoiding owner collision must not make the searcher reward obscure questions.

## 5.5 Do not over-correct into construct criticism

The ACL-2026 Imperfective-Paradox discussion reinforces construct validity, but generic “benchmark/metric is wrong” is not now a preferred generator.

The scientific object should be challenged only when:

> fixing the object changes the substantive scientific conclusion.

---

# 6. Recommended next-round starting policy

Do **not** begin by repairing W1–W30.

The next round should open fresh standing-problem pools from at least three independent sources, ideally before looking for modern papers that instantiate them:

1. **Strong-author lineage without successor generation**  
   Reconstruct what question existed *before* the recent paper, then jump to a different scientific object.

2. **Older theory with a genuinely changed foundation-model assumption**  
   Require a same-quantity contradiction or a concrete new prediction, not “old concept × LLM.”

3. **New experimental leverage whose target question predates the tool**  
   Examples: a new causal intervention, matched training setup, controllable architecture, or theorem that makes an old unresolved question identifiable.

4. **Foundation-model defaults whose scientific consequence is bigger than the component**  
   Do not enumerate components mechanically. A component is worth studying only if its answer revises a general claim about learning/computation.

At each fresh pool, ask first:

> **Would an excellent researcher want the answer if my preferred method did not exist?**

Then:

> **If the result goes either way, what belief changes?**

Only after both are strong should owner search begin.

---

# 7. Bottom line

This round found **no new candidate that clears Main-level problem taste + novelty + identification + feasibility simultaneously**.

That is acceptable because the search surface was broad and the strongest failures were informative:

- several apparently excellent questions are already first-class research programs;
- several weaker unowned openings do not have enough reward upper bound;
- forcing a survivor now would mean lowering standards or reverting to successor-paper search.

Current portfolio remains:

> **L42 — bounded pilot only; no approved Mainline.**  
> **WATCH — test-time-computation compilability; autoregressive learnability of equivalent computations.**  
> **Open-ended search remains ACTIVE.**
