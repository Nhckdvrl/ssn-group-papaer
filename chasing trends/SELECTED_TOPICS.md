# Selected Topics — chasing trends

Started: 2026-09-19

This file contains only formal chasing-trends candidates that have survived the current genealogy-first audit and are **PILOT-AUTHORIZED**.

Admission is deliberately strict:

- the topic must grow from a real literature pressure rather than a template;
- dangerous nearest priors must be read deeply enough to establish an honest ownership boundary;
- data / compute / recipe / engineering feasibility are part of topic quality;
- the first pilot must be cheap and discriminative;
- formal candidates do not remain in a vague SERIOUS/HOLD state: after audit they are either PILOT-AUTHORIZED or KILL.

---

## CT02 — Is Context Utility Rankable? Set-Dependent Routing for Sparse Attention

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Detailed registration:** `topics/CT02_IS_CONTEXT_UTILITY_RANKABLE.md`

### Mother question

Can sparse-attention context utility be represented by a single scalar ranking, or does the marginal value of a context block depend on which other blocks are already retained?

### Scientific pressure

Recent learned sparse-attention systems increasingly optimize **context ranking** itself. SAS shows that dense-attention ranking is misaligned with downstream utility and trains Qwen3 block routers directly from LM loss, but it still deploys a scalar score followed by Top-K and reuses the same gate checkpoints across multiple runtime budgets.

Formal nearby work improves how importance is learned, how sparsity evolves across layers/steps, how budget is allocated, or how dense attention is approximated. R-KV already adds redundancy to importance but still collapses the result into a scalar score before Top-K.

CT02 therefore audits a deeper shared assumption:

> **is context utility rankable at all?**

### Minimum identification

In a small candidate pool of context blocks, exactly enumerate subsets and measure:

- whether near-optimal subsets across budgets admit a nested chain;
- whether block marginal-utility rankings reverse as the retained set changes;
- scalar-ranking regret versus exact subset oracle;
- whether the effect survives downstream LM-loss intervention and is not explained by simple redundancy.

### Kill boundary

Kill if near-optimal subsets are overwhelmingly nested, SAS scalar ranking has negligible oracle regret, the effect is only semantic redundancy already covered by R-KV, real tasks do not reproduce synthetic interactions, or exploiting the effect destroys practical sparse-attention speed.

---

## CT03 — Counterfactual Credit for MoE Routing

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Detailed registration:** `topics/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md`

### Mother question

Can a pretrained sparse MoE router receive useful token-level credit for **unexecuted experts** without explicitly rerunning the downstream model for many alternative routes?

### Method thesis

Use one standard forward/backward pass plus a small number of local candidate-expert forwards to estimate the loss effect of replacing a routed expert:

[
\widehat{\Delta L}_{i\rightarrow j}
\approx
\nabla_h L^\top (h^{i\rightarrow j}-h).
]

Distill this approximate counterfactual utility into the routers, while retaining ordinary Top-K inference.

### Minimum identification

Before training the full method, calibrate the local estimator against exact alternative-route loss on hard reasoning tokens and multiple MoE layers. Continue only if it predicts beneficial replacements substantially better than router score / random baselines and yields a large supervision-cost reduction.

### Kill boundary

Kill if the estimator has weak exact-counterfactual fidelity, works only in the final layer, loses its efficiency after candidate expansion, or router-only adaptation fails to improve real reasoning benchmarks.

---

**Current selected topic count = 2.**
