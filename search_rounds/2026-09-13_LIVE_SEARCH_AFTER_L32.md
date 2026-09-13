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

---

## Hook C — Why can deleting task-specific Transformer layers improve accuracy?

**Status:** `DROP / PARENT ALREADY EXPLAINS BOTTLENECK + MATURE DEPTH-REDUNDANCY OWNERS`

### Origin

Naim et al., ACL 2026 Findings, *TELL-TALE: Task Efficient LLMs with Task Aware Layer Elimination*, reports that task-aware inference-time deletion of entire Transformer layers can match or improve the original model across 9 tasks and 5 model families while reducing compute. The effect also combines with fine-tuning.

Sources:
- https://aclanthology.org/2026.findings-acl.1136/
- https://arxiv.org/abs/2510.22767

### Missing sentence attempted

> If a trained Transformer chose to keep these layers, why does bypassing some of them improve the task rather than merely preserve performance?

This initially looked like a strong `restriction helps performance` mother with an exceptionally cheap causal operation.

### Owner assassination

The natural answer space is already heavily constrained by the mother and nearby work:

- **TELL-TALE itself** does not leave the benefit unexplained: its mutual-information analysis explicitly argues that some selected layers act as bottlenecks that degrade task-relevant information, and deletion removes those bottlenecks.
- **ShortGPT** already establishes large layer-level redundancy and direct whole-layer removal in LLMs.
- **The Curse of Depth** (NeurIPS 2025) supplies a causal/theoretical explanation for widespread ineffective deep layers in Pre-LN Transformers via variance growth and increasingly identity-like deep blocks, with a normalization intervention.
- Earlier early-exit/layer-pruning and layer-wise decoding work already establishes that task-relevant predictions and useful information can peak before the final depth.

A cleaner causal test of TELL-TALE's MI claim could verify whether a winning deletion skips a representation-damaging transformation, but the strongest result would still read as a mechanistic validation/refinement of an explanation the parent already states, inside a mature layer-redundancy literature.

### Strongest reviewer compression

> `ShortGPT: many layers are redundant + Curse of Depth: why deep Pre-LN blocks become ineffective + TELL-TALE: task-selected layers can be detrimental and MI identifies bottlenecks = why deletion helps.`

### Anti-resurrection

Do not reopen as `why does pruning improve accuracy`, `harmful/detrimental layers`, `task-specific bottleneck layers`, `intermediate layer knew the answer before a later layer ruined it`, or another MI/early-exit/logit-lens analysis unless a new stable result contradicts the redundancy/bottleneck account on the same quantity.

---

## Hook D — Is Lost-in-Conversation mainly caused by conditioning on the model's own premature answers?

**Status:** `DROP / DIRECT CAUSAL SUCCESSOR COLLISION`

### Origin

ICLR 2026 Outstanding Paper *LLMs Get Lost In Multi-Turn Conversation* establishes a large, stable mother: when the same underlying instruction is progressively revealed over conversation turns rather than given fully in one turn, leading LLMs lose roughly 39% performance on average. The paper attributes most of the degradation to unreliability and reports premature assumptions, early answer attempts, answer bloat, and failure to recover after wrong turns.

Sources:
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/59f6421e64707225fdf5b28840679a07-Abstract-Conference.html
- https://arxiv.org/abs/2505.06120

### Missing sentence attempted

The clean causal question looked excellent:

> Is the multi-turn failure caused mainly by fragmented user information, or by feeding the model its own premature assistant responses back as future context?

A decisive E01 would replay the exact same accumulated user shards while changing only assistant-side history: full history versus neutralized/omitted prior assistant turns, with length controls. This has the desired L32-like structure: same trajectories, inference-only intervention, one causal channel.

### Why it dies

A September-2026 successor now owns almost exactly this experiment and conclusion:

**Li et al., arXiv 2609.05882, *What if LLMs Ate Their Words: Causal History Effects in Multi-Turn Interaction*.** It retrospectively replays completed sharded trajectories while editing only assistant-generated history. Neutralizing prior assistant responses changes downstream performance even under length-matched controls; its `Turn Surgery` intervention changes one assistant turn at a time and finds beneficial interventions in a majority of selected degraded trajectories, including many fail→success reversals. It then links consequential history edits to downstream hidden-state changes in an open-weight model.

This is not merely a nearby mitigation paper: it directly performs the selective causal-history intervention that would have been our E01.

Other 2026 successors further crowd the parent with intent-mismatch explanations, curriculum-RL abstention/recovery training, and history condensation, so a generic `premature commitment causes multi-turn failure` study is no longer independently owned.

### Strongest reviewer compression

> `ICLR Outstanding gives the Lost-in-Conversation mother and premature-commitment hypothesis; Li et al. 2609.05882 directly edits/neutralizes assistant history and performs turn-level causal surgery = the proposed causal-channel localization.`

### Anti-resurrection

Do not reopen as `remove assistant history`, `self-generated context contamination`, `which previous assistant turn caused the failure`, `neutralize premature answers`, or `assistant history vs user history` unless a qualitatively different same-quantity contradiction appears beyond the September-2026 causal-history paper.
