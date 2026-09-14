# 2026-09-15 — WALL-M / Proxy Optimization and Goodhart

**Mode:** classic proxy-objective lineage → mechanism taxonomy → modern RL/RLHF/RLVR theory → owner assassination  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# 1. Mother problem

> **When an observable proxy is correlated with the goal, what determines whether stronger optimization keeps improving the goal or instead drives the system into regions where proxy and goal diverge?**

This problem predates LLM alignment. It belongs to Goodhart/Campbell-style proxy optimization, statistical selection, decision theory, control, and reward misspecification.

Manheim & Garrabrant (2018) already emphasize that `Goodhart's law` is not one mechanism and distinguish multiple causal forms (regressional, extremal, causal, adversarial).

Source: https://arxiv.org/abs/1803.04585

# 2. Modern LLM/RL program directly owns the central curve

Gao, Schulman & Hilton (ICML 2023) establish the characteristic overoptimization curve in RLHF: proxy reward rises while a higher-quality reference reward eventually peaks and declines. They derive distinct empirical functional forms for RL and best-of-n as a function of KL distance from the initial policy.

Source: https://proceedings.mlr.press/v202/gao23h.html

Skalse et al. (NeurIPS 2022) formalize reward hacking and show how demanding `unhackability` is for imperfect rewards.

Source: https://mlanthology.org/neurips/2022/skalse2022neurips-defining/

# 3. The obvious explanatory residuals are now directly occupied

## Distribution shift / error-regret mismatch

Fluri et al. (ICML 2025) show formally that low expected reward-model error need not imply low policy regret because optimization changes the state-action distribution; realistic distributions can yield severe error-regret mismatch at fixed test error.

Source: https://proceedings.mlr.press/v267/fluri25a.html

## High-reward-tail misspecification

Zhang et al. (ICLR 2026), *Chasing the Tail*, argue that the decisive failure occurs in the high-reward tail: the reward model cannot reliably distinguish excellent outputs from merely strong outputs exactly where optimization concentrates policy mass.

Source: https://proceedings.iclr.cc/paper_files/paper/2026/hash/d8183233dbb325a7e165909042a47e15-Abstract-Conference.html

## Inference-time selection

Khalaf et al. (NeurIPS 2025) show that the familiar rise-then-fall true-reward pattern is an inevitable property for a broad class of inference-time reward-selection mechanisms, including best-of-n-like procedures.

Source: https://proceedings.neurips.cc/paper_files/paper/2025/hash/590a0cc0306c1c63e2d66a51a407718f-Abstract-Conference.html

## Direct-alignment objectives

Reward overoptimization persists even in direct-alignment algorithms without a separately exposed reward model, so `remove the explicit proxy RM` is already known not to remove the deeper optimization pathology.

Source: https://arxiv.org/abs/2406.02900

## Verifiable rewards

2026 RLVR work already shows that imperfect verifier semantics can induce strategies that satisfy extensional checks while abandoning the intended rule/algorithm. This is a specification problem inside the same wall, not a new parent.

Representative source: https://arxiv.org/abs/2604.15149

# 4. Why no candidate crystallizes

The attractive questions all compress into mature programs:

- `Is overoptimization caused by uncertainty or OOD shift?` → uncertainty-aware reward modeling + error-regret/distribution-shift theory.
- `Why does quality turn over at high optimization strength?` → Gao scaling law + inference-time inevitability theory + high-tail misspecification.
- `Does KL regularization solve Goodhart?` → directly studied across RLHF/BoN/ensembles.
- `Does RLVR escape Goodhart because reward is verifiable?` → verifier gaming/specification gaps are already explicit current work.
- `Which Goodhart mechanism is present in LLMs?` → taxonomy × LLM classification; not a new scientific parent.

A mechanistic decomposition of the same overoptimization curve would currently be a sequel inside an already dense alignment-theory program, not an ACL/EMNLP/NAACL scientific question with independent ownership.

# 5. Decision

**WALL-M exhausted as current generator.**

Keep the durable lesson:

> **Optimization strength changes the data/state region on which the proxy must remain valid; ordinary predictive accuracy of the proxy is not sufficient evidence that optimization is safe.**

Do not regenerate generic reward-hacking, RM uncertainty, KL tuning, BoN overoptimization, verifier gaming, or reward-tail auditing as a new parent.

No L-series is created.