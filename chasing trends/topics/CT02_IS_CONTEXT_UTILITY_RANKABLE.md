# CT02 — Is Context Utility Rankable? Set-Dependent Routing for Sparse Attention

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Primary target:** ICLR / ICML / NeurIPS; ACL Main is plausible if the final story centers language/reasoning behavior.  
**Startup/HF trigger:** Tencent SAS public paper + Qwen3 AttnGate checkpoints/code.  
**Do not interpret this registration as authorization to build the full method before the diagnostic pilot survives.**

---

# 1. Mother question

Current sparse-attention systems usually reduce context selection to:

> assign each candidate token/block a scalar score → retain Top-K.

This assumes that a **ranking** is a sufficient representation of context utility.

CT02 asks:

> **Can the utility of context blocks actually be represented by one scalar ranking, or is sparse-attention utility intrinsically set-dependent because blocks can be redundant, complementary, or useful only conditional on what has already been retained?**

A particularly clean consequence is cross-budget nestedness.

For one score vector, Top-K sets must form a nested chain:

[
S_1 subset S_2 subset cdots subset S_K.
]

If the utility-optimal sparse subsets at different budgets do not admit even an approximately nested optimal chain, then no single budget-independent ranking can be jointly optimal across those budgets.

The broader question is not merely whether "diversity helps." It is:

> **when does the ranking abstraction itself stop being expressive enough for sparse context routing?**

---

# 2. Why now

## 2.1 Sparse attention is moving from heuristic selection to learned routing

Formal academic work has rapidly advanced sparse attention:

- **Native Sparse Attention** — ACL 2025 Best Paper  
  Natively trained, hardware-aligned hierarchical sparsity.
  https://aclanthology.org/2025.acl-long.1126/

- **SeerAttention-R: Sparse Attention Adaptation for Long Reasoning** — ICLR 2026  
  Lightweight self-distilled gating for long reasoning.
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/b56d827a2b8433517e722e0272c7f464-Abstract-Conference.html

- **vAttention: Verified Sparse Attention via Sampling** — ICLR 2026  
  Shows Top-K and sampling are complementary depending on the attention distribution and provides approximation guarantees.
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/55cb562b1f5af71f6707f3ff3c7941e6-Abstract-Conference.html

- **Evolving Sparsity** — ACL 2026 Main  
  Makes token importance dynamic across decoding steps and model layers.
  https://aclanthology.org/2026.acl-long.530/

- **The Sparse Frontier** — Findings ACL 2026  
  Systematically studies selection granularity, importance estimation, budget allocation, and cache management; finds fixed budgets increasingly suboptimal as sequence length grows.
  https://aclanthology.org/2026.findings-acl.1926/

This literature has made **which units to retain** a first-class algorithmic object.

## 2.2 SAS exposes a new failure of the current supervision target

**SAS: Simple Attention Sparsification via End-to-End Optimization of Context Ranking** (Tencent, arXiv 2026-09-11) keeps a pretrained Qwen3 backbone frozen and trains lightweight context routers directly from the LM loss rather than distilling dense-attention weights.

Its key result is:

> dense-attention ranking is not the same as downstream utility under a sparse budget.

SAS therefore upgrades the selector target from:

[
	ext{imitate dense attention}
]

to:

[
	ext{learn downstream-useful context ranking}.
]

Crucially, however, SAS still formulates sparse attention as **context ranking**:

[
s_i = R_	heta(q, B_i), quad S_K = operatorname{TopK}(s,K).
]

The public implementation trains with block size 64 and Top-K 31 historical blocks, while the released 4B/8B/14B gate checkpoints can be evaluated at 1024/2048/4096-token budgets without retraining.

Paper:
https://arxiv.org/abs/2609.13141

Code:
https://github.com/Tencent-Hunyuan/Simple-Attention-Sparsification

HF gates:
https://huggingface.co/tencent/Simple-Attention-Sparsification

This creates a precise next question:

> after fixing the **supervision target**, is the **ranking representation itself** still the correct abstraction?

---

# 3. Startup/HF inspiration → academic question

The startup/HF evidence is useful because SAS provides an unusually clean public instrument:

- Qwen3-4B / 8B / 14B;
- frozen dense backbones;
- router-only checkpoints;
- same selector architecture;
- full training/evaluation code;
- sparse SGLang backend;
- runtime-selectable attention budgets;
- a recent result showing ranking quality matters much more under tight budgets.

But the paper is only the trigger.

The academic ownership question is:

> **does sparse context utility obey the structural assumptions required by scalar Top-K routing?**

That question exists independently of Tencent/SAS.

---

# 4. Exact novelty boundary

## Not the claim

CT02 is **not**:

- dense attention is a bad supervision target;
- sparse attention needs better importance scores;
- token importance changes across time/layers;
- fixed budgets are bad;
- redundant tokens should be penalized;
- diversity-aware selection is useful;
- submodular/greedy selection is useful;
- a new Top-K scorer improves benchmarks.

All of those have nearby or direct prior art.

## The claim

The decisive unknown is:

> **whether per-query sparse-attention utility can be compressed into a single ranking at all.**

Operationally, CT02 tests two structural properties.

### A. Cross-budget nestedness

Let (U(S)) be the downstream utility of allowing a query to attend to block subset (S).

For each budget (k):

[
S_k^* in argmax_{|S|=k} U(S).
]

A single ranking can be simultaneously optimal across budgets only if there exists an optimal or near-optimal nested chain:

[
S_1^* subset S_2^* subset cdots.
]

CT02 asks how often this property fails and where.

### B. Conditional marginal utility

For block (i):

[
Delta_i(S)=U(Scup{i})-U(S).
]

If the ordering of (Delta_i(S)) and (Delta_j(S)) reverses as the already-selected set (S) changes, block utility is genuinely set-dependent.

This is stronger than:

> token i is globally redundant.

It says:

> whether i is worth selecting depends on what else has already been selected.

---

# 5. Dangerous nearest priors

## 5.1 SAS — closest immediate trigger

**What it owns**

- end-to-end LM-loss supervision for sparse context ranking;
- continuous soft gates through hard Top-K sparse training;
- strong controlled comparison against dense-attention distillation;
- public matched Qwen3 gate artifacts.

**What it does not currently ask**

- whether a ranking is a sufficient representation;
- whether optimal subsets across budgets are nested;
- whether marginal block value changes with the selected set;
- whether a set-conditioned selector is needed.

Important: SAS itself already notes that layer-wise attention distillation can miss cross-layer complementarity. CT02 is **not** relabeling that observation. CT02 targets the within-routing decision: whether selected context utility can be represented by one ordered list.

## 5.2 SeerAttention-R — ICLR 2026

Uses a learned self-distilled gate and sparse Top-K routing.

**Boundary:** improves how scalar importance is learned; does not test rankability/set-dependent marginal utility.

## 5.3 vAttention — ICLR 2026

Shows Top-K works best when attention is concentrated, while sampling is better when attention is diffuse; combines them with approximation guarantees.

**Boundary:** the target is reliable approximation of dense attention, not whether downstream-optimal context is a non-additive set function.

## 5.4 The Sparse Frontier — Findings ACL 2026

Shows sparse-attention behavior varies strongly with sequence length, task, granularity, and budget; fixed production budgets are often suboptimal.

**Boundary:** studies allocation and method trade-offs, not whether the per-query selected set is representable by one ranking.

## 5.5 Evolving Sparsity — ACL 2026 Main

Shows token importance evolves across decoding steps and layers.

**Boundary:** changes when/how a scalar importance signal is estimated; it does not ask whether utility conditional on the selected set invalidates scalar ranking.

## 5.6 R-KV — NeurIPS 2025

This is a critical collision.

R-KV explicitly shows that attention importance alone over-retains repetitive reasoning tokens. It adds a redundancy score based on key-vector similarities and uses:

[
Z_i=lambda I_i-(1-lambda)R_i,
]

then retains Top-K tokens.

Therefore:

> **"importance + redundancy" is already done and cannot be CT02's novelty.**

The remaining distinction is exact:

> R-KV compresses relational redundancy back into an unconditional per-token scalar and still performs Top-K. CT02 asks whether such scalarization itself loses conditional set utility.

Paper:
https://proceedings.neurips.cc/paper_files/paper/2025/hash/57e0358aed314784cad14a26e1eba642-Abstract-Conference.html

## 5.7 Learning What Matters — dangerous July 2026 preprint

**Learning What Matters: Supervising Sparse Attention Routing with Causal Evidence Sets** directly challenges attention distillation and trains routers from intervention-derived evidence sets.

It is especially dangerous because:

- it studies multi-hop evidence;
- its stronger router lets a block's score depend on other block summaries;
- it can represent multiple sufficient evidence sets.

However, its deployed router still ultimately returns Top-K blocks at a fixed ratio, and the paper does not appear to study:

- budget-nestedness of utility-optimal subsets;
- ranking reversals of conditional marginal utility;
- whether one ranking can serve multiple budgets;
- a set-conditioned sparse-attention decision rule.

It is currently an arXiv preprint, not the academic ownership anchor.

Paper:
https://arxiv.org/abs/2607.21692

### Novelty consequence

If this preprint or a successor is found to already test the same nestedness / set-dependent-utility question, CT02 is KILL.

---

# 6. Cross-domain prior: method idea is not novelty

Set-conditioned / diversity-aware selection already exists in adjacent domains.

Examples include:

- marginal-gain video-token selection;
- submodular visual-token selection;
- budget-adaptive relevance/coverage selection;
- submodular data selection;
- diversity-aware retrieval.

Therefore:

> **"use submodular selection" or "add diversity" is not a contribution.**

Cross-domain work is useful only to show that non-additive subset utility is algorithmically tractable.

CT02's academic contribution must begin with:

> the scalar-ranking abstraction used by internal LLM sparse attention is empirically insufficient.

Only then may a method follow.

---

# 7. Reviewer compression

## Compression 1

> "This is just R-KV with a fancier diversity score."

**Answer**

No. R-KV already proves redundancy matters, but collapses redundancy and importance into one scalar (Z_i) and applies Top-K.

CT02's decisive statistic is whether **conditional marginal rankings reverse** and whether **near-optimal subsets across budgets fail nestedness**. If those do not happen, CT02 dies even if a new diversity score improves accuracy.

## Compression 2

> "This is VLM/RAG submodular selection transplanted to sparse attention."

**Answer**

If the project begins by importing a greedy/submodular selector, this criticism is correct and the topic should be killed.

The project only survives if independent internal-attention interventions first establish that:

- current ranking-based routers have measurable representational regret;
- the regret is predicted by set interaction, not generic semantic diversity;
- the phenomenon appears in real LLM sparse-attention states.

## Compression 3

> "Just make the router budget-conditioned."

**Answer**

Budget conditioning is sufficient only if failures are mainly cross-budget nonnestedness and a separate scalar ranking per budget closes the oracle gap.

If conditional marginal ranking reversals persist **within the same budget**, the problem is deeper: utility depends on the already selected set.

The pilot explicitly separates these two worlds.

---

# 8. Competing explanations

The first experiment must distinguish at least four possibilities.

## H1 — Ranking is essentially sufficient

Near-optimal subsets admit nested chains; SAS/R-KV-style rankings lose little.

**Consequence:** KILL.

## H2 — Only budget dependence matters

Optimal sets differ across budgets, but a budget-conditioned scalar scorer explains almost all regret.

**Consequence:** project may shrink to budget-conditioned routing; only continue if this remains academically distinct after prior audit.

## H3 — Redundancy explains the gap

Set dependence is mostly duplicate suppression and R-KV-like scalar redundancy closes it.

**Consequence:** KILL as already-covered mechanism unless a substantially different structural result remains.

## H4 — Genuine conditional complementarity exists

The marginal value of a block changes with which other blocks are retained; ranking reversals persist after accounting for simple redundancy and budget.

**Consequence:** strongest CT02 world. A set-conditioned routing rule is justified.

---

# 9. Minimum pilot

## 9.1 Model / artifact

Primary:

- Qwen3-4B dense backbone;
- released SAS Qwen3-4B AttnGate checkpoint;
- SAS block size 64;
- no backbone training.

Do **not** retrain SAS for the first pilot.

## 9.2 Data

Use existing datasets only.

Primary real tasks:

- LongBench multi-document QA subsets such as 2WikiMultihopQA / MuSiQue / HotpotQA-compatible tasks;
- a small reasoning-prefix sample from MATH/GPQA if needed to test generated-history context.

Synthetic examples may be used only as sanity checks for:
- redundant evidence;
- complementary two-hop evidence;
- distractors.

Synthetic data is not the paper contribution.

## 9.3 Local candidate pool

For a sampled query/head/layer:

1. obtain SAS block scores;
2. build a manageable candidate pool (Mapprox8	ext{–}12) from high-scoring blocks plus controlled alternatives;
3. cache Q/K/V;
4. enumerate subsets for small (k) or all (2^M) subsets where feasible.

This avoids a combinatorial full-context search while still exactly testing the ranking assumption inside a local routing decision.

## 9.4 Utility

Measure at two levels.

### Cheap local utility

Restricted-attention output error relative to the dense attention output.

Purpose:
> high-throughput discovery, not final causal claim.

### Downstream calibrated utility

For selected states, patch the chosen attention subset and continue the frozen model forward.

Measure:

- gold next-token / target-span NLL;
- correct-answer log probability where defined;
- optionally downstream generation on a small validation subset.

Purpose:
> verify that local set-interaction signals predict actual model behavior.

## 9.5 Core diagnostics

### Nested-optimal-chain violation

For budgets (k=1,ldots,K), enumerate near-optimal subsets.

Ask:

> does there exist an (epsilon)-optimal nested chain?

This is more robust than comparing one arbitrarily chosen optimum under ties.

### Ranking regret

Compare utility of:

- SAS Top-K;
- dense-attention Top-K;
- R-KV-style importance-minus-redundancy score;
- budget-specific scalar oracle/ranker where possible;
- exact subset oracle in the small candidate pool.

### Conditional ranking reversal

Measure how often:

[
Delta_i(S_1)>Delta_j(S_1)
]

but

[
Delta_i(S_2)<Delta_j(S_2).
]

### Interaction strength

Measure pairwise conditional interaction:

[
I_{ij}(S)=Delta_i(Scup{j})-Delta_i(S).
]

Do not call every nonzero interaction a mechanism. The key question is whether it produces meaningful ranking regret.

---

# 10. Pilot success criteria

Continue only if all are broadly true:

1. **Robust non-rankability**  
   A substantial fraction of real-task states lack an approximately optimal nested chain under tight budgets.

2. **Material regret**  
   The best set-aware oracle materially beats SAS/dense-attention scalar Top-K within the same candidate pool.

3. **Not just redundancy**  
   R-KV-style redundancy correction does not close most of the gap.

4. **Downstream calibration**  
   Local set-interaction diagnostics predict target-token loss / real model behavior.

5. **Structured boundary**  
   Violations concentrate in interpretable regimes such as multi-hop/complementary evidence or very tight budgets rather than appearing as noise everywhere.

---

# 11. Hard kill conditions

KILL CT02 if any of these occurs:

- >=90–95% of relevant states admit near-optimal nested chains;
- SAS scalar ranking is already within negligible regret of the exact subset oracle;
- apparent interaction disappears under downstream intervention;
- the only robust effect is semantic redundancy already captured by R-KV-like scoring;
- real LongBench/reasoning states do not reproduce the synthetic effect;
- a direct recent paper already studies sparse-attention rankability/nestedness/set-dependent marginal utility;
- the method required to exploit the effect adds enough sequential/selection overhead to erase realistic sparse-attention speed gains;
- the story collapses into "another diversity-aware token selector."

Do not rescue with:
- more benchmarks;
- a larger model zoo;
- a new dataset;
- a generic submodular objective;
- an expensive agent environment.

---

# 12. Growth path if the pilot survives

The full project should grow in this order.

## Part I — Scientific diagnosis

Establish:

> scalar Top-K ranking has a measurable representational limitation.

Main figures:

- nestedness violation vs attention budget;
- scalar-ranking regret vs interaction strength;
- task/layer/head distribution.

## Part II — Explain the failure

Separate:

- redundancy;
- complementarity;
- budget dependence;
- attention-softmax effects;
- multi-hop evidence structure.

The paper should identify which one actually predicts regret.

## Part III — Method, only after diagnosis

Two possible methods depending on the pilot.

### World A — budget dependence dominates

Use a lightweight budget-conditioned router:

[
s_i = R_	heta(q,B_i,k).
]

### World B — genuine set dependence survives

Use a set-conditioned marginal router.

A hardware-conscious design would likely be two-stage:

1. cheap SAS-style scalar prefilter to (M) candidates;
2. low-dimensional conditional correction / marginal-gain selection among those candidates.

The second stage must remain far cheaper than the sparse attention it saves.

Do not commit to "submodular" or a specific pairwise formula before the empirical structure is known.

## Part IV — Standard validation

Compare against:

- full attention;
- SAS;
- SeerAttention-R;
- strong training-free sparse attention;
- R-KV where the decoding/KV setting is comparable;
- any new direct prior found during execution.

Use:

- reasoning;
- long-context QA;
- optionally one tool/function benchmark only if evaluator cost is controlled.

Benchmark gain validates the formulation; it is not the mother contribution.

---

# 13. Expected main knowledge sentence

The strongest possible paper sentence is:

> **Sparse-attention context utility is not generally rankable: under tight budgets and compositional evidence, block marginal utility changes with the retained set, so no budget-independent Top-K ranking can recover near-optimal sparse context; modeling conditional set utility closes this structural gap.**

A weaker but still potentially publishable world is:

> one global ranking is insufficient across budgets, but budget-conditioned rankings are enough.

That weaker world needs another novelty audit before method development.

---

# 14. Data / compute / engineering audit

## Pilot

Cheap relative to typical sparse-attention training:

- frozen Qwen3-4B;
- public 33M-parameter SAS router;
- no SFT/RL/pretraining;
- Q/K/V capture + subset enumeration in a small local candidate pool;
- targeted downstream forward interventions.

The pilot should fit comfortably on a single modern high-memory GPU; parallel GPUs only accelerate state collection.

## Full method

Only after survival:

- train router only, keep backbone frozen;
- start with Qwen3-4B;
- do not reproduce SAS's full 4B/8B/14B matrix initially;
- require wall-clock/selector-overhead accounting, not just FLOPs.

The public SAS code already exposes:
- training recipes;
- AttnGate architecture;
- Qwen3 checkpoints;
- SGLang sparse backend;
- reasoning/LongBench evaluation.

This substantially lowers engineering risk.

---

# 15. Specialized audits triggered

From `framework/SPECIALIZED_AUDITS.md`:

- **Public Artifact Maturity:** A — runnable code and router checkpoints.
- **Proxy Fidelity:** local attention-output subset oracle must be calibrated to downstream LM loss.
- **Real Resource, Not Proxy Resource:** method must report selector overhead and actual sparse-attention speed.
- **Trend Maturity:** sparse attention is highly crowded; a generic selector variant is not enough.
- **Mechanism Composition:** if pairwise/budget modules are combined, each must correspond to a measured failure source.
- **Representation × Consumer:** dense-attention approximation and downstream task utility must remain distinct quantities.

---

# 16. Why this is a startup/HF-inspired topic rather than a startup patch

The startup/HF artifact contributes three things:

1. a **changed premise** — end-to-end LM-loss routing makes dense-attention imitation no longer the dominant bottleneck;
2. a **public instrument** — matched frozen backbones and tiny released gate checkpoints;
3. a **serving fact** — one selector is explicitly reused at multiple runtime budgets.

The scientific question then moves one level down:

> not "what score should the selector learn?"  
> but "is a score ranking expressive enough to represent sparse context utility?"

That question is judged against formal ACL/ICLR/NeurIPS sparse-attention literature, not against startup novelty.

---

# 17. Verdict

> **PILOT-AUTHORIZED**

Reason:

- the pressure is current and real;
- the startup artifact materially lowers pilot cost;
- formal academic nearest priors are strong but do not appear to answer the same decisive unknown;
- R-KV and cross-domain diversity selection sharply constrain the novelty boundary rather than killing it;
- the decisive pilot is inference-only and can kill the topic cheaply;
- if the phenomenon survives, the method follows from a structural failure of the current Top-K routing abstraction rather than from arbitrary module invention.

The first task is **not** to train a set-aware router.

The first task is:

> **measure whether sparse-attention utility is rankable.**
