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

**Current selected topic count = 1.**
