# 2026-09-13 — Pressure-First Search XI

Continuation after `PRESSURE_FIRST_SEARCH_X.md`. This rolling log deliberately switches scientific objects rather than reconstructing dead parents. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor; this file makes no portfolio promotion.

Doctrine: **scientific pressure first → decisive matched/stress test → phenomenon second**.

---

## P49 — Did instruction tuning destroy example-based in-context learning?

**Status:** `DROP / DIRECT MODERN-REGIME OWNER + OLD TRADE-OFF PROGRAM`

### Pressure
A tempting training/inference mismatch is that instruction tuning repeatedly teaches explicit rule-following, while deployment often asks the same model to infer a latent task from demonstrations. One could ask whether post-training overwrites example-based induction or merely biases the model toward explicit rules.

### Why dead
EMNLP 2025 already reports a systematic instruction-following vs few-shot-ICL trade-off under adaptation. More importantly, 2026 work directly compares rule-based and example-based ICL and reports that instruction tuning strongly amplifies rule learning while leaving example-based capacity comparatively intact. Earlier representation work also connects instruction tuning and ICL states. The strongest likely answer is therefore already inside an active program rather than a fresh parent.

**Reviewer compression:** `IT/ICL trade-off + rule-vs-example modern comparison + representation convergence = destroy-vs-bias is a refinement.`

**Anti-resurrection:** do not reopen as `SFT erases ICL`, `rule following suppresses examples`, or `examples are still latent but unread` via a new checkpoint or patch.

Sources: EMNLP 2025 *Improving Instruct Models for Free*; 2026 *LLMs Learn Better In-Context from Rules than from Examples*; Findings ACL 2024 ICL/IT representation work.

---

## P50 — Are linear concept representations a genuine property of LMs, or an artifact of the probe/intervention coordinate system?

**Status:** `DROP / FOUNDATIONAL QUESTION ALREADY AN ACTIVE THEORY PROGRAM`

### Pressure
A large fraction of interpretability assumes concepts are represented by directions, subspaces, or sparse features. The attractive stress test is to ask whether causal success of a linear direction identifies a genuinely linear internal variable.

### Why dead
Recent theory already attacks exactly the identification premise: NeurIPS 2025 shows that unconstrained nonlinear causal abstractions can become vacuous; ICLR 2025 connects emergence of linear representations to data frequency; ICLR 2026 derives feature geometry/superposition from data correlations and regularization. The question is important, but `is representation really linear?` is no longer an unowned premise. A new coordinate transform or intervention would be compressed into this existing foundations program.

**Anti-resurrection:** do not reopen generic `linear representation is gauge-dependent`, `directions are probe artifacts`, or `SAE features are not ontological variables` without a narrower scientific quantity that the recent theory cannot already predict.

---

## P51 — Autoregressive reasoning fails because training never exposes the model to its own intermediate mistakes

**Status:** `DROP / EXPOSURE-BIAS FAMILY ALREADY ACTIVE`

### Pressure
Reasoning models train on clean teacher trajectories but must condition on self-generated intermediate states at inference. A clean A/B would be `wrong intermediate state is intrinsically unrecoverable` versus `the model could recover but was never trained on that state distribution`.

### Why dead
2025–2026 reasoning work already explicitly frames teacher/student trajectory mismatch and error accumulation as exposure bias and proposes on-policy or correction-oriented training. The parent is crowded, and any fresh perturb-and-recover experiment would mainly re-identify the premise of those methods.

**Anti-resurrection:** do not reopen generic `reasoning exposure bias`, `teacher-forced CoT vs free-running CoT`, or `self-generated error states are OOD` with another model or perturbation.

---

## P52 — Why does long context hurt even when retrieval is perfect and irrelevant tokens are masked?

**Status:** `DROP / SUCCESSOR THEORY ALREADY OWNS THE NATURAL MECHANISM`

### Pressure
EMNLP Findings 2025 reports a striking mother: keeping the relevant information fixed, simply making the context longer can reduce performance by 13.9–85%; the drop persists with whitespace distractors, perfect retrieval, and even attention-masked irrelevant tokens. The intuitive RQ is whether the failure comes from information competition or from the changed positional computation itself.

### Why dead
By 2026 the same research line proves intrinsic RoPE failures that depend on length alone: loss of locality and token-relevance consistency, including position/token aliasing; ICLR 2026 independently gives a geometric RoPE account of long-input breakdown. Thus `content/retrieval vs positional computation` is no longer open enough for a new Main parent.

**Reviewer compression:** `length-only mother + RoPE length-only theory + independent geometric mechanism = the obvious explanation space has been consumed.`

**Anti-resurrection:** do not reopen as `masked padding still hurts`, `absolute position rather than distractors`, or `why perfect retrieval is insufficient` unless a same-quantity contradiction survives RoPE replacement/control.

Sources: EMNLP Findings 2025 *Context Length Alone Hurts LLM Performance Despite Perfect Retrieval*; 2026 *RoPE Distinguishes Neither Positions Nor Tokens in Long Contexts, Provably*; ICLR 2026 *Frayed RoPE and Long Inputs*.

---

## P53 — Good-enough parsing: is the syntactic structure missing, or present but overridden by semantic plausibility?

**Status:** `DROP / PORTFOLIO-REDUNDANT + ACTIVE PSYCHOLINGUISTIC PROGRAM`

### Pressure
Human good-enough processing admits a crisp question: on an implausible-but-grammatical sentence, does a model construct the syntactic/thematic relation incorrectly, or construct it correctly and later prefer the plausible interpretation?

### Why dead
This is scientifically real but wrong for the current portfolio. 2024–2025 work already evaluates good-enough processing across constructions, model architecture/scale, Turkish thematic-role illusions, and cross-linguistic grammaticality illusions. More importantly, the proposed internal A/B recreates the same `state distorted vs correct state overridden downstream` skeleton already represented by L33 and killed P41. A new phenomenon label would not create an independent scientific object.

**Anti-resurrection:** do not reopen via Moses/Escher/comparative illusions, another language, thematic-role reversal, or another plausibility manipulation unless the scientific distinction is genuinely different from state-vs-selection.

---

## P54 — Conditional presupposition: human-like judgment from pragmatic computation or shallow trigger matching?

**Status:** `PRESSURE ONLY — NOT SELECTION — NO COMPUTE`

### Pressure
Recent theory-grounded studies of the proviso problem and presupposition projection find an uncomfortable mismatch: LLMs can often reproduce human-like ratings while their explanations/diagnostics suggest shallow surface-pattern matching. The scientific object is attractive because presupposition projection has genuine formal-theoretic alternatives rather than being a competence benchmark.

Potential RQ:
> When a model projects a presupposition from a conditional, is the result causally computed from the antecedent–presupposition relation, or is a trigger/construction prior sufficient to drive the same judgment?

### Why not promoted
The current evidence does not yet provide a selective causal operation. Removing/changing antecedent content changes the semantics itself; steering a presupposition feature would merely show causal use of a feature, not distinguish pragmatic computation from learned construction priors. The 2026 CoNLL Outstanding paper already states the behavioral `human-like rating without coherent pragmatic reasoning` mismatch, so a new paper must identify **where/when relational computation is necessary**, not rediscover shallow pattern matching.

**Blocker:** find a matched intervention that keeps truth-conditional/lexical content available while selectively breaking relational integration, plus a construction-level negative control. Until then this is only a pressure.

Sources: CoNLL 2026 Outstanding *Presupposition and Reasoning in Conditionals*; LREC 2026 *Do Language Models Know Theo Has a Wife? Investigating the Proviso Problem*; LREC 2026 *There Is No Spoon*.

---

## P55 — Packing/document boundaries as a scientific variable rather than a hardware trick

**Status:** `DROP / METHOD-AND-DATA-ORGANIZATION PROGRAM, NOT A CLEAN MODEL-SCIENCE LAW`

### Pressure
Decoder pretraining/SFT often concatenates unrelated examples for efficiency, while inference usually treats a prompt/document as a coherent discourse. It is tempting to ask whether the model learns a general boundary-gating computation or merely adapts to the packing convention.

### Why dead
2025–2026 work already directly studies packing vs padding, related-vs-unrelated samples, cross-contamination, continuity-preserving packing, and data organization. The natural experiment therefore collapses into a data/training-recipe paper, which is explicitly low priority for this project. We currently lack a scientific invariant that remains interesting after the packing method name is removed.

**Anti-resurrection:** do not reopen as `random packing teaches context ignoring`, `document separators gate attention`, or `packing contamination` unless there is a general computation law independent of the training recipe.

---

## Round checkpoint

**New survivor: 0.**

This is not a round closeout. Several independent pools remain active. In particular, P54 is only a pressure and must not consume the search; next batches should continue switching objects across decoding/generation, post-training assumptions, representational geometry, classical psycholinguistic laws, and weakly identified causal explanations.