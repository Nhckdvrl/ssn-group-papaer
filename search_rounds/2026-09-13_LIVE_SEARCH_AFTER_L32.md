# 2026-09-13 — Live Search After L32

**Purpose:** rolling post-L32 provenance-first search log. Persist seriously investigated dead hooks immediately so an interrupted round does not rediscover them.

**Rule:** only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing. Everything below is dead/non-actionable unless a qualitatively different scientific contradiction appears.

---

## Hook A — Why can one random supervised token per reasoning trajectory be enough?

**Status:** `DROP / REVIEWER-COMPRESSIBLE + CROWDED SPARSE-TOKEN PARENT`

### Origin

Liu et al. (arXiv 2609.04565), *Extremely Sparse Supervision Incentivizes Reasoning Ability*, reports a striking mother result in on-policy distillation: supervising only one or two generated tokens per reasoning trajectory (roughly 0.05% of tokens) often matches or exceeds dense token-level supervision. The effect is reported across nine Qwen3 teacher–student configurations and extended to coding, Llama models, and PPO/RLVR.

Source: https://arxiv.org/abs/2609.04565

### Missing sentence attempted

> If nearly all token losses can be deleted, why does one arbitrary supervised token still transmit enough learning signal to improve reasoning?

### Why it dies

The strongest easy version is already reviewer-compressible. Uniformly choosing one token from every on-policy trajectory is a stochastic subsample of the dense token objective; across many trajectories its gradient is a high-variance estimator of dense token supervision rather than evidence for a new hidden reasoning unit. A paper whose strongest conclusion is “one random token works because token-level gradients are redundant / can be stochastically subsampled” is therefore too close to ordinary stochastic-gradient logic.

The non-random fallback — only a sparse subset of *special* reasoning tokens matters — is also already a crowded scientific parent:

- ICML 2025 *Critical Tokens Matter* identifies sparse trajectory tokens whose replacement strongly changes reasoning success and uses them for token-level preference optimization.
- ICLR 2026 *Reshaping Reasoning in LLMs* explicitly reports that RL primarily optimizes a sparse subset of critical tokens and changes reasoning-pattern frequencies through them.
- nearby 2025–2026 selective-token fine-tuning / token-importance optimization work further owns the broad claim that sparse reasoning-token supervision can be sufficient or superior.

Thus the attractive anomaly decomposes into two already-predictable stories: **random sparse supervision ≈ stochastic gradient subsampling**, or **selected sparse supervision ≈ critical-token optimization**. The exact 0.05% operating point is striking but not by itself a new Main-level inference.

### Strongest reviewer compression

> `Dense OPD token loss + random token subsampling gives an unbiased/high-variance gradient estimate; critical-token work already shows a small subset of reasoning tokens has disproportionate causal/training value = the sparse-supervision result.`

### Anti-resurrection

Do not reopen as `why one token is enough`, `reasoning only needs sparse corrections`, `find the best supervised token`, or `positive-vs-negative critical-token reward` unless a future result violates both the stochastic-subsampling account and existing critical-token/pattern-selection explanations on the same quantity.

---

## Hook B — Why does knowledge distillation help reasoning but slow factual recall only in mid-training?

**Status:** `DROP / MOTHER PAPER ALREADY OWNS EXPLANATION + COST`

### Origin

He et al. (arXiv 2609.01532), *Knowledge Distillation During Mid-Training Favors Reasoning over Factual Recall*, finds a clean stage-dependent contrast: forward-KL distillation improves reasoning and factual recall during from-scratch pretraining, but during mid-training it continues to improve reasoning while slowing factual-recall acquisition relative to ordinary next-token prediction.

Source: https://arxiv.org/abs/2609.01532

### Why it initially looked good

The mother is large and simple: **the same broad KD mechanism changes sign for factual learning depending on training stage while reasoning keeps benefiting.** This is exactly the kind of training-stage anomaly current search prefers.

### Why it dies

The natural missing sentence is not actually left open. The paper itself traces the stage dependence to the interaction between:

- **teacher predictive confidence**, which is systematically higher on procedural/reasoning-oriented tokens than on knowledge-intensive ones; and
- the **student's evolving knowledge state**, where factual predictions have already become lower-entropy by mid-training.

It then performs the relevant intervention by introducing **Switch Distillation**: distill where teacher entropy is low and fall back to ground-truth cross-entropy otherwise. This substantially closes the factual-recall trade-off while retaining reasoning gains, including after post-training.

So `why does mid-training KD favor reasoning?` is already the mother's explanatory center, not an unexplained side result. Any deeper alternative would need to contradict the reported entropy/state account rather than merely add representation analysis.

A faithful re-identification is also expensive: the released setup uses large-scale OLMo pretraining/mid-training trajectories, so an unrelated small-model reproduction would not identify the published stage effect.

### Strongest reviewer compression

> `The mother itself establishes the stage-dependent trade-off, identifies teacher-confidence × student-state asymmetry, and fixes it with an entropy-routed objective.`

### Anti-resurrection

Do not reopen as `KD teaches procedures but overwrites facts`, `teacher entropy explains reasoning-vs-knowledge`, `why pretraining and mid-training KD differ`, or another hidden-state decomposition unless a new same-quantity result directly violates Switch Distillation's proposed mechanism.
